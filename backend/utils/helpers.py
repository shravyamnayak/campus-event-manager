from models.notification import Notification
from extensions import db

def send_notification(user_id, title, message, notif_type='info'):
    """Create a notification for a user."""
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notif_type
    )
    db.session.add(notif)
    db.session.commit()

def send_bulk_notification(user_ids, title, message, notif_type='info'):
    """Send notification to multiple users."""
    for uid in user_ids:
        notif = Notification(
            user_id=uid,
            title=title,
            message=message,
            type=notif_type
        )
        db.session.add(notif)
    db.session.commit()

def check_venue_conflict(venue_id, start_dt, end_dt, exclude_event_id=None):
    """Check if a venue has a booking conflict."""
    from models.event import Event
    query = Event.query.filter(
        Event.venue_id == venue_id,
        Event.status.in_(['pending', 'approved']),
        Event.start_datetime < end_dt,
        Event.end_datetime > start_dt
    )
    if exclude_event_id:
        query = query.filter(Event.id != exclude_event_id)
    return query.first()