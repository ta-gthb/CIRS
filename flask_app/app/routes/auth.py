from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import _
from datetime import datetime, timedelta
from . import auth_bp
from ..models.models import User, db, get_ist_time
from ..utils.email_utils import generate_otp, queue_email_otp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role') # citizen or authority
        
        if role == 'authority':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username, role='authority').first()
            
            if user and user.check_password(password):
                if not user.is_active:
                    flash(_('Account is inactive.'), 'danger')
                    return redirect(url_for('auth.login'))
                
                login_user(user)
                
                # Security Check: Force password change if default
                if password == 'admin123':
                    flash(_('Security Warning: You are using the default password. Please change it immediately.'), 'warning')
                    return redirect(url_for('admin.profile'))

                if user.role == 'authority' and not user.email_verified:
                    flash(_('Please verify your email id before accessing administrative tasks.'), 'warning')
                    return redirect(url_for('admin.profile'))
                
                return redirect(url_for('admin.dashboard'))
            else:
                flash(_('Invalid username or password.'), 'danger')
                return redirect(url_for('auth.login'))

        # Citizen Flow (OTP)
        phone = request.form.get('phone')
        user = User.query.filter_by(phone=phone).first()
        
        if user and user.account_deletion_status == 'approved':
            # Check 30 days rule
            wait_period = timedelta(days=30)
            if get_ist_time() < user.deleted_at + wait_period:
                next_date = (user.deleted_at + timedelta(days=31)).strftime('%d/%m/%Y')
                flash(_('You can register to the system again on %(date)s as your account is deleted recently', date=next_date), 'warning')
                return redirect(url_for('auth.login'))
            else:
                # Reset deleted account for re-registration
                user.account_deletion_status = 'none'
                user.is_active = True
                user.deleted_at = None
                db.session.commit()

        if not user:
            if role == 'citizen':
                # Auto-register citizen
                serial_count = User.query.filter_by(role='citizen').count() + 1
                year = get_ist_time().year
                citizen_id = f"CTZN10CIRS{year}{serial_count:07d}"
                user = User(phone=phone, role='citizen', is_active=True, citizen_id=citizen_id)
                db.session.add(user)
                db.session.commit()
            else:
                # This should theoretically not be reached with the new logic, but kept for safety
                flash(_('Officer not registered. Contact administrator.'), 'danger')
                return redirect(url_for('auth.login'))
        
        if user.role != role:
            flash(_('Number registered as %(role)s. Choose correct role.', role=user.role), 'warning')
            return redirect(url_for('auth.login'))
            
        if user.account_deletion_status == 'approved' or not user.is_active:
            flash(_('Account is inactive or deleted.'), 'danger')
            return redirect(url_for('auth.login'))

        # Simulation: demo OTP 1234
        user.otp_code = '1234'
        user.otp_expires_at = get_ist_time() + timedelta(minutes=10)
        db.session.commit()
        
        return redirect(url_for('auth.verify_otp', phone=phone))
        
    return render_template('login.html')

@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    phone = request.args.get('phone')
    if request.method == 'POST':
        otp = request.form.get('otp')
        user = User.query.filter_by(phone=phone).first()
        
        if user and (otp == '1234' or user.otp_code == otp) and user.otp_expires_at > get_ist_time():
            user.otp_code = None
            db.session.commit()
            login_user(user)
            if user.role == 'authority':
                if not user.email_verified:
                    flash(_('Please verify your email id before accessing administrative tasks.'), 'warning')
                    return redirect(url_for('admin.profile'))
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('citizen.dashboard'))
        else:
            flash(_('Invalid or expired OTP.'), 'danger')
            
    return render_template('verify_otp.html', phone=phone)


@auth_bp.route('/verify-email', methods=['GET', 'POST'])
@login_required
def verify_email():
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        if not current_user.email_otp_code or not current_user.email_otp_expires_at:
            flash(_('No email verification is pending.'), 'warning')
            return redirect(url_for('auth.verify_email'))

        if otp and current_user.email_otp_code == otp and current_user.email_otp_expires_at > get_ist_time():
            if current_user.pending_email:
                current_user.email = current_user.pending_email
            current_user.pending_email = None
            current_user.email_verified = True
            current_user.email_otp_code = None
            current_user.email_otp_expires_at = None
            db.session.commit()
            flash(_('Email id verified successfully.'), 'success')
            if current_user.role == 'authority':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('citizen.profile'))

        flash(_('Invalid or expired OTP.'), 'danger')

    return render_template('verify_email.html', email=current_user.pending_email or current_user.email)


@auth_bp.route('/resend-email-otp', methods=['POST'])
@login_required
def resend_email_otp():
    target_email = current_user.pending_email or current_user.email
    if not target_email:
        flash(_('Please add an email id first.'), 'warning')
        return redirect(url_for('citizen.profile') if current_user.role == 'citizen' else url_for('admin.profile'))

    current_user.pending_email = target_email
    current_user.email_verified = False
    current_user.email_otp_code = generate_otp()
    current_user.email_otp_expires_at = get_ist_time() + timedelta(minutes=10)
    db.session.commit()

    queue_email_otp(target_email, current_user.email_otp_code)
    flash(_('A new verification OTP has been sent to your email id.'), 'success')
    return redirect(url_for('auth.verify_email'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
