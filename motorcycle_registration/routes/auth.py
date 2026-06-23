from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timezone
from models import db, User
from forms import LoginForm
from routes.oauth import active_providers

auth_bp = Blueprint("auth", __name__)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "請先登入"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def init_login_manager(app):
    login_manager.init_app(app)


def _safe_next(default_endpoint="bulletin.dashboard"):
    next_page = request.args.get("next")
    if next_page and next_page.startswith("/") and not next_page.startswith("//"):
        return next_page
    return url_for(default_endpoint)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if not current_user.has_complete_profile():
            return redirect(url_for("oauth.complete_profile"))
        return redirect(url_for("bulletin.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.role == "admin" and check_password_hash(user.password_hash, form.password.data):
            user.last_login_at = datetime.now(timezone.utc)
            db.session.commit()
            login_user(user)
            return redirect(_safe_next())
        if user and user.role != "admin":
            flash("一般使用者請使用 Google 登入", "error")
        else:
            flash("管理員帳號或密碼錯誤", "error")

    return render_template("login.html", form=form, oauth_providers=active_providers)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("bulletin.dashboard"))
    flash("一般使用者請使用 Google 帳號登入並補齊報名資料", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("已登出", "success")
    return redirect(url_for("auth.login"))
