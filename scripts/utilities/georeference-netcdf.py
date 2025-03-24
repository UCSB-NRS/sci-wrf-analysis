# --------------------------------------------------------------------------------
# Author: Pat McCornack
# Date: 01/24/25
# Purpose: Writes CRS (WGS84) to unreferenced netCDF. Used to reference Clemesha's
#          Coastal Low Cloud dataset for plotting. 
#
# --------------------------------------------------------------------------------

import xarray as xr
import rioxarray as rio
import netCDF4

# Define input/output paths
data_dir = '/Users/patmccornack/Documents/ucsb_fog_project/_repositories/sci-wrf-analysis/data/geospatial/clemesha-lcl/DailyCLC_SeasonalCycleCLC_data/'
fname = 'SeasonalCycle_CLC_040723.nc'
fpath = data_dir + fname

outdir = '/Users/patmccornack/Documents/ucsb_fog_project/_repositories/sci-wrf-analysis/data/geospatial/clemesha-lcl/'
outfname = f'{fname.split('.')[0].replace('_','-')}-referenced.nc'

# Open dataset
ds = xr.open_dataset(fpath)

# Add missing attributes
ds["lat"].attrs = {"units": "degrees_north", "long_name": "latitude"}
ds["lon"].attrs = {"units": "degrees_east", "long_name": "longitude"}

# Add CRS
ds = ds.rio.write_crs('EPSG:4326')

# Save out
ds.to_netcdf(outdir + outfname)