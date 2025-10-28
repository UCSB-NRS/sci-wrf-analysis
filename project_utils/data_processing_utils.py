## PURPOSE: These functions are used to process the GOES and WRF CLDFRA
##          data into a single joined dataset.
## AUTHOR: Pat McCornack
## DATE: 08/31/2025

## TO DO: 
##        2. Write docstrings for each function. 

### calc_cldfra_threshold
###       1. Refactor to save out plots - was originally in a notebook
###       2. Adjust handling of ROI boundaries


# ENVIRONMENT ----------------------------
from pathlib import Path

import numpy as np
import pandas as pd

import xarray as xr
import geopandas as gpd

import matplotlib as plt
import seaborn as sns

from project_utils.utils import get_bounds
from project_utils.utils import get_freq

# FUNCTIONS -----------------------------------

def join_wrf_goes(wrf_fpath, goes_fpath, out_fpath, resolution='1_km'):
    print('Preprocessing...')

    # Open datasets
    cldfra_ds = xr.open_dataset(wrf_fpath)
    goes_da = xr.open_dataarray(goes_fpath)

    # Preprocess
    cldfra_ds = cldfra_ds.groupby('time').mean()  # Remove duplicates - these were extracted twice 
    goes_da['time'] = pd.to_datetime(goes_da['time'].values).ceil('30min')  # Format GOES timestamps
    
    ## Optionally resample WRF to 4km
    if resolution == '4_km':
        cldfra_ds = cldfra_ds.coarsen(lat=4, lon=4, boundary='trim').mean()
    else: 
        ## If 1km, Subset WRF to daylight hours 
        common_times = goes_da['time'].values[np.isin(goes_da['time'], cldfra_ds['time'])]  
        goes_da = goes_da.sel(time=common_times)
        cldfra_ds = cldfra_ds.sel(time=common_times)
    
        times = cldfra_ds['time'].to_dataframe().reset_index(drop=True)  # Check hours
        times = pd.to_datetime(times['time'])
        print('Common Hours:', times.dt.hour.unique())

    ## Get common lat/lon extent around SCI
    latmax, latmin = np.min([cldfra_ds['lat'].max(), goes_da['lat'].max()]), np.max([cldfra_ds['lat'].min(), goes_da['lat'].min()])
    lonmax, lonmin = np.min([cldfra_ds['lon'].max(), goes_da['lon'].max()]), np.max([cldfra_ds['lon'].min(), goes_da['lon'].min()])

    cldfra_ds = cldfra_ds.sel(lat=slice(latmin, latmax), lon=slice(lonmin, lonmax))
    goes_da = goes_da.sel(lat=slice(latmin, latmax), lon=slice(lonmin, lonmax))

    ## Reindex GOES to align with WRF
    goes_da = goes_da.reindex_like(cldfra_ds, method='nearest')

    ## Join all data
    print("Joining...")
    clc_ds = xr.Dataset({'cldfra' : cldfra_ds['cldfra'], 'goes' : goes_da})

    clc_ds.to_netcdf(out_fpath, format="NETCDF4", engine="h5netcdf")
    print('Joined data written to: ', out_fpath)

def get_roi_bounds(interim_clc_fpath, out_fpath):
    ## Purpose: Calculates boundaries of regions of interest (roi) using user-specified coordinates
    ##          as center of region. 
    
    print("Calculating ROI boundaries...")
    
    # Load in data
    clc_ds = xr.open_dataset(interim_clc_fpath)

    # Get regions of interest
    ## Define centers of regions of interest
    site_dict = {
        'site' : ['west-end', 'coche-point', 'inland', 'nw-ocean', 'se-ocean'],
        'lat' : [34.012499, 34.033456, 34.00346, 34.12030, 33.91093],
        'lon' : [-119.882897, -119.600946, -119.76288, -119.95199, -119.60004]
    }

    ## Get regions of interest using point coordinates as centers
    site_df = pd.DataFrame(site_dict)

    bounds_df = pd.DataFrame()
    for i, site in site_df.iterrows():
        print(i, site)
        bounds_df = pd.concat([bounds_df, get_bounds(clc_ds, site)])

    site_df = site_df.merge(bounds_df, on='site')
    
    print("ROI Boundaries written to:", out_fpath)
    site_df.to_csv(out_fpath)

