from src.config.config import PATH
from src.model.model import train_model
from src.utils.sendMessage import *

if __name__ == '__main__':
    # subprocess.run(['tail', '-f', 'train_output.txt'])
    body = "Training has started"
    send_email(body)
    send_sms(body)
    try:
        train_model(PATH)
        body = "Training has ended"
        send_email(body)
        send_sms(body)
    except Exception as e:
        body = f"Training has ended by a error\n({e})"
        send_email(body)
        send_sms(body)
