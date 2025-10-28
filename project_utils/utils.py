## Purpose: Utility functions used by project scripts
## Date: 08/29/2025
## Author: Pat McCornack

import numpy as np
import pandas as pd


# Define function to get roi boundaries for specified sites
def get_bounds(ds, site, resolution='1_km'):
    ds = ds.isel(time=0)  # Only need space dimensions
    target_lat = site['lat']
    target_lon = site['lon']
    
    # Find the nearest lat/lon index
    lat_idx = np.abs(ds['lat'] - target_lat).argmin().item()
    lon_idx = np.abs(ds['lon'] - target_lon).argmin().item()

    # Extract the 3×3 neighboring grid cells
    if resolution == '1_km':
        lat_slice = slice(lat_idx - 1, lat_idx + 2)
        lon_slice = slice(lon_idx - 1, lon_idx + 2)
        subset = ds.isel(lat=lat_slice, lon=lon_slice)
    else:
        subset = ds.isel(lat=lat_idx, lon=lon_idx)

    lat_min, lat_max = subset['lat'].min(), subset['lat'].max()
    lon_min, lon_max = subset['lon'].min(), subset['lon'].max()

    # Make polygons encompass cells
    lat_spacing = np.abs(ds['lat'].diff(dim='lat')).mean().item()  # Degrees
    lon_spacing = np.abs(ds['lon'].diff(dim='lon')).mean().item()  # Degrees
    lat_min = lat_min - lat_spacing / 2
    lat_max = lat_max + lat_spacing / 2
    lon_min = lon_min - lon_spacing / 2
    lon_max = lon_max + lon_spacing / 2

    # Define polygon corners
    rect_corners = [
        (lon_min, lat_min),  # Bottom-left
        (lon_max, lat_min),  # Bottom-right
        (lon_max, lat_max),  # Top-right
        (lon_min, lat_max),  # Top-left
        (lon_min, lat_min)   # Closing the rectangle
    ]
    bounds_dict = {'site' : site['site'],
                    'lat_min' : [float(lat_min.values)],
                    'lat_max' : [float(lat_max.values)],
                    'lon_min' : [float(lon_min.values)],
                    'lon_max' : [float(lon_max.values)],
                    'bounds' : [rect_corners]}


    return pd.DataFrame(bounds_dict)

# Get dataframe of statistics
def get_freq(ds, var, roi_df):
    freq_df = pd.DataFrame()

    # Get overall frequencies
    ds_gp = ds.sum('time')
    total_count = ds.count('time')
    ds_gp = (ds_gp / total_count) * 100
    ds_gp = ds_gp.mean(dim=['lat', 'lon'])

    overall_dict = {
        'site' : 'overall',
        'goes_freq' : ds_gp['goes_binary'].values,
        'wrf_freq' : ds_gp[var].values,
        'match_freq' : ds_gp['match'].values
    }
    freq_df = pd.concat([freq_df, pd.DataFrame(overall_dict, index=[0])])

    # Get ROI frequencies
    for name in roi_df['site'].tolist():
        # Subset to specific region of interest
        site_coords = roi_df.loc[roi_df['site'] == name]
        roi_ds = ds.sel(lat=slice(site_coords['lat_min'].values[0], site_coords['lat_max'].values[0]), lon=slice(site_coords['lon_min'].values[0], site_coords['lon_max'].values[0]))
        
        # Getting % of matching observations, aggregated by year
        total_count = roi_ds.count('time')
        roi_ds = roi_ds.sum('time')
        roi_ds = (roi_ds / total_count) * 100

        # Average over the ROI
        roi_ds_mean = roi_ds.mean()

        # Create site dataframe
        data_dict = {'site' : name, 
                    'goes_freq' : roi_ds_mean['goes_binary'].values,
                    'wrf_freq' : roi_ds_mean[var].values,
                    'match_freq' : roi_ds_mean['match'].values}

        # Join together with all sites
        freq_df = pd.concat([freq_df, pd.DataFrame(data_dict, index=[0])])
    return freq_df

# Get ROI mean monthly frequencies
def get_monthly_freq(ds, roi_df):
    freq_df = pd.DataFrame()
    for name in roi_df['site'].tolist():
        # Subset to specific region of interest
        site_coords = roi_df.loc[roi_df['site'] == name]
        roi_ds = ds.sel(lat=slice(site_coords['lat_min'].values[0], site_coords['lat_max'].values[0]), lon=slice(site_coords['lon_min'].values[0], site_coords['lon_max'].values[0]))
        
        # Getting % of matching observations, aggregated by year
        months_ds = roi_ds.groupby('time.month').sum('time')
        months_count = roi_ds.groupby('time.month').count('time')
        months_ds = (months_ds / months_count) * 100
        months_ds

        for month in list(months_ds['month'].values):

            # Average over the ROI
            roi_ds_mean = months_ds.sel(month=month).mean()

            # Create site dataframe
            data_dict = {'site' : name,
                        'month' : month, 
                        'goes_freq' : roi_ds_mean['goes_binary'].values,
                        'cldfra_freq' : roi_ds_mean['cldfra_binary'].values,
                        'match_freq' : roi_ds_mean['match'].values}
            site_freq_df = pd.DataFrame(data_dict, index=[0])

            # Join together with all sites
            freq_df = pd.concat([freq_df, site_freq_df])

    return freq_df

# Get ROI mean frequencies by year
def get_yearly_freq(ds, roi_df):
    freq_df = pd.DataFrame()
    for name in roi_df['site'].tolist():
        # Subset to specific region of interest
        site_coords = roi_df.loc[roi_df['site'] == name]
        roi_ds = ds.sel(lat=slice(site_coords['lat_min'].values[0], site_coords['lat_max'].values[0]), lon=slice(site_coords['lon_min'].values[0], site_coords['lon_max'].values[0]))
        
        # Getting % of matching observations, aggregated by year
        years_ds = roi_ds.groupby('time.year').sum('time')
        years_count = roi_ds.groupby('time.year').count('time')
        years_ds = (years_ds / years_count) * 100
        years_ds

        for year in list(years_ds['year'].values):

            # Average over the ROI
            roi_ds_mean = years_ds.sel(year=year).mean()

            # Create site dataframe
            data_dict = {'site' : name,
                        'year' : year, 
                        'goes_freq' : roi_ds_mean['goes_binary'].values,
                        'cldfra_freq' : roi_ds_mean['cldfra_binary'].values,
                        'match_freq' : roi_ds_mean['match'].values}
            site_freq_df = pd.DataFrame(data_dict, index=[0])

            # Join together with all sites
            freq_df = pd.concat([freq_df, site_freq_df])
    return freq_df
