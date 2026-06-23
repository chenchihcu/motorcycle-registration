"""Google OAuth routes for public user login."""
import os
import secrets
from datetime import datetime, timezone
from flask import Blueprint, redirect, url_for, flash, request, current_app, session, render_template
from flask_login import login_user, current_user
from authlib.integrations.flask_client import OAuth
from werkzeug.security import generate_password_hash
from models import db, User
from forms import ProfileCompletionForm

oauth_bp = Blueprint("oauth", __name__, url_prefix="/oauth")

_oauth = None

# 有設定憑證的 providers 清單，由 init_oauth() 填入。
active_providers: list[str] = []
_PENDING_GOOGLE_PROFILE = "pending_google_profile"
_OAUTH_NEXT = "oauth_next"

_PROVIDER_CONFIGS: dict[str, dict] = {
    "google": {
        "env_client_id": "GOOGLE_CLIENT_ID",
        "env_client_secret": "GOOGLE_CLIENT_SECRET",
        "register_kwargs": {
            "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
            "client_kwargs": {"scope": "openid email profile"},
        },
    },
}

_ALLOWED_PROVIDERS = frozenset(["google"])


def init_oauth(app):
    global _oauth
    _oauth = OAuth(app)
    active_providers.clear()

    for provider, cfg in _PROVIDER_CONFIGS.items():
        client_id = os.getenv(cfg["env_client_id"], "")
        client_secret = os.getenv(cfg["env_client_secret"], "")

        if not client_id or not client_secret:
            app.logger.warning(
                "OAuth %s: 未設定 %s / %s，已跳過註冊",
                provider, cfg["env_client_id"], cfg["env_client_secret"],
            )
            continue

        _oauth.register(
            name=provider,
            client_id=client_id,
            client_secret=client_secret,
            **cfg["register_kwargs"],
        )
        active_providers.append(provider)

    app.logger.info("OAuth active providers: %s", active_providers)


def _safe_next(default_endpoint="bulletin.dashboard"):
    next_page = session.pop(_OAUTH_NEXT, None) or request.args.get("next")
    if next_page and next_page.startswith("/") and not next_page.startswith("//"):
        return next_page
    return url_for(default_endpoint)


def _unique_google_username(oauth_id):
    base = f"google_{oauth_id[:12]}"
    candidate = base
    suffix = 1
    while User.query.filter_by(username=candidate).first():
        suffix += 1
        candidate = f"{base}_{suffix}"
    return candidate


def _apply_profile_form(user, form):
    user.name = form.name.data.strip()
    user.license_plate = form.license_plate.data.strip().upper()
    user.phone = form.phone.data.strip()
    user.emergency_contact_name = form.emergency_contact_name.data.strip()
    user.emergency_contact_phone = form.emergency_contact_phone.data.strip()
    user.mark_profile_complete_if_ready()


@oauth_bp.route("/login/<provider>")
def login(provider):
    if current_user.is_authenticated:
        if not current_user.has_complete_profile():
            return redirect(url_for("oauth.complete_profile"))
        return redirect(url_for("bulletin.dashboard"))

    if provider not in _ALLOWED_PROVIDERS:
        flash("不支援的登入方式", "error")
        return redirect(url_for("auth.login"))

    if provider not in active_providers:
        flash(f"{provider} 登入尚未設定（缺少憑證）", "error")
        return redirect(url_for("auth.login"))

    if _oauth is None:
        flash("OAuth 尚未初始化", "error")
        return redirect(url_for("auth.login"))

    next_page = request.args.get("next")
    if next_page and next_page.startswith("/") and not next_page.startswith("//"):
        session[_OAUTH_NEXT] = next_page

    redirect_uri = url_for("oauth.callback", provider=provider, _external=True)
    return _oauth.create_client(provider).authorize_redirect(redirect_uri)


@oauth_bp.route("/callback/<provider>")
def callback(provider):
    if provider not in _ALLOWED_PROVIDERS:
        flash("登入失敗：不支援的登入方式", "error")
        return redirect(url_for("auth.login"))

    if provider not in active_providers:
        flash(f"{provider} 登入尚未設定（缺少憑證）", "error")
        return redirect(url_for("auth.login"))

    try:
        token = _oauth.create_client(provider).authorize_access_token()
    except Exception as e:
        current_app.logger.error(f"OAuth {provider} token error: {e}")
        flash(f"{provider} 登入驗證失敗，請稍後再試", "error")
        return redirect(url_for("auth.login"))

    try:
        client = _oauth.create_client(provider)
        userinfo = token.get("userinfo") or {}
        if not userinfo:
            userinfo = client.userinfo()
        oauth_id = userinfo.get("sub", "")
        name = userinfo.get("name", f"Google_{oauth_id[:8]}")
        email = userinfo.get("email", "")
    except Exception as e:
        current_app.logger.error(f"OAuth {provider} userinfo error: {e}")
        flash("取得使用者資訊失敗", "error")
        return redirect(url_for("auth.login"))

    if not oauth_id:
        flash(f"{provider} 登入失敗：無法取得身份識別", "error")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(oauth_provider=provider, oauth_id=oauth_id).first()
    if user:
        if email and not user.email:
            user.email = email
        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()
        login_user(user)
        if not user.has_complete_profile():
            flash("請先補齊報名必要資料", "info")
            return redirect(url_for("oauth.complete_profile"))
        flash("Google 登入成功", "success")
        return redirect(_safe_next())

    session[_PENDING_GOOGLE_PROFILE] = {
        "oauth_provider": provider,
        "oauth_id": oauth_id,
        "email": email,
        "name": name,
    }
    flash("請先補齊報名必要資料", "info")
    return redirect(url_for("oauth.complete_profile"))


@oauth_bp.route("/complete-profile", methods=["GET", "POST"])
def complete_profile():
    pending = session.get(_PENDING_GOOGLE_PROFILE)

    if current_user.is_authenticated:
        form = ProfileCompletionForm(obj=current_user)
    elif pending:
        form = ProfileCompletionForm(data={"name": pending.get("name", "")})
    else:
        flash("請先使用 Google 登入", "error")
        return redirect(url_for("auth.login"))

    if form.validate_on_submit():
        if current_user.is_authenticated:
            user = User.query.get(current_user.id)
        else:
            pending = session.get(_PENDING_GOOGLE_PROFILE)
            if not pending:
                flash("登入資料已逾時，請重新使用 Google 登入", "error")
                return redirect(url_for("auth.login"))

            user = User.query.filter_by(
                oauth_provider=pending["oauth_provider"],
                oauth_id=pending["oauth_id"],
            ).first()
            if not user:
                user = User(
                    username=_unique_google_username(pending["oauth_id"]),
                    password_hash=generate_password_hash(secrets.token_urlsafe(32)),
                    email=pending.get("email") or None,
                    name=form.name.data.strip(),
                    license_plate=form.license_plate.data.strip().upper(),
                    oauth_provider=pending["oauth_provider"],
                    oauth_id=pending["oauth_id"],
                    role="user",
                )
                db.session.add(user)

        _apply_profile_form(user, form)
        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()
        session.pop(_PENDING_GOOGLE_PROFILE, None)
        login_user(user)
        flash("資料已完成，您可以開始報名活動", "success")
        return redirect(_safe_next())

    return render_template("complete_profile.html", form=form)
