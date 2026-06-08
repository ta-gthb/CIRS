try:
    import gevent.monkey
    gevent.monkey.patch_all()
except ImportError:
    pass

from app import create_app, socketio, db
from app.models.models import User

app = create_app()

# Force table creation and seeding at runtime
with app.app_context():
    try:
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
            print(f"Admin seeded at runtime: {admin_phone}")
        
        print("Database verification/seeding complete.")
    except Exception as e:
        print(f"Runtime database setup warning: {e}")

if __name__ == '__main__':
    socketio.run(app, debug=True)
