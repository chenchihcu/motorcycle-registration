"""第三方登入 OAuth 路由 — Google / Apple / Line"""
import os
import secrets
from flask import Blueprint, redirect, url_for, flash, request, current_app
from flask_login import login_user, current_user
from authlib.integrations.flask_client import OAuth
from models import db, User

oauth_bp = Blueprint("oauth", __name__, url_prefix="/oauth")

_oauth = None


def init_oauth(app):
    global _oauth
    _oauth = OAuth(app)

    # Google OAuth
    _oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
        client_kwargs={"scope": "openid email profile"},
    )

    # Apple OAuth
    _oauth.register(
        name="apple",
        server_metadata_url="https://appleid.apple.com/.well-known/openid-configuration",
        client_id=os.getenv("APPLE_CLIENT_ID", ""),
        client_secret=os.getenv("APPLE_CLIENT_SECRET", ""),
        client_kwargs={"scope": "name email"},
    )

    # Line OAuth
    _oauth.register(
        name="line",
        authorize_url="https://access.line.me/oauth2/v2.1/authorize",
        access_token_url="https://api.line.me/oauth2/v2.1/token",
        client_id=os.getenv("LINE_CHANNEL_ID", ""),
        client_secret=os.getenv("LINE_CHANNEL_SECRET", ""),
        client_kwargs={
            "scope": "openid profile email",
            "token_endpoint_auth_method": "client_secret_post",
        },
        userinfo_endpoint="https://api.line.me/v2/profile",
    )


@oauth_bp.route("/login/<provider>")
def login(provider):
    if current_user.is_authenticated:
        return redirect(url_for("bulletin.dashboard"))
    if _oauth is None or provider not in ["google", "apple", "line"]:
        flash("不支援的登入方式", "error")
        return redirect(url_for("auth.login"))
    redirect_uri = url_for("oauth.callback", provider=provider, _external=True)
    return _oauth.create_client(provider).authorize_redirect(redirect_uri)


@oauth_bp.route("/callback/<provider>")
def callback(provider):
    if _oauth is None or provider not in ["google", "apple", "line"]:
        flash("登入失敗：不支援的登入方式", "error")
        return redirect(url_for("auth.login"))

    try:
        token = _oauth.create_client(provider).authorize_access_token()
    except Exception as e:
        current_app.logger.error(f"OAuth {provider} token error: {e}")
        flash(f"{provider} 登入驗證失敗", "error")
        return redirect(url_for("auth.login"))

    # 取得使用者資訊
    try:
        if provider == "line":
            userinfo = token.get("userinfo") or {}
            oauth_id = userinfo.get("sub", token.get("id_token", ""))
            name = userinfo.get("name", f"Line_{oauth_id[:8]}")
            email = userinfo.get("email", "")
        elif provider == "apple":
            userinfo = token.get("userinfo") or {}
            oauth_id = userinfo.get("sub", token.get("id_token", "")[:20])
            name = userinfo.get("name", {}).get("firstName", "") or f"Apple_{oauth_id[:8]}"
            email = userinfo.get("email", "")
        else:
            userinfo = token.get("userinfo") or {}
            oauth_id = userinfo.get("sub", "")
            name = userinfo.get("name", f"Google_{oauth_id[:8]}")
            email = userinfo.get("email", "")
    except Exception as e:
        current_app.logger.error(f"OAuth {provider} userinfo error: {e}")
        flash("取得使用者資訊失敗", "error")
        return redirect(url_for("auth.login"))

    if not oauth_id:
        flash("登入失敗：無法取得身份識別", "error")
        return redirect(url_for("auth.login"))

    # 查詢或建立使用者
    user = User.query.filter_by(oauth_provider=provider, oauth_id=oauth_id).first()
    if not user:
        # 嘗試用 email 找既有帳號
        if email:
            user = User.query.filter_by(username=email.split("@")[0]).first()
        if not user:
            # 自動註冊
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
