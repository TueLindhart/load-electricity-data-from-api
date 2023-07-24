import time
from datetime import datetime, timedelta

from load_from_api import load_data
from upload_to_drive import upload_file_to_drive


def load_data_from_api_and_upload_to_drive(refresh_token: str):
    current_date = datetime.now()
    date_to = current_date
    date_from = date_to - timedelta(days=720)

    # Load data for the last 720 days over 2 iterations as maximum 720 days are allowed per request
    for i in [0, 720]:
        date_to = date_to - timedelta(days=i)
        date_from = date_from - timedelta(days=i)
        result = load_data(refresh_token, date_from, date_to)

        if result["status"] == "success":
            upload_file_to_drive(file_path=result["file_path"])
        else:
            return {"status": "error"}

    return {"status": "success"}


def main():
    # Code here to check if there is any new tokens

    # Code here to get new tokens

    # Temporarily load refresh_token from refresh_token.txt to test the code
    with open("refresh_token.txt", "r") as f:
        refresh_token = f.read()
    refresh_tokens = [refresh_token]

    for refresh_token in refresh_tokens:
        result = load_data_from_api_and_upload_to_drive(refresh_token)

        if result["status"] == "success":
            print("Successfully loaded data from API and uploaded to Google Drive")
        else:
            # Retry once again if it failed the first time
            # Sleep for 60 seconds to avoid 1 minute rescriction on data token calls
            time.sleep(secs=60)
            result = load_data_from_api_and_upload_to_drive(refresh_token)


if __name__ == "__main__":
    main()
