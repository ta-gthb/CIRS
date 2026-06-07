from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import _
from datetime import datetime, timedelta
from . import auth_bp
from ..models.models import User, db

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        role = request.form.get('role') # citizen or authority
        
        user = User.query.filter_by(phone=phone).first()
        
        if user and user.account_deletion_status == 'approved':
            # Check 30 days rule
            wait_period = timedelta(days=30)
            if datetime.utcnow() < user.deleted_at + wait_period:
                next_date = (user.deleted_at + timedelta(days=31)).strftime('%d/%m/%Y')
                flash(_('You can register to the system again on %(date)s', date=next_date), 'warning')
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
                year = datetime.utcnow().year
                citizen_id = f"CTZN10CIRS{year}{serial_count:07d}"
                user = User(phone=phone, role='citizen', is_active=True, citizen_id=citizen_id)
                db.session.add(user)
                db.session.commit()
            else:
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
        user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()
        
        return redirect(url_for('auth.verify_otp', phone=phone))
        
    return render_template('login.html')

@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    phone = request.args.get('phone')
    if request.method == 'POST':
        otp = request.form.get('otp')
        user = User.query.filter_by(phone=phone).first()
        
        if user and (otp == '1234' or user.otp_code == otp) and user.otp_expires_at > datetime.utcnow():
            user.otp_code = None
            db.session.commit()
            login_user(user)
            if user.role == 'authority':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('citizen.dashboard'))
        else:
            flash(_('Invalid or expired OTP.'), 'danger')
            
    return render_template('verify_otp.html', phone=phone)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
