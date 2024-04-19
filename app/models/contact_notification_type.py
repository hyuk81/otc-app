from app.config import db

# Define the association table for many-to-many relationship between Contact and NotificationType
contact_notification_types = db.Table('contact_notification_types',
    db.Column('contact_id', db.Integer, db.ForeignKey('contacts.contact_id'), primary_key=True),
    db.Column('type_id', db.Integer, db.ForeignKey('notification_types.type_id'), primary_key=True)
)
