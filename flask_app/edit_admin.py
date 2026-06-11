from app import create_app, db
from app.models.models import User
import sys

def add_admin(phone, name, state, district, lat, lng, lat_min, lat_max, lon_min, lon_max):
    app = create_app()
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(phone=phone).first()
        if existing_user:
            print(f"\nError: User with phone {phone} already exists (Name: {existing_user.name}, Role: {existing_user.role})")
            return False

        try:
            new_admin = User(
                phone=phone,
                name=name,
                role='authority',
                assigned_state=state,
                assigned_district=district,
                latitude=lat,
                longitude=lng,
                lat_min=lat_min,
                lat_max=lat_max,
                lon_min=lon_min,
                lon_max=lon_max,
                is_active=True
            )
            db.session.add(new_admin)
            db.session.commit()
            print(f"\nSuccessfully added Admin Officer: {name} ({phone}) for {district}, {state}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"\nError adding admin to database: {e}")
            return False

def remove_admin(phone):
    app = create_app()
    with app.app_context():
        # Check if user exists and is an admin
        admin = User.query.filter_by(phone=phone, role='authority').first()
        if not admin:
            print(f"\nError: No Admin Officer found with phone {phone}")
            return False

        try:
            name = admin.name
            district = admin.assigned_district
            db.session.delete(admin)
            db.session.commit()
            print(f"\nSuccessfully removed Admin Officer: {name} ({phone}) from {district}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"\nError removing admin from database: {e}")
            return False

if __name__ == "__main__":
    print("--- Admin Officer Management ---")
    print("1. Add New Admin Officer")
    print("2. Remove Existing Admin Officer")
    print("3. Exit")
    
    choice = input("\nSelect an option (1-3): ").strip()
    
    if choice == '1':
        print("\n--- Add New Admin Officer ---")
        phone = input("Enter Phone Number: ").strip()
        name = input("Enter Name: ").strip()
        state = input("Enter Assigned State: ").strip()
        district = input("Enter Assigned District: ").strip()
        try:
            lat = float(input("Enter Central Latitude: ").strip())
            lng = float(input("Enter Central Longitude: ").strip())
            lat_min = float(input("Enter District Min Latitude: ").strip())
            lat_max = float(input("Enter District Max Latitude: ").strip())
            lon_min = float(input("Enter District Min Longitude: ").strip())
            lon_max = float(input("Enter District Max Longitude: ").strip())
            
            add_admin(phone, name, state, district, lat, lng, lat_min, lat_max, lon_min, lon_max)
        except ValueError:
            print("\nError: Latitude/Longitude values must be numbers.")
            
    elif choice == '2':
        print("\n--- Remove Admin Officer ---")
        phone = input("Enter Phone Number of Admin to remove: ").strip()
        confirm = input(f"Are you sure you want to remove admin with phone {phone}? (y/n): ").strip().lower()
        if confirm == 'y':
            remove_admin(phone)
        else:
            print("Operation cancelled.")
            
    elif choice == '3':
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid choice. Exiting...")
        sys.exit(1)
