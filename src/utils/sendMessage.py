from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from config import TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER


def send_email(body):
    to = "wgre2000@gmail.com"
    subject = "AI Training"

    from_email = "ai@linux.my"
    password = "stihqedirmfdhvju"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("wgre2000@gmail.com", password)
    text = msg.as_string()
    server.sendmail(from_email, to, text)
    # print('SENT')
    server.quit()


def send_sms(body):
    # Create Twilio client
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    # Send SMS
    message = client.messages.create(body=body, from_=TWILIO_NUMBER, to='+595993381844')

    # Print sent message SID
    # print(message.sid)

