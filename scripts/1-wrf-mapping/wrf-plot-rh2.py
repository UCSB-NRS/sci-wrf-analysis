#=======================================================================
#
#  plot_wrf_rh2_sb.py
#
#  Plot 2-m relative humidity from WRF forecast (Santa Barbara domain).
#
#=======================================================================


import wrf
import matplotlib
import numpy as np
import xarray as xr
import pandas as pd
import netCDF4 as nc
import cartopy.crs as crs
import matplotlib.pyplot as plt
import matplotlib.image as image
import matplotlib.colors as colors
from metpy.plots import USCOUNTIES
from cartopy.feature import NaturalEarthFeature
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.crs as ccrs
from wrf import (to_np, getvar, smooth2d, get_cartopy, cartopy_xlim, cartopy_ylim, latlon_coords)
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import rcParams
from pathlib import Path
rcParams['font.family']     = 'sans-serif'
rcParams['font.sans-serif'] = 'Helvetica'
plt.rcParams.update({'figure.autolayout': True})

#-- Define filepaths
root_dir = Path().resolve().parents[1]
data_dir = root_dir / 'data' / 'geospatial'
fname = 'wrf-vertical-profile/' + 'wrfout-2008-08-vertprofile.nc'
fpath = str(data_dir / fname)

out_dir = root_dir / 'outputs' / 'spatial-analysis-figs' / 'wrf-rh2-sci'

print('----------------------------')
print("Root Directory: ", root_dir)
print("Data Directory: ", data_dir)
print("Out Directory: ", out_dir)
print('----------------------------')

# Define plot boundaries
# Santa Cruz Island:    
lonmin = -119.5049
lonmax = -119.9401
latmin = 33.9487
latmax = 34.1

# Define station locations
sauclat = 34.001033
sauclon = -119.817817

upemlat = 34.012531
upemlon = -119.801828


#-- Get the data.
ncfile     =  nc.Dataset(fpath)
ntimes      =  ncfile.variables['Times'][:].shape[0]


