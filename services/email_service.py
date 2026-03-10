import os
import smtplib
from email.mime.text import MIMEText
from flask_mail import Message, Mail
from flask import current_app
from extensions import mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from dotenv import load_dotenv
import secrets
import string

load_dotenv()

SECRET_KEY = "super-secret-key"
serializer = URLSafeTimedSerializer(SECRET_KEY)


# Generate token
def generate_reset_token(email):
    return serializer.dumps(email, salt="password-reset")


# Verify token
def verify_reset_token(token, max_age=86400):
    try:
        email = serializer.loads(token, salt="password-reset", max_age=max_age)
        return {"valid": True, "email": email}
    except SignatureExpired:
        return {"valid": False, "message": "Token expired"}
    except Exception:
        return {"valid": False, "message": "Invalid token"}


# Send reset email
def send_reset_email(email, token):
    reset_link = f"{os.getenv('RESET_URL')}?token={token}"

    body = f"""
Reset your password:

Click the link below:

{reset_link}

This link expires in 24 hours.
"""

    msg = MIMEText(body)
    msg['Subject'] = "Password Reset"
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = email

    try:
        with smtplib.SMTP(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
            server.send_message(msg)
        print(f"✅ Password reset email sent successfully to {email}")
    except Exception as e:
        print(f"❌ Email sending failed: {str(e)}")
        print(f"🔧 Error type: {type(e).__name__}")
        return False


def send_otp_email(email, otp):
    try:
        print(f"📧 Attempting to send OTP to {email}")
        print(f"🔧 Mail Server: {current_app.config.get('MAIL_SERVER')}")
        print(f"🔧 Mail Port: {current_app.config.get('MAIL_PORT')}")
        print(f"🔧 Mail Username: {current_app.config.get('MAIL_USERNAME')}")
        print(f"🔧 Mail TLS: {current_app.config.get('MAIL_USE_TLS')}")

        msg = Message(
            subject="Your Login OTP",
            recipients=[email]
        )
        msg.body = f"Your OTP is {otp}. It expires in 5 minutes."
        mail.send(msg)
        print(f"✅ OTP email sent successfully to {email}")
    except Exception as e:
        print(f"❌ Email sending failed: {str(e)}")
        print(f"🔧 Error type: {type(e).__name__}")
        raise e


def generate_random_password(length=12):
    """Generate a random password with letters, digits, and special characters"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def send_credentials_email(email, username, password):
    """Send login credentials to the client's email using Flask-Mail"""
    body = f"""
    Welcome to Our Platform!

    Your account has been created successfully. Here are your login details:

    Username: {username}
    Password: {password}

    Please log in at: {os.getenv('FRONTEND_URL', 'http://localhost:5173/')}

    For security reasons, we recommend changing your password after first login.

    Best regards,
    The Team
    """

    try:
        msg = Message(
            subject="Your Account Credentials",
            sender=os.getenv("MAIL_USERNAME", "21bq1a0569@gmail.com"),
            recipients=[email],
            body=body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False