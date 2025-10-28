#!/usr/bin/env python
# coding: utf-8


# ---------------------------------------------------------------------------------------
# This script is modified from the original received from 
# Charles Jones and the CLIVAC lab on 01/23/25.
#
# Purpose: Create plots of fog, low, mid, and high clouds for Santa Cruz Island. Used 
#          to compare WRF clouds with met station data as well as a GOES derived dataset. Plots wind field
#          as well. 
# ---------------------------------------------------------------------------------------


# In[97]:


# this script reads and plots fog and cloud layers from wrf output 

# Gert-Jan Duine, ERI UCSB, September 2020
# gertjan.duine@gmail.com / duine@eri.ucsb.edu

import pandas as pd # pandas is more labeled tabular oriented. works well if headers are provided in files.
import numpy as np
import netCDF4
from netCDF4 import Dataset
import wrf
import xarray as xr
from math import ceil

# plotting features/packages
from cartopy import crs
from cartopy.feature import NaturalEarthFeature, COLORS
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
import matplotlib as mpl
import cartopy.crs as crs
from cartopy.feature import NaturalEarthFeature
import matplotlib.colors as colors

from pathlib import Path

from wrf import (to_np, getvar, smooth2d, get_cartopy, cartopy_xlim,
                 cartopy_ylim, latlon_coords)


# File path definitions
root_dir = Path().resolve().parents[1]
data_dir = root_dir / "data" / "01_raw"

fname = "wrf-vert-profile-2008-08.nc"
fpath = str(data_dir / fname)

outfolder = root_dir / "outputs" / "figures" / "additional_analyses" / "wrf-clouds-sci" / "wrf-clouds-with-wind-field" # Where to save figures to 

print('----------------------------')
print("Root Directory: ", root_dir)
print("Data Directory: ", data_dir)
print("File Path: ", fpath)
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

# In[104]:


# Download and create the states, land, and oceans using cartopy features
states = cfeature.NaturalEarthFeature(category='cultural', scale='10m',
                                              facecolor='none',
                                              name='admin_1_states_provinces')
land = cfeature.NaturalEarthFeature(category='physical', name='land',
                                            scale='10m',
                                            facecolor='green')#facecolor='green')
ocean = cfeature.NaturalEarthFeature(category='physical', name='ocean',
                                             scale='10m',
                                             facecolor='blue')
#                                              facecolor=cfeature.COLORS['water']
cldLvls=np.arange(0.1,1.1,0.1) # a range for clouds

# define cloud levels
low_cloud=120 # <---------- fill out cloud levels here for a height_agl
mid_cloud=2000
high_cloud=5000

# fog level
low_cloud_fog=30 # <------------ fill out fog levels here
mid_cloud_fog=120

# it is easier to have fog as latest in the range. 
# low, middle and high clouds are 0,1,2 in array by defition. l=3 is defined as fog layer for easiness in looping
layerFileName=['Low','Middle','High','Fog']
layerTitle=['Low-level','Mid-level','High-level','Low-level']


# strings for in plot titles
hgtRange=[str(low_cloud)+' m < z < '+str(mid_cloud)+' m agl',
          str(mid_cloud)+' m < z < '+str(high_cloud)+' m agl',
          str(high_cloud)+' m and above',
          str(low_cloud_fog)+' m < z < '+str(mid_cloud_fog)+' m agl']

# Tickmark Locations
dxInt = np.arange(lonmin,lonmax,0.05)
dx = dxInt#[1:-1]
dy = np.arange(latmin,latmax,0.05)

# Wind Set Up -------------------------
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
# ----------------------------------------

# start reading file
print('working on file ', fpath)
ncfile = netCDF4.Dataset(fpath)
ntimes     =  ncfile.variables['Times'][:].shape[0]
ter = wrf.getvar(ncfile, "ter", timeidx=2)   
# landmask=wrf.getvar(ncfile,"LANDMASK",timeidx=-1)
# ter=ter2*landmask

# Get the latitude and longitude points
lats, lons = latlon_coords(ter)
# Get the cartopy mapping object
cart_proj = get_cartopy(ter)

timesteps = len(ncfile.variables['Times'])

