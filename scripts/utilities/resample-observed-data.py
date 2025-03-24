# ---------------------------------------------
# Author: Pat McCornack
# Date: 01/31/25
# Purpose: Resamples the quarter-hourly data to coarser resolutions (e.g. hourly, monthly).
#
# ---------------------------------------------


import pandas as pd
from pathlib import Path

root_dir = Path().resolve().parents[1]
data_dir = root_dir / 'data' / 'observational' / 'clean-datasets'
df_fnames = ['sci-sauc-clean-2003-2008.csv', 'sci-upem-clean-2005-2010.csv']

out_dir = root_dir / 'data' / 'observational' / 'aggregated-datasets'
out_fname = ['sauc-hourly.csv', 'upem-hourly.csv']

for i in range(len(df_fnames)):
    df = pd.read_csv(data_dir / df_fnames[i], index_col='time (PST)')
    df = df.drop(df.columns[0], axis=1)
    df.index = pd.to_datetime(df.index)


    df_avg_cols = df[['air temperature (C)', 'relative humidity (%)', 'wind speed (m/s)', 'wind gust (m/s)', 'wind direction (deg)']].resample('h').mean()
    df_sum_cols = df[['fog', 'fog tips', 'rain (mm)']].resample('h').sum()
    df_hourly = pd.concat([df_sum_cols, df_avg_cols], axis=1)

    df_hourly.to_csv(out_dir / out_fname[i])
    print("------------------------------------")
    print("Saved to: ", out_dir / out_fname[i])
    print("------------------------------------")
