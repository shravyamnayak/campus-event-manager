import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, redirect, url_for
from flask_login import login_required, current_user
from extensions import db, login_manager
from config import config
from models.user import User

def create_app(config_name='default'):
    app = Flask(
        __name__,
        template_folder='../frontend/templates',
        static_folder='../frontend/static'
    )
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.events import events_bp
    from routes.venues import venues_bp
    from routes.bookings import bookings_bp
    from routes.notifications import notifications_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(venues_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(notifications_bp)
    
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        from models.event import Event
        from models.booking import Booking
        from models.venue import Venue
        from models.notification import Notification
        
        if current_user.is_admin():
            stats = {
                'total_events': Event.query.count(),
                'pending_events': Event.query.filter_by(status='pending').count(),
                'approved_events': Event.query.filter_by(status='approved').count(),
                'total_users': User.query.count(),
                'total_venues': Venue.query.count(),
                'total_bookings': Booking.query.count(),
            }
            pending_events = Event.query.filter_by(status='pending').order_by(Event.created_at.desc()).all()
            return render_template('dashboard/admin.html', stats=stats, pending_events=pending_events)
        
        elif current_user.is_faculty():
            my_events = Event.query.filter_by(organizer_id=current_user.id).order_by(Event.created_at.desc()).all()
            upcoming = Event.query.filter_by(status='approved', is_public=True).limit(5).all()
            return render_template('dashboard/faculty.html', my_events=my_events, upcoming=upcoming)
        
        else:
            my_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.registered_at.desc()).all()
            upcoming = Event.query.filter_by(status='approved', is_public=True).limit(6).all()
            return render_template('dashboard/student.html', my_bookings=my_bookings, upcoming=upcoming)
    
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    app.run(host='0.0.0.0', port=5000, debug=True)