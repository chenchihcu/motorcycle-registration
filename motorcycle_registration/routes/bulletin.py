from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from models import db, BulletinPost, Event, Registration
from datetime import datetime, timezone

bulletin_bp = Blueprint("bulletin", __name__)


@bulletin_bp.route("/")
@bulletin_bp.route("/dashboard")
@login_required
def dashboard():
    q = request.args.get("q", "").strip()

    query = BulletinPost.query
    if q:
        query = query.filter(BulletinPost.content.contains(q))
    posts = query.order_by(BulletinPost.created_at.desc()).limit(50).all()

    upcoming_events = Event.query.filter(
        Event.event_date_start >= datetime.now(timezone.utc).date()
    ).order_by(Event.event_date_start.asc()).limit(5).all()

    # 關聯最近一個未來活動的統計
    featured_event = upcoming_events[0] if upcoming_events else None
    if featured_event:
        active_regs = Registration.query.filter_by(
            event_id=featured_event.id, cancelled_at=None
        ).all()
        featured_people = sum(r.attendees_count for r in active_regs)
        featured_vehicles = len(active_regs)
    else:
        featured_people = 0
        featured_vehicles = 0

    # 每個即將到來活動的統計
    event_stats = {}
    for ev in upcoming_events:
        regs = Registration.query.filter_by(event_id=ev.id, cancelled_at=None).all()
        event_stats[ev.id] = {
            "people": sum(r.attendees_count for r in regs),
            "vehicles": len(regs),
        }

    # 最近結束的 3 個活動
    today = datetime.now(timezone.utc).date()
    past_events = Event.query.filter(
        Event.event_date_start < today
    ).order_by(Event.event_date_start.desc()).limit(3).all()
    past_stats = {}
    for ev in past_events:
        regs = Registration.query.filter_by(event_id=ev.id, cancelled_at=None).all()
        past_stats[ev.id] = {
            "people": sum(r.attendees_count for r in regs),
            "vehicles": len(regs),
        }

    return render_template(
        "dashboard.html",
        posts=posts,
        featured_event=featured_event,
        featured_people=featured_people,
        featured_vehicles=featured_vehicles,
        upcoming_events=upcoming_events,
        event_stats=event_stats,
        past_events=past_events,
        past_stats=past_stats,
    )
