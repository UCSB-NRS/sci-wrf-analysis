#==================================================
# Author: Pat McCornack
# Date: 01-23-25
# 
# Purpose: Aggregate daily WRF outputs into single netcdf file.
#
#==================================================

import netCDF4
import numpy 
import xarray
import dask
from pathlib import Path

# Specify filepaths
type = 'wrf-vertical-profile'  # 'wrf-vertical-profile' / wrf-surface
out_fname = 'wrfout-2008-08-vertprofile.nc'

root_dir = Path().resolve().parents[1]
data_dir = root_dir / 'data' / 'geospatial' / type /'daily-netcdfs'
in_fpath  = str(data_dir / '*')
print(in_fpath)

out_fpath = str(data_dir.parent / out_fname)

# Aggregate files
ds = xarray.open_mfdataset(in_fpath, combine='nested', concat_dim='Time')
ds.to_netcdf(out_fpath)
print("Wrote: ", out_fpath)