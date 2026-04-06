import os

PATH = './chest_xray'
TRAINED_MODEL_PATH = './trained_model'

TWILIO_SID = os.environ.get('TWILIO_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER', '')
TWILIO_RECIPIENT = os.environ.get('TWILIO_RECIPIENT', '')

GMAIL_USER = os.environ.get('GMAIL_USER', '')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD', '')
EMAIL_RECIPIENT = os.environ.get('EMAIL_RECIPIENT', '')
