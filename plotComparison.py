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
@click.option('--folder', default='/home/zetison/results/forecastData/')
def main(sourceid,folder):
	

	########################################################################
	# Get YR/wrf data
	df_YR = pd.read_csv(folder+'df_YR_'+sourceid+'.csv')
	df_wrf = pd.read_csv(folder+'df_wrf_'+sourceid+'.csv')
	df_YR['time'] = pd.to_datetime(df_YR['time'])
	df_wrf['time'] = pd.to_datetime(df_wrf['time'])
	
	########################################################################
	## Get observation data
	# Define endpoint and parameters
	if sourceid == 'SN76914':
		timeresolution = 'PT1H'
	else:
		timeresolution = 'PT10M'
	
	startdate = df_wrf['time'][0]
	enddate = df_wrf['time'].iloc[-1]
	endpoint = 'https://frost.met.no/observations/v0.jsonld'
	parameters = {
			'sources': sourceid,
			'referencetime': startdate.strftime("%Y-%m-%dT%H:%M:%S.000Z")+'/'+enddate.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
			'elements': 'air_temperature,wind_speed',
			'timeresolutions': timeresolution,
			'fields': 'value, referenceTime',
			'qualities': 0, # 0 = original value found to be good, 1 = original value suspicious (likely correct), ...
	}
	
	data = getYRdata(endpoint, parameters, 'data')
	
	fields = ['referenceTime','air_temperature','wind_speed']
	# This will return a Dataframe with all of the observations in a table format
	df = pd.DataFrame()
	for i in range(len(data)):
		row = pd.DataFrame(data[i])
		for j in range(1,len(fields)):
			row[fields[j]] = data[i]['observations'][j-1]['value']
		df = df.append(row)
	
	df = df.reset_index()
	
	# These additional columns will be kept
	df_obs = df[fields].copy()
	# Convert the time value to something Python understands
	df_obs['referenceTime'] = pd.to_datetime(df_obs['referenceTime']).dt.tz_convert(None)
	
	########################################################################
	# Plot data
	fig, axs = plt.subplots(2)
	lines = axs[0].plot(df_obs.referenceTime,df_obs.air_temperature,'r',df_YR.time,df_YR.air_temperature,'g',df_wrf.time,df_wrf.air_temperature,'b')
	lines2 = axs[1].plot(df_obs.referenceTime,df_obs.wind_speed,'r',df_YR.time,df_YR.wind_speed,'g',df_wrf.time,df_wrf.wind_speed,'b')
	axs[0].legend(('Observated data', 'YR forecast', 'WRF forecast'))
	axs[1].legend(('Observated data', 'YR forecast', 'WRF forecast'))
	axs[0].set(xlabel='Time', ylabel='Temperature [°C]')
	axs[1].set(xlabel='Time', ylabel='Wind speed [m/s]')
	axs[0].set_xlim(startdate,enddate)
	axs[1].set_xlim(startdate,enddate)
	plt.show()
	
if __name__ == '__main__':
    main()
	
	
	
	
