import paramiko
import os
import logging
import mysql.connector
from app.config import (SFTP_HOST, SFTP_PORT, SFTP_USER, SFTP_PASSWORD, SFTP_FILE_NEWORDERS, FILE_NEW_ORDER_DOWNLOAD, DB_HOST, DB_HOSTPORT, DB_USER, DB_PASS, DATABASE)

# Configure logging
logging.basicConfig(
    filename='sftp_monitor.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def download_new_files(sftp, sftp_directory, file_names, local_directory):
    for file_name in file_names:
        local_path = os.path.join(local_directory, file_name)
        remote_path = os.path.join(sftp_directory, file_name)
        try:
            sftp.get(remote_path, local_path)
            logging.info(f"Downloaded {file_name} to {local_path}")
            record_file_download(file_name)  # Record in the database
        except Exception as e:
            logging.error(f"Failed to download {file_name}: {str(e)}")

def record_file_download(file_name):
    conn = None
    try:
        conn = mysql.connector.connect(host=DB_HOST, port=DB_HOSTPORT, database=DATABASE, user=DB_USER, password=DB_PASS)
        conn.autocommit = False  # Ensure transactions are managed manually
        cur = conn.cursor()
        # Insert or update the record in the database
        cur.execute("""
            INSERT INTO files (filename, processed, notified)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
            processed = VALUES(processed), notified = VALUES(notified)
        """, (file_name, False, False))
        conn.commit()
        cur.close()
    except Exception as e:
        logging.error(f"Failed to record or update {file_name} in the database: {str(e)}")
        if conn:
            conn.rollback()  # Rollback in case of an error
    finally:
        if conn:
            conn.close()

def monitor_sftp_new_orders():
    transport = paramiko.Transport((SFTP_HOST, int(SFTP_PORT)))
    try:
        transport.connect(username=SFTP_USER, password=SFTP_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            # Fetch currently tracked files from the database
            current_files_in_db = fetch_current_files_in_db()
            current_files = set(sftp.listdir(SFTP_FILE_NEWORDERS))
            new_files = current_files - current_files_in_db
            if new_files:
                logging.info("New files detected: " + ', '.join(new_files))
                download_new_files(sftp, SFTP_FILE_NEWORDERS, new_files, FILE_NEW_ORDER_DOWNLOAD)
        except Exception as e:
            logging.error("Failed to monitor directory: " + str(e))
        finally:
            sftp.close()
    except Exception as e:
        logging.error("Failed to connect to SFTP: " + str(e))
    finally:
        transport.close()

def fetch_current_files_in_db():
    """Fetch the list of files currently known in the database."""
    conn = mysql.connector.connect(host=DB_HOST, port=DB_HOSTPORT, database=DATABASE, user=DB_USER, password=DB_PASS)
    files = set()
    try:
        cur = conn.cursor()
        cur.execute("SELECT filename FROM files")
        for (filename,) in cur:
            files.add(filename)
        cur.close()
    finally:
        conn.close()
    return files

if __name__ == '__main__':
    monitor_sftp_new_orders()