#-- Get forecast range maximum and minimum wind speed.
ds          =  xr.open_dataset(fpath)
x1, y1      =  wrf.ll_to_xy(ncfile, 34.70, -120.70).values
x2, y2      =  wrf.ll_to_xy(ncfile, 34.20, -119.20).values
ds          =  ds.sel(south_north=slice(y2,y1), west_east=slice(x1,x2))
ds          =  ds.assign(si10=np.sqrt(ds["U10"]**2 + ds["V10"]**2))
var         =  ds["si10"].data
var         =  2.23694 * var      #-- m/s to mph.
wsp_min     =  0
wsp_max     =  ( ceil(var.max() / 2.) * 2 ) 

for t in np.arange(0,timesteps,1):#(0,73,1): # loop over times in file

    # Get the variables
    timeWRF=getvar(ncfile,'Times',t)
    slp         =  getvar(ncfile, "slp", timeidx=t, units="hPa")  
    hgt         =  getvar(ncfile, "HGT")
    lats, lons  =  latlon_coords(slp)
    cart_proj   =  get_cartopy(slp)
    var, _      =  getvar(ncfile, "wspd_wdir10", timeidx=t, units="mph")
    u10         =  2.23694 * getvar(ncfile, "U10", timeidx=t) 
    v10         =  2.23694 * getvar(ncfile, "V10", timeidx=t)

    # make string from the time in WRF using pandas
    ts = pd.to_datetime(to_np(timeWRF))
    tsPDT = ts - pd.DateOffset(hours=7)
    tWRFstrPDT=tsPDT.strftime('%Y%m%d %H')
    tWRFstrPDT_fName=tsPDT.strftime('%Y%m%d_%H')

    # From roughly low_thresh=30, it goes beyond first model level mass point (which is around 25-30 m)
    # so it should be 30...
    cloudFrac=wrf.g_cloudfrac.get_cloudfrac(ncfile,timeidx=t,vert_type='height_agl',
                                            low_thresh=low_cloud,
                                            mid_thresh=mid_cloud,
                                            high_thresh=high_cloud) # this is all three layers, we subselect later.
    
    cloudFracFog=wrf.g_cloudfrac.get_cloudfrac(ncfile,timeidx=t,vert_type='height_agl',
                                               low_thresh=low_cloud_fog,mid_thresh=mid_cloud_fog) # this is fog layer
    
    for l in range(len(layerTitle)): # range over cloude layers. 0,1,2 is low,middle,high clouds. 3 is fog layer
        print('working on',layerTitle[l],'cloud layer, plot',t)

        nrPlot=t+1 # plot counter. Start at 1 instead of 0
    
        # Create a figure that will have 3 subplots
        fig = plt.figure(figsize=(15,9))
        ax_cld = fig.add_subplot(1,1,1,projection=cart_proj)
        ax_cld.set_extent([lonmin,lonmax,latmin,latmax], crs=crs.PlateCarree())

        # Plot terrain 
        #-- Plot terrain height.
        levels_hgt =  np.arange(200,740,50)
        CL         =  plt.contour(to_np(lons), to_np(lats), to_np(hgt), levels=levels_hgt, colors='Black', linewidths=0.5, transform=crs.PlateCarree())
        ax_cld.clabel(CL, CL.levels, inline=True, fontsize=6)
        #terrainContour=ax_cld.contourf(to_np(lons), to_np(lats), to_np(ter), terLvls, cmap=tmap,
        #            transform=crs.PlateCarree()) # terrain elevation map with color grading

        # Station points
        ax_cld.scatter([sauclon, upemlon], [sauclat, upemlat], color='red', zorder=5, s=40, label='Stations', transform=ccrs.Geodetic())

        #-- Plot 10-m wind speed.
        levels  =  np.arange(wsp_min,wsp_max+2,2)
        ticks   =  levels
        CF      =  plt.contourf(to_np(lons), to_np(lats), to_np(var), levels=levels, extend='max', transform=crs.PlateCarree(), cmap=cmap)
        

        # l=0: low clouds, l=1: middle clouds, l=2: high clouds, l=3: self-defined fog layer
        if l==3:
            cloudcontours=ax_cld.contourf(to_np(lons), to_np(lats), to_np(cloudFracFog[0,:,:]), cldLvls,
                    transform=crs.PlateCarree(), zorder=1,
                    cmap=get_cmap("Greys_r"),alpha=1,extend='neither') # alpha=0.9 
            cloudContourLine=ax_cld.contour(to_np(lons), to_np(lats), to_np(cloudFracFog[0,:,:]), cldLvls,
                    colors='k',linewidths=0.5,transform=crs.PlateCarree(), zorder=5)
            
        else:
            cloudcontours=ax_cld.contourf(to_np(lons), to_np(lats), to_np(cloudFrac[l,:,:]), cldLvls,
                    transform=crs.PlateCarree(), zorder=1,
                    cmap=get_cmap("Greys_r"),alpha=1,extend='neither') # alpha=0.9       
            cloudContourLine=ax_cld.contour(to_np(lons), to_np(lats), to_np(cloudFrac[l,:,:]), cldLvls,
                    colors='k',linewidths=0.5,transform=crs.PlateCarree(), zorder=5)

