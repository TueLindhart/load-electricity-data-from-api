import io
import os

import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build


def authenticate():
    scopes = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    ]
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


def load_google_forms_as_df():
    credentials = authenticate()
    service = build("drive", "v3", credentials=credentials)

    request = service.files().export_media(fileId=os.getenv("SHEET_ID"), mimeType="text/csv")
    response = request.execute()

    # Load google forms sheet as dataframe
    df = pd.read_csv(io.StringIO(response.decode("utf-8")))

    # Create unique ID using last 10 indices in token
    # Using this ID to map loaded data to metadata
    df["id"] = df.iloc[:, 3].apply(lambda x: x[-10:]).astype(str)

    return df


if __name__ == "__main__":
    # Path to the file to upload
    # upload_file_to_drive(file_path=file_path)
    df = load_google_forms_as_df()
    print(df)
