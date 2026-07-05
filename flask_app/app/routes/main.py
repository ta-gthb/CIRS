from flask import render_template, jsonify, request, session, redirect, url_for, current_app
from flask_login import login_required, current_user
from . import main_bp
from ..models.models import User, Report, Message, db, get_ist_time
from datetime import timedelta

@main_bp.route('/')
def index():
    resolved_count = Report.query.filter_by(status='resolved').count()
    
    # Online users (active in last 5 minutes)
    now = get_ist_time()
    online_threshold = now - timedelta(minutes=5)
    online_users = User.query.filter(User.last_seen >= online_threshold).count()
    
    # Total registered users
    total_users = User.query.count()
    
    cities_count = db.session.query(Report.city).filter(Report.city != None).distinct().count()
    
    # Fetch all reports for the public map
    all_reports = Report.query.all()
    
    return render_template('index.html', 
                           resolved=resolved_count, 
                           online_users=online_users,
                           total_users=total_users,
                           cities=cities_count,
                           reports=all_reports)

@main_bp.route('/set_language/<lang_code>')
def set_language(lang_code):
    if lang_code in current_app.config['LANGUAGES']:
        session['language'] = lang_code
    return redirect(request.referrer or url_for('main.index'))

@main_bp.route('/api/messages/<int:report_id>', methods=['GET'])
@login_required
def get_messages(report_id):
    report = Report.query.get_or_404(report_id)
    
    if current_user.role == 'authority' and (not current_user.email_verified or not current_user.email or current_user.pending_email):
        return jsonify({'error': _('Please verify your email id before accessing administrative tasks.')}), 403

    # Security: Author or Authority
    if current_user.role != 'authority' and report.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    messages = Message.query.filter_by(report_id=report_id).order_by(Message.timestamp.asc()).all()
    return jsonify([{
        'sender': m.sender.name or m.sender.phone,
        'role': m.sender.role,
        'content': m.content,
        'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M')
    } for m in messages])

@main_bp.route('/api/messages/<int:report_id>', methods=['POST'])
@login_required
def send_message(report_id):
    report = Report.query.get_or_404(report_id)
    
    if current_user.role == 'authority' and (not current_user.email_verified or not current_user.email or current_user.pending_email):
        return jsonify({'error': _('Please verify your email id before accessing administrative tasks.')}), 403

    if current_user.role != 'authority' and report.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    content = request.json.get('content')
    if not content:
        return jsonify({'error': 'Content is required'}), 400
        
    message = Message(report_id=report_id, sender_id=current_user.id, content=content)
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'sender': current_user.name or current_user.phone,
        'role': current_user.role,
        'content': message.content,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M')
    })
