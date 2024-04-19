import logging
from logging.handlers import RotatingFileHandler

def setup_global_logger():
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)

    fh = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    return logger
