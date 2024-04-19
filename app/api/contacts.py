from flask import request, jsonify
from app.models.contact import Contact
from app.services import contact_service

@app.route('/contacts', methods=['POST'])
def create_contact():
    data = request.json
    contact = contact_service.create_contact(data['name'], data['email'], data.get('phone'))
    return jsonify(contact), 201

@app.route('/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    contact = contact_service.get_contact(contact_id)
    return jsonify(contact), 200

# Implement other routes similarly
