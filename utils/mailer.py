from flask_mail import Message
from extensions import mail


def send_reset_email(email, token):
    reset_link = f"http://localhost:3000/reset-password?token={token}"

    msg = Message(
        subject="Password Reset",
        recipients=[email],
        body=f"Click the link to reset your password:\n\n{reset_link}\n\nThis link expires in 10 minutes."
    )

    mail.send(msg)
