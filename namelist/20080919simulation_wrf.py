# -*- coding: utf-8 -*-
#!/usr/bin/python3
"""
Created on Fri Oct 25 15:47:20 2024

autoexe WRF precedure in PYTHON.
    Reason: 1) Time expense to learn bash syntax makes it expensive to DIY your own WRF working procedure.
            2) bash don't support complicate data structure. Make the code hard to understand and modify.
This is the Simulation version. Like wise there is Forecasting version differs in existence of 
assimulation system and data source. 


***Befor use***
1)Datapath directory must be like this
FNL    ERA5    xxx
       PL SF
2)namelist setting need to be changed in the difinition of Class--Namelist

@author: gosure
"""

import f90nml 
import os
from datetime import datetime

class Namelist:
    def __init__(self,wpspath,wrfpath):
        self.wps = {
            'share':{
                'max_dom':1,
                'start_date':'2008-09-19_00:00:00',
                'end_date':['2008-09-21_00:00:00'],
                'interval_seconds': 21600  #time frequency of met_em
                },
            'geogrid':{
                'e_we':550,
                'e_sn':350,
                'dx':18000, ##### fm 不用变
                'dy':18000, #####
                'ref_lat':34.510,  # denote center point
                'ref_lon':104.642,
                'truelat1':38.210,
                'truelat2':38.210,
                'stand_lon':97.998,  #normally=ref_lon
                },
            'ungrib':{
                'prefix':'' #intentionaly blank
                },
            'metgrid':{
                'fg_name':'' #intentionaly blank
                }
        }
        self.wrf = {
            "time_control": {
                'run_days': 0,
                'run_hours': 0,
                'start_year': 2008,
                'start_month': 9,
                'start_day':  19,
                'start_hour': 0,
                'end_year':2008,
                'end_month':9,
                'end_day':21,
                'end_hour':0,
                "interval_seconds": 21600,   #same above
                "history_interval": [60],    #out_frequency 1h
                },
            "domains": {
                "time_step": 60,
                "max_dom": 1,
                "e_we": [550],
                "e_sn": [350],
                "e_vert": [51],
                "num_metgrid_levels": 27,     ######FNL 34/27 老数据是27   ERA5 38
                "dx": [18000],   ####fm不用变
                "dy": [18000],
                },
            "physics": {
                "mp_physics": [16],
                "cu_physics": [1],
                "ra_lw_physics": [1],
                "ra_sw_physics": [1],
                "bl_pbl_physics": [2],
                "sf_sfclay_physics": [2],
                "sf_surface_physics": [2],
                "radt": [3],
                "bldt": [0],
                "cudt": [5],
                "icloud": 1,
                "num_land_cat": 21,
                "sf_urban_physics": [0],
                "do_radar_ref": 0,
                "topo_wind": 0
               },
            "fdda":{
                'grid_fdda':0}
        }
        self.wpspath=wpspath
        self.wrfpath=wrfpath
               
    def updatewps(self): 
        old_namelist=f90nml.read(self.wpspath+'/namelist.wps')
        keys1=self.wps.keys()
        for i in keys1:
            keys2=self.wps[i].keys()
            for j in keys2:    
                old_namelist[i][j]=self.wps[i][j]
        old_namelist.write(self.wpspath+'/namelist.wps','w')
        
    def updatewrf(self):
        old_namelist=f90nml.read(self.wrfpath+'/namelist.input')
        keys1=self.wrf.keys()
        for i in keys1:
            keys2=self.wrf[i].keys()
            for j in keys2:    
                old_namelist[i][j]=self.wrf[i][j]
        old_namelist.write(self.wrfpath+'/namelist.input','w')
    
    def record(self,recordpath):
        date_obj = datetime.strptime(self.wps['share']['start_date'], "%Y-%m-%d_%H:%M:%S")
        time = date_obj.strftime("%Y%m%d")
        os.system(f'cp  {wpspath}/namelist.wps {recordpath}/{time}namelist.wps')
        os.system(f'cp {wrfpath}/namelist.input {recordpath}/{time}namelist.input')
        os.system(f'cp {recordpath}/../simulation_wrf.py {recordpath}/{time}simulation_wrf.py')



