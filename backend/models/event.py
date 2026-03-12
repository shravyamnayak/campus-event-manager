from extensions import db
from datetime import datetime

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.Enum('academic','cultural','sports','seminar','workshop','other'), default='other')
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum('pending','approved','rejected','cancelled'), default='pending')
    max_attendees = db.Column(db.Integer, default=100)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='event', lazy=True, cascade='all, delete-orphan')
    
    def attendee_count(self):
        from models.booking import Booking
        return Booking.query.filter_by(event_id=self.id, status='registered').count()
    
    def is_full(self):
        return self.attendee_count() >= self.max_attendees
    
    def is_upcoming(self):
        return self.start_datetime > datetime.utcnow()
    
    def is_ongoing(self):
        now = datetime.utcnow()
        return self.start_datetime <= now <= self.end_datetime
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_type': self.event_type,
            'start_datetime': self.start_datetime.isoformat(),
            'end_datetime': self.end_datetime.isoformat(),
            'venue_id': self.venue_id,
            'venue_name': self.venue.name if self.venue else None,
            'organizer_id': self.organizer_id,
            'organizer_name': self.organizer.name if self.organizer else None,
            'status': self.status,
            'max_attendees': self.max_attendees,
            'attendee_count': self.attendee_count(),
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Event {self.title}>'