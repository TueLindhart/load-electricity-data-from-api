import os

from google.oauth2 import service_account
from googleapiclient.discovery import build


def authenticate():
    scopes = ["https://www.googleapis.com/auth/drive"]
    credentials = service_account.Credentials.from_service_account_file(
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS"), scopes=scopes
    )
    return credentials


def upload_file_to_drive(file_path: str):
    credentials = authenticate()
    service = build("drive", "v3", credentials=credentials)
    file_name = os.path.basename(file_path)
    metadata = {
        "name": file_name,
        "parents": [os.getenv("TARGET_FOLDER_ID")],
    }

    media_body = service.files().create(body=metadata, media_body=file_path, fields="id").execute()

    print(f'File ID: {media_body["id"]}')


if __name__ == "__main__":
    # Path to the file to upload
    file_path = "path/to/file"
    upload_file_to_drive(file_path=file_path)
