import io
import json
from datetime import datetime, timedelta
from typing import List, TypedDict

import pandas as pd

# import click
import requests

# Define the base URL for the API
BASE_URL = "https://api.eloverblik.dk/customerapi"

# Define the HEADERS for the requests
HEADERS = {"Content-Type": "application/json"}


class LoadDataResponse(TypedDict):
    status: str
    file_paths: List[str]
    access_token: str | None
    metering_point_ids: List[str]
    error: str


# Get a data access token
def get_data_access_token(refresh_token: str):
    HEADERS["Authorization"] = f"Bearer {refresh_token}"
    response = requests.get(f"{BASE_URL}/api/token", headers=HEADERS)
    if response.status_code == 200:
        return response.json()["result"]
    else:
        print(f"Error getting data access token with error code {response.status_code} and reason {response.reason}")
        return None


# Get a list of metering points
def get_metering_points(access_token: str):
    HEADERS["Authorization"] = f"Bearer {access_token}"
    response = requests.get(f"{BASE_URL}/api/meteringpoints/meteringpoints", headers=HEADERS)
    if response.status_code == 200:
        return response.json()["result"]
    else:
        print(f"Error getting metering points with error code {response.status_code} and reason {response.reason}")
        return None


def get_metering_points_master_and_charge_data(access_token: str, metering_point_ids: List[str]):
    HEADERS["Authorization"] = f"Bearer {access_token}"

    # Get metadata
    data = {"meteringPoints": {"meteringPoint": metering_point_ids}}
    response_master = requests.post(
        f"{BASE_URL}/api/meteringpoints/masterdata/export",
        headers=HEADERS,
        data=json.dumps(data),
    )
    if response_master.status_code == 200:
        csv_file = io.StringIO(response_master.text)
        df_master = pd.read_csv(csv_file, sep=";", encoding="utf-8")  # Kan ikke få encoding til at virke
    else:
        print(
            f"Error getting meta data with error code {response_master.status_code} and reason {response_master.reason}"
        )
        df_master = None

    # Get charges data from metering point
    response_charge = requests.post(
        f"{BASE_URL}/api/meteringpoints/charges/export",
        headers=HEADERS,
        data=json.dumps(data),
    )
    if response_charge.status_code == 200:
        csv_file = io.StringIO(response_charge.text)
        df_charge = pd.read_csv(csv_file, sep=";", encoding="utf-8")  # Kan ikke få encoding til at virke
    else:
        print(
            f"Error getting charge data with error code {response_charge.status_code} and reason {response_charge.reason}"
        )
        df_charge = None

    return df_master, df_charge


# Get meter data
def get_meter_data(
    access_token: str,
    metering_point_ids: List[str],
    date_from: str,
    date_to: str,
    aggregation: str,
):
    HEADERS["Authorization"] = f"Bearer {access_token}"
    data = {"meteringPoints": {"meteringPoint": metering_point_ids}}
    response = requests.post(
        # f"{BASE_URL}/api/meterdata/gettimeseries/{date_from}/{date_to}/{aggregation}",  # noqa: E501
        f"{BASE_URL}/api/meterdata/timeseries/export/{date_from}/{date_to}/{aggregation}",  # noqa: E501
        headers=HEADERS,
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
    data_id: str,
    refresh_token: str | None = None,
    access_token: str | None = None,
    metering_point_ids: List[str] = [],
    date_from: str | datetime | None = None,
    date_to: str | datetime | None = None,
    get_master_and_charge_data: bool = True,
):
    if refresh_token is None and access_token is None:
        raise ValueError("Both refresh_token and access_token can't be None")

    if date_to is None:
        date_to = datetime.now()

    if date_from is None:
        date_from = datetime.now() - timedelta(days=720)

    if isinstance(date_from, datetime):
        date_from = date_from.strftime("%Y-%m-%d")

    if isinstance(date_to, datetime):
        date_to = date_to.strftime("%Y-%m-%d")

    # Use the functions
    if access_token is None and refresh_token is not None:
        print("Getting access token...")
        access_token = get_data_access_token(refresh_token)

    if access_token is None:
        return LoadDataResponse(
            status="error",
            file_paths=[],
            error="Error getting access token",
            metering_point_ids=[],
            access_token=None,
        )

    if not metering_point_ids:
        print("Getting metering points...")
        metering_points = get_metering_points(access_token)
        if metering_points is None:
            return LoadDataResponse(
                status="error",
                file_paths=[],
                error="Error getting metering points",
                metering_point_ids=[],
                access_token=None,
            )
        metering_point_ids = [metering_point["meteringPointId"] for metering_point in metering_points]

    print("Getting meter data...")
    df_meter_data = get_meter_data(access_token, metering_point_ids, date_from, date_to, "Hour")
    if df_meter_data is None:
        return LoadDataResponse(
            status="error",
            file_paths=[],
            error="Error getting meter data",
            metering_point_ids=[],
            access_token=None,
        )

    # Add id
    df_meter_data["id"] = data_id

    file_paths = []
    for metering_point_id in metering_point_ids:
        df_metering_point_id: pd.DataFrame = df_meter_data.loc[
            df_meter_data["metering_point_id"] == int(metering_point_id)
        ]
        file_path = f"data/electricity_data/{metering_point_id}-{date_from}-{date_to}-ts.csv"
        df_metering_point_id.to_csv(file_path, index=False)
        file_paths.append(file_path)

        print(f"Saved electricity use data to {file_path}")

    # Save or append df_master to CSV
    if get_master_and_charge_data:
        print("Getting metering point master and charge data")
        df_master, df_charge = get_metering_points_master_and_charge_data(
            access_token=access_token,
            metering_point_ids=metering_point_ids,
        )

        if df_master is None or df_charge is None:
            return LoadDataResponse(
                status="error",
                file_paths=[],
                error="Error getting master or charge data",
                metering_point_ids=[],
                access_token=None,
            )

        for metering_point_id in metering_point_ids:
            # save master data for metering point id
            master_file_path = f"data/master_data/{metering_point_id}-master_data.csv"
            df_master_metering_point_id = df_master.loc[df_master.iloc[:, 0] == metering_point_id]
            df_master_metering_point_id.to_csv(master_file_path, index=False)
            file_paths.append(master_file_path)
            print(f"Saved master data for metering ID = {metering_point_id} to {master_file_path}")

            charge_file_path = f"data/charge_data/{metering_point_id}-charge_data.csv"
            df_charge_metering_point_id = df_charge.loc[df_charge.iloc[:, 0] == metering_point_id]
            df_charge_metering_point_id.to_csv(charge_file_path, index=False)
            file_paths.append(charge_file_path)
            print(f"Saved chage data for metering ID = {metering_point_id} to {charge_file_path}")

    return LoadDataResponse(
        status="success",
        file_paths=file_paths,
        error="No error",
        metering_point_ids=metering_point_ids,
        access_token=access_token,
    )
