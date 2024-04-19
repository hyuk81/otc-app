from app.config import db
from app.models.contact_notification_type import contact_notification_types

class NotificationType(db.Model):
    __tablename__ = 'notification_types'

    type_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)

    # Relationship with contacts through association table
    contacts = db.relationship('Contact', secondary='contact_notification_types', back_populates='notification_types')
