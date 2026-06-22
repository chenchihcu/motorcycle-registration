from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Registration, Event, Message
from forms import SettingsForm, PasswordForm
from datetime import datetime, timezone, date

user_bp = Blueprint("user", __name__, url_prefix="/my")
members_bp = Blueprint("members", __name__)


@members_bp.route("/members")
@login_required
def members():
    members_list = User.query.order_by(User.created_at.asc()).all()
    return render_template("members/list.html", members=members_list)


@user_bp.route("/registrations")
@login_required
def registrations():
    now = date.today()

    # 進行中報名：未取消且活動日期 >= 今天
    active = (
        Registration.query.filter_by(user_id=current_user.id, cancelled_at=None)
        .join(Event)
        .filter(Event.event_date >= now)
        .order_by(Event.event_date.asc())
        .all()
    )

    # 歷史紀錄：已取消或活動已結束
    history = (
        Registration.query.filter(
            Registration.user_id == current_user.id,
            db.or_(
                Registration.cancelled_at != None,
                Event.event_date < now,
            ),
        )
        .join(Event)
        .order_by(Registration.registered_at.desc())
        .all()
    )

    return render_template(
        "my/registrations.html",
        active=active,
        history=history,
    )


@user_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = SettingsForm(obj=current_user)
    password_form = PasswordForm()

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.license_plate = form.license_plate.data
        db.session.commit()
        flash("個人資料已更新", "success")
        return redirect(url_for("user.settings"))

    return render_template(
        "my/settings.html",
        form=form,
        password_form=password_form,
    )


@user_bp.route("/settings/password", methods=["POST"])
@login_required
def change_password():
    form = PasswordForm()
    if form.validate_on_submit():
        if not check_password_hash(current_user.password_hash, form.old_password.data):
            flash("舊密碼不正確", "error")
            return redirect(url_for("user.settings"))

        user = User.query.get(current_user.id)
        user.password_hash = generate_password_hash(form.new_password.data)
        db.session.commit()
        flash("密碼已更新", "success")

    return redirect(url_for("user.settings"))


@user_bp.route("/messages")
@login_required
def messages():
    msgs = (
        Message.query.filter_by(user_id=current_user.id)
        .order_by(Message.created_at.desc())
        .all()
    )
    return render_template("my/messages.html", messages=msgs)