class wps_class:
    def __init__(self,datacat,datapath,wpspath,nml):
        self.datacat=datacat
        self.wpspath=wpspath
        self.nml=nml
        self.datapath=datapath
        
    def geogrid(self):
        os.chdir(self.wpspath)
        os.system("./geogrid.exe")
        
    def ungrib(self):
        os.chdir(self.wpspath)
        os.system('rm FNL* PL* SF* PFILE* ')
        if self.datacat=="FNL":
            nml.wps['ungrib']['prefix']="FNL"
            nml.wps['metgrid']['fg_name']='FNL'
            nml.updatewps()
            os.chdir(self.wpspath)
            datapath=self.datapath+"/FNL/*grib*"
            os.system('./link_grib.csh '+datapath)
            os.system('rm Vtable')
            os.system(f"ln -s {self.wpspath}/ungrib/Variable_Tables/Vtable.GFS Vtable")
            os.system("./ungrib.exe")
        if self.datacat=="ERA5":
            os.chdir(self.wpspath)
            os.system("rm Vtable")
            os.system(f'ln -s {self.wpspath}/ungrib/Variable_Tables/Vtable.ERA-interim.pl Vtable')

            datapath=self.datapath+"/ERA5/PL/*grib*"
            os.system('./link_grib.csh '+datapath)
            nml.wps['ungrib']['prefix']="PL"
            nml.updatewps()
            os.system('./ungrib.exe')
            datapath=self.datapath+"/ERA5/SF/*grib*"
            os.system('./link_grib.csh '+datapath)
            nml.wps['ungrib']['prefix']="SF"
            nml.updatewps()
            os.system('./ungrib.exe')
            
    def metgrid(self):
        os.chdir(self.wpspath)
        os.system('rm met_em*')
        if self.datacat=="FNL":
            nml.wps['metgrid']['fg_name']=['FNL']
            os.system("./metgrid.exe")
        if self.datacat=="ERA5":
            nml.wps['metgrid']['fg_name']=['PL',"SF"]
            os.system("./metgrid.exe")
    
            
class wrf_class:
    def __init__(self,wrfpath,cpus):
        self.cpus=cpus
        self.wrfpath=wrfpath
    def real(self):
        os.chdir(wrfpath)
        os.system('rm met_em*')
        os.system(f"ln -s {wpspath}/met_em* .")
        os.system("./real.exe")
    def wrf(self):
        os.chdir(wrfpath)
        self.modi_sbatch()
        os.system(f'sbatch {subname}')
    def modi_sbatch(self):  
        node_cpus=64     #北京超算单节点有64个核心，如果服务器变了这里也要改。
        if self.cpus%node_cpus==0:
            N=int(self.cpus/node_cpus)
        else:    
            N=1+int(self.cpus/node_cpus)
        os.system(f'sed -i "s/^#SBATCH -N .*/#SBATCH -N {N}/" {subname}')
        os.system(f'sed -i "s/^#SBATCH -n .*/#SBATCH -n {self.cpus}/" {subname}')

        
        
########  basic  #########
wpspath='/public23/home/sc61341/gsj/WPS'
wrfpath='/public23/home/sc61341/gsj/WRF/run'
datapath='/public23/home/sc61341/gsj/data'  #data/FNL data/ERA5/PL data/ERA5/SF  Directory should follow this pattern.
recordpath='/public23/home/sc61341/gsj/work/namelist/'
datacat='FNL'   # FNL,ERA5
subname='subgsj.sh'
########  init  #########
nml=Namelist(wpspath,wrfpath)
nml.updatewps()
nml.updatewrf()
nml.record(recordpath)
wps=wps_class(datacat,datapath,wpspath,nml)
cpus= int(nml.wps['geogrid']['e_we']/25) * int(nml.wps['geogrid']['e_sn']/25) 
wrf=wrf_class(wrfpath, cpus)

########  DIY your procedure here  ##########

#wps.geogrid()
wps.ungrib()
wps.metgrid()
wrf.real()
wrf.wrf()






