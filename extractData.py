# Script based on https://frost.met.no/python_example.html
# Libraries needed (pandas is not standard and must be installed in Python)
import requests
import pandas as pd
from netCDF4 import Dataset
import numpy as np
import wrf
from datetime import date
from os import path
# Insert your own client ID here
client_id = '24c65298-cf22-4c73-ad01-7c6b2c009626'
today = date.today()
today = today.strftime("%Y-%m-%d")
startdate = today+"T00:00:00.000Z"

def getYRdata(endpoint, parameters, field):
	# Issue an HTTP GET request
	r = requests.get(endpoint, parameters, auth=(client_id,''))
	# Extract JSON data
	json = r.json()
	
	# Check if the request worked, print out any errors
	if r.status_code == 200:
	    return json[field]
	    print('Data retrieved from frost.met.no!')
	else:
	    print('Error! Returned status code %s' % r.status_code)
	    print('Message: %s' % json['error']['message'])
	    print('Reason: %s' % json['error']['reason'])


sourceIDlist = ["SN18700", # OSLO - BLINDERN          
						    "SN76914"] # ITASMOBAWS1

for sourceID in sourceIDlist:
	########################################################################
	# Get coordinates for observation point (lon,lat,masl)
	endpoint = 'https://frost.met.no/sources/v0.jsonld'
	parameters = {
			'ids': sourceID,
			}
	
	data_source = getYRdata(endpoint, parameters, 'data')
	masl = data_source[0]['masl']
	lon = data_source[0]['geometry']['coordinates'][0]
	lat = data_source[0]['geometry']['coordinates'][1]
	
	########################################################################
	# Get data from WRF file
	i_domain = 4
	ncfile = Dataset('wrfout_d0'+str(i_domain)+'.nc')
	xy = wrf.ll_to_xy(ncfile, lat, lon, as_int=False)
	if ncfile.MAP_PROJ_CHAR == 'Cylindrical Equidistant' and i_domain == 1:
		xy[0] += 360/0.25
	
	#HGT = getvar(ncfile, "HGT")
	#maslg = HGT.interp(west_east=xy[0], south_north=xy[1])
	#lat_lon = wrf.xy_to_ll(ncfile,xy[0],xy[1])
	fields = ['time','T','wind_speed']
	df_wrf = pd.DataFrame({'time': wrf.getvar(ncfile, fields[1], wrf.ALL_TIMES).Time})
	df_wrf['air_temperature'] = wrf.to_np(wrf.getvar(ncfile, 'tc', wrf.ALL_TIMES).interp(west_east=xy[0], south_north=xy[1], bottom_top=0))
	df_wrf['wind_speed'] = wrf.g_wind.get_destag_wspd(ncfile, wrf.ALL_TIMES).interp(west_east=xy[0], south_north=xy[1], bottom_top=0)
	
	df_wrf['time'] = pd.to_datetime(df_wrf['time'])
	
	########################################################################
	# Get YR forecast
	endpoint = 'https://api.met.no/weatherapi/locationforecast/2.0/complete'
	startdate = df_wrf['time'][0]
	enddate = df_wrf['time'].iloc[-1]
	parameters = {
	    'altitude': masl,
			'lon': str(lon),
	    'lat': str(lat),
	}
	fields = ['time','air_temperature','wind_speed']
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
	
	########################################################################
	# Append to historic data
	folder = '/home/zetison/results/forecastData/'
	if path.exists(folder+'df_wrf_'+sourceID+'.csv'):
		df_YR_hist = pd.read_csv(folder+'df_YR_'+sourceID+'.csv')
		df_wrf_hist = pd.read_csv(folder+'df_wrf_'+sourceID+'.csv')
		
		df_YR_hist = df_YR_hist[df_YR_hist['time'] <= str(startdate)]
		df_wrf_hist = df_wrf_hist[df_wrf_hist['time'] <= str(startdate)]
		
		df_YR_hist.append(df_YR)
		df_wrf_hist.append(df_wrf)
		
		
		df_YR_hist.to_csv(folder+'df_YR_'+sourceID+'.csv', index=False)
		df_wrf_hist.to_csv(folder+'df_wrf_'+sourceID+'.csv', index=False)
		
	else:
		df_YR.to_csv(folder+'df_YR_'+sourceID+'.csv', index=False)
		df_wrf.to_csv(folder+'df_wrf_'+sourceID+'.csv', index=False)
		
		
		
		
		
		
		
		
	
