import pandas as pd
import numpy as np

def remove_outliers_z(df) -> pd.DataFrame:
    flat_values = df.values.flatten()
    # Calculate the overall mean and standard deviation
    mean = np.mean(flat_values)
    std_dev = np.std(flat_values)
    # Calculate Z-scores for all values in the DataFrame
    z_scores = (df - mean) / std_dev
    # Set a threshold for Z-scores (e.g., 3)
    threshold = 3
    # Create a mask for values within the threshold
    mask = np.abs(z_scores) < threshold
    # Apply the mask to keep only values within the threshold
    df_no_outliers = df[mask]
    return df_no_outliers

def remove_outliers_corner(df) -> pd.DataFrame:
    df.iloc[42,0] = 0
    df.iloc[43,0] = 0
    df.iloc[43,1] = 0
    df.iloc[43,2] = 0
    df.iloc[44,0] = 0
    df.iloc[44,1] = 0
    df.iloc[44,2] = 0
    df.iloc[45,0] = 0
    df.iloc[45,1] = 0
    df.iloc[45,2] = 0
    df.iloc[45,3] = 0
    return df