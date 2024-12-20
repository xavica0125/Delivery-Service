from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import smtplib, ssl
from celery import shared_task
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


@shared_task
def send_password_reset_email(user_id, domain, protocol, token):
    from django.contrib.auth.models import User

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return
    msg = MIMEMultipart()

    # Attach the message
    msg.attach(MIMEText("This is your password reset link.", "plain"))

    # Set the email subject, sender, and receiver
    msg["Subject"] = "Password Reset Link"
    msg["From"] = settings.EMAIL_USER
    msg["To"] = user.email

    reset_link = f"{protocol}://{domain}/reset/{urlsafe_base64_encode(force_bytes(user.pk))}/{token}/"

    # Update the message body to include the reset link
    msg.attach(
        MIMEText(f"Click the link to reset your password: {reset_link}", "plain")
    )
    # Establish a connection to the SMTP server
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        # Log in to the email account
        server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)

        # Send the email
        server.sendmail(settings.EMAIL_USER, user.email, msg.as_string())
