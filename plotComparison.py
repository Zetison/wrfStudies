import requests
import pandas as pd
from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import click

client_id = '24c65298-cf22-4c73-ad01-7c6b2c009626'
#sourceid = "SN18700" # OSLO - BLINDERN
#sourceid = "SN76914" # ITASMOBAWS1 - Rikshospitalet in Oslo

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


@click.command()
@click.option('--sourceid', default='SN18700')
@click.option('--timeresolution', default='PT1H')
@click.option('--folder', default='/home/zetison/results/forecastData/')
def main(sourceid,folder,timeresolution):
	

	########################################################################
	# Get YR/wrf data
	try:
		df_YR = pd.read_csv(folder+'df_YR_'+sourceid+'.csv')
		df_YR['time'] = pd.to_datetime(df_YR['time'])
		yrDataFound = True
	except:
		yrDataFound = False
	
	try:
		df_wrf = pd.read_csv(folder+'df_wrf_'+sourceid+'.csv')
		df_wrf['time'] = pd.to_datetime(df_wrf['time'])
		wrfDataFound = True
	except:
		wrfDataFound = False
	
	########################################################################
	## Get observation data
	# Define endpoint and parameters
	try:	
		startdate = df_wrf['time'][0]
		enddate = df_wrf['time'].iloc[-1]
	except:
		startdate = '2020-09-22 00:00:00'
		enddate = '2020-09-29 00:00:00'

	if sourceid[0:2] == 'SN':
		endpoint = 'https://frost.met.no/observations/v0.jsonld'
		parameters = {
				'sources': sourceid,
				'referencetime': startdate.strftime("%Y-%m-%dT%H:%M:%S.000Z")+'/'+enddate.strftime("%Y-%m-%dT%H:%M:01.000Z"),
				'elements': 'air_temperature,wind_speed,wind_from_direction',
				'timeresolutions': timeresolution,
				'fields': 'value, referenceTime',
				'qualities': 0,
		}
		
		data = getYRdata(endpoint, parameters, 'data')
		
		fields = ['time','air_temperature','wind_speed', 'wind_from_direction']
		# This will return a Dataframe with all of the observations in a table format
		df = pd.DataFrame()
		for i in range(len(data)):
			row = pd.DataFrame({'time': [data[i]['referenceTime']] })
			noFields = min(len(fields),len(data[i]['observations'])+1)
			for j in range(1,noFields):
				row[fields[j]] = data[i]['observations'][j-1]['value']
			df = df.append(row)
		
		df = df.reset_index()
		
		# These additional columns will be kept
		df_obs = df[fields].copy()
		# Convert the time value to something Python understands
		df_obs['time'] = pd.to_datetime(df_obs['time']).dt.tz_convert(None)
	elif sourceid == 'Frankfurt':
		df_obs = pd.read_csv(folder+'df_meteoblue_'+sourceid+'.csv', skiprows=9)
		df_obs['time'] = pd.to_datetime(df_obs['timestamp'])
		df_obs['air_temperature'] = df_obs['Airport Frankfurt Main Temperature [2 m elevation corrected]']
		df_obs['wind_speed'] = df_obs['Airport Frankfurt Main Wind Speed [10 m]']
		df_obs['wind_from_direction'] = df_obs['Airport Frankfurt Main Wind Direction [10 m]']


	########################################################################
	# Plot data
	fig, axs = plt.subplots(3, sharex=True)
	if yrDataFound:
		lines = axs[0].plot(df_YR.time,df_YR.air_temperature,'g', label = 'MetCoOp forecast')
		lines2 = axs[1].plot(df_YR.time,df_YR.wind_speed,'g', label = 'MetCoOp forecast')
		lines3 = axs[2].plot(df_YR.time,df_YR.wind_from_direction,'g', label = 'MetCoOp forecast')

	if wrfDataFound:	
		lines = axs[0].plot(df_wrf.time,df_wrf.air_temperature,'b', label = 'WRF forecast')
		lines2 = axs[1].plot(df_wrf.time,df_wrf.wind_speed,'b', label = 'WRF forecast')

	lines = axs[0].plot(df_obs.time,df_obs.air_temperature,'r', label = 'Observation data')
	lines2 = axs[1].plot(df_obs.time,df_obs.wind_speed,'r', label = 'Observation data')
	lines3 = axs[2].plot(df_obs.time,df_obs.wind_from_direction,'r', label = 'Observation data')
	axs[0].legend()
	axs[1].legend()
	axs[2].legend()
	axs[0].set(xlabel='Time', ylabel='Temperature [°C]')
	axs[1].set(xlabel='Time', ylabel='Wind speed [m/s]')
	axs[2].set(xlabel='Time', ylabel='Wind from direction [degrees]')
	axs[0].set_xlim(startdate,enddate)
	axs[1].set_xlim(startdate,enddate)
	axs[2].set_xlim(startdate,enddate)
	plt.show()
	
if __name__ == '__main__':
    main()
	
	
	
	
