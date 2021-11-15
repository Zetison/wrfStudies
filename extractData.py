# Script based on https://frost.met.no/python_example.html
# Libraries needed (pandas is not standard and must be installed in Python)
import requests
import pandas as pd
from netCDF4 import Dataset
import numpy as np
import wrf
from datetime import date,datetime
from os import path
import click
from os.path import expanduser
home = expanduser("~")
import json

# Insert your own client ID here
client_id = '24c65298-cf22-4c73-ad01-7c6b2c009626'

def getMetdata(endpoint, parameters, field):
    # Issue an HTTP GET request
    rObj = requests.get(endpoint, parameters, auth=(client_id,''))
    rObj = requests.get(rObj.url, auth=(client_id,''))
    # Extract JSON data
    json = rObj.json()
    
    # Check if the request worked, print out any errors
    if rObj.status_code == 200:
        return json[field]
        print('Data retrieved from frost.met.no!')
    else:
        print('Error! Returned status code %s' % rObj.status_code)
        print('Message: %s' % json['error']['message'])
        print('Reason: %s' % json['error']['reason'])

def getYRdata(endpoint, parameters, field):
    # Issue an HTTP GET request
    headers = {
            'User-Agent': 'jonv',
            'From': 'jonvegard.venas@sintef.no'  # This is another valid field
    }

    rObj = requests.get(endpoint, parameters, headers=headers)
    # Check if the request worked, print out any errors
    if rObj.status_code == 200:
        return rObj.json()[field]
        print('Data retrieved from frost.met.no!')
    else:
        print('Error! Returned status code %s' % rObj.status_code)
        print('url: %s' % rObj.url)
        
