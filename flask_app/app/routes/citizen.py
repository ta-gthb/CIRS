import os
import math
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from . import citizen_bp
from ..models.models import Report, User, db, ReportImage, VoiceNote, Upvote, Comment
from ..utils.cloudinary_utils import upload_to_cloudinary
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
                           reports=reports, 
                           google_maps_api_key=current_app.config.get('GOOGLE_MAPS_API_KEY'))

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
                           reports=reports, 
                           google_maps_api_key=current_app.config.get('GOOGLE_MAPS_API_KEY'))

@citizen_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@citizen_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    current_user.name = request.form.get('name')
    current_user.address = request.form.get('address')
    current_user.state = request.form.get('state')
    current_user.district = request.form.get('district')
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('citizen.profile'))

@citizen_bp.route('/report', methods=['GET', 'POST'])
@login_required
def submit_report():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        priority = request.form.get('priority')
        lat_val = request.form.get('latitude')
        lng_val = request.form.get('longitude')
        lat = float(lat_val) if lat_val else None
        lng = float(lng_val) if lng_val else None
        city = request.form.get('city')
        state = request.form.get('state')
        
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
                                db.session.add(upvote)
                                db.session.commit()
                                flash('A similar report already exists in this location. Your upvote has been added to it.', 'info')
                            else:
                                flash('A similar report already exists and you have already upvoted it.', 'warning')
                        else:
                            flash('You have already submitted a similar report in this location.', 'warning')
                        return redirect(url_for('citizen.dashboard'))

        report = Report(
            title=title,
            description=description,
            category=category,
            priority=priority,
            latitude=lat,
            longitude=lng,
            city=city,
            state=state,
            user_id=current_user.id
        )
        db.session.add(report)
        db.session.flush()
        
        # Handle Image Uploads
        images = request.files.getlist('images')
        if len(images) > 3:
            flash('You can only upload up to 3 images.', 'danger')
            return redirect(url_for('citizen.submit_report'))

        for img in images:
            if img.filename:
                url, public_id = upload_to_cloudinary(img, folder="civic_issue/reports")
                report_img = ReportImage(url=url, public_id=public_id, report_id=report.id)
                db.session.add(report_img)
                
        # Handle Voice Note Upload
        voice = request.files.get('voice')
        if voice and voice.filename:
            url, _ = upload_to_cloudinary(voice, folder="civic_issue/voice")
            voice_note = VoiceNote(url=url, report_id=report.id)
            db.session.add(voice_note)
            
        db.session.commit()
        flash('Report submitted successfully!', 'success')
        return redirect(url_for('citizen.dashboard'))
        
    return render_template('submit_report.html', 
                           google_maps_api_key=current_app.config.get('GOOGLE_MAPS_API_KEY'))

@citizen_bp.route('/upvote/<int:report_id>', methods=['POST'])
@login_required
def upvote(report_id):
    report = Report.query.get_or_404(report_id)
    
    if report.user_id == current_user.id:
        return jsonify({'success': False, 'message': 'You cannot upvote your own report.'}), 400
        
    existing_upvote = Upvote.query.filter_by(user_id=current_user.id, report_id=report_id).first()
    if existing_upvote:
        return jsonify({'success': False, 'message': 'Already upvoted'}), 400
        
    upvote = Upvote(user_id=current_user.id, report_id=report_id)
    report.upvotes_count += 1
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
    flash('Comment added.', 'success')
    return redirect(request.referrer)

@citizen_bp.route('/reopen-report/<int:report_id>', methods=['POST'])
@login_required
def reopen_report(report_id):
    report = Report.query.get_or_404(report_id)
    if report.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('citizen.status'))
        
    if report.status == 'resolved':
        report.status = 'acknowledged'
        db.session.commit()
        flash('Report reopened.', 'info')
    else:
        flash('Report cannot be reopened.', 'warning')
        
    return redirect(url_for('citizen.status'))

@citizen_bp.route('/request-deletion', methods=['POST'])
@login_required
def request_deletion():
    current_user.account_deletion_status = 'requested'
    db.session.commit()
    flash('Deletion request submitted to your assigned officer.', 'info')
    return redirect(url_for('citizen.profile'))
