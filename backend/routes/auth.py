from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=True)
            if request.is_json:
                return jsonify({'success': True, 'role': user.role, 'name': user.name})
            return redirect(url_for('dashboard'))
        
        msg = 'Invalid email or password.'
        if request.is_json:
            return jsonify({'success': False, 'error': msg}), 401
        flash(msg, 'danger')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        role = data.get('role', 'student')
        department = data.get('department', '').strip()
        
        if role not in ['faculty', 'student']:
            role = 'student'
        
        if User.query.filter_by(email=email).first():
            msg = 'Email already registered.'
            if request.is_json:
                return jsonify({'success': False, 'error': msg}), 400
            flash(msg, 'danger')
            return render_template('register.html')
        
        user = User(name=name, email=email, role=role, department=department)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        if request.is_json:
            return jsonify({'success': True, 'role': user.role})
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/api/me')
@login_required
def me():
    return jsonify(current_user.to_dict())