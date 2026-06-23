from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Registration, BulletinPost, Event
from forms import RegistrationForm
from datetime import datetime, timezone

registration_bp = Blueprint("registration", __name__, url_prefix="/events")


@registration_bp.route("/<int:event_id>/register", methods=["POST"])
@login_required
def register(event_id):
    event = Event.query.get_or_404(event_id)
    form = RegistrationForm(meta={'csrf': False})

    if not current_user.has_complete_profile():
        flash("請先補齊報名必要資料", "error")
        return redirect(url_for("oauth.complete_profile"))

    if not form.validate_on_submit():
        flash("請輸入正確的出席人數", "error")
        return redirect(url_for("events.detail", event_id=event_id))

    existing = Registration.query.filter_by(
        event_id=event_id, user_id=current_user.id, cancelled_at=None
    ).first()
    if existing:
        flash("您已經報名此活動", "error")
        return redirect(url_for("events.detail", event_id=event_id))

    if event.max_attendees:
        active_count = Registration.query.filter_by(
            event_id=event_id, cancelled_at=None
        ).count()
        if active_count >= event.max_attendees:
            flash("此活動名額已滿，無法報名", "error")
            return redirect(url_for("events.detail", event_id=event_id))

    registration = Registration(
        event_id=event_id,
        user_id=current_user.id,
        attendees_count=form.attendees_count.data,
        ip_address=request.remote_addr,
    )
    db.session.add(registration)

    post = BulletinPost(
        content=f"{current_user.name} 已報名「{event.title}」活動（出席 {form.attendees_count.data} 人）",
        post_type="system",
        event_id=event_id,
        created_by=current_user.id,
    )
    db.session.add(post)
    db.session.commit()

    flash("報名成功！", "success")
    return redirect(url_for("events.detail", event_id=event_id))


@registration_bp.route("/<int:event_id>/cancel", methods=["POST"])
@login_required
def cancel(event_id):
    event = Event.query.get_or_404(event_id)
    registration = Registration.query.filter_by(
        event_id=event_id, user_id=current_user.id, cancelled_at=None
    ).first()
    if not registration:
        flash("您尚未報名此活動", "error")
        return redirect(url_for("events.detail", event_id=event_id))

    registration.cancelled_at = datetime.now(timezone.utc)
    registration.cancellation_reason = "使用者自行取消"

    post = BulletinPost(
        content=f"{current_user.name} 已取消「{event.title}」活動報名",
        post_type="system",
        event_id=event_id,
        created_by=current_user.id,
    )
    db.session.add(post)
    db.session.commit()

    flash("已取消報名", "success")
    return redirect(url_for("events.detail", event_id=event_id))


