import io
import os

import pandas as pd


def load_prior_metadata():
    if os.path.exists("data/meta_data/meta_data.csv"):
        return pd.read_csv("data/meta_data/meta_data.csv")
    else:
        return pd.DataFrame()


def check_new_tokens(
    prior_meta_data_df: pd.DataFrame,
    current_meta_data_df: pd.DataFrame,
):
    # Use sets to see if any new tokens
    if not prior_meta_data_df.empty:
        prior_ids = set(prior_meta_data_df["id"].tolist())
    else:
        prior_ids = set()

    current_ids = set(current_meta_data_df["id"].tolist())

    return list(current_ids - prior_ids)


def decode_data_text(data_text: str):
    return data_text.encode("latin1").decode("utf-8")


def map_text_to_df(data_text: str):
    decoded_data = decode_data_text(data_text=data_text)
    data_file_like = io.StringIO(decoded_data)
    return pd.read_csv(data_file_like, delimiter=";", encoding="utf-8")


def process_commaseparated_columns(col: pd.Series):
    return col.str.replace(",", ".").astype(float)
