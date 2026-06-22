from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from models import db, User
from forms import LoginForm, RegisterForm

auth_bp = Blueprint("auth", __name__)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "請先登入"


class LoginUser(UserMixin):
    def __init__(self, user):
        self.id = user.id
        self.username = user.username
        self.name = user.name
        self.license_plate = user.license_plate
        self.role = user.role


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if user:
        return LoginUser(user)
    return None


def init_login_manager(app):
    login_manager.init_app(app)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("bulletin.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(LoginUser(user))
            next_page = request.args.get("next")
            return redirect(next_page or url_for("bulletin.dashboard"))
        flash("帳號或密碼錯誤", "error")
    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("bulletin.dashboard"))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("帳號已存在", "error")
            return render_template("register.html", form=form)
        user = User(
            username=form.username.data,
            password_hash=generate_password_hash(form.password.data),
            name=form.name.data,
            license_plate=form.license_plate.data,
        )
        db.session.add(user)
        db.session.commit()
        flash("註冊成功，請登入", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("已登出", "success")
    return redirect(url_for("auth.login"))
