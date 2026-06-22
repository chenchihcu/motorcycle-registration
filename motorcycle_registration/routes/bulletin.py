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

    active_regs = Registration.query.filter_by(cancelled_at=None).all()
    total_people = sum(r.attendees_count for r in active_regs)
    total_vehicles = len(active_regs)

    upcoming_events = Event.query.filter(
        Event.event_date >= datetime.now(timezone.utc).date()
    ).order_by(Event.event_date.asc()).limit(5).all()

    return render_template(
        "dashboard.html",
        posts=posts,
        total_people=total_people,
        total_vehicles=total_vehicles,
        upcoming_events=upcoming_events,
    )