#         clabels=ax_cld.clabel(cloudcontours,
#                       inline=1,inline_spacing=0,fontsize=8,fmt='%1.1f',colors='k')
        
                #-- Plot 10-m winds.
        skip  =  2
        QV    =  ax_cld.quiver(to_np(lons[::skip,::skip]), to_np(lats[::skip,::skip]), to_np(u10[::skip, ::skip]), to_np(v10[::skip, ::skip]), scale=500, width=0.002, transform=crs.PlateCarree())
        QK    =  ax_cld.quiverkey(QV,                             #-- Incoming quiver handle.
                                X              =  0.065,        #-- Determine the location of label, all limited to [0,1].
                                Y              =  0.280,        #-- Determine the location of label, all limited to [0,1].
                                coordinates    =  'figure',
                                U              =  25,           #-- Reference arrow length means the wind speed is U mph.
                                angle          =  0,            #-- Reference arrow placement angle. The default is 0, which means horizontal placement.
                                label          =  '25 mph',     #-- Referencearrow label.
                                labelpos       =  'S',          #-- Side where label appears relative to the reference arrow (S means south).
                                fontproperties =  {'size' : 8},  #-- Label font size.
                                zorder=20
                                )
        

        # xticks
        ax_cld.set_xticks(dx, crs=crs.PlateCarree())
        lon_formatter = LongitudeFormatter()
        ax_cld.xaxis.set_major_formatter(lon_formatter)
        # yticks
        ax_cld.set_yticks(dy, crs=crs.PlateCarree())
        lat_formatter = LatitudeFormatter()
        ax_cld.yaxis.set_major_formatter(lat_formatter)
        # tick params
        ax_cld.tick_params(direction='out', labelsize=14, length=5, pad=2, color='black')    

        
        ax_cld.add_feature(states, linewidth=.5, edgecolor="black")
        ax_cld.add_feature(cfeature.COASTLINE, edgecolor='k', linewidth=2.0,zorder=3)


        #t = QK.text.set_backgroundcolor('white')

    
        # Draw the oceans, land, and states
        #ax_cld.add_feature(ocean)

        # Add a color bar for clouds 
        cbar_ax = fig.add_axes([ax_cld.get_position().x1 + 0.02, 
                                ax_cld.get_position().y0, 
                                0.02, 
                                ax_cld.get_position().height])
        cbar = fig.colorbar(cloudcontours, cax=cbar_ax)
        cbar.set_label('Cloud fraction', fontsize=12)

        # Add a color bar for wind field
        cbar_wind_ax = fig.add_axes([ax_cld.get_position().x1 + 0.08,  # Offset for proper spacing
                                    ax_cld.get_position().y0, 
                                    0.02, 
                                    ax_cld.get_position().height])  
        CB = plt.colorbar(CF, cax=cbar_wind_ax, ticks=ticks, extend='max')
        CB.set_label('Wind Speed (mph)', fontsize=9)
        CB.ax.tick_params(labelsize=7, size=0)

        ax_cld.set_ylabel('Latitude $^\circ$N',fontsize=18)
        ax_cld.set_xlabel('Longitude $^\circ$W',fontsize=18)

        ax_cld.set_title(layerTitle[l]+" clouds ("+ hgtRange[l] + ") - " + tWRFstrPDT + ":00 PDT",fontsize=14)

        nrPlotStr=str(nrPlot)
        # save figure
        fName= str(outfolder) + '/Fig_clouds_'+layerFileName[l]+'.'+ nrPlotStr.zfill(5) + '.png'
        fig.savefig(fName, bbox_inches='tight', dpi=100)
        fig.clf() # close figure
        plt.close() # close figure
        nrPlot+=1

        del cloudcontours,cloudContourLine,nrPlot,cbar, QV, QK, CF # loop for cloud layers
        
    del timeWRF,cloudFrac,cloudFracFog,ax_cld,fName,tWRFstrPDT # loop over time
    
del ter

exit

# %%
