import pandas as pd


def load_prior_metadata():
    return pd.read_csv("data/meta_data/meta_data.csv")


def check_new_tokens(
    prior_meta_data_df: pd.DataFrame,
    current_meta_data_df: pd.DataFrame,
):
    # Use sets to see if any new tokens
    prior_ids = set(prior_meta_data_df["id"].tolist())
    current_ids = set(current_meta_data_df["id"].tolist())

    return list(current_ids - prior_ids)
