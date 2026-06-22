from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Event, Registration, User
from forms import EventForm
from datetime import datetime, date, timezone
from sqlalchemy import extract

events_bp = Blueprint("events", __name__, url_prefix="/events")


@events_bp.route("")
def list_events():
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "").strip()

    query = Event.query
    if q:
        query = query.filter(
            db.or_(
                Event.title.contains(q),
                Event.description.contains(q),
            )
        )
    events = query.order_by(Event.event_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    event_stats = {}
    for event in events.items:
        active_regs = Registration.query.filter_by(
            event_id=event.id, cancelled_at=None
        ).all()
        total_people = sum(r.attendees_count for r in active_regs)
        total_vehicles = len(active_regs)
        event_stats[event.id] = {"people": total_people, "vehicles": total_vehicles}
    return render_template(
        "events/list.html",
        events=events,
        event_stats=event_stats,
        today=date.today(),
    )


@events_bp.route("/<int:event_id>")
def detail(event_id):
    event = Event.query.get_or_404(event_id)
    active_regs = Registration.query.filter_by(
        event_id=event.id, cancelled_at=None
    ).all()
    total_people = sum(r.attendees_count for r in active_regs)
    total_vehicles = len(active_regs)

    # 報名者清單（含 user 資料）
    attendee_list = (
        Registration.query.filter_by(event_id=event.id, cancelled_at=None)
        .join(User)
        .order_by(Registration.registered_at.asc())
        .all()
    )

    user_registered = None
    if current_user.is_authenticated:
        user_registered = Registration.query.filter_by(
            event_id=event.id, user_id=current_user.id
        ).first()

    return render_template(
        "events/detail.html",
        event=event,
        total_people=total_people,
        total_vehicles=total_vehicles,
        attendee_list=attendee_list,
        user_registered=user_registered,
    )


@events_bp.route("/<int:event_id>/route")
def route(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template("events/route.html", event=event)


@events_bp.route("/calendar")
@events_bp.route("/calendar/<int:year>/<int:month>")
def calendar(year=None, month=None):
    import calendar as cal_mod

    today = date.today()
    if year is None or month is None:
        year = today.year
        month = today.month

    # 產生月曆行
    cal_rows = cal_mod.monthcalendar(year, month)

    # 查詢當月所有活動
    events_in_month = Event.query.filter(
        extract("year", Event.event_date) == year,
        extract("month", Event.event_date) == month,
    ).order_by(Event.event_date.asc()).all()

    # 依日期分組
    events_by_day = {}
    for ev in events_in_month:
        day = ev.event_date.day
        events_by_day.setdefault(day, []).append(ev)

    # 上下月導覽
    if month == 1:
        prev_month = date(year - 1, 12, 1)
    else:
        prev_month = date(year, month - 1, 1)
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    return render_template(
        "events/calendar.html",
        year=year,
        month=month,
        calendar_rows=cal_rows,
        events_by_day=events_by_day,
        prev_month=prev_month,
        next_month=next_month,
    )
