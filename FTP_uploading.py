import ftplib
import os
from dotenv import load_dotenv

def run():
    # Load environment variables from .env
    load_dotenv()

    # Get FTP credentials from environment variables
    ftp_host = os.getenv("FTP_HOST")
    ftp_user = os.getenv("FTP_USER")
    ftp_password = os.getenv("FTP_PASSWORD")

    def upload_file_to_ftp(local_file, ftp_host, ftp_user, ftp_password, remote_file_path):
        try:
            # Connect to FTP server
            ftp = ftplib.FTP(ftp_host)
            ftp.login(ftp_user, ftp_password)

            # Change directory (if needed)
            ftp.cwd('/public_html/')

            # Open the local file
            if os.path.exists(local_file):
                print(f"File {local_file} exists and is ready for upload.")
            else:
                print(f"File {local_file} does not exist.")
                return

            with open(local_file, 'rb') as file:
                # Upload the file
                ftp.storbinary(f'STOR {os.path.basename(remote_file_path)}', file)

            print(f"Successfully uploaded {local_file} to {ftp_host}/{remote_file_path}")
        
        except ftplib.all_errors as e:
            print(f"FTP error: {e}")
            print(f"Failed to upload {local_file} to {ftp_host}/{remote_file_path}")
        
        finally:
            # Close FTP connection
            ftp.quit()

    # Local file to upload
    local_json_file = "godkjente_plantevernmidler_data.json"

    # Remote file path on the FTP server
    remote_file_path = "/public_html/godkjente_plantevernmidler_data.json"

    # Upload file
    upload_file_to_ftp(local_json_file, ftp_host, ftp_user, ftp_password, remote_file_path)
    
if __name__ == "__main__":
    run()