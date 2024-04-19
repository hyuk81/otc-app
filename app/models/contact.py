from app.config import db  # Make sure this import points to where your db instance is initialized.
from app.models.notification import NotificationType
from app.models.contact_notification_type import contact_notification_types

class Contact(db.Model):
    __tablename__ = 'contacts'

    contact_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Contact {self.name}>'

    # Relationship with notification_types through the association table
    notification_types = db.relationship('NotificationType', secondary=contact_notification_types, back_populates='contacts')