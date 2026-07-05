import os
import math
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from flask_babel import _
from sqlalchemy import or_
from . import citizen_bp
from ..models.models import Report, User, db, ReportImage, VoiceNote, Upvote, Comment, get_ist_time
from ..utils.storage_utils import upload_file
from ..utils.geo_utils import reverse_geocode
from ..utils.email_utils import generate_otp, queue_email_otp, is_valid_email
from sqlalchemy import func

def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine formula to calculate distance in meters"""
    R = 6371000 # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

@citizen_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'citizen':
        return redirect(url_for('main.index'))
        
    # Highly reported issues (by upvotes) near citizen location (if available)
    # For now, simple sorting by upvotes as proximity requires more complex SQL or post-processing
    reports = Report.query.order_by(Report.upvotes_count.desc()).limit(10).all()
    
    return render_template('citizen_dashboard.html', 
                           reports=reports)

@citizen_bp.route('/public-forum')
@login_required
def public_forum():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('public_forum.html', reports=reports)

@citizen_bp.route('/status')
@login_required
def status():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Report.query.filter_by(user_id=current_user.id)
    
    if start_date:
        query = query.filter(Report.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(Report.created_at < end_dt)
        
    my_reports = query.order_by(Report.created_at.desc()).all()
    
    return render_template('status.html', 
                           reports=my_reports, 
                           start_date=start_date, 
                           end_date=end_date)

@citizen_bp.route('/live-map')
@login_required
def live_map():
    reports = Report.query.all()
    return render_template('live_map.html', 
                           reports=reports)

@citizen_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@citizen_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    email_address = (request.form.get('email') or '').strip().lower()
    current_email = (current_user.email or '').strip().lower()
    email_needs_verification = bool(email_address) and email_address != current_email

    if email_address and not is_valid_email(email_address):
        flash(_('Please enter a valid email id.'), 'danger')
        return redirect(url_for('citizen.profile'))

    if email_address:
        existing_user = User.query.filter(
            User.id != current_user.id,
            or_(User.email == email_address, User.pending_email == email_address)
        ).first()
        if existing_user:
            flash(_('This email id is already registered with another account.'), 'danger')
            return redirect(url_for('citizen.profile'))

    current_user.name = request.form.get('name')
    current_user.address = request.form.get('address')
    current_user.state = request.form.get('state')
    current_user.district = request.form.get('district')

    if email_needs_verification:
        current_user.pending_email = email_address
        current_user.email_verified = False
        current_user.email_otp_code = generate_otp()
        current_user.email_otp_expires_at = get_ist_time() + timedelta(minutes=10)

    try:
        db.session.flush()
        if email_needs_verification:
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash(_('Failed to send verification OTP to your email id. Please try again.'), 'danger')
        return redirect(url_for('citizen.profile'))

    if email_needs_verification:
        queue_email_otp(email_address, current_user.email_otp_code)
        flash(_('A verification OTP has been sent to your email id.'), 'success')
        return redirect(url_for('auth.verify_email'))

    flash(_('Profile updated successfully!'), 'success')
    return redirect(url_for('citizen.profile'))

@citizen_bp.route('/report', methods=['GET', 'POST'])
@login_required
def submit_report():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        lat_val = request.form.get('latitude')
        lng_val = request.form.get('longitude')
        
        if not title or not description or not category:
            flash(_('All fields (Title, Description, Category) are required.'), 'danger')
            return redirect(url_for('citizen.submit_report'))
        
        if not lat_val or not lng_val:
            flash(_('Location is required. Please enable GPS and allow location access.'), 'danger')
            return redirect(url_for('citizen.submit_report'))

        lat = float(lat_val) if lat_val else None
        lng = float(lng_val) if lng_val else None
        city = request.form.get('city')
        state = request.form.get('state')
        address = ""

        # Try to get city (district), state and full address from coordinates
        if lat and lng:
            geo_city, geo_state, geo_addr = reverse_geocode(lat, lng)
            if geo_city and not city:
                city = geo_city
            if geo_state and not state:
                state = geo_state
            if geo_addr:
                address = geo_addr

        # If city/state still unknown, find nearest admin officer using border info (bounding boxes)
        # as a fallback to ensure the report is seen by SOMEONE
        if lat and lng and (not city or not state):
            admins = User.query.filter_by(role='authority').filter(User.latitude.isnot(None), User.longitude.isnot(None)).all()
            if admins:
                # 1. Check if the point is inside any admin's district bounding box
                matching_admins = []
                for admin in admins:
                    if admin.lat_min and admin.lat_max and admin.lon_min and admin.lon_max:
                        if admin.lat_min <= lat <= admin.lat_max and admin.lon_min <= lng <= admin.lon_max:
                            matching_admins.append(admin)
                
                nearest_admin = None
                if matching_admins:
                    # If inside multiple boxes, pick the one with nearest centroid
                    min_dist = float('inf')
                    for admin in matching_admins:
                        dist = calculate_distance(lat, lng, admin.latitude, admin.longitude)
                        if dist < min_dist:
                            min_dist = dist
                            nearest_admin = admin
                else:
                    # 2. If not inside any box, pick the one with the absolute nearest centroid
                    min_distance = float('inf')
                    for admin in admins:
                        dist = calculate_distance(lat, lng, admin.latitude, admin.longitude)
                        if dist < min_distance:
                            min_distance = dist
                            nearest_admin = admin
                
                if nearest_admin:
                    # Only override if we don't have a specific city/state from geocoding
                    if not city: city = nearest_admin.assigned_district
                    if not state: state = nearest_admin.assigned_state
        
        if lat and lng:
            # Check for duplicates within 100m and same category
            existing_reports = Report.query.filter_by(category=category, status='pending').all()
            for existing in existing_reports:
                if existing.latitude and existing.longitude:
                    distance = calculate_distance(lat, lng, existing.latitude, existing.longitude)
                    if distance <= 100:
                        # Duplicate found - upvote instead (if not own)
                        if existing.user_id != current_user.id:
                            existing_upvote = Upvote.query.filter_by(user_id=current_user.id, report_id=existing.id).first()
                            if not existing_upvote:
                                upvote = Upvote(user_id=current_user.id, report_id=existing.id)
                                existing.upvotes_count += 1
                                existing.update_priority()
                                db.session.add(upvote)
                                db.session.commit()
                                flash(_('A similar report already exists in this location. Your upvote has been added to it.'), 'info')
                            else:
                                flash(_('A similar report already exists and you have already upvoted it.'), 'warning')
                        else:
                            flash(_('You have already submitted a similar report in this location.'), 'warning')
                        return redirect(url_for('citizen.dashboard'))

        report = Report(
            title=title,
            description=description,
            category=category,
            priority='low',
            latitude=lat,
            longitude=lng,
            city=city,
            state=state,
            address=address,
            user_id=current_user.id
        )
        db.session.add(report)
        db.session.flush()
        
        # Handle Image Uploads
        images = request.files.getlist('images')
        
        # Check if at least one image is provided
        has_valid_image = any(img.filename for img in images)
        if not has_valid_image:
            flash(_('Please upload or capture at least one image of the issue.'), 'danger')
            return redirect(url_for('citizen.submit_report'))

        if len(images) > 3:
            flash(_('You can only upload up to 3 images.'), 'danger')
            return redirect(url_for('citizen.submit_report'))

        try:
            for img in images:
                if img.filename:
                    url, public_id = upload_file(img, folder="civic_issue/reports")
                    report_img = ReportImage(url=url, public_id=public_id, report_id=report.id)
                    db.session.add(report_img)
                    
            # Handle Voice Note Upload
            voice = request.files.get('voice')
            if voice and voice.filename:
                url, unused_id = upload_file(voice, folder="civic_issue/voice")
                voice_note = VoiceNote(url=url, report_id=report.id)
                db.session.add(voice_note)
        except Exception as e:
            db.session.rollback()
            print(f"File upload error: {e}")
            flash(_('Failed to upload files. Please try again later.'), 'danger')
            return redirect(url_for('citizen.submit_report'))
            
        db.session.commit()
        flash(_('Report submitted successfully!'), 'success')
        return redirect(url_for('citizen.dashboard'))
        
    return render_template('submit_report.html')

@citizen_bp.route('/upvote/<int:report_id>', methods=['POST'])
@login_required
def upvote(report_id):
    report = Report.query.get_or_404(report_id)
    
    if report.user_id == current_user.id:
        return jsonify({'success': False, 'message': _('You cannot upvote your own report.')}), 400
        
    existing_upvote = Upvote.query.filter_by(user_id=current_user.id, report_id=report_id).first()
    if existing_upvote:
        return jsonify({'success': False, 'message': _('Already upvoted')}), 400
        
    upvote = Upvote(user_id=current_user.id, report_id=report_id)
    report.upvotes_count += 1
    report.update_priority()
    db.session.add(upvote)
    db.session.commit()
    return jsonify({'success': True, 'upvotes': report.upvotes_count})

@citizen_bp.route('/comment/<int:report_id>', methods=['POST'])
@login_required
def add_comment(report_id):
    content = request.form.get('content')
    if not content:
        return redirect(request.referrer)
        
    comment = Comment(content=content, user_id=current_user.id, report_id=report_id)
    db.session.add(comment)
    db.session.commit()
    flash(_('Comment added.'), 'success')
    return redirect(request.referrer)

@citizen_bp.route('/reopen-report/<int:report_id>', methods=['POST'])
@login_required
def reopen_report(report_id):
    report = Report.query.get_or_404(report_id)
    if report.user_id != current_user.id:
        flash(_('Unauthorized.'), 'danger')
        return redirect(url_for('citizen.status'))
        
    if report.status == 'resolved':
        # Check if resolved within 7 days
        if report.resolved_at:
            if get_ist_time() > report.resolved_at + timedelta(days=7):
                flash(_('Report cannot be reopened after 7 days of resolution.'), 'warning')
                return redirect(url_for('citizen.status'))
        
        report.status = 'acknowledged'
        db.session.commit()
        flash(_('Report reopened.'), 'info')
    else:
        flash(_('Report cannot be reopened.'), 'warning')
        
    return redirect(url_for('citizen.status'))

@citizen_bp.route('/request-deletion', methods=['POST'])
@login_required
def request_deletion():
    if not current_user.state or not current_user.district:
        flash(_('Please update your State and District in your profile before requesting account deletion.'), 'warning')
        return redirect(url_for('citizen.profile'))
    
    current_user.account_deletion_status = 'requested'
    db.session.commit()
    flash(_('Deletion request submitted to your assigned officer. Your account will be deleted after approval of Admin Officer.'), 'info')
    return redirect(url_for('citizen.profile'))
