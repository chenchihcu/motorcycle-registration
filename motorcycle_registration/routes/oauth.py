"""第三方登入 OAuth 路由 — Google / Line (Apple 已移除)"""
import os
import secrets
from flask import Blueprint, redirect, url_for, flash, request, current_app
from flask_login import login_user, current_user
from authlib.integrations.flask_client import OAuth
from models import db, User

oauth_bp = Blueprint("oauth", __name__, url_prefix="/oauth")

_oauth = None

# 有設定憑證的 providers 清單，由 init_oauth() 填入
active_providers: list[str] = []

# 各 provider 的環境變數對照
_PROVIDER_CONFIGS: dict[str, dict] = {
    "google": {
        "env_client_id": "GOOGLE_CLIENT_ID",
        "env_client_secret": "GOOGLE_CLIENT_SECRET",
        "register_kwargs": {
            "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
            "client_kwargs": {"scope": "openid email profile"},
        },
    },
    "line": {
        "env_client_id": "LINE_CHANNEL_ID",
        "env_client_secret": "LINE_CHANNEL_SECRET",
        "register_kwargs": {
            "authorize_url": "https://access.line.me/oauth2/v2.1/authorize",
            "access_token_url": "https://api.line.me/oauth2/v2.1/token",
            "client_kwargs": {
                "scope": "openid profile email",
                "token_endpoint_auth_method": "client_secret_post",
            },
            "userinfo_endpoint": "https://api.line.me/v2/profile",
        },
    },
}

_ALLOWED_PROVIDERS = frozenset(["google", "line"])


def init_oauth(app):
    global _oauth, active_providers
    _oauth = OAuth(app)
    active_providers = []

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


@oauth_bp.route("/login/<provider>")
def login(provider):
    if current_user.is_authenticated:
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

    # 取得使用者資訊
    try:
        userinfo = token.get("userinfo") or {}

        if provider == "line":
            oauth_id = userinfo.get("sub", token.get("id_token", ""))
            name = userinfo.get("name", f"Line_{oauth_id[:8]}")
            email = userinfo.get("email", "")
        else:  # google
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

    # 查詢或建立使用者
    user = User.query.filter_by(oauth_provider=provider, oauth_id=oauth_id).first()
    if not user:
        if email:
            user = User.query.filter_by(username=email.split("@")[0]).first()
        if not user:
            safe_username = f"{provider}_{oauth_id[:12]}"
            user = User(
                username=safe_username,
                password_hash=secrets.token_hex(32),
                name=name or f"{provider.title()}用戶",
                license_plate=f"{provider.upper()}-{oauth_id[:6].upper()}",
                oauth_provider=provider,
                oauth_id=oauth_id,
                role="user",
            )
            db.session.add(user)
        else:
            user.oauth_provider = provider
            user.oauth_id = oauth_id
        db.session.commit()

    from routes.auth import LoginUser
    login_user(LoginUser(user))
    flash(f"{provider} 登入成功", "success")
    return redirect(url_for("bulletin.dashboard"))
