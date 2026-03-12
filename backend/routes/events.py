from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models.event import Event
from models.venue import Venue
from models.booking import Booking
from models.user import User
from extensions import db
from utils.decorators import faculty_or_admin_required, admin_required
from utils.helpers import send_notification, send_bulk_notification, check_venue_conflict
from datetime import datetime

events_bp = Blueprint('events', __name__)

@events_bp.route('/events')
@login_required
def list_events():
    events = Event.query.filter_by(is_public=True).order_by(Event.start_datetime).all()
    venues = Venue.query.filter_by(is_available=True).all()
    return render_template('events/list.html', events=events, venues=venues)

@events_bp.route('/events/<int:event_id>')
@login_required
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    user_booking = Booking.query.filter_by(event_id=event_id, user_id=current_user.id).first()
    return render_template('events/detail.html', event=event, user_booking=user_booking)

@events_bp.route('/events/new', methods=['GET', 'POST'])
@login_required
@faculty_or_admin_required
def create_event():
    venues = Venue.query.filter_by(is_available=True).all()
    return render_template('events/form.html', venues=venues, event=None)

# ── API endpoints ──────────────────────────────────────────────────

@events_bp.route('/api/events', methods=['GET'])
@login_required
def api_list_events():
    status_filter = request.args.get('status')
    type_filter = request.args.get('type')
    
    query = Event.query
    if not current_user.is_admin():
        query = query.filter_by(is_public=True)
    if status_filter:
        query = query.filter_by(status=status_filter)
    if type_filter:
        query = query.filter_by(event_type=type_filter)
    
    events = query.order_by(Event.start_datetime).all()
    return jsonify([e.to_dict() for e in events])

@events_bp.route('/api/events', methods=['POST'])
@login_required
@faculty_or_admin_required
def api_create_event():
    data = request.get_json()
    
    try:
        start_dt = datetime.fromisoformat(data['start_datetime'])
        end_dt = datetime.fromisoformat(data['end_datetime'])
    except (KeyError, ValueError):
        return jsonify({'error': 'Invalid datetime format'}), 400
    
    if end_dt <= start_dt:
        return jsonify({'error': 'End time must be after start time'}), 400
    
    venue_id = data.get('venue_id')
    if venue_id:
        conflict = check_venue_conflict(venue_id, start_dt, end_dt)
        if conflict:
            return jsonify({'error': f'Venue conflict with event: {conflict.title}'}), 409
    
    event = Event(
        title=data['title'],
        description=data.get('description', ''),
        event_type=data.get('event_type', 'other'),
        start_datetime=start_dt,
        end_datetime=end_dt,
        venue_id=venue_id,
        organizer_id=current_user.id,
        max_attendees=int(data.get('max_attendees', 100)),
        is_public=data.get('is_public', True),
        status='pending' if not current_user.is_admin() else 'approved'
    )
    db.session.add(event)
    db.session.commit()
    
    # Notify admins if not admin
    if not current_user.is_admin():
        admins = User.query.filter_by(role='admin').all()
        admin_ids = [a.id for a in admins]
        send_bulk_notification(
            admin_ids,
            'New Event Pending Approval',
            f'"{event.title}" submitted by {current_user.name} needs your approval.',
            'info'
        )
    
    return jsonify({'success': True, 'event': event.to_dict()}), 201

@events_bp.route('/api/events/<int:event_id>', methods=['PUT'])
@login_required
def api_update_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if event.organizer_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'title' in data: event.title = data['title']
    if 'description' in data: event.description = data['description']
    if 'event_type' in data: event.event_type = data['event_type']
    if 'max_attendees' in data: event.max_attendees = int(data['max_attendees'])
    if 'is_public' in data: event.is_public = data['is_public']
    
    if 'start_datetime' in data and 'end_datetime' in data:
        start_dt = datetime.fromisoformat(data['start_datetime'])
        end_dt = datetime.fromisoformat(data['end_datetime'])
        venue_id = data.get('venue_id', event.venue_id)
        if venue_id:
            conflict = check_venue_conflict(venue_id, start_dt, end_dt, exclude_event_id=event_id)
            if conflict:
                return jsonify({'error': f'Venue conflict: {conflict.title}'}), 409
        event.start_datetime = start_dt
        event.end_datetime = end_dt
        event.venue_id = venue_id
    
    db.session.commit()
    return jsonify({'success': True, 'event': event.to_dict()})

@events_bp.route('/api/events/<int:event_id>/approve', methods=['POST'])
@login_required
@admin_required
def api_approve_event(event_id):
    event = Event.query.get_or_404(event_id)
    action = request.get_json().get('action', 'approve')
    
    if action == 'approve':
        event.status = 'approved'
        notif_type = 'success'
        msg = f'Your event "{event.title}" has been approved!'
    else:
        event.status = 'rejected'
        notif_type = 'danger'
        msg = f'Your event "{event.title}" was rejected.'
    
    db.session.commit()
    send_notification(event.organizer_id, f'Event {action.capitalize()}d', msg, notif_type)
    return jsonify({'success': True, 'status': event.status})

@events_bp.route('/api/events/<int:event_id>/cancel', methods=['POST'])
@login_required
def api_cancel_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if event.organizer_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    event.status = 'cancelled'
    db.session.commit()
    
    # Notify all registered attendees
    registered = Booking.query.filter_by(event_id=event_id, status='registered').all()
    attendee_ids = [b.user_id for b in registered]
    send_bulk_notification(
        attendee_ids,
        'Event Cancelled',
        f'The event "{event.title}" has been cancelled.',
        'warning'
    )
    return jsonify({'success': True})

@events_bp.route('/api/events/<int:event_id>', methods=['DELETE'])
@login_required
def api_delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    db.session.delete(event)
    db.session.commit()
    return jsonify({'success': True})