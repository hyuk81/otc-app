from app.config import db
from app.models.contact import Contact

def create_contact(name, email, phone=None):
    new_contact = Contact(name=name, email=email, phone=phone)
    db.session.add(new_contact)
    db.session.commit()
    return new_contact

def get_contact(contact_id):
    return Contact.query.get(contact_id)

# Implement update and delete similarly
