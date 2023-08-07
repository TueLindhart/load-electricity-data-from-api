import time
from datetime import datetime, timedelta

from google_drive_utils import load_google_forms_as_df, upload_file_to_drive
from load_from_api import load_data
from utils import check_new_tokens, load_prior_metadata

from electricity_api_loader.send_error_mail import send_email


def load_data_from_api_and_upload_to_drive(refresh_token: str, data_id: str):
    current_date = datetime.now()
    date_to = current_date
    date_from = date_to - timedelta(days=720)

    # Load data for the last 720 days over 2 iterations as maximum 720 days are allowed per request
    # Not adding files together to single file as it requires greater restructuring of code.
    for i in [0, 720]:
        date_to = date_to - timedelta(days=i)
        date_from = date_from - timedelta(days=i)
        result = load_data(refresh_token, data_id, date_from, date_to)

        if result["status"] == "success":
            file_paths = result["file_paths"]
            for file_path in file_paths:
                upload_file_to_drive(file_path=file_path)
        else:
            return {"status": "error"}

    return {"status": "success"}


def main():
    # Code here to check if there is any new tokens
    prior_metadata_df = load_prior_metadata()
    current_metadata_df = load_google_forms_as_df()

    # Code here to get new tokens
    new_token_ids = check_new_tokens(prior_meta_data_df=prior_metadata_df, current_meta_data_df=current_metadata_df)

    if not new_token_ids:
        return "No new tokens"

    # Properly better to properly rename columns than using indices
    refresh_tokens = current_metadata_df.loc[current_metadata_df["id"].isin(new_token_ids)].iloc[:, 3].tolist()
    refresh_tokens = current_metadata_df.set_index("id").loc[new_token_ids].iloc[:, 3].tolist()

    # Load data and collect any failed runs
    failed_runs = []
    for id_, refresh_token in zip(new_token_ids, refresh_tokens):
        # Load data
        result = load_data_from_api_and_upload_to_drive(refresh_token, data_id=id_)

        if result["status"] == "success":
            print(f"ID={id_} Successfully loaded data from API and uploaded to Google Drive")
            continue

        # Retry once again if it failed the first time
        # Sleep for 60 seconds to avoid 1 minute rescriction on data token calls
        time.sleep(60)
        result = load_data_from_api_and_upload_to_drive(refresh_token, data_id=id_)
        if result["status"] != "success":
            failed_runs.append(id_)

    # If any failed runs then send email alert
    if any(failed_runs):
        content = f"Following data ID's failed to collect data: {failed_runs}"
        send_email(content=content)


if __name__ == "__main__":
    main()
