# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 15:37:22 2024

@author: lenovo
"""
import numpy as np
import xarray as xr
import re
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker  # 导入刻度格式化器
import matplotlib.colors as mcolors
import matplotlib as mpl
import cmaps


####################### Normally the only change part #######################
geopath='/public23/home/sc61341/gsj/WPS/'
wrfinputpath=['/public23/home/sc61341/gsj/model_1.0/test/em_real/',
              '/public23/home/sc61341/gsj/model_3_5/test/em_real/',
              '/public23/home/sc61341/gsj/model_5_10/test/em_real/',
              '/public23/home/sc61341/gsj/model_10_8/test/em_real/']

cmap=plt.get_cmap(cmaps.so4_21_r)
levels=np.arange(0,2100,100)
#############################   var    #################################
geo=xr.open_dataset(geopath+'geo_em.d01.nc', engine='netcdf4')
h=xr.open_dataset(geopath+'geo_em.d01.nc', engine='netcdf4').HGT_M.values[0,:,:]  #real
hf=[]
for i in wrfinputpath:
    inp=xr.open_dataset(i+'wrfinput_d01', engine='netcdf4').HGT.values[0,:,:]
    hf.append(inp)


##############################   coord    ############################
lat=geo.CLAT.values[0,:,:]
lon=geo.CLONG.values[0,:,:]



################################   draw     #################################


#  draw real
fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()},figsize=(10, 10))
ax.add_feature(cfeature.COASTLINE) #海岸线
ax.add_feature(cfeature.BORDERS)
china_provinces = cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces_lines', scale='10m', facecolor='none')
ax.add_feature(china_provinces, edgecolor='black', linewidth=0.5)
ax.set(xlim=(np.min(lon),np.max(lon)))
ax.set(ylim=(np.min(lat),np.max(lat)))    
ax.set_xticks(np.arange(np.min(lon)-2, np.max(lon)+ 4, 4))  
ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())  # 格式化为经度格式
ax.set_yticks(np.arange(np.min(lat)-2, np.max(lat)+ 4, 4))  
ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())  # 格式化为纬度格式
ax.set_title('real terrain')
contourf=ax.contourf(lon,lat,h,cmap=cmap,alpha=0.7,levels=levels,extend='both')
cbar = fig.colorbar(contourf,orientation='vertical', ax=ax, shrink=0.6)
plt.savefig(f'terrain_plot_real.png', dpi=900, bbox_inches='tight')



#  wrfinput
for i in range(0,len(hf)):
    matches = re.findall(r'(\d+)', wrfinputpath[i])
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()},figsize=(10, 10))
    ax.add_feature(cfeature.COASTLINE) #海岸线
    ax.add_feature(cfeature.BORDERS)
    china_provinces = cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces_lines', scale='10m', facecolor='none')
    ax.add_feature(china_provinces, edgecolor='black', linewidth=0.5)
    ax.set(xlim=(np.min(lon),np.max(lon)))
    ax.set(ylim=(np.min(lat),np.max(lat)))    
    ax.set_xticks(np.arange(np.min(lon)-2, np.max(lon)+ 4, 4))  
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())  # 格式化为经度格式
    ax.set_yticks(np.arange(np.min(lat)-2, np.max(lat)+ 4,4))  
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())  # 格式化为纬度格式
    
    ax.set_title(f'filtered terrain rc={matches[2]},p={matches[3]}')
    contourf=ax.contourf(lon,lat,hf[i],cmap=cmap,alpha=0.7,levels=levels,extend='both')
    cbar = fig.colorbar(contourf,orientation='vertical', ax=ax, shrink=0.6)
    plt.savefig(f'terrain_plot_rc{matches[2]}p{matches[3]}.png', dpi=900, bbox_inches='tight')



























