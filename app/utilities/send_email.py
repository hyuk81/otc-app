# app/utilities/send_email.py
from flask_mail import Mail, Message
from app.config import get_mail_settings

mail = Mail()  # Initialize it without app here

def init_mail(app):
    # Load email settings from config and initialize Flask-Mail with app context
    app.config.update(get_mail_settings())  # Assuming get_mail_settings is imported from app.config
    mail.init_app(app)

def send_email(subject, recipients, body):
    assert isinstance(recipients, list), "Recipients should be a list"
    assert all(isinstance(recipient, str) for recipient in recipients), "Each recipient should be a string"

    msg = Message(subject, recipients=recipients, body=body)
    with mail.connect() as conn:
        conn.send(msg)