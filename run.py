from flask import ( Flask, render_template, request, redirect, url_for, flash )
from app.utilities.get_inventory import run_inventory_update
from app.utilities.inventory_upload import upload_inventory_files
from app.utilities.monitor_sftp import monitor_sftp_new_orders
from app.utilities.check_db_new_orderfiles import check_and_notify_files
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.config import ( init_app, db )
from app.models.contact import Contact
from app.models.notification import NotificationType
from app.models.contact_notification_type import contact_notification_types
from app.utilities.send_email import init_mail
from app.config import get_mail_settings

class Config:
    SCHEDULER_API_ENABLED = True
    JOBS = [
        {
            'id': 'scheduled_inventory_update',
            'func': 'app.utilities.get_inventory:run_inventory_update',
            'trigger': 'interval',
            'minutes': 2  # Execution interval
        },
        {
            'id': 'monitor_sftp_files',
            'func': 'app.utilities.monitor_sftp:monitor_sftp_new_orders',
            'trigger': 'interval',
            'minutes': 1  # Adjust the comment to match the interval
        },
        {
            'id': 'file_check_notify',
            'func': 'app.utilities.check_db_new_orderfiles:check_and_notify_files', 
            'trigger': 'interval',
            'minutes': 1
        }
    ]
    
#app = Flask(__name__)
app = Flask(__name__, template_folder='app/templates')

app.config.from_object(Config())  # Load scheduler config
init_app(app)
init_mail(app)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

@app.route('/update_inventory')
def update_inventory():
    # This function will be called when you access http://<host>:<port>/update_inventory
    run_inventory_update()
    return "Inventory update initiated!"

@app.route('/upload_inventory')
def upload_inventory():
    upload_inventory_files()
    return "Inventory files are being uploaded."

@app.route('/jobs')
def list_jobs():
    jobs = scheduler.get_jobs()
    return '\n'.join(str(job) for job in jobs)

@app.route('/neworders')
def check_orders():
    monitor_sftp_new_orders()
    return "Checking for new orders."

@app.route('/newfilesnotice')
def check_new_orderfiles():
    check_and_notify_files()
    return "checking for new files"

""" @app.route('/add_contact', methods=['GET', 'POST'])
def add_contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone')  # Optional

        new_contact = Contact(name=name, email=email, phone=phone)
        db.session.add(new_contact)
        db.session.commit()

        return redirect(url_for('add_contact'))
    return render_template('add_contact.html') """

@app.route('/add_contact', methods=['GET', 'POST'])
def add_contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone', None)  # Optional

        new_contact = Contact(name=name, email=email, phone=phone)
        db.session.add(new_contact)
        db.session.commit()
        return redirect(url_for('add_contact'))

    contacts = Contact.query.all()  # Retrieve all contacts
    return render_template('add_contact.html', contacts=contacts)

@app.route('/delete_contact/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    flash('Contact deleted successfully', 'success')
    return redirect(url_for('add_contact'))

@app.route('/notification_types', methods=['GET', 'POST'])
def notification_types():
    if request.method == 'POST':
        description = request.form['description']
        if description:
            notification_type = NotificationType(description=description)
            db.session.add(notification_type)
            db.session.commit()
            flash('Notification type added successfully!', 'success')
        return redirect(url_for('notification_types'))

    notification_types = NotificationType.query.all()
    return render_template('notification_types.html', notification_types=notification_types)

@app.route('/delete_notification_type/<int:type_id>', methods=['POST'])
def delete_notification_type(type_id):
    notification_type = NotificationType.query.get_or_404(type_id)
    db.session.delete(notification_type)
    db.session.commit()
    flash('Notification type deleted successfully', 'success')
    return redirect(url_for('notification_types'))

@app.route('/associate_notifications', methods=['GET', 'POST'])
def associate_notifications():
    if request.method == 'POST':
        contact_id = request.form.get('contact_id')
        selected_type_ids = request.form.getlist('notification_type_ids')  # This retrieves all selected notification type IDs as a list

        contact = Contact.query.get_or_404(contact_id)
        selected_types = [NotificationType.query.get(int(nt_id)) for nt_id in selected_type_ids]

        # Set to add and remove notification types efficiently
        current_types_set = set(contact.notification_types)
        selected_types_set = set(selected_types)

        # Add new notification types that are not already associated
        for notification_type in selected_types_set:
            if notification_type not in current_types_set:
                contact.notification_types.append(notification_type)

        # Remove unselected notification types that are currently associated
        for notification_type in list(current_types_set):
            if notification_type not in selected_types_set:
                contact.notification_types.remove(notification_type)

        db.session.commit()
        flash('Notification types updated for the contact.', 'success')
        return redirect(url_for('associate_notifications'))

    contacts = Contact.query.all()
    notification_types = NotificationType.query.all()
    return render_template('associate_notification.html', contacts=contacts, notification_types=notification_types)

@app.route('/delete_association/<int:contact_id>/<int:type_id>', methods=['GET'])
def delete_association(contact_id, type_id):
    contact = Contact.query.get_or_404(contact_id)
    notification_type = NotificationType.query.get_or_404(type_id)
    if notification_type in contact.notification_types:
        contact.notification_types.remove(notification_type)
        db.session.commit()
        flash('Notification type removed from contact.', 'success')
    else:
        flash('Notification type not found in contact.', 'error')
    return redirect(url_for('associate_notifications'))

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port='3000', debug=True)
    app.run(host='0.0.0.0')
