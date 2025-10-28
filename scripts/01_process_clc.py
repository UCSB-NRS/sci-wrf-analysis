## PURPOSE: This script processes the GOES cloud albedo and WRF CLDFRA data into a single
##          joined netcdf dataset with binary cloud / no cloud values. Processes both
##          1km-resolution, daytime only data and 4km-resolution data. 

## AUTHOR: Pat McCornack
## DATE: 08/31/25

## NOTES: 
##        1. This script can be run piecewise or as a sequence. Each function saves out a 
##           dataset that is used in the next function. Skipping steps can save time if 
##           making small modifications - simply comment out that step. 
##         2. Some steps take a significant amount of time to run. 
##         3. !! Need to finish refactoring the threshold scripts.

# %% Set up Environment
# ENVIRONMENT ----------------------
import importlib
from pathlib import Path
import project_utils.data_processing_utils as dp
importlib.reload(dp)  # reload updated functions

# Define root directory
root_dir = Path().resolve().parent  # Assumes cwd is project root


# MAIN ----------------------------
# %% 1km resolution data   
print("1km Data")
## Define filepaths
wrf_fpath = root_dir / 'data' / '01_raw' / 'wrf-low-cldfra.nc'
goes_fpath = root_dir / 'data' / '01_raw' / 'goes-cldalbedo-1km' / 'cldalb-sci.nc'
interim_clc_fpath =  root_dir / 'data' / '02_interim' / 'goes-wrf-clc-interim.nc'
roi_bounds_fpath = root_dir / 'data' / '02_interim' / 'roi-boundaries.csv'
cldfra_threshold_fpath = root_dir / 'data' / '02_interim' / 'cldfra-threshold.txt'
processed_outfpath = root_dir / 'data' / '03_processed' / 'goes-wrf-clc-1km-binary.nc'

## Process 1km data  
#dp.join_wrf_goes(wrf_fpath, goes_fpath, interim_clc_fpath)
#p.get_roi_bounds(interim_clc_fpath, roi_bounds_fpath)
#dp.calc_cloudfra_threshold(interim_clc_fpath, roi_bounds_fpath)
dp.calc_binary_clc(interim_clc_fpath, cldfra_threshold_fpath, processed_outfpath)


# %% 4 km resolution data
print("4km data")

## Define filepaths
wrf_fpath = root_dir / 'data' / '01_raw' / 'wrf-low-cldfra.nc'
goes_fpath = root_dir / 'data' / '01_raw' / 'goes-4km' / 'sci-goes-4km.nc'
interim_clc_fpath =  root_dir / 'data' / '02_interim' / 'goes-wrf-clc-4km-interim.nc'
roi_bounds_fpath = root_dir / 'data' / '02_interim' / 'roi-boundaries-4km.csv'
cldfra_threshold_fpath = root_dir / 'data' / '02_interim' / 'cldfra-threshold-4km.txt'
processed_outfpath = root_dir / 'data' / '03_processed' / 'goes-wrf-clc-4km-binary.nc'

## Process 4km data
#dp.join_wrf_goes(wrf_fpath, goes_fpath, interim_clc_fpath, resolution='4_km')
#dp.get_roi_bounds(interim_clc_fpath, roi_bounds_fpath)   # !! SE Ocean currently broken
#dp.calc_cloudfra_threshold(interim_clc_fpath, roi_bounds_fpath, cldfra_threshold_fpath)
dp.calc_binary_clc(interim_clc_fpath, cldfra_threshold_fpath, processed_outfpath, 
                   resolution='4_km')


# %%