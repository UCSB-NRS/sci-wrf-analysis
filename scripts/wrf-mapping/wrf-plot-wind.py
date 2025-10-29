#============================================================
#
#  plot_wrf_wsp_sb.py
#
#  Plot 10-m winds from WRF forecast (Santa Barbara domain).
#
#============================================================


import pathlib
import wrf
import matplotlib
import numpy as np
import xarray as xr
import pandas as pd
import netCDF4 as nc
from math import ceil
import cartopy.crs as crs
import matplotlib.pyplot as plt
import matplotlib.image as image
import matplotlib.colors as colors
from metpy.plots import USCOUNTIES
from cartopy.feature import NaturalEarthFeature
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from wrf import (to_np, getvar, smooth2d, get_cartopy, cartopy_xlim, cartopy_ylim, latlon_coords)
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import rcParams
rcParams['font.family']     = 'sans-serif'
rcParams['font.sans-serif'] = 'Helvetica'


#-- Define a custom colormap.
wind_colors = [
    "#fdfdfd", 
    "#04e9e7",
    "#019ff4",
    "#02fd02",
    "#01c501",
    "#fdf802",
    "#fd9500",
    "#fd0000",
    "#bc0000",
    "#9854c6",]
#cmap = matplotlib.colors.ListedColormap(wind_colors)
def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap
cmap = truncate_colormap(plt.cm.jet, minval=0.30, maxval=1.0, n=100)


#-- Load WRF output.
root_dir = Path().resolve().parents[1]
data_dir = root_dir / "data" / "01_raw"
fname = "wrf-vert-profile-2008-08.nc"
ncfile = nc.Dataset(str(data_dir / fname))

ntimes     =  ncfile.variables['Times'][:].shape[0]


#-- Get forecast range maximum and minimum wind speed.
ds          =  xr.open_dataset(path+infile)
x1, y1      =  wrf.ll_to_xy(ncfile, 34.70, -120.70).values
x2, y2      =  wrf.ll_to_xy(ncfile, 34.20, -119.20).values
ds          =  ds.sel(south_north=slice(y2,y1), west_east=slice(x1,x2))
ds          =  ds.assign(si10=np.sqrt(ds["U10"]**2 + ds["V10"]**2))
var         =  ds["si10"].data
var         =  2.23694 * var      #-- m/s to mph.
wsp_min     =  0
wsp_max     =  ( ceil(var.max() / 2.) * 2 ) 



for k in range(ntimes):


  #-- Get plotting variables.
  t           =  getvar(ncfile, "Times", timeidx=k)
  slp         =  getvar(ncfile, "slp", timeidx=k, units="hPa")  
  hgt         =  getvar(ncfile, "HGT")
  lats, lons  =  latlon_coords(slp)
  cart_proj   =  get_cartopy(slp)
  var, _      =  getvar(ncfile, "wspd_wdir10", timeidx=k, units="mph")
  u10         =  2.23694 * getvar(ncfile, "U10", timeidx=k) 
  v10         =  2.23694 * getvar(ncfile, "V10", timeidx=k)

 
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
  fig     =  plt.figure()
  ax      =  plt.axes(projection=cart_proj)
  ax.add_feature(USCOUNTIES.with_scale('5m'), edgecolor='Black', linewidths=0.8)


  #-- Plot 10-m wind speed.
  levels  =  np.arange(wsp_min,wsp_max+2,2)
  ticks   =  levels
  CF      =  plt.contourf(to_np(lons), to_np(lats), to_np(var), levels=levels, extend='max', transform=crs.PlateCarree(), cmap=cmap)
  
 
  #-- Plot terrain height.
  levels_hgt =  np.arange(200,2600+100,100)
  CL         =  plt.contour(to_np(lons), to_np(lats), to_np(hgt), levels=levels_hgt, colors='Black', linewidths=0.5, transform=crs.PlateCarree())
  ax.clabel(CL, CL.levels, inline=True, fontsize=6)


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
  ax.set_xlim( cartopy_xlim( getvar(ncfile, "HGT", timeidx=k) ) )
  ax.set_ylim( cartopy_ylim( getvar(ncfile, "HGT", timeidx=k) ) )
  gl               =  ax.gridlines(color="black", linestyle="dotted", linewidth=0, draw_labels=True)
  gl.top_labels    =  False
  gl.right_labels  =  False
  gl.xformatter    =  LONGITUDE_FORMATTER
  gl.yformatter    =  LATITUDE_FORMATTER
  gl.xpadding      =  14
  gl.ypadding      =  14
  gl.xlabel_style  =  { 'size':8 }
  gl.ylabel_style  =  { 'size':8 }
  ax.set_xticks([-120.6, -120.4, -120.2, -120.0, -119.8, -119.6, -119.4], crs=crs.PlateCarree())
  ax.set_yticks([ 34.3, 34.4, 34.5, 34.6 ], crs=crs.PlateCarree())
  ax.tick_params(axis='both',which='major', direction='out', labelcolor='white', pad=10, labelsize=0.0001, zorder=-1, left=True, right=False, bottom=True, length=10)



  #-- Add info labels.
  tvalid    =  ''.join( ['Valid: ', timestamp ])
  infost    =  '10-m Winds' 
  plt.gcf().text(0.785, 0.76, infost, fontsize=9)
  plt.gcf().text(0.680, 0.72, tvalid, fontsize=9)

  
  #-- Make things tidy.
  ax.set_extent([-120.70, -119.20, 34.20, 34.70])
  divider =  make_axes_locatable(ax)
  cax     =  fig.add_axes([ax.get_position().x1 + 0.02, ax.get_position().y0 + 0.175, 0.02, 0.545*ax.get_position().height])
  CB      =  plt.colorbar(CF, ticks=ticks, orientation='vertical', extendfrac='auto', extendrect=True, aspect=18, drawedges=True, cax=cax)
  CB.set_label('', fontsize=9)
  CB.ax.set_title('mph', fontsize=9)
  CB.ax.tick_params(labelsize=7, size=0)


  #-- Save figure.
  figtype   =  '.png'
  savedate  =  ''.join( [ str( df.index.day.values[0] ).zfill(2),   '-',
                          str( df.index.month.values[0] ).zfill(2), '-',
                          str( df.index.year.values[0] ),           '-',
                          str( df.index.hour.values[0] ).zfill(2),  ':',
                          str( df.index.minute.values[0] ).zfill(2) ] )
  savename  =  ''.join(['dom2.wind10m.', str(k+1).zfill(2),  figtype ])  
#  savename  =  ''.join(['wrfout-wsp-', 'sb-', str(k).zfill(2), 'h', figtype ])  
  savepath  = root_dir / "outputs" / "figures" / "additional-analyses" / "wrf-clouds-sci" / "wrf-wind" # Where to save figures to 
  plt.savefig(savepath+savename, bbox_inches='tight', dpi=140)
  plt.close()
  print(savename)
  

 


