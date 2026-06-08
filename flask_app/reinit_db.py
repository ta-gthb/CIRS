from app import create_app, db
from app.models.models import User
import sys

print("!!! WARNING: THIS WILL WIPE ALL DATA IN YOUR DATABASE !!!")
# In a real CLI, we might ask for confirmation, but here we'll just provide the script.

app = create_app()

try:
    with app.app_context():
        print("Dropping all existing tables...")
        db.drop_all()
        
        print("Creating all tables from scratch...")
        db.create_all()
        
        # Seed Admin
        admin_phone = '9876543210'
        admin = User(
            phone=admin_phone,
            name='Admin Officer 1',
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
        db.session.add(admin)
        db.session.commit()
        
        print("Database reinitialized and admin seeded successfully.")
except Exception as e:
    print(f"ERROR during database reinitialization: {e}")
    sys.exit(1)
