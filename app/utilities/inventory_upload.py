import os
import shutil  # Import shutil for file moving operations
import paramiko
from app.config import (FILE_NEW_INVENTORY, FILE_UPLOADED_INVENTORY, SFTP_HOST, SFTP_PORT,
                        SFTP_USER, SFTP_PASSWORD, SFTP_FILE_INVENTORY)
import time

def upload_inventory_files():
    # Set up the connection to the SFTP server
    transport = paramiko.Transport((SFTP_HOST, int(SFTP_PORT)))
    transport.connect(username=SFTP_USER, password=SFTP_PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)

    try:
        # List all files in the local directory specified in FILE_NEW_INVENTORY
        files = os.listdir(FILE_NEW_INVENTORY)
        for file in files:
            local_path = os.path.join(FILE_NEW_INVENTORY, file)
            remote_path = os.path.join(SFTP_FILE_INVENTORY, file)
            
            # Upload each file
            sftp.put(local_path, remote_path)
            print(f"Successfully uploaded {file} to {remote_path}")
            
            # Assuming you want to wait after uploading each file before moving it
            time.sleep(10)  # Wait before moving the file

            # Move the file to the uploaded directory
            uploaded_path = os.path.join(FILE_UPLOADED_INVENTORY, file)
            shutil.move(local_path, uploaded_path)
            print(f"Moved {file} to {uploaded_path}")

    except Exception as e:
        print(f"Failed to upload files: {e}")
    finally:
        # Close the SFTP connection
        sftp.close()
        transport.close()

if __name__ == "__main__":
    upload_inventory_files()
