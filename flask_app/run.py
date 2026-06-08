try:
    import gevent.monkey
    gevent.monkey.patch_all()
except ImportError:
    pass

from app import create_app, socketio, db

app = create_app()

# Force table creation at runtime
with app.app_context():
    try:
        db.create_all()
        print("Database tables verified/created at runtime.")
    except Exception as e:
        print(f"Runtime table creation warning: {e}")

if __name__ == '__main__':
    socketio.run(app, debug=True)
