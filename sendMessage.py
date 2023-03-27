import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

def send_email():
    to = "wgre2000@gmail.com"
    subject = "AI Training"
    body = "Training has ended"

    from_email = "ai@linux.my" # Reemplaza con tu dirección de correo electrónico
    password = "stihqedirmfdhvju" # Reemplaza con tu contraseña de Gmail

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
    print('SENT')
    server.quit()
