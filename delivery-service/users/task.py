from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import smtplib, ssl
from celery import shared_task
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import requests
from django.utils import timezone
from .models import FuelPrice
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from decimal import Decimal
import pytz


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


@shared_task
def get_fuel_prices():
    most_recent_price_date = str(
        timezone.localdate(timezone.now(), pytz.timezone("US/Central"))
    )
    r = requests.get(
        f"https://api.eia.gov/v2/petroleum/pri/gnd/data?api_key={settings.EIA_KEY}&frequency=weekly&data[0]=value&facets[duoarea][]=NUS&facets[duoarea][]=STX&facets[product][]=EPD2DXL0&facets[product][]=EPMPU&facets[series][]=EMD_EPD2DXL0_PTE_NUS_DPG&facets[series][]=EMM_EPMPU_PTE_STX_DPG&facets[process][]=PTE&start={most_recent_price_date}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"
    )

    response_dict = r.json()
    price_list = [
        response_dict["response"]["data"][x]["value"] for x in range(2)
    ]  # From response_dict, add price values to list, these are strings

    FuelPrice.objects.create(
        gas_price=Decimal(price_list[0]), diesel_price=Decimal(price_list[1])
    )


"""schedule, _ = CrontabSchedule.objects.get_or_create(
    minute="0", hour="7", day_of_week="monday"
)

task, _ = PeriodicTask.objects.get_or_create(
    crontab=schedule,
    name="Get fuel prices",
    task="users.task.get_fuel_prices",
)"""
