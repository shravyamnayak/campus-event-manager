from flask import (Blueprint, render_template, request,
                   redirect, jsonify, flash)
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from extensions import db

auth_bp = Blueprint('auth', __name__)


def _is_json_request():
    """True when the request was made via fetch() with Content-Type: application/json"""
    return request.is_json or request.content_type == 'application/json'


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if _is_json_request():
            return jsonify({'success': True, 'redirect': '/dashboard'})
        return redirect('/dashboard')

    if request.method == 'POST':
        try:
            if _is_json_request():
                data = request.get_json(force=True, silent=True) or {}
            else:
                data = request.form.to_dict()

            email    = str(data.get('email', '')).strip().lower()
            password = str(data.get('password', ''))

            if not email or not password:
                raise ValueError('Email and password are required.')

            user = User.query.filter_by(email=email).first()
            if not user or not user.check_password(password) or not user.is_active:
                raise ValueError('Invalid email or password.')

            login_user(user, remember=True)

            if _is_json_request():
                return jsonify({
                    'success': True,
                    'role': user.role,
                    'name': user.name,
                    'redirect': '/dashboard'
                })
            return redirect('/dashboard')

        except ValueError as e:
            if _is_json_request():
                return jsonify({'success': False, 'error': str(e)}), 401
            flash(str(e), 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if _is_json_request():
            return jsonify({'success': True, 'redirect': '/dashboard'})
        return redirect('/dashboard')

    if request.method == 'POST':
        try:
            if _is_json_request():
                data = request.get_json(force=True, silent=True) or {}
            else:
                data = request.form.to_dict()

            name       = str(data.get('name', '')).strip()
            email      = str(data.get('email', '')).strip().lower()
            password   = str(data.get('password', ''))
            role       = str(data.get('role', 'student')).strip()
            department = str(data.get('department', '')).strip()

            # ── Validation ──────────────────────────────────────
            if not name:
                raise ValueError('Full name is required.')
            if not email:
                raise ValueError('Email address is required.')
            if not password:
                raise ValueError('Password is required.')
            if len(password) < 6:
                raise ValueError('Password must be at least 6 characters.')
            if '@' not in email:
                raise ValueError('Please enter a valid email address.')
            if role not in ('student', 'faculty'):
                role = 'student'

            if User.query.filter_by(email=email).first():
                raise ValueError('An account with that email already exists.')

            # ── Create user ──────────────────────────────────────
            user = User(
                name=name,
                email=email,
                role=role,
                department=department
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            login_user(user, remember=True)

            if _is_json_request():
                return jsonify({
                    'success': True,
                    'role': user.role,
                    'name': user.name,
                    'redirect': '/dashboard'
                })
            return redirect('/dashboard')

        except ValueError as e:
            db.session.rollback()
            if _is_json_request():
                return jsonify({'success': False, 'error': str(e)}), 400
            flash(str(e), 'danger')
            return render_template('register.html')

        except Exception as e:
            db.session.rollback()
            err = 'An unexpected error occurred. Please try again.'
            if _is_json_request():
                return jsonify({'success': False, 'error': err}), 500
            flash(err, 'danger')
            return render_template('register.html')

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect('/login')


@auth_bp.route('/api/me')
@login_required
def me():
    return jsonify(current_user.to_dict())