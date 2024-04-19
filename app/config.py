import configparser
config = configparser.ConfigParser()
config.read('instance/config.ini')
import logging
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler

# Initialize SQLAlchemy
db = SQLAlchemy()

# Database Configuration
DB_HOST = config.get('database', 'db_host')
DB_HOSTPORT = config.get('database', 'db_hostport')
DB_USER = config.get('database', 'db_user')
DB_PASS = config.get('database', 'db_pass')
DATABASE = config.get('database', 'database')

def init_app(app):
    """Initialize the Flask application with configurations and database."""
    
    # Database configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_HOSTPORT}/{DATABASE}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Load the SECRET_KEY
    app.config['SECRET_KEY'] = config.get('security', 'SECRET_KEY')

    # Initialize db with app
    db.init_app(app)

    # Logger setup
    setup_global_logger()

def setup_global_logger():
    """Setup a global logger for the entire application."""
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)  # Or DEBUG, ERROR, WARNING, etc.

    # Create file handler which logs even debug messages
    fh = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5)
    fh.setLevel(logging.INFO)  # Or any other level

    # Create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


# Set up a dictionary to store configuration that Flask-Mail can use
def get_mail_settings():
    return {
        "MAIL_SERVER": config.get('email', 'email_host'),
        "MAIL_PORT": int(config.get('email', 'email_port')),
        "MAIL_USERNAME": config.get('email', 'email_user'),
        "MAIL_PASSWORD": config.get('email', 'email_pass'),
        "MAIL_USE_TLS": config.getboolean('email', 'email_use_tls'),
        "MAIL_DEFAULT_SENDER": config.get('email', 'email_from_address')
    }

# Email Configuration
EMAIL_HOST = config.get('email', 'email_host')
EMAIL_PORT = config.get('email', 'email_port')
EMAIL_USER = config.get('email', 'email_user')
EMAIL_PASS = config.get('email', 'email_pass')
EMAIL_USE_TLS = config.getboolean('email', 'email_use_tls')
EMAIL_FROM_ADDRESS = config.get('email', 'email_from_address')
EMAIL_RECIPIENT = config.get('email', 'email_recipient')

# SFTP Configuration
SFTP_HOST = config.get('sftp', 'sftp_host')
SFTP_PORT = config.get('sftp', 'sftp_port')
SFTP_USER = config.get('sftp', 'sftp_user')
SFTP_PASSWORD = config.get('sftp', 'sftp_password')

# SFTP File Location Configuration
SFTP_FILE_NEWORDERS = config.get('SFTP File Locations', 'file_neworders')
SFTP_FILE_INVENTORY = config.get('SFTP File Locations', 'file_inventory')
SFTP_FILE_ORDERCONFIRMS = config.get('SFTP File Locations', 'file_orderconfirms')

#API endpoints and keys
API_ACCOUNT_ID = config.get('api', 'account_id')
API_APPLICATION_KEY = config.get('api', 'application_key')
PRODUCT_INFO_ENDPOINT = config.get('api', 'product_info_endpoint')
PRODUCT_AVAILABILITY_ENDPOINT = config.get('api', 'product_availability_endpoint')

# File Location Configuration
FILE_NEW_INVENTORY = config.get('File Locations', 'file_new_inventory')
FILE_UPLOADED_INVENTORY = config.get('File Locations', 'file_uploaded_inventory')
PRODUCTS_JSON_FILE = config.get('File Locations', 'products_json')
FILE_NEW_ORDER_DOWNLOAD = config.get('File Locations', 'file_new_order_download')