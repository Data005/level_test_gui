import pandas as pd
import numpy as np
import statistics as sts
import os

def data_process(df):
    # Check if the file exists and handle FileNotFoundError
    file_path = 'data/main.csv'
    if not os.path.exists(file_path):
        main = pd.DataFrame()
        print(f"Warning: {file_path} not found. Starting with an empty DataFrame.")
    else:
        try:
            main = pd.read_csv(file_path)
        except pd.errors.EmptyDataError:
            main = pd.DataFrame()
            print(f"Warning: {file_path} is empty. Starting with an empty DataFrame.")
    
    column_list = df.columns
    trend_mean = []
    trend_std = []
    trend_cv_percent = []
    trend_range = []

    # Process data from row 6 onwards, excluding the last row
    df_mini = df.iloc[6:-1]
    
    for col in column_list:
        # Convert data to float, handling missing values gracefully
        data = pd.to_numeric(df_mini[col], errors='coerce').dropna()
        
        # Calculate statistics if data is not empty
        if not data.empty:
            mean_val = sts.mean(data)
            std_val = sts.stdev(data) if len(data) > 1 else 0  # std requires at least 2 data points
            
            # Handle division by zero if mean is zero
            cv_percent_val = (std_val / mean_val) * 100 if mean_val != 0 else np.nan
            range_val = max(data) - min(data) if len(data) > 1 else np.nan
        else:
            mean_val, std_val, cv_percent_val, range_val = np.nan, np.nan, np.nan, np.nan
        
        trend_mean.append(round(mean_val, 2))
        trend_std.append(round(std_val, 3))
        trend_cv_percent.append(round(cv_percent_val, 3))
        trend_range.append(round(range_val, 3))
    
    # Create a new DataFrame to hold the statistics
    stats_df = pd.DataFrame({
        'Mean': trend_mean,
        'StdDev': trend_std,
        'CV%': trend_cv_percent,
        'Range': trend_range
    }, index=column_list).transpose()
    
    # Insert the statistics DataFrame into the original DataFrame at index 5
    df = pd.concat([df.iloc[:5], stats_df, df.iloc[5:]]).reset_index(drop=True)
    
    # Align indices before concatenating along columns
    df.reset_index(drop=True, inplace=True)
    main.reset_index(drop=True, inplace=True)
    
    # Add the new df to the main df according to column names
    main = pd.concat([main, df], axis=1)
    
    return main
