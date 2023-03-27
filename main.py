from config import PATH
from model import train_model
import subprocess
from sendMessage import send_email

if __name__ == '__main__':
    # subprocess.run(['tail', '-f', 'train_output.txt'])
    train_model(PATH)
    send_email()
