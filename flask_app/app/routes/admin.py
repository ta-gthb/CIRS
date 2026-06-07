from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_babel import _
from datetime import datetime, timedelta
from . import admin_bp
from ..models.models import Report, User, db

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'authority':
        return redirect(url_for('main.index'))
        
    assigned_state = current_user.assigned_state
    assigned_district = current_user.assigned_district
    
    # Filtering parameters
    priority_filter = request.args.get('priority')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Report.query
    if assigned_state:
        query = query.filter_by(state=assigned_state)
    if assigned_district:
        query = query.filter_by(city=assigned_district)
        
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    if start_date:
        query = query.filter(Report.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        # Add 1 day to end_date to include the full day
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(Report.created_at < end_dt)
        
    pending = query.filter_by(status='pending').count()
    resolved = query.filter_by(status='resolved').count()
    acknowledged = query.filter_by(status='acknowledged').count()
    total_assigned = query.count()
    
    reports = query.order_by(Report.created_at.desc()).all()
    
    # Deletion requests (filtered by area)
    del_query = User.query.filter_by(account_deletion_status='requested')
    if assigned_state:
        del_query = del_query.filter_by(state=assigned_state)
    if assigned_district:
        del_query = del_query.filter_by(district=assigned_district)
    
    deletion_requests = del_query.all()
    
    return render_template('admin_dashboard.html', 
                           pending=pending, 
                           resolved=resolved,
                           acknowledged=acknowledged,
                           total_assigned=total_assigned,
                           reports=reports, 
                           deletion_requests=deletion_requests,
                           priority_filter=priority_filter,
                           start_date=start_date,
                           end_date=end_date)

@admin_bp.route('/profile')
@login_required
def profile():
    if current_user.role != 'authority':
        return redirect(url_for('main.index'))
    return render_template('admin_profile.html', user=current_user)

@admin_bp.route('/report-details/<int:report_id>')
@login_required
def report_details(report_id):
    if current_user.role != 'authority':
        return jsonify({'error': _('Unauthorized')}), 403
    
    report = Report.query.get_or_404(report_id)
    images = [{'url': img.url} for img in report.images]
    voice_notes = [{'url': vn.url} for vn in report.voice_notes]
    
    return jsonify({
        'id': report.id,
        'title': report.title,
        'description': report.description,
        'category': report.category,
        'priority': report.priority,
        'status': report.status,
        'latitude': report.latitude,
        'longitude': report.longitude,
        'city': report.city,
        'state': report.state,
        'created_at': report.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'images': images,
        'voice_notes': voice_notes
    })

@admin_bp.route('/approve-report/<int:report_id>')
@login_required
def approve_report(report_id):
    report = Report.query.get_or_404(report_id)
    report.status = 'acknowledged'
    db.session.commit()
    flash(_('Report approved.'), 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/resolve-report/<int:report_id>', methods=['POST'])
@login_required
def resolve_report(report_id):
    notes = request.form.get('notes')
    report = Report.query.get_or_404(report_id)
    report.status = 'resolved'
    report.resolution_notes = notes
    db.session.commit()
    flash(_('Report resolved.'), 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/approve-deletion/<int:user_id>')
@login_required
def approve_deletion(user_id):
    user = User.query.get_or_404(user_id)
    user.account_deletion_status = 'approved'
    user.is_active = False
    db.session.commit()
    flash(_('User deletion approved.'), 'success')
    return redirect(url_for('admin.dashboard'))
