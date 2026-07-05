import secrets
import smtplib
import ssl
import re
import threading
from email.message import EmailMessage

from flask import current_app


EMAIL_PATTERN = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def generate_otp(length=6):
    digits = '0123456789'
    return ''.join(secrets.choice(digits) for _ in range(length))


def is_valid_email(email_address):
    return bool(email_address and EMAIL_PATTERN.match(email_address))


def send_email_otp(recipient_email, otp_code):
    sender_email = current_app.config['EMAIL_SENDER']
    smtp_host = current_app.config['EMAIL_SMTP_HOST']
    smtp_port = current_app.config['EMAIL_SMTP_PORT']
    smtp_username = current_app.config['EMAIL_SMTP_USERNAME']
    smtp_password = current_app.config['EMAIL_SMTP_PASSWORD']
    use_tls = current_app.config['EMAIL_SMTP_USE_TLS']
    smtp_timeout = current_app.config.get('EMAIL_SMTP_TIMEOUT', 10)

    if not smtp_password:
        raise RuntimeError('EMAIL_SMTP_PASSWORD is not configured')

    message = EmailMessage()
    message['Subject'] = 'CIRS Email Verification OTP'
    message['From'] = sender_email
    message['To'] = recipient_email
    message.set_content(
        f'Your CIRS email verification OTP is {otp_code}. It will expire in 10 minutes.'
    )

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_host, smtp_port, timeout=smtp_timeout) as server:
        server.ehlo()
        if use_tls:
            server.starttls(context=context)
            server.ehlo()
        server.login(smtp_username, smtp_password)
        server.send_message(message)


def queue_email_otp(recipient_email, otp_code):
    app = current_app._get_current_object()

    def _deliver():
        with app.app_context():
            send_email_otp(recipient_email, otp_code)

    try:
        import gevent
        gevent.spawn(_deliver)
        return True
    except Exception:
        worker = threading.Thread(target=_deliver, daemon=True)
        worker.start()
        return True