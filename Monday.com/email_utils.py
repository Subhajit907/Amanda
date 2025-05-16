import smtplib
from email.message import EmailMessage
from config import ALERT_EMAIL

def send_alert(subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = ALERT_EMAIL
    msg["To"] = ALERT_EMAIL
    msg.set_content(body)
    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login(ALERT_EMAIL, "your_password")
        server.send_message(msg)
