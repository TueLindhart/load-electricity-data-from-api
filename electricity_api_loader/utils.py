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
