# Script based on https://frost.met.no/python_example.html
# Libraries needed (pandas is not standard and must be installed in Python)
import requests
import pandas as pd
import matplotlib.pyplot as plt
# Insert your own client ID here
client_id = '24c65298-cf22-4c73-ad01-7c6b2c009626'
#sourceID = "SN18703" # OSLO - BLINDERN TESTFELT
#sourceID = "SN18700" # OSLO - BLINDERN
#sourceID = "SN18701" # OSLO - BLINDERN PLU
sourceID = "SN76914" # ITASMOBAWS1
startdate = "2020-08-17T16:00:00.000Z"

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

endpoint = 'https://frost.met.no/sources/v0.jsonld'
parameters = {
		'ids': sourceID,
		}

data_source = getYRdata(endpoint, parameters, 'data')
#print(df[0].masl)

# Define endpoint and parameters
endpoint = 'https://frost.met.no/observations/v0.jsonld'
parameters = {
    'sources': sourceID,
		'referencetime': startdate+'/2021-08-14T16:00:00.000Z',
    'elements': 'air_temperature,wind_speed',
		'timeresolutions': 'PT1H',
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
df2 = df[fields].copy()
# Convert the time value to something Python understands
df2['referenceTime'] = pd.to_datetime(df2['referenceTime'])

parameters['elements'] = 'air_temperature,wind_speed'
data = getYRdata(endpoint, parameters, 'data')
# This will return a Dataframe with all of the observations in a table format


endpoint = 'https://api.met.no/weatherapi/locationforecast/2.0/complete'
parameters = {
    'altitude': data_source[0]['masl'],
		'lon': str(data_source[0]['geometry']['coordinates'][0]),
    'lat': str(data_source[0]['geometry']['coordinates'][1]),
}
fields = ['time','air_temperature','wind_speed']
data_YR = getYRdata(endpoint, parameters, 'properties')

data_YR = data_YR['timeseries']

df = pd.DataFrame()
for i in range(len(data_YR)):
	row = pd.DataFrame(data_YR[i])
	for j in range(1,len(fields)):
		row[fields[j]] = data_YR[i]['data']['instant']['details'][fields[j]]
	df = df.append(row)

df_YR = df[fields].copy()
# Convert the time value to something Python understands
df_YR['time'] = pd.to_datetime(df_YR['time'])
fig, axs = plt.subplots(2)
lines = axs[0].plot(df2.referenceTime,df2.air_temperature,'r',df_YR.time,df_YR.air_temperature,'b')
lines2 = axs[1].plot(df2.referenceTime,df2.wind_speed,'r',df_YR.time,df_YR.wind_speed,'b')
axs[0].legend(('Observated data', 'YR forecast'))
axs[1].legend(('Observated data', 'YR forecast'))
axs[0].set(xlabel='Time', ylabel='Temperature [°C]')
axs[1].set(xlabel='Time', ylabel='Wind speed [m/s]')
axs[0].set_xlim(pd.to_datetime(startdate),pd.to_datetime('2020-08-21 00:00:00+00:00'))
axs[1].set_xlim(pd.to_datetime(startdate),pd.to_datetime('2020-08-21 00:00:00+00:00'))
plt.show()
