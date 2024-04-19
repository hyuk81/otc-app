import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import (EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, EMAIL_USE_TLS, EMAIL_FROM_ADDRESS, EMAIL_RECIPIENT)

def send_notification(subject, body):
    """Send an email notification."""
    message = MIMEMultipart()
    message['From'] = EMAIL_FROM_ADDRESS
    message['To'] = EMAIL_RECIPIENT
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        text = message.as_string()
        server.sendmail(EMAIL_FROM_ADDRESS, EMAIL_RECIPIENT, text)
        server.quit()
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")