import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_email_reminder(email: str, message: str):
    msg = MIMEText(message)
    msg["Subject"] = "Password Recovery"
    msg["From"] = "ahuekweprinceugo@gmail.com"
    msg["To"] = email

    # Connect to the Gmail SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()  # Identify ourselves to the server
        server.starttls()  # Secure the connection
        server.ehlo()  # Re-identify as an encrypted connection
        # Login using the correct environment variable for the password
        server.login("ahuekweprinceugo@gmail.com", os.getenv("GMAIL_PASS"))
        # Send the email
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())
