# ml_models/utils/helpers.py

import pandas as pd
import os

def load_raw_data(file_path):
    """Load raw data from a CSV file."""
    return pd.read_csv(file_path)

def save_processed_data(data, file_path):
    """Save processed data to a CSV file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    data.to_csv(file_path, index=False)
