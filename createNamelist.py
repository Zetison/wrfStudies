from datetime import timedelta
import numpy as np
import json
import requests
import ftplib
import netCDF4
import f90nml
import pandas as pd
from pathlib import Path
from os.path import expanduser, isfile, basename
from os import getpid
import click
import copy
home = expanduser("~")
@click.command()
@click.option('--wps_nml_path', default=home+'/kode/wrfStudies/namelist.wps.all_options')
@click.option('--wrf_nml_path', default=home+'/kode/wrfStudies/namelist.input.all_options')
@click.option('--config_nml_path', default=home+'/kode/wrfStudies/configurations/standard.nml')
@click.option('--pathtoresults', default=home+'/results/WRF')
@click.option('--pathtoinput', default=home+'/kode/wrfStudies/studies')
@click.option('--geogdatapath', default=home+'/WPS_DATA/WPS_GEOG')
@click.option('--wpsdatapath', default=home+'/kode/WRF/Build_WRF/DATA')
@click.option('--gfsres', default='0p25')
@click.option('--case', default='debug')
@click.option('--runglobal/--no-runglobal', default=False)
@click.option('--output', default='wps')
@click.option('--start_date', default='2020-12-05 12:00:00')
@click.option('--ncepuserfilename', default='NCEPuserData.json')
def main(wps_nml_path,wrf_nml_path,config_nml_path,pathtoresults,pathtoinput,geogdatapath,wpsdatapath,gfsres,case,runglobal,output,start_date,ncepuserfilename):
    wrf_nml = f90nml.read(wrf_nml_path)
    wps_nml = f90nml.read(wps_nml_path)
    config_nml = f90nml.read(config_nml_path)
    input_nml = f90nml.read(pathtoinput+'/'+case+'.nml')

    days    = input_nml['time_control']['run_days']
    hours   = input_nml['time_control']['run_hours']
    minutes = input_nml['time_control']['run_minutes']
    seconds = input_nml['time_control']['run_seconds']

    if start_date:
        start_date = pd.to_datetime(start_date)

        input_nml['share']['start_date'] = start_date.strftime("%Y-%m-%d_%H:%M:%S")
    else:
        start_date = input_nml['share']['start_date']
        start_date = pd.to_datetime(start_date)

    end_date = start_date + timedelta(days=days,hours=hours,minutes=minutes,seconds=seconds)
    input_nml['share']['end_date'] = end_date.strftime("%Y-%m-%d_%H:%M:%S")

    pathtoresults += '/'+case+'/'+start_date.strftime("%Y%m%d%H")
    Path(pathtoresults).mkdir(parents=True, exist_ok=True)
    if output == 'wps':
        output_nml = copy.deepcopy(wps_nml)
        output_path = pathtoresults+'/namelist.wps'
    elif output == 'wrf':
        output_nml = copy.deepcopy(wrf_nml)
        output_path = pathtoresults+'/namelist.input'

    # Update default values with values from the configuration namelist file
    for namelist in config_nml:
        for subnamelist in config_nml[namelist]:
            try:
                output_nml[namelist][subnamelist] = config_nml[namelist][subnamelist]
            except Exception:
                continue

    max_dom = input_nml['share']['max_dom']
    if output == 'wps':
        output_nml['geogrid']['geog_data_path'] = geogdatapath
        output_nml['geogrid']['opt_geogrid_tbl_path'] = pathtoresults
        output_nml['metgrid']['opt_output_from_metgrid_path'] = pathtoresults+'/wps_io/'
        output_nml['metgrid']['opt_metgrid_tbl_path'] = pathtoresults
    elif output == 'wrf':
        # Transfer identical fields for consistency
        output_nml['domains']['max_dom'] = max_dom
        output_nml['domains']['adaptation_domain'] = max_dom
        for field in ['parent_id','parent_grid_ratio','i_parent_start','j_parent_start','e_we','e_sn']:
            output_nml['domains'][field] = input_nml['geogrid'][field]

        output_nml['time_control']['start_year']  = start_date_y
        output_nml['time_control']['start_month'] = start_date.month
        output_nml['time_control']['start_day']   = start_date.day
        output_nml['time_control']['start_hour']  = start_date.hour
        output_nml['time_control']['end_year']    = end_date.year
        output_nml['time_control']['end_month']   = end_date.month
        output_nml['time_control']['end_day']     = end_date.day
        output_nml['time_control']['end_hour']    = end_date.hour

    # Update default values with values from the input namelist file
    for namelist in input_nml:
        for subnamelist in input_nml[namelist]:
            try:
                output_nml[namelist][subnamelist] = input_nml[namelist][subnamelist]
            except Exception:
                continue

    # Check available GFS resolution
    interval_seconds = input_nml['share']['interval_seconds']
    interval_hours = np.round(interval_seconds/3600).astype(int)

    if output == 'wps':
        for hour in np.arange(0,np.ceil(days*24+hours+minutes/60+seconds/3600).astype(int)+interval_hours,interval_hours):
            start_date_ymd = start_date.strftime("%Y%m%d")
            start_date_ymdh = start_date.strftime("%Y%m%d%H")
            start_date_h = start_date.strftime("%H")
            start_date_y = start_date.strftime("%Y")
            filename = wpsdatapath+'/GFS_%s_%s_%03dh' % (gfsres, start_date_ymdh, hour)
            ncepuserfile = open(ncepuserfilename)
            NCEPuserData = json.load(ncepuserfile) 
            if not isfile(filename):
                print('Downloading NCEP data file %s' % basename(filename))
                user = 'anonymous'
                passwdNCEP = NCEPuserData['email'] 
                server = 'ftpprd.ncep.noaa.gov'
                path = 'pub/data/nccf/com/gfs/prod/gfs.%s/atmos' % (start_date.strftime("%Y%m%d/%H"))
                gfsFile = 'gfs.t%sz.pgrb2.%s.f%03d' % (start_date_h, gfsres, hour)

                try:
                    ftp = ftplib.FTP(server, user, passwdNCEP)
                    ftp.cwd(path)
                    ftp.retrbinary("RETR " + gfsFile, open(filename, 'wb').write)
                    ftp.quit()
                except Exception:
                    if interval_seconds < 10800 or not gfsres == '0p25':
                        raise Exception('Could not download '+basename(filename)+' as it does no longer exist on UCAR or NCEP servers')
                    else:
                        data = "email=%s&passwd=%s&action=login" % (NCEPuserData['email'], NCEPuserData['passwd'])
                        url = 'https://rda.ucar.edu/cgi-bin/login'
                        authFileName = 'auth_status.rda.ucar.edu.'+str(getpid())
                        cookies = {'enwiki_session': authFileName}
                        responseAuth = requests.post(url, data=data, cookies=cookies)
                        responseAuth.raise_for_status() # ensure we notice bad responses
                        url = 'https://rda.ucar.edu/data/ds084.1/%s/%s/gfs.%s.%s.f%03d.grib2' % (start_date_y, start_date_ymd, gfsres, start_date_ymd, start_date_h, hour)
                        responseGFS = requests.post(url, cookies=responseAuth.cookies)
                        responseGFS.raise_for_status() # ensure we notice bad responses
                        with open(filename, "wb") as f:
                            f.write(responseGFS.content)
            else:
                print('Found file '+basename(filename))

        if not input_nml['geogrid'].get('pole_lat'):
            ref_lat = output_nml['geogrid']['ref_lat']
            ref_lon = output_nml['geogrid']['ref_lon']
            output_nml['geogrid']['pole_lat'] = 90.0 - ref_lat
            output_nml['geogrid']['pole_lon'] = 180.0
            if runglobal:
                output_nml['geogrid']['stand_lon'] = -ref_lon
            else:
                output_nml['geogrid']['stand_lon'] = ref_lon

        if output_nml['geogrid']['map_proj'] == 'lat-lon':
            del output_nml['geogrid']['truelat1']
            del output_nml['geogrid']['truelat2']
        else:
            del output_nml['geogrid']['pole_lat']
            del output_nml['geogrid']['pole_lon']

        if runglobal: 
            del output_nml['geogrid']['dx']
            del output_nml['geogrid']['dy']
            del output_nml['geogrid']['ref_lat']
            del output_nml['geogrid']['ref_lon']
       
        # If ref_x/ref_y is not specified use the default calculations (and not the one given in wps_nml)
        if not input_nml['geogrid'].get('ref_x'):
            del output_nml['geogrid']['ref_x']

        if not input_nml['geogrid'].get('ref_y'):
            del output_nml['geogrid']['ref_y']
    elif output == 'wrf':
        dx = [''] * max_dom
        dy = [''] * max_dom
        output_nml['time_control']['interval_seconds'] = interval_seconds
        if not input_nml['time_control'].get('auxinput4_interval'):
            output_nml['time_control']['auxinput4_interval'] = interval_seconds

        for i in range(max_dom):
            base_url = pathtoresults+'/wps_io/geo_em.d%02d.nc' % (i+1)
            try:
                nc_geo = netCDF4.Dataset(base_url)
            except Exception:
                print('Could not find the file '+base_url)

            dx[i] = nc_geo.DX
            dy[i] = nc_geo.DY
    
        output_nml['domains']['dx'] = dx
        output_nml['domains']['dy'] = dy
        base_url = pathtoresults+'/wps_io/met_em.d01.%s.nc' % start_date.strftime("%Y-%m-%d_%H:%M:%S")
        try:
            nc_met = netCDF4.Dataset(base_url)
        except Exception:
            print('Could not find the file '+base_url)

        output_nml['domains']['num_metgrid_levels'] = nc_met.dimensions['num_metgrid_levels'].size
        output_nml['domains']['num_metgrid_soil_levels'] = nc_met.dimensions['num_st_layers'].size

    # Fix domain dependent fields to have exactly max_dom entries
    for parent_start in [False,True]: # Set i_parent_start and j_parent_start after potentially dependent fields
        for namelist in output_nml:
            for subnamelist in output_nml[namelist]:
                item = output_nml[namelist][subnamelist]
                if isinstance(item,list):
                    del output_nml[namelist][subnamelist][max_dom:]
                else:
                    item = [item]
                    output_nml[namelist][subnamelist] = item

                if output == 'wps':
                    itemold = wps_nml[namelist][subnamelist]
                elif output == 'wrf':
                    itemold = wrf_nml[namelist][subnamelist]

                if not isinstance(itemold,list):
                    itemold = [itemold]

                noValues = len(item)
                if noValues < max_dom and len(itemold) > 1:
                    lastValue = output_nml[namelist][subnamelist][-1]
                    if subnamelist == 'i_parent_start' or subnamelist == 'j_parent_start':
                        if parent_start:
                            if subnamelist == 'j_parent_start':
                                E = 'E_WE'
                            else:
                                E = 'E_SN'

                            for i in range(noValues,max_dom):
                                parent_grid_ratio = output_nml[namelist]['parent_grid_ratio'][i]
                                value = (output_nml[namelist][E][i-1] - 1) // parent_grid_ratio + 1 
                                output_nml[namelist][subnamelist] += [value]
                    else:
                        if not parent_start:
                            if subnamelist == 'parent_id':
                                output_nml[namelist][subnamelist] += list(np.arange(noValues,max_dom))
                            else:
                                output_nml[namelist][subnamelist] += [lastValue] * (max_dom - noValues)

    output_nml.end_comma = True
    output_nml.column_width = 100
    output_nml.indent = 1 
    output_nml.write(output_path, force=True)


if __name__ == '__main__':
    main()
