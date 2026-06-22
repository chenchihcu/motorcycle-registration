from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Message, Event
from forms import MessageForm

message_bp = Blueprint("message", __name__, url_prefix="/messages")


@message_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = MessageForm()
    form.event_id.choices = [(0, "--- 不指定活動 ---")] + [
        (e.id, e.title) for e in Event.query.order_by(Event.event_date.desc()).all()
    ]
    if form.validate_on_submit():
        msg = Message(
            user_id=current_user.id,
            subject=form.subject.data,
            content=form.content.data,
            event_id=form.event_id.data if form.event_id.data and form.event_id.data > 0 else None,
        )
        db.session.add(msg)
        db.session.commit()
        flash("訊息已送出，感謝您的回饋", "success")
        return redirect(url_for("bulletin.dashboard"))
    return render_template("messages/new.html", form=form)