@click.command()
@click.option('--folder', default=home+'/results/forecastData/')
@click.option('--append/--no-append', default=True)
@click.option('--extract_yr/--no-extract_yr', default=False)
@click.option('--extract_wrf/--no-extract_wrf', default=False)
@click.option('--extract_met/--no-extract_met', default=False)
def main(folder,append,extract_yr,extract_wrf,extract_met): 
    #sourceIDlist = ["424242"]
    sourceIDlist = ['424242',  # Frankfurt airport
                    '2925507', # Fränkisch-Crumbach
                    '2926120', # Flörsheim
                    '2925533', # Frankfurt am Main
                    '2926300', # Fleisbach
                    '7290400', # Airport Frankfurt Main
                    '2926419', # Flacht
                    '2925550', # Frankenthal
                    '3220966', # Landkreis Darmstadt-Dieburg
                    '2925665', # Frammersbach
                    '7290401', # Niederrad
                    'SN18700', # OSLO - BLINDERN          
                    'SN6700',  # RV3 Svingen - Elverum
                    'SN71900', # Bessaker
                    'SN71990', # Buholmråsa fyr
                    'SN76914'] # ITASMOBAWS1 - Rikshospitalet i Oslo
    for sourceID in sourceIDlist:
        ########################################################################
        # Get coordinates for observation point (lon,lat)
        if sourceID[0:2] == 'SN': # Assume Norwegian station number format
            endpoint = 'https://frost.met.no/sources/v0.jsonld'
            parameters = {
                    'ids': sourceID,
                    }
            
            data_source = getMetdata(endpoint, parameters, 'data')
            masl = data_source[0]['masl']
            lon = data_source[0]['geometry']['coordinates'][0]
            lat = data_source[0]['geometry']['coordinates'][1]
        else:
            masl = np.NAN
            df = pd.read_json(home+'/kode/wrfStudies/city.list.json')
            lon = df[df.id == float(sourceID)].coord.item()['lon']
            lat = df[df.id == float(sourceID)].coord.item()['lat']
        
        ########################################################################
        # Get data from met file
        if extract_met:
            print('Not implemented')

                        
        ########################################################################
        # Get data from WRF file
        if extract_wrf:
            print('Extracting wrf data')
            i_domain = 10
            isOutside = True
            while isOutside:
                if i_domain < 0:
                    print('The observation station '+str(sourceID)+' is not inside the solution domain')
                    break

                i_domain -= 1
                try:
                    ncfile = Dataset('wrfout_d0'+str(i_domain)+'.nc')
                except:
                    continue

                xy = wrf.ll_to_xy(ncfile, lat, lon, as_int=False)

                if ncfile.MAP_PROJ_CHAR == 'Cylindrical Equidistant' and i_domain == 1:
                    xy[0] += 360/0.25
                
                #HGT = getvar(ncfile, "HGT")
                #maslg = HGT.interp(west_east=xy[0], south_north=xy[1])
                #lat_lon = wrf.xy_to_ll(ncfile,xy[0],xy[1])
                df_wrf = pd.DataFrame({'time': wrf.getvar(ncfile, 'Times', wrf.ALL_TIMES)})
                df_wrf['air_temperature'] = wrf.to_np(wrf.getvar(ncfile, 'T2', wrf.ALL_TIMES).interp(west_east=xy[0], south_north=xy[1]))-273.15
                if df_wrf.isnull().values.any():
                    continue
                else:
                    isOutside = False

                df_wrf['wind_speed'] = wrf.g_uvmet.get_uvmet10_wspd_wdir(ncfile, wrf.ALL_TIMES).interp(west_east=xy[0], south_north=xy[1])[0]
                df_wrf['wind_from_direction'] = wrf.g_uvmet.get_uvmet10_wspd_wdir(ncfile, wrf.ALL_TIMES).interp(west_east=xy[0], south_north=xy[1])[1]
                
                df_wrf['time'] = pd.to_datetime(df_wrf['time'])
                df_wrf = df_wrf.reset_index()
                
                if path.exists(folder+'df_wrf_'+sourceID+'.csv') and append:
                    df_wrf_hist = pd.read_csv(folder+'df_wrf_'+sourceID+'.csv')
                    if datetime.strptime(df_wrf_hist['time'].iloc[-1],"%Y-%m-%d %H:%M:%S") < df_wrf['time'].iloc[-1]:
                        df_wrf_hist = df_wrf_hist[df_wrf_hist['time'] <= str(df_wrf['time'][0])]
                        df_wrf_hist = df_wrf_hist.append(df_wrf)
                        df_wrf_hist.to_csv(folder+'df_wrf_'+sourceID+'.csv', index=False)
                else:
                    df_wrf.to_csv(folder+'df_wrf_'+sourceID+'.csv', index=False)

                print('Successfully extracted wrf data for ' + sourceID)

                        
        ########################################################################
        # Get YR forecast
        if extract_yr:
            endpoint = 'https://api.met.no/weatherapi/locationforecast/2.0/complete'
            endpoint = 'https://api.met.no/weatherapi/locationforecast/2.0/compact'
            parameters = {
                'lon': str(lon),
                'lat': str(lat),
            }
            if not np.isnan(masl):
                parameters['altitude'] = masl

            fields = ['time','air_temperature','wind_speed', 'wind_from_direction']
            data_YR = getYRdata(endpoint, parameters, 'properties')
            
            data_YR = data_YR['timeseries']
            
            df = pd.DataFrame()
            for i in range(len(data_YR)):
                row = pd.DataFrame({'time': [data_YR[i]['time']] })
                for j in range(1,len(fields)):
                    row[fields[j]] = data_YR[i]['data']['instant']['details'][fields[j]]
                df = df.append(row)
            
            df_YR = df[fields].copy()
            # Convert the time value to something Python understands
            df_YR['time'] = pd.to_datetime(df_YR['time']).dt.tz_convert(None)
            df_YR = df_YR.reset_index()
            
            if path.exists(folder+'df_YR_'+sourceID+'.csv') and append:
                df_YR_hist = pd.read_csv(folder+'df_YR_'+sourceID+'.csv')
                df_YR_hist = df_YR_hist[df_YR_hist['time'] <= str(df_YR['time'][0])]
                df_YR_hist = df_YR_hist.append(df_YR)
                df_YR_hist.to_csv(folder+'df_YR_'+sourceID+'.csv', index=False)
            else:
                df_YR.to_csv(folder+'df_YR_'+sourceID+'.csv', index=False)

            print('Successfully extracted YR data for ' + sourceID)
            
if __name__ == '__main__':
    main()
