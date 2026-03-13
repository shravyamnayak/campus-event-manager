from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.booking import Booking
from models.event import Event
from extensions import db
from utils.helpers import send_notification

bookings_bp = Blueprint('bookings', __name__)

 
@bookings_bp.route('/api/bookings/stats')
@login_required
def api_booking_stats():
    try:
        if current_user.is_admin():
            base = Booking.query
        else:
            base = Booking.query.filter_by(user_id=current_user.id)
 
        total      = base.count()
        registered = base.filter_by(status='registered').count()
        waitlisted = base.filter_by(status='waitlisted').count()
        cancelled  = base.filter_by(status='cancelled').count()
 
        return jsonify({
            'success':    True,
            'total':      total,
            'registered': registered,
            'waitlisted': waitlisted,
            'cancelled':  cancelled,
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False, 'error': str(e),
            'total': 0, 'registered': 0, 'waitlisted': 0, 'cancelled': 0
        }), 500
    
@bookings_bp.route('/bookings')
@login_required
def list_bookings():
    if current_user.is_admin():
        bookings = Booking.query.order_by(Booking.registered_at.desc()).all()
    else:
        bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.registered_at.desc()).all()
    return render_template('bookings/list.html', bookings=bookings)

@bookings_bp.route('/api/bookings', methods=['GET'])
@login_required
def api_list_bookings():
    if current_user.is_admin():
        bookings = Booking.query.all()
    else:
        bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return jsonify([b.to_dict() for b in bookings])

@bookings_bp.route('/api/bookings', methods=['POST'])
@login_required
def api_create_booking():
    data = request.get_json()
    event_id = data.get('event_id')
    event = Event.query.get_or_404(event_id)
    
    if event.status != 'approved':
        return jsonify({'error': 'Event is not approved for registration'}), 400
    
    existing = Booking.query.filter_by(event_id=event_id, user_id=current_user.id).first()
    if existing:
        if existing.status == 'cancelled':
            existing.status = 'registered' if not event.is_full() else 'waitlisted'
            db.session.commit()
            return jsonify({'success': True, 'booking': existing.to_dict()})
        return jsonify({'error': 'Already registered for this event'}), 400
    
    status = 'waitlisted' if event.is_full() else 'registered'
    booking = Booking(event_id=event_id, user_id=current_user.id, status=status)
    db.session.add(booking)
    db.session.commit()
    
    send_notification(
        current_user.id,
        f'Registered for {event.title}',
        f'You have successfully registered for "{event.title}".' if status == 'registered' else f'You have been waitlisted for "{event.title}".',
        'success' if status == 'registered' else 'warning'
    )
    # Notify organizer
    send_notification(
        event.organizer_id,
        'New Registration',
        f'{current_user.name} registered for your event "{event.title}".',
        'info'
    )
    return jsonify({'success': True, 'booking': booking.to_dict()}), 201

@bookings_bp.route('/api/bookings/<int:booking_id>/cancel', methods=['POST'])
@login_required
def api_cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    booking.status = 'cancelled'
    db.session.commit()
    
    # Promote waitlisted if slot opens
    waitlisted = Booking.query.filter_by(
        event_id=booking.event_id, status='waitlisted'
    ).order_by(Booking.registered_at).first()
    
    if waitlisted:
        waitlisted.status = 'registered'
        db.session.commit()
        send_notification(
            waitlisted.user_id,
            'You\'re off the waitlist!',
            f'A spot opened up for "{booking.event.title}". You are now registered!',
            'success'
        )
    
    return jsonify({'success': True})

@bookings_bp.route('/api/events/<int:event_id>/attendees', methods=['GET'])
@login_required
def api_event_attendees(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    bookings = Booking.query.filter_by(event_id=event_id).all()
    return jsonify([b.to_dict() for b in bookings])


@bookings_bp.route('/bookings/<int:booking_id>')
@login_required
def booking_detail(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    # Only owner or admin can view
    if booking.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('bookings.list_bookings'))
    return render_template('bookings/detail.html', booking=booking)