from app import create_app, db
from app.models.models import User

app = create_app()

with app.app_context():
    db.create_all()
    
    # Seed Admin
    admin_phone = '9876543210'
    admin = User.query.filter_by(phone=admin_phone).first()
    if not admin:
        admin = User(
            phone=admin_phone,
            name='Admin Officer 1',
            role='authority',
            assigned_state='West Bengal',
            assigned_district='Kolkata',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Admin seeded: {admin_phone}")
    else:
        print("Admin already exists.")
