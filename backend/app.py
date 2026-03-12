import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, redirect, jsonify
from flask_login import login_required, current_user
from dotenv import load_dotenv

load_dotenv()


def create_app():
    root_dir     = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_dir = os.path.join(root_dir, 'frontend', 'templates')
    static_dir   = os.path.join(root_dir, 'frontend', 'static')

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )

    # ── Config ────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')

    MYSQL_USER     = os.environ.get('MYSQL_USER',     'campus_user')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'campus_pass')
    MYSQL_HOST     = os.environ.get('MYSQL_HOST',     'db')
    MYSQL_PORT     = os.environ.get('MYSQL_PORT',     '3306')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'campus_events')

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle':  300,
    }

    # ── Extensions ────────────────────────────────────────────────────
    from extensions import db, login_manager
    db.init_app(app)
    login_manager.init_app(app)

    # ── User loader ───────────────────────────────────────────────────
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── Blueprints ────────────────────────────────────────────────────
    from routes.auth          import auth_bp
    from routes.events        import events_bp
    from routes.venues        import venues_bp
    from routes.bookings      import bookings_bp
    from routes.notifications import notifications_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(venues_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(notifications_bp)

    # ── Core routes  (ALL inside create_app) ─────────────────────────
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect('/dashboard')
        return render_template('index.html')

    @app.route('/ping')                          # ← inside create_app ✅
    def ping():
        return jsonify({'status': 'ok'})

    @app.route('/dashboard')
    @login_required
    def dashboard():
        from models.event   import Event
        from models.booking import Booking
        from models.venue   import Venue

        if current_user.is_admin():
            stats = {
                'total_events'   : Event.query.count(),
                'pending_events' : Event.query.filter_by(status='pending').count(),
                'approved_events': Event.query.filter_by(status='approved').count(),
                'total_users'    : User.query.count(),
                'total_venues'   : Venue.query.count(),
                'total_bookings' : Booking.query.count(),
            }
            pending_events = (Event.query
                              .filter_by(status='pending')
                              .order_by(Event.created_at.desc())
                              .all())
            return render_template('dashboard/admin.html',
                                   stats=stats,
                                   pending_events=pending_events)

        elif current_user.is_faculty():
            my_events = (Event.query
                         .filter_by(organizer_id=current_user.id)
                         .order_by(Event.created_at.desc())
                         .all())
            upcoming  = (Event.query
                         .filter_by(status='approved', is_public=True)
                         .order_by(Event.start_datetime)
                         .limit(5).all())
            return render_template('dashboard/faculty.html',
                                   my_events=my_events,
                                   upcoming=upcoming)

        else:
            my_bookings = (Booking.query
                           .filter_by(user_id=current_user.id)
                           .order_by(Booking.registered_at.desc())
                           .all())
            upcoming    = (Event.query
                           .filter_by(status='approved', is_public=True)
                           .order_by(Event.start_datetime)
                           .limit(6).all())
            return render_template('dashboard/student.html',
                                   my_bookings=my_bookings,
                                   upcoming=upcoming)

    # ── Create DB tables ──────────────────────────────────────────────
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables ready")
        except Exception as e:
            print(f"⚠️  DB warning (is MySQL running?): {e}")

    return app                                   # ← must be inside create_app, last line


# ── Entry point ───────────────────────────────────────────────────────
if __name__ == '__main__':
    app = create_app()
    print("🚀 CampusConnect running at http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)