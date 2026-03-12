from extensions import db
from datetime import datetime

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum('registered','waitlisted','cancelled'), default='registered')
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('event_id', 'user_id', name='unique_booking'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'event_title': self.event.title if self.event else None,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'status': self.status,
            'registered_at': self.registered_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Booking event={self.event_id} user={self.user_id}>'