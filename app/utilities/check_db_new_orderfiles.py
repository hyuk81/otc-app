# app/utilities/check_db_new_orderfiles.py
from app.config import db
from app.models.file import File
from app.models.contact import Contact
from app.models.notification import NotificationType
from app.utilities.send_email import send_email

def check_and_notify_files():
    files_to_notify = File.query.filter_by(notified=False).all()
    if not files_to_notify:
        return  # No files to process

    # Get contacts who need to be notified for 'new order'
    contacts = Contact.query.join(Contact.notification_types).filter(NotificationType.type_id == 1).all()
    recipients = [contact.email for contact in contacts]

    # Email body preparation
    body = f"New files need your attention: {', '.join([file.filename for file in files_to_notify])}"
    
    # Send email
    send_email("Notification for New Files", recipients, body)

    # Mark files as notified
    for file in files_to_notify:
        file.notified = True
    db.session.commit()
