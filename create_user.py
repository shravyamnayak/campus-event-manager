"""
Run this inside the Flask container to create any user.
Usage:
  docker exec -it campus_flask python3 /app/create_user.py
"""
import sys
import os
sys.path.insert(0, '/app/backend')

from dotenv import load_dotenv
load_dotenv('/app/.env')

from app import create_app
from extensions import db
from models.user import User

app = create_app()

with app.app_context():
    print("\n=== CampusConnect User Creator ===\n")

    name       = input("Full Name       : ").strip()
    email      = input("Email           : ").strip().lower()
    password   = input("Password        : ").strip()
    role       = input("Role (admin/faculty/student) [student]: ").strip() or 'student'
    department = input("Department      : ").strip()

    if role not in ('admin', 'faculty', 'student'):
        role = 'student'

    existing = User.query.filter_by(email=email).first()
    if existing:
        print(f"\n⚠  User {email} already exists.")
        update = input("Update password? (y/n): ").strip().lower()
        if update == 'y':
            existing.set_password(password)
            db.session.commit()
            print(f"✅ Password updated for {email}")
        sys.exit(0)

    user = User(name=name, email=email, role=role, department=department)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    print(f"\n✅ User created successfully!")
    print(f"   Email : {email}")
    print(f"   Role  : {role}")
    print(f"   ID    : {user.id}\n")