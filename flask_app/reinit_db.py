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
        
        # Seed Admins
        admins = [
            {
                'phone': '9876543210',
                'name': 'Kolkata Admin',
                'assigned_district': 'Kolkata',
                'lat': 22.5726, 'lng': 88.3639,
                'lat_min': 22.4700, 'lat_max': 22.6500,
                'lon_min': 88.2500, 'lon_max': 88.4500
            },
            {
                'phone': '9876543211',
                'name': 'Howrah Admin',
                'assigned_district': 'Howrah',
                'lat': 22.5958, 'lng': 88.2636,
                'lat_min': 22.5000, 'lat_max': 22.7000,
                'lon_min': 88.1500, 'lon_max': 88.3500
            }
        ]

        for a in admins:
            admin = User(
                phone=a['phone'],
                name=a['name'],
                role='authority',
                assigned_state='West Bengal',
                assigned_district=a['assigned_district'],
                latitude=a['lat'],
                longitude=a['lng'],
                lat_min=a['lat_min'],
                lat_max=a['lat_max'],
                lon_min=a['lon_min'],
                lon_max=a['lon_max'],
                is_active=True
            )
            db.session.add(admin)
        
        db.session.commit()
        
        print(f"Database reinitialized and {len(admins)} admins seeded successfully.")
except Exception as e:
    print(f"ERROR during database reinitialization: {e}")
    sys.exit(1)
