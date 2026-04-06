from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from model.src.config.config import (
    TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER, TWILIO_RECIPIENT,
    GMAIL_USER, GMAIL_APP_PASSWORD, EMAIL_RECIPIENT
)


def send_email(body):
    if not all([GMAIL_USER, GMAIL_APP_PASSWORD, EMAIL_RECIPIENT]):
        print('[sendMessage] Email no configurado — revisar variables de entorno.')
        return

    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = 'AI Training'
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    server.sendmail(GMAIL_USER, EMAIL_RECIPIENT, msg.as_string())
    server.quit()


def send_sms(body):
    if not all([TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER, TWILIO_RECIPIENT]):
        print('[sendMessage] Twilio no configurado — revisar variables de entorno.')
        return

    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(body=body, from_=TWILIO_NUMBER, to=TWILIO_RECIPIENT)

