try:
    import gevent.monkey
    gevent.monkey.patch_all()
except ImportError:
    pass

from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)
