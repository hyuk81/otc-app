from app.config import db
from app.models.notification import NotificationType

def create_notification_type(description):
    new_type = NotificationType(description=description)
    db.session.add(new_type)
    db.session.commit()
    return new_type

# Implement retrieve, update, delete similarly
