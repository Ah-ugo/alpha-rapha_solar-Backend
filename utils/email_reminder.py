import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_email_reminder(email: str, message: str, subject: str):
    msg = MIMEText(message)
    msg["Subject"] = subject if subject else "Password Recovery"
    msg["From"] = "ahuekweprinceugo@gmail.com"
    msg["To"] = email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("ahuekweprinceugo@gmail.com", os.getenv("GMAIL_PASS"))
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())
