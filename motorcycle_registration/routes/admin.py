from flask import Blueprint, render_template, redirect, url_for, flash, request, Response, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import db, Event, User, Registration, BulletinPost, Message
from forms import EventForm, BulletinForm
from datetime import datetime, timezone, timedelta
import csv
import io

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("需要管理員權限", "error")
            return redirect(url_for("bulletin.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route("")
@login_required
@admin_required
def dashboard():
    total_events = Event.query.count()
    upcoming_events = Event.query.filter(
        Event.event_date >= datetime.now(timezone.utc).date()
    ).count()
    total_users = User.query.count()
    total_messages = Message.query.count()
    unread_messages = Message.query.filter_by(is_read=False).count()
    active_regs = Registration.query.filter_by(cancelled_at=None).count()

    recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()
    recent_posts = BulletinPost.query.order_by(BulletinPost.created_at.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_events=total_events,
        upcoming_events=upcoming_events,
        total_users=total_users,
        total_messages=total_messages,
        unread_messages=unread_messages,
        active_regs=active_regs,
        recent_events=recent_events,
        recent_posts=recent_posts,
    )


@admin_bp.route("/api/registration-trends")
@login_required
@admin_required
def registration_trends():
    days = request.args.get("days", 30, type=int)
    start_date = datetime.now(timezone.utc).date() - timedelta(days=days - 1)

    # 按日期聚合報名數
    results = (
        db.session.query(
            db.func.date(Registration.registered_at).label("date"),
            db.func.count(Registration.id).label("count"),
        )
        .filter(Registration.registered_at >= start_date)
        .group_by(db.func.date(Registration.registered_at))
        .order_by("date")
        .all()
    )

    data = {str(r.date): r.count for r in results}
    labels = [(start_date + timedelta(days=i)).isoformat() for i in range(days)]
    values = [data.get(d, 0) for d in labels]

    return jsonify({"labels": labels, "values": values})


@admin_bp.route("/events")
@login_required
@admin_required
def events_list():
    events = Event.query.order_by(Event.event_date.desc()).all()
    return render_template("admin/events_list.html", events=events)


@admin_bp.route("/events/new", methods=["GET", "POST"])
@login_required
@admin_required
def events_new():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            event_date=form.event_date.data,
            google_maps_embed_url=form.google_maps_embed_url.data,
            route_waypoints=form.route_waypoints.data,
            created_by=current_user.id,
        )
        db.session.add(event)
        db.session.commit()

        post = BulletinPost(
            content=f"📢 新活動：{event.title}（{event.event_date}）",
            post_type="system",
            event_id=event.id,
            created_by=current_user.id,
        )
        db.session.add(post)
        db.session.commit()

        flash("活動建立成功", "success")
        return redirect(url_for("admin.events_list"))
    return render_template("admin/event_form.html", form=form, title="建立新活動")


@admin_bp.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def events_edit(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        form.populate_obj(event)
        event.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        flash("活動已更新", "success")
        return redirect(url_for("admin.events_list"))
    return render_template("admin/event_form.html", form=form, title="編輯活動")


@admin_bp.route("/events/<int:event_id>/delete", methods=["POST"])
@login_required
@admin_required
def events_delete(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash("活動已刪除", "success")
    return redirect(url_for("admin.events_list"))


@admin_bp.route("/events/<int:event_id>/export-route")
@login_required
@admin_required
def export_route(event_id):
    event = Event.query.get_or_404(event_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["序號", "地點", "備註"])

    if event.route_waypoints:
        for i, waypoint in enumerate(event.route_waypoints.strip().split("\n"), 1):
            waypoint = waypoint.strip()
            if waypoint:
                writer.writerow([i, waypoint, ""])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=route_{event.id}.csv"},
    )


@admin_bp.route("/bulletin", methods=["GET", "POST"])
@login_required
@admin_required
def bulletin():
    form = BulletinForm()
    if form.validate_on_submit():
        post = BulletinPost(
            content=form.content.data,
            post_type="manual",
            created_by=current_user.id,
        )
        db.session.add(post)
        db.session.commit()
        flash("公告已發布", "success")
        return redirect(url_for("admin.bulletin"))

    posts = BulletinPost.query.order_by(BulletinPost.created_at.desc()).all()
    return render_template("admin/bulletin.html", form=form, posts=posts)


@admin_bp.route("/bulletin/<int:post_id>/delete", methods=["POST"])
@login_required
@admin_required
def bulletin_delete(post_id):
    post = BulletinPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("公告已刪除", "success")
    return redirect(url_for("admin.bulletin"))


@admin_bp.route("/messages")
@login_required
@admin_required
def messages():
    msgs = Message.query.filter_by(reply_to_id=None).order_by(Message.created_at.desc()).all()
    return render_template("admin/messages.html", messages=msgs)


@admin_bp.route("/messages/<int:msg_id>/read", methods=["POST"])
@login_required
@admin_required
def messages_read(msg_id):
    msg = Message.query.get_or_404(msg_id)
    msg.is_read = True
    db.session.commit()
    return redirect(url_for("admin.messages"))


@admin_bp.route("/messages/<int:msg_id>/reply", methods=["POST"])
@login_required
@admin_required
def messages_reply(msg_id):
    original = Message.query.get_or_404(msg_id)
    content = request.form.get("content", "").strip()
    if not content:
        flash("請輸入回覆內容", "error")
        return redirect(url_for("admin.messages"))

    reply = Message(
        user_id=original.user_id,
        event_id=original.event_id,
        reply_to_id=original.id,
        subject=f"Re: {original.subject or '無主旨'}",
        content=content,
        is_read=False,
    )
    db.session.add(reply)

    # 標記原訊息為已讀
    original.is_read = True
    db.session.commit()

    flash("回覆已送出", "success")
    return redirect(url_for("admin.messages"))
