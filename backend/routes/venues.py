from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.venue import Venue
from extensions import db
from utils.decorators import admin_required

venues_bp = Blueprint('venues', __name__)

@venues_bp.route('/venues')
@login_required
def list_venues():
    venues = Venue.query.all()
    return render_template('venues/list.html', venues=venues)

@venues_bp.route('/api/venues', methods=['GET'])
@login_required
def api_list_venues():
    venues = Venue.query.all()
    return jsonify([v.to_dict() for v in venues])

@venues_bp.route('/api/venues', methods=['POST'])
@login_required
@admin_required
def api_create_venue():
    data = request.get_json()
    venue = Venue(
        name=data['name'],
        location=data.get('location', ''),
        capacity=int(data['capacity']),
        amenities=data.get('amenities', ''),
        is_available=data.get('is_available', True)
    )
    db.session.add(venue)
    db.session.commit()
    return jsonify({'success': True, 'venue': venue.to_dict()}), 201

@venues_bp.route('/api/venues/<int:venue_id>', methods=['PUT'])
@login_required
@admin_required
def api_update_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    data = request.get_json()
    if 'name' in data: venue.name = data['name']
    if 'location' in data: venue.location = data['location']
    if 'capacity' in data: venue.capacity = int(data['capacity'])
    if 'amenities' in data: venue.amenities = data['amenities']
    if 'is_available' in data: venue.is_available = data['is_available']
    db.session.commit()
    return jsonify({'success': True, 'venue': venue.to_dict()})

@venues_bp.route('/api/venues/<int:venue_id>', methods=['DELETE'])
@login_required
@admin_required
def api_delete_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    db.session.delete(venue)
    db.session.commit()
    return jsonify({'success': True})

@venues_bp.route('/api/venues/<int:venue_id>/availability', methods=['GET'])
@login_required
def api_venue_availability(venue_id):
    from models.event import Event
    venue = Venue.query.get_or_404(venue_id)
    bookings = Event.query.filter(
        Event.venue_id == venue_id,
        Event.status.in_(['pending', 'approved'])
    ).all()
    return jsonify({
        'venue': venue.to_dict(),
        'bookings': [{'id': e.id, 'title': e.title, 'start': e.start_datetime.isoformat(),
                      'end': e.end_datetime.isoformat(), 'status': e.status} for e in bookings]
    })