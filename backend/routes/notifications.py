from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models.notification import Notification
from extensions import db

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/api/notifications', methods=['GET'])
@login_required
def api_list_notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).limit(50).all()
    return jsonify([n.to_dict() for n in notifs])

@notifications_bp.route('/api/notifications/unread-count', methods=['GET'])
@login_required
def api_unread_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})

@notifications_bp.route('/api/notifications/<int:notif_id>/read', methods=['POST'])
@login_required
def api_mark_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    if notif.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    notif.is_read = True
    db.session.commit()
    return jsonify({'success': True})

@notifications_bp.route('/api/notifications/read-all', methods=['POST'])
@login_required
def api_mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False)\
        .update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})