from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_babel import Babel, _
import os
from .config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
socketio = SocketIO()
babel = Babel()

def get_locale():
    from flask import request, session, current_app
    lang = session.get('language')
    if lang:
        return lang
    return request.accept_languages.best_match(current_app.config['LANGUAGES'].keys())

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    
    # Register models
    with app.app_context():
        from .models.models import User, Report, Upvote, Comment, ReportImage, VoiceNote, Message

    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Explicitly set translation directory to avoid any path issues
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(app.root_path, 'translations')
    babel.init_app(app, locale_selector=get_locale)

    from .routes import auth_bp, citizen_bp, admin_bp, main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(citizen_bp, url_prefix='/citizen')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(main_bp)

    return app