for k in range(ntimes):

  
  u10         =  2.23694 * getvar(ncfile, "U10", timeidx=k)  #-- m/s to mph,
  v10         =  2.23694 * getvar(ncfile, "V10", timeidx=k)  #-- m/s to mph.
  hgt         =  getvar(ncfile, "HGT")
  t           =  getvar(ncfile, "Times", timeidx=k)
  var         =  getvar(ncfile, "rh2",   timeidx=k)
  var         =  smooth2d(var, 3, cenweight=4)
  lats, lons  =  latlon_coords(var)
  cart_proj   =  get_cartopy(var)


  #-- Get time stamp in local time.
  t           =  getvar(ncfile, "Times", timeidx=k)
  s           =  pd.Series(data=t.values)
  df          =  pd.DataFrame(index=s)
  df.index    =  df.index.tz_localize('UTC')
  df.index    =  df.index.tz_convert(tz='US/Pacific')
  timestamp   =  ''.join( [ str( df.index.day.values[0] ).zfill(2),   '-',
                          str( df.index.month.values[0] ).zfill(2), '-',
                          str( df.index.year.values[0] ),           ' ',
                          str( df.index.hour.values[0] ).zfill(2),  ':',
                          str( df.index.minute.values[0] ).zfill(2) ] )


  #-- Create a figure
  fig     =  plt.figure(figsize=(15,9))
  ax      =  plt.axes(projection=cart_proj)
  ax.add_feature(USCOUNTIES.with_scale('5m'), edgecolor='Black', linewidths=0.8)

  ax.set_extent([lonmin,lonmax,latmin,latmax], crs=crs.PlateCarree())


  # Station points
  ax.scatter([sauclon, upemlon], [sauclat, upemlat], color='red', zorder=5, s=40, label='Stations', transform=ccrs.Geodetic())
  

  #-- Set contour levels and colorbar ticks.
  levels  =  np.arange(0,100+5,5)
  ticks   =  np.arange(0,100+10,10) 


  #-- Truncate colormap.
  cmap    =  plt.cm.BrBG
  n       =  64
  minval  =  0.10
  maxval  =  0.90  
  cmap    =  colors.LinearSegmentedColormap.from_list('trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval), cmap(np.linspace(minval, maxval, n)))


  #-- Plot 2-m relative humidity.
  CF  =  plt.contourf(to_np(lons), to_np(lats), to_np(var), levels=levels, extend='neither', transform=crs.PlateCarree(), cmap=cmap)


  #-- Plot terrain height.
  hgt        =  smooth2d(hgt, 3, cenweight=4)
  levels_hgt =  np.arange(200,740,50)
  CL         =  plt.contour(to_np(lons), to_np(lats), to_np(hgt), levels=levels_hgt, colors='Black', linewidths=0.5, transform=crs.PlateCarree())
  ax.clabel(CL, CL.levels, inline=False, fontsize=6)

   
  #-- Plot 10-m winds.
  skip  =  2
  QV    =  plt.quiver(to_np(lons[::skip,::skip]), to_np(lats[::skip,::skip]), to_np(u10[::skip, ::skip]), to_np(v10[::skip, ::skip]), scale=500, width=0.002, transform=crs.PlateCarree())
  QK    =  ax.quiverkey(QV,                             #-- Incoming quiver handle.
                        X              =  0.065,        #-- Determine the location of label, all limited to [0,1].
                        Y              =  0.280,        #-- Determine the location of label, all limited to [0,1].
                        coordinates    =  'figure',
                        U              =  25,           #-- Reference arrow length means the wind speed is U mph.
                        angle          =  0,            #-- Reference arrow placement angle. The default is 0, which means horizontal placement.
                        label          =  '25 mph',     #-- Referencearrow label.
                        labelpos       =  'S',          #-- Side where label appears relative to the reference arrow (S means south).
                        fontproperties =  {'size' : 8}  #-- Label font size.
                        )     
  t = QK.text.set_backgroundcolor('white')


  #-- Set map parameters.
  gl               =  ax.gridlines(color="black", linestyle="dotted", linewidth=0, draw_labels=True)
  gl.top_labels    =  False
  gl.right_labels  =  False
  gl.xformatter    =  LONGITUDE_FORMATTER
  gl.yformatter    =  LATITUDE_FORMATTER
  gl.xpadding      =  14
  gl.ypadding      =  14
  gl.xlabel_style  =  { 'size':8 }
  gl.ylabel_style  =  { 'size':8 }
  #ax.set_xticks([-120.6, -120.4, -120.2, -120.0, -119.8, -119.6, -119.4], crs=crs.PlateCarree())
  #ax.set_yticks([ 34.3, 34.4, 34.5, 34.6 ], crs=crs.PlateCarree())
  ax.tick_params(axis='both',which='major',direction='out', labelcolor='white', pad=10, labelsize=0.0001, zorder=-1, left=True, right=False, bottom=True, length=10)


  #-- Add info labels.
  tvalid    = ''.join( ['Valid: ', timestamp ])
  infost    = '2-m Relative Humidity'
  plt.gcf().text(0.695, 0.76, infost, fontsize=9)
  plt.gcf().text(0.680, 0.72, tvalid, fontsize=9)


  #-- Make things tidy.
  #ax.set_extent([-120.70, -119.20, 34.20, 34.70])
  divider =  make_axes_locatable(ax)
  cax     =  fig.add_axes([ax.get_position().x1 + 0.02, ax.get_position().y0 + 0.175, 0.02, 0.545*ax.get_position().height])
  CB      =  plt.colorbar(CF, ticks=ticks, orientation='vertical', extendfrac='auto', extendrect=False, aspect=18, drawedges=True, cax=cax)
  CB.set_label('', fontsize=9)
  CB.ax.set_title('%', fontsize=9)
  CB.ax.tick_params(labelsize=9, size=0)


  #-- Save figure.
  figtype   =  '.png'
  savedate  =  ''.join( [ str( df.index.day.values[0] ).zfill(2),   '-',
                          str( df.index.month.values[0] ).zfill(2), '-',
                          str( df.index.year.values[0] ),           '-',
                          str( df.index.hour.values[0] ).zfill(2),  ':',
                          str( df.index.minute.values[0] ).zfill(2) ] )
  savename  =  ''.join(['dom2.relhum.2m.', str(k+1).zfill(2),  figtype ])  
  outfpath = str(out_dir / savename)
  fig.set_size_inches(15, 9) # Ensure a consistent size
  fig.savefig(outfpath, dpi=100)
  plt.close()
  print(savename)
 