def calc_cldfra_threshold(interim_clc_fpath, roi_bounds_fpath, out_fpath):
    print("Calculating CLDFRA threshold for cloud / no cloud...")
    
    # Load in data
    clc_ds = xr.open_dataset(interim_clc_fpath)
    site_df = pd.read_csv(roi_bounds_fpath)

    # Get frequencies for range of cloud fraction thresholds
    thresholds = np.arange(0, 1.05, 0.05)
    clc_ds['goes_binary'] = xr.where(clc_ds['goes'] > 8.5, 1, 0)

    freq_df = pd.DataFrame()
    for threshold in thresholds: 
        clc_ds['cldfra_binary'] = xr.where(clc_ds['cldfra'] > threshold, 1, 0)
        clc_ds['match'] = xr.where((clc_ds['goes_binary'] == clc_ds['cldfra_binary']), 1, 0)
        df = get_freq(clc_ds, 'cldfra_binary', site_df)
        df['threshold'] = threshold
        freq_df = pd.concat([freq_df, df])

    # CLDFRA Threshold vs. Match
    # Create a dictionary for alpha values
    alpha_map = {hue: 0.5 if hue != 'overall' else 1 for hue in freq_df['site'].unique()}

    # Plot Match Frequency vs. Cloud Frac
    fig, ax = plt.subplots(figsize=(15,6))
    for site, subset in freq_df.groupby('site'):
        sns.lineplot(data=subset, x='threshold', y='match_freq', label=site, alpha=alpha_map[site], ax=ax)
        ax.set(title='Match Frequency vs. Cloud Fraction Threshold',
        xlabel='Cloud Fraction Threshold',
        ylabel=f'Match Frequency (%)')
        ax.set_xticks(np.arange(0,1.05,0.1))
        plt.legend(loc='upper right', bbox_to_anchor=(1.225, 1))
        plt.show()

    # Calculate difference betwen GOES and WRF CLDFRA clc frequencies
    freq_df['diff'] = freq_df['goes_freq'] - freq_df['wrf_freq']


    # Plot threshold vs. differences
    unique_sites = freq_df['site'].unique()
    palette = dict(zip(unique_sites, sns.color_palette('Set1', len(unique_sites))))  # Define color map for sites

    fig, ax = plt.subplots(figsize=(15,8))
    sns.lineplot(data=freq_df,
            x='diff',
            y='threshold',
            hue='site',
            palette=palette,
            ax=ax)
    plt.axvline(0, color='black', linestyle='--', alpha=0.5)
    ax.set(title='Difference in GOES/WRF Frequencies vs. Cloud Fraction Threshold',
    xlabel='GOES/WRF Frequency Difference',
    ylabel='Cloud Fraction Threshold')
    ax.set_yticks(np.arange(0,1.05,0.1))
    plt.legend(loc='upper right', bbox_to_anchor=(1.225, 1))
    plt.show()

    # Calculate the cldfra threshold
    min_thresholds = []
    for site in freq_df['site'].unique():
        site_df = freq_df.loc[freq_df['site'] == site].reset_index()
        idx = (site_df['diff'].abs()).idxmin()
        min_thresholds.append(site_df.loc[idx, 'threshold'])

        cldfra_threshold = np.mean(min_thresholds)
        print(cldfra_threshold)
        
    # Write out cldfra threshold
    print("Saving out CLDFRA threshold...")
    with open(out_fpath, "w") as f:
        f.write("Cloud fraction threshold calculated by script:\n")
        f.write(str(cldfra_threshold))

def calc_binary_clc(interim_clc_fpath, cldfra_threshold_fpath, out_fpath, resolution='1_km'):
    # Converts the combined GOES/WRF CLC dataset into binary cloud/no cloud values.
    print("Calculating binary clc raster...")
    
    # Read data
    clc_ds = xr.open_dataset(interim_clc_fpath)

    # Read in cloud fraction threshold. This is calculated by another script.
    with open(cldfra_threshold_fpath, 'r') as f:
        lines = f.readlines()
        cldfra_threshold = float(lines[1].strip())
        
    # Calculate binary values 
    if resolution == '1_km':  # 4_km data is already binary
        clc_ds['goes_binary'] = xr.where(clc_ds['goes'] > 8.5, 1, 0)  # 8.5 per communication with Rachel Clemesha
    else:
        clc_ds = clc_ds.rename({'goes' : 'goes_binary'})
    clc_ds['cldfra_binary'] = xr.where(clc_ds['cldfra'] > cldfra_threshold, 1, 0)
    clc_ds['match'] = xr.where((clc_ds['goes_binary'] == clc_ds['cldfra_binary']), 1, 0)  # Checks whether GOES record matches WRF simulation
    # clc_ds = clc_ds.drop_vars(['cldfra', 'goes'], errors='ignore')

    # Save out binary dataset
    print("Saving binary CLC to: ", out_fpath)
    clc_ds.to_netcdf(out_fpath, format="NETCDF4", engine="h5netcdf")
    