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
import requests

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


def send_otp_email_ses(email, otp):
    """Send OTP using AWS SES API"""
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        region = os.getenv('AWS_SES_REGION', 'us-east-1')
        access_key = os.getenv('AWS_SES_ACCESS_KEY_ID')
        secret_key = os.getenv('AWS_SES_SECRET_ACCESS_KEY')
        from_email = os.getenv('AWS_SES_FROM_EMAIL', '21bq1a0569@gmail.com')
        
        if not access_key or not secret_key:
            print("❌ AWS SES credentials not found")
            return False
            
        # Create SES client
        ses = boto3.client(
            'ses',
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        
        # Send email
        response = ses.send_email(
            Source=from_email,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': 'Your Login OTP'},
                'Body': {'Text': {'Data': f"Your OTP is {otp}. It expires in 5 minutes."}}
            }
        )
        
        print(f"✅ OTP email sent via AWS SES to {email}")
        print(f"📧 Message ID: {response.get('MessageId')}")
        return True
        
    except ImportError:
        print("❌ boto3 not installed - adding to requirements")
        return False
    except ClientError as e:
        print(f"❌ AWS SES error: {e}")
        return False
    except Exception as e:
        print(f"❌ AWS SES error: {str(e)}")
        return False


def send_otp_email(email, otp):
    """Send OTP using Flask-Mail with proper error logging"""
    try:
        print(f"📧 Attempting to send OTP to {email}")
        print(f"🔧 Mail Server: {current_app.config.get('MAIL_SERVER')}")
        print(f"🔧 Mail Port: {current_app.config.get('MAIL_PORT')}")
        print(f"🔧 Mail Username: {current_app.config.get('MAIL_USERNAME')}")
        print(f"🔧 Mail TLS: {current_app.config.get('MAIL_USE_TLS')}")
        print(f"🔧 Mail SSL: {current_app.config.get('MAIL_USE_SSL')}")
        print(f"🔧 Mail Debug: {current_app.config.get('MAIL_DEBUG')}")
        print(f"🔧 Mail Password Set: {'Yes' if current_app.config.get('MAIL_PASSWORD') else 'No'}")

        msg = Message(
            subject="Your Login OTP",
            sender=current_app.config.get('MAIL_DEFAULT_SENDER'),
            recipients=[email]
        )
        msg.body = f"Your OTP is {otp}. It expires in 5 minutes."
        
        # Enable SMTP debugging
        import smtplib
        smtplib.SMTP.debuglevel = 1
        
        mail.send(msg)
        print(f"✅ OTP email sent successfully to {email}")
        
    except Exception as e:
        print(f"❌ SMTP ERROR: {str(e)}")
        print(f"❌ ERROR TYPE: {type(e).__name__}")
        print(f"❌ ERROR DETAILS: {repr(e)}")
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