import pandas as pd
import numpy as np
import os, os.path
import seaborn as sns
import tqdm
import matplotlib.pyplot as plt
import tqdm


def read_files_to_df_dict(data_path: str) -> dict[str, pd.DataFrame]:
    files = os.listdir(data_path)
    df_dict = {file: pd.read_csv(os.path.join(data_path, file)) for file in files}
    df_dict.pop("README.md")
    return df_dict


def concat_df_dict(df_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return pd.concat(df_dict.values(), ignore_index=True)
