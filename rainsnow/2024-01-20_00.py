# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 11:09:22 2024
    draw  snow or rain
@author: lenovo
"""
import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker  # 导入刻度格式化器
import matplotlib.colors as mcolors
############### setting  ################################
#designed for comparision of WRF&FM. IF run one model,make wrfoutpath and title list the same.
wrfout_path=['/public23/home/sc61341/gsj/work/wrfout/fmout_d01_2024-01-20_00:00:00',
             '/public23/home/sc61341/gsj/work/wrfout/wrfout_d01_2024-01-20_00:00:00']
title=['fm','wrf']  #final title:  model_time

varname='SNOW'  #SNOW  RAIN  一般不画SNOWH  
ts='2024-01-20_00'  # YYYY-MM-DD_HH format; start_time
dt_hour=24          #24h prep or 12h prep or 6h prep

#################  functions ########################

def it(ts):
    time2 = np.array([t[:13] for t in time])
    # 在数组中查找匹配的时间字符串
    return np.where(time2 == ts)[0][0]


############## file read #################################
dslist=[]
for i in wrfout_path:
    ds=xr.open_dataset(i,engine='netcdf4')
    dslist.append(ds)


for i in range(0,len(dslist)):
    ds=dslist[i]
    ##############  coord&var  #############################
    lat=ds.XLAT.values[0,:,:]
    lon=ds.XLONG.values[0,:,:]
    time=np.array(ds.Times.values,dtype='str')
    
    if varname=='RAIN' :
        var=ds.RAINC.values + ds.RAINSH.values + ds.RAINNC.values
    elif varname == 'SNOW' :
        var=ds.SNOW.values
    elif varname == 'SNOWH':
        var=ds.SNOWH.values
    
    ######################   cmap   #################
    if varname=='RAIN':
        levels=[0.1,10.0,25.0,50.0,100.0,250.0,500.0]#雨量等级
        colors=['#A6F28F','#3DBA3D','#61BBFF','#0000FF','#FA00FA','#800040']#颜色列表
        cmap=mcolors.ListedColormap(colors)#产生颜色映射
        norm=mcolors.BoundaryNorm(levels,cmap.N)#生成索引
    elif varname=="SNOW":
        levels = [0, 0.1, 2.5, 5, 10, 25, 50] #雪量
        colors = ["#ffffff", "#c5e7b0", "#68b165", "#329ed8", "#286ab3", "#ec46f6"]
        cmap = mcolors.ListedColormap(colors)
        norm=mcolors.BoundaryNorm(levels,cmap.N)#生成索引
    else: 
        print("Wrong varname is set, recheck the setting part.")
        os._exit()
        
    
    
    
    ######################   draw   ###################
    its=it(ts) #初始时刻对应序号
    while its<=(len(time)-dt_hour):
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()},figsize=(15, 10))
        ax.add_feature(cfeature.COASTLINE) #海岸线
        ax.add_feature(cfeature.BORDERS)
        china_provinces = cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces_lines', scale='10m', facecolor='none')
        ax.add_feature(china_provinces, edgecolor='black', linewidth=0.5) #省界
        ax.set(xlim=(np.min(lon),np.max(lon)))
        ax.set(ylim=(np.min(lat),np.max(lat)))    
        ax.set_xticks(np.arange(np.min(lon)-2, np.max(lon)+ 4, 4))  
        ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())  # 格式化为经度格式
        ax.set_yticks(np.arange(np.min(lat)-2, np.max(lat)+ 4, 4))  
        ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())  # 格式化为纬度格式
        ax.set_title(f'{title[i]}   {dt_hour}hour_from_{time[its][:13]}')
        contourf=ax.contourf(lon,lat,var[its+24]-var[its],cmap=cmap,alpha=0.7,levels=levels,norm=norm )  #
        cbar = fig.colorbar(contourf, ax=ax, shrink=0.8,orientation='horizontal')
        plt.savefig(f'{title[i]}_{dt_hour}hour_from_{time[its][:13]}', dpi=900)
        its+=24        



os.system(f'cp rainsnow.py {ts}.py')