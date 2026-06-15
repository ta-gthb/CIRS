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
                'admin_id': 'CIRS10ADMN20260001',
                'username': 'kolkata_admin',
                'name': 'Kolkata Admin',
                'assigned_district': 'Kolkata',
                'lat': 22.5726, 'lng': 88.3639,
                'lat_min': 22.4700, 'lat_max': 22.6500,
                'lon_min': 88.2500, 'lon_max': 88.4500
            },
            {
                'phone': '9876543211',
                'admin_id': 'CIRS10ADMN20260002',
                'username': 'howrah_admin',
                'name': 'Howrah Admin',
                'assigned_district': 'Howrah',
                'lat': 22.5958, 'lng': 88.2636,
                'lat_min': 22.5000, 'lat_max': 22.7000,
                'lon_min': 88.1500, 'lon_max': 88.3500
            },
            {
                'phone': '9876543212',
                'admin_id': 'CIRS10ADMN20260003',
                'username': 's24p_admin',
                'name': 'South 24 Parganas Admin',
                'assigned_district': 'South 24 Parganas',
                'lat': 22.1367, 'lng': 88.5565,
                'lat_min': 21.4833, 'lat_max': 22.5625,
                'lon_min': 88.0625, 'lon_max': 89.0806
            }
        ]

        for a in admins:
            admin = User(
                phone=a['phone'],
                admin_id=a['admin_id'],
                username=a['username'],
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
            admin.set_password('admin123')
            db.session.add(admin)
        
        db.session.commit()
        
        print(f"Database reinitialized and {len(admins)} admins seeded successfully.")
except Exception as e:
    print(f"ERROR during database reinitialization: {e}")
    sys.exit(1)
