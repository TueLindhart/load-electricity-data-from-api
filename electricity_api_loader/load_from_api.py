import io
import json
from datetime import datetime, timedelta
from typing import List

import pandas as pd

# import click
import requests

# Define the base URL for the API
base_url = "https://api.eloverblik.dk/customerapi"

# Define the headers for the requests
headers = {"Content-Type": "application/json"}


# Get a data access token
def get_data_access_token(refresh_token: str):
    headers["Authorization"] = f"Bearer {refresh_token}"
    response = requests.get(f"{base_url}/api/token", headers=headers)
    if response.status_code == 200:
        return response.json()["result"]
    else:
        print(f"Error getting data access token with error code {response.status_code} and reason {response.reason}")
        return None


# Get a list of metering points
def get_metering_points(access_token: str):
    headers["Authorization"] = f"Bearer {access_token}"
    response = requests.get(f"{base_url}/api/meteringpoints/meteringpoints", headers=headers)
    if response.status_code == 200:
        return response.json()["result"]
    else:
        print(f"Error getting metering points with error code {response.status_code} and reason {response.reason}")
        return None


# Get meter data
def get_meter_data(
    access_token: str,
    metering_point_ids: List[str],
    date_from: str,
    date_to: str,
    aggregation: str,
):
    headers["Authorization"] = f"Bearer {access_token}"
    data = {"meteringPoints": {"meteringPoint": metering_point_ids}}
    response = requests.post(
        # f"{base_url}/api/meterdata/gettimeseries/{date_from}/{date_to}/{aggregation}",  # noqa: E501
        f"{base_url}/api/meterdata/timeseries/export/{date_from}/{date_to}/{aggregation}",  # noqa: E501
        headers=headers,
        data=json.dumps(data),
    )

    if response.status_code == 200:
        csv_file = io.StringIO(response.text)
        df = pd.read_csv(csv_file, sep=";", encoding="utf-8")  # Kan ikke få encoding til at virke
        df.columns = ["metering_point_id", "from_date", "to_date", "consumption", "unit", "quality", "type"]
        return df
    else:
        print(f"Error getting meter data with error code {response.status_code} and reason {response.reason}")
        return None


def load_data(
    refresh_token: str,
    data_id: str,
    date_from: str | datetime | None = None,
    date_to: str | datetime | None = None,
):
    if date_to is None:
        date_to = datetime.now()

    if date_from is None:
        date_from = datetime.now() - timedelta(days=720)

    if isinstance(date_from, datetime):
        date_from = date_from.strftime("%Y-%m-%d")

    if isinstance(date_to, datetime):
        date_to = date_to.strftime("%Y-%m-%d")

    # Use the functions
    print("Getting access token...")
    access_token = get_data_access_token(refresh_token)
    if access_token is None:
        return {"status": "error", "file_path": None, "error": "Error getting access token"}

    print("Getting metering points...")
    metering_points = get_metering_points(access_token)
    if metering_points is None:
        return {"status": "error", "file_path": None, "error": "Error getting metering points"}

    print("Getting meter data...")
    metering_point_ids = [metering_point["meteringPointId"] for metering_point in metering_points]
    df_meter_data = get_meter_data(access_token, metering_point_ids, date_from, date_to, "Hour")
    if df_meter_data is None:
        return {"status": "error", "file_path": None, "error": "Error getting meter data"}

    # Add id
    df_meter_data["id"] = data_id

    file_paths = []
    for metering_point_id in metering_point_ids:
        df_metering_point_id: pd.DataFrame = df_meter_data.loc[
            df_meter_data["metering_point_id"] == int(metering_point_id)
        ]
        file_path = f"data/{date_from}-{date_to}-{metering_point_id}.csv"
        df_metering_point_id.to_csv(file_path, index=False)
        file_paths.append(file_path)

        print(f"Saved data to {file_path}")

    return {"status": "success", "file_paths": file_paths}


if __name__ == "__main__":
    with open("refresh_token.txt", "r") as f:
        refresh_token = f.read()
    load_data(
        refresh_token=refresh_token,
        data_id=refresh_token[-10:],
        date_from="2023-07-23",
        date_to="2023-07-24",
    )
