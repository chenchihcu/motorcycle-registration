import os
from flask import Flask, render_template, redirect, url_for, request
from flask_login import current_user
from config import get_config
from models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())
    db.init_app(app)

    with app.app_context():
        db.create_all()

        # --- Migration: copy old event_date → event_date_start/end ---
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            cols = {c["name"] for c in inspector.get_columns("events")}
            if "event_date_start" not in cols:
                db.session.execute(text(
                    "ALTER TABLE events ADD COLUMN event_date_start DATE"
                ))
                db.session.execute(text(
                    "UPDATE events SET event_date_start = event_date WHERE event_date_start IS NULL"
                ))
                db.session.commit()
                print("[migration] added event_date_start column")
            if "event_date_end" not in cols:
                db.session.execute(text(
                    "ALTER TABLE events ADD COLUMN event_date_end DATE"
                ))
                db.session.execute(text(
                    "UPDATE events SET event_date_end = event_date_start WHERE event_date_end IS NULL"
                ))
                db.session.commit()
                print("[migration] added event_date_end column")
        except Exception as e:
            print(f"[migration] skip: {e}")

        # --- Migration: Google OAuth profile/contact fields ---
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            cols = {c["name"] for c in inspector.get_columns("users")}
            user_columns = {
                "email": "VARCHAR(255)",
                "phone": "VARCHAR(30)",
                "emergency_contact_name": "VARCHAR(100)",
                "emergency_contact_phone": "VARCHAR(30)",
                "profile_completed_at": "TIMESTAMP",
                "last_login_at": "TIMESTAMP",
            }
            for column, column_type in user_columns.items():
                if column not in cols:
                    db.session.execute(text(
                        f"ALTER TABLE users ADD COLUMN {column} {column_type}"
                    ))
                    print(f"[migration] added users.{column} column")
            db.session.execute(text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_oauth_identity "
                "ON users (oauth_provider, oauth_id) "
                "WHERE oauth_provider IS NOT NULL AND oauth_id IS NOT NULL"
            ))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"[migration] user profile fields skip: {e}")

        # --- Migration: Google identity replaces per-IP registration uniqueness ---
        try:
            if db.engine.dialect.name == "postgresql":
                from sqlalchemy import text
                db.session.execute(text(
                    "ALTER TABLE registrations DROP CONSTRAINT IF EXISTS uq_event_ip"
                ))
                db.session.commit()
                print("[migration] dropped registrations.uq_event_ip constraint")
        except Exception as e:
            db.session.rollback()
            print(f"[migration] drop uq_event_ip skip: {e}")

        # 自動建立預設管理員（如尚未存在）
        try:
            from werkzeug.security import generate_password_hash
            from models import User
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    password_hash=generate_password_hash('admin123'),
                    name='管理員',
                    license_plate='ADMIN-001',
                    role='admin',
                )
                db.session.add(admin)
                db.session.commit()
                print('[startup] OK 預設管理員 admin 已建立')
        except Exception as e:
            print(f'[startup] WARN 建立管理員失敗: {e}')

        # 自動建立測試資料（僅首次安裝用，偵測 events 為空時）
        try:
            from models import Event
            if Event.query.count() == 0:
                import seed_data
                seed_data.seed_with_current_app()
                print('[startup] OK 測試資料已建立（20 events + 5 users + registrations）')
        except Exception as e:
            print(f'[startup] WARN 建立測試資料失敗: {e}')

    from routes.auth import auth_bp, init_login_manager
    from routes.oauth import oauth_bp
    from routes.events import events_bp
    from routes.registration import registration_bp
    from routes.bulletin import bulletin_bp
    from routes.message import message_bp
    from routes.admin import admin_bp
    from routes.user import user_bp, members_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(registration_bp)
    app.register_blueprint(bulletin_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(members_bp)

    init_login_manager(app)
    from routes.oauth import init_oauth
    init_oauth(app)

    @app.before_request
    def require_complete_profile():
        allowed_endpoints = {
            "static",
            "oauth.complete_profile",
            "auth.logout",
        }
        if (
            current_user.is_authenticated
            and not current_user.has_complete_profile()
            and request.endpoint not in allowed_endpoints
        ):
            return redirect(url_for("oauth.complete_profile"))

    @app.context_processor
    def inject_globals():
        import datetime
        from models import Message
        ctx = {
            "app_name": app.config.get("APP_NAME", "重機車隊報名系統"),
            "current_year": datetime.datetime.now().year,
        }
        # 未讀通知計數（全域 navbar badge）
        try:
            from flask_login import current_user
            if current_user.is_authenticated:
                ctx["unread_count"] = Message.query.filter_by(
                    user_id=current_user.id, is_read=False, reply_to_id=None
                ).count()
            else:
                ctx["unread_count"] = 0
        except Exception:
            ctx["unread_count"] = 0
        return ctx

    # 一鍵建立大量測試資料（僅首次安裝用，受 secret key 保護）
    @app.route('/seed-data/<secret>')
    def seed_data(secret):
        if secret != app.config.get('SECRET_KEY', 'dev')[:16]:
            return 'Invalid key', 403
        try:
            import seed_data
            seed_data.seed()
            return 'Seed data created', 200
        except Exception as e:
            return f'Seed error: {e}', 500

    # 一鍵建立預設管理員（僅在無管理員時可呼叫，首次安裝用）
    @app.route('/setup-admin')
    def setup_admin():
        from models import User
        from werkzeug.security import generate_password_hash
        if User.query.filter_by(username='admin').first():
            return 'Admin already exists', 200
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            name='管理員',
            license_plate='ADMIN-001',
            role='admin',
        )
        db.session.add(admin)
        db.session.commit()
        return 'Admin created: admin / admin123', 200

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
