import pandas as pd
import statistics as sts

def data_process(df):
    try:
        # Load the main DataFrame; if not present, create a new one
        main = pd.read_csv('data\main.csv')
    except FileNotFoundError:
        main = pd.DataFrame()

    column_list = df.columns
    trend_mean = []
    trend_std = []
    trend_cv_percent = []
    trend_range = []

    # Process data from row 6 onwards, excluding the last row
    df_mini = df[6:-1]
    
    for col in column_list:
        data = df_mini[col].astype(float).tolist()
        mean_val = sts.mean(data)
        std_val = sts.stdev(data)
        cv_percent_val = (std_val / mean_val) * 100
        range_val = int(max(data) - min(data))
        
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
    
    
    # Add the new df to the main df according to column names
    main = pd.concat([main, df], axis=1)
    return main
