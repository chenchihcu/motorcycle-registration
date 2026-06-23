from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    license_plate = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    oauth_provider = db.Column(db.String(20), nullable=True)
    oauth_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    registrations = db.relationship("Registration", backref="user", lazy="dynamic")
    messages = db.relationship("Message", backref="user", lazy="dynamic")


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.Date, nullable=False, index=True)
    google_maps_embed_url = db.Column(db.Text, nullable=True)
    route_waypoints = db.Column(db.Text, nullable=True)
    max_attendees = db.Column(db.Integer, nullable=True)
    max_vehicles = db.Column(db.Integer, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))
    creator = db.relationship("User", backref="created_events")
    registrations = db.relationship("Registration", backref="event", lazy="dynamic")


class Registration(db.Model):
    __tablename__ = "registrations"
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    attendees_count = db.Column(db.Integer, nullable=False, default=1)
    ip_address = db.Column(db.String(45), nullable=False)
    registered_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancellation_reason = db.Column(db.String(200), nullable=True)
    __table_args__ = (
        db.UniqueConstraint("event_id", "user_id", name="uq_event_user"),
        db.UniqueConstraint("event_id", "ip_address", name="uq_event_ip"),
    )


class BulletinPost(db.Model):
    __tablename__ = "bulletin_posts"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_type = db.Column(db.String(20), nullable=False, default="manual")
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))
    creator = db.relationship("User", backref="bulletin_posts")
    event = db.relationship("Event", backref="bulletin_posts")


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=True)
    reply_to_id = db.Column(db.Integer, db.ForeignKey("messages.id"), nullable=True)
    subject = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    event_rel = db.relationship("Event", backref="messages")
    replies = db.relationship(
        "Message", backref=db.backref("parent", remote_side=[id]),
        lazy="dynamic", foreign_keys=[reply_to_id]
    )
