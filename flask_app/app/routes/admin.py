from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_babel import _
from datetime import datetime, timedelta
from sqlalchemy import or_
from . import admin_bp
from ..models.models import Report, User, db, get_ist_time
from ..utils.email_utils import generate_otp, send_email_otp, is_valid_email


@admin_bp.before_request
def ensure_verified_email_for_admin_tasks():
    if not current_user.is_authenticated or current_user.role != 'authority':
        return

    if request.endpoint == 'admin.profile':
        return

    if current_user.email_verified and current_user.email and not current_user.pending_email:
        return

    flash(_('Please add and verify your email id to perform administrative tasks.'), 'warning')
    return redirect(url_for('admin.profile'))

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

@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role != 'authority':
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Check if it's a phone update or password update
        action = request.form.get('action')
        
        if action == 'update_phone':
            new_phone = request.form.get('phone')
            if not new_phone or len(new_phone) != 10:
                flash(_('Please enter a valid 10-digit phone number.'), 'danger')
            else:
                # Check if phone is already taken
                existing_user = User.query.filter_by(phone=new_phone).first()
                if existing_user and existing_user.id != current_user.id:
                    flash(_('This phone number is already registered.'), 'danger')
                else:
                    current_user.phone = new_phone
                    db.session.commit()
                    flash(_('Phone number updated successfully.'), 'success')

        elif action == 'update_email':
            email_address = (request.form.get('email') or '').strip().lower()
            current_email = (current_user.email or '').strip().lower()
            email_needs_verification = bool(email_address) and email_address != current_email

            if not email_address:
                flash(_('Please enter an email id.'), 'danger')
            elif not is_valid_email(email_address):
                flash(_('Please enter a valid email id.'), 'danger')
            else:
                existing_user = User.query.filter(
                    User.id != current_user.id,
                    or_(User.email == email_address, User.pending_email == email_address)
                ).first()
                if existing_user:
                    flash(_('This email id is already registered with another account.'), 'danger')
                else:
                    if email_needs_verification:
                        current_user.pending_email = email_address
                        current_user.email_verified = False
                        current_user.email_otp_code = generate_otp()
                        current_user.email_otp_expires_at = get_ist_time() + timedelta(minutes=10)

                    try:
                        db.session.flush()
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
                        flash(_('Failed to send verification OTP to your email id. Please try again.'), 'danger')
                        return redirect(url_for('admin.profile'))

                    if email_needs_verification:
                        try:
                            send_email_otp(email_address, current_user.email_otp_code)
                            flash(_('A verification OTP has been sent to your email id.'), 'success')
                        except Exception:
                            current_app.logger.exception('Failed to send email OTP to %s', email_address)
                            flash(_('OTP could not be sent. Please check email settings and try again.'), 'danger')
                        return redirect(url_for('auth.verify_email'))

                    flash(_('Email id updated successfully.'), 'success')
        
        elif action == 'change_password':
            current_pwd = request.form.get('current_password')
            new_pwd = request.form.get('new_password')
            confirm_pwd = request.form.get('confirm_password')
            
            if not current_user.check_password(current_pwd):
                flash(_('Incorrect current password.'), 'danger')
            elif new_pwd != confirm_pwd:
                flash(_('New passwords do not match.'), 'danger')
            elif len(new_pwd) < 6:
                flash(_('New password must be at least 6 characters long.'), 'danger')
            else:
                current_user.set_password(new_pwd)
                db.session.commit()
                flash(_('Password updated successfully.'), 'success')
        
        return redirect(url_for('admin.profile'))

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
    report.resolved_at = get_ist_time()
    db.session.commit()
    flash(_('Report resolved.'), 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/reject-report/<int:report_id>', methods=['POST'])
@login_required
def reject_report(report_id):
    if current_user.role != 'authority':
        return jsonify({'error': _('Unauthorized')}), 403
        
    notes = request.form.get('notes')
    report = Report.query.get_or_404(report_id)
    report.status = 'rejected'
    report.resolution_notes = notes # Reuse resolution_notes for rejection reason
    db.session.commit()
    flash(_('Report rejected.'), 'info')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/approve-deletion/<int:user_id>')
@login_required
def approve_deletion(user_id):
    user = User.query.get_or_404(user_id)
    user.account_deletion_status = 'approved'
    user.is_active = False
    user.deleted_at = get_ist_time()
    
    # Delete pending reports of this user
    pending_reports = Report.query.filter_by(user_id=user.id, status='pending').all()
    for report in pending_reports:
        db.session.delete(report)
        
    db.session.commit()
    flash(_('User deletion approved. Pending reports removed.'), 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/reject-deletion/<int:user_id>')
@login_required
def reject_deletion(user_id):
    user = User.query.get_or_404(user_id)
    user.account_deletion_status = 'none'
    db.session.commit()
    flash(_('User deletion request rejected.'), 'info')
    return redirect(url_for('admin.dashboard'))
