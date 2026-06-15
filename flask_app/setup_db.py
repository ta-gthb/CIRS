from app import create_app, db
from app.models.models import User
import sys

print("Starting database setup...")
app = create_app()

try:
    with app.app_context():
        # db.create_all() will now find all models because they are imported in create_app()
        db.create_all()
        print("Database tables created/verified.")
        
        # Seed Admin 1 (Kolkata)
        admin_phone = '9876543210'
        admin = User.query.filter_by(phone=admin_phone).first()
        if not admin:
            admin = User(
                phone=admin_phone,
                admin_id='CIRS10ADMN20260001',
                username='kolkata_admin',
                name='Kolkata Admin',
                role='authority',
                assigned_state='West Bengal',
                assigned_district='Kolkata',
                latitude=22.5726,
                longitude=88.3639,
                lat_min=22.4700,
                lat_max=22.6500,
                lon_min=88.2500,
                lon_max=88.4500,
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print(f"Admin seeded: {admin_phone} / kolkata_admin / CIRS10ADMN20260001 (Kolkata)")
        else:
            print("Kolkata Admin already exists.")

        # Seed Admin 2 (Howrah)
        howrah_phone = '9876543211'
        howrah_admin = User.query.filter_by(phone=howrah_phone).first()
        if not howrah_admin:
            howrah_admin = User(
                phone=howrah_phone,
                admin_id='CIRS10ADMN20260002',
                username='howrah_admin',
                name='Howrah Admin',
                role='authority',
                assigned_state='West Bengal',
                assigned_district='Howrah',
                latitude=22.5958,
                longitude=88.2636,
                lat_min=22.5000,
                lat_max=22.7000,
                lon_min=88.1500,
                lon_max=88.3500,
                is_active=True
            )
            howrah_admin.set_password('admin123')
            db.session.add(howrah_admin)
            print(f"Admin seeded: {howrah_phone} / howrah_admin / CIRS10ADMN20260002 (Howrah)")
        else:
            print("Howrah Admin already exists.")
            
        db.session.commit()
except Exception as e:
    print(f"ERROR during database setup: {e}")
    sys.exit(1)
