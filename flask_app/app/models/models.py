from datetime import datetime
from flask_login import UserMixin
from .. import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='citizen') # citizen, authority
    state = db.Column(db.String(100))
    district = db.Column(db.String(100))
    address = db.Column(db.Text)
    assigned_state = db.Column(db.String(100))
    assigned_district = db.Column(db.String(100))
    account_deletion_status = db.Column(db.String(20), default='none') # none, requested, approved
    is_active = db.Column(db.Boolean, default=True)
    deleted_at = db.Column(db.DateTime)
    latitude = db.Column(db.Float) # Centroid Lat
    longitude = db.Column(db.Float) # Centroid Lng
    lat_min = db.Column(db.Float)
    lat_max = db.Column(db.Float)
    lon_min = db.Column(db.Float)
    lon_max = db.Column(db.Float)
    otp_code = db.Column(db.String(6))
    otp_expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    citizen_id = db.Column(db.String(25), unique=True, index=True)
    
    reports = db.relationship('Report', backref='author', lazy=True, foreign_keys='Report.user_id')
    upvotes = db.relationship('Upvote', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='pending') # pending, acknowledged, in_progress, resolved
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    upvotes_count = db.Column(db.Integer, default=0)
    resolution_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    images = db.relationship('ReportImage', backref='report', lazy=True)
    voice_notes = db.relationship('VoiceNote', backref='report', lazy=True)
    upvotes = db.relationship('Upvote', backref='report', lazy=True)
    comments = db.relationship('Comment', backref='report', lazy=True)

class Upvote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'report_id', name='unique_user_report_upvote'),)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ReportImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(100))
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)

class VoiceNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    duration = db.Column(db.Float)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    sender = db.relationship('User', backref='sent_messages')
    report = db.relationship('Report', backref='messages')
