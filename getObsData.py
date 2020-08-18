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
start_date = "2020-08-13T16:00:00.000Z"

def getYRdata(endpoint, parameters, field):
	# Issue an HTTP GET request
	r = requests.get(endpoint, parameters, auth=(client_id,''))
	# Extract JSON data
	json = r.json()
	
	# Check if the request worked, print out any errors
	if r.status_code == 200:
	    data = json[field]
	    print('Data retrieved from frost.met.no!')
	else:
	    print('Error! Returned status code %s' % r.status_code)
	    print('Message: %s' % json['error']['message'])
	    print('Reason: %s' % json['error']['reason'])
	
	return data

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
    'elements': 'air_temperature',
		'referencetime': '2020-08-13T16:00:00.000Z/2021-08-14T16:00:00.000Z',
		'timeresolutions': 'PT10M',
		'qualities': 0, # 0 = original value found to be good, 1 = original value suspicious (likely correct), ...
}
fields = ['referenceTime','value']

data = getYRdata(endpoint, parameters, 'data')

# This will return a Dataframe with all of the observations in a table format
df = pd.DataFrame()
for i in range(len(data)):
	row = pd.DataFrame(data[i])
	for j in range(1,len(fields)):
		row[fields[j]] = data[i]['observations'][fields[j]]
	df = df.append(row)

df = df.reset_index()

# These additional columns will be kept
#columns = ['sourceId','referenceTime','elementId','value','unit','timeOffset']
df2 = df[fields].copy()
# Convert the time value to something Python understands
df2['referenceTime'] = pd.to_datetime(df2['referenceTime'])

parameters['elements'] = 'wind_speed'
data = getYRdata(endpoint, parameters, 'data')
# This will return a Dataframe with all of the observations in a table format
df_ws = pd.DataFrame()
for i in range(len(data)):
	row = pd.DataFrame(data[i])
	for j in range(1,len(fields)):
		row[fields[j]] = data[i]['observations'][fields[j]]
	df_ws = df_ws.append(row)

df_ws = df_ws.reset_index()
df2['wind_speed'] = df_ws['wind_speed'].copy()


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
lines = axs[0].plot(df2.referenceTime,df2.value,'r',df_YR.time,df_YR.air_temperature,'b')
lines2 = axs[1].plot(df2.referenceTime,df2.value,'r',df_YR.time,df_YR.wind_speed,'b')
axs[0].legend(('Observated data', 'YR forecast'))
axs[1].legend(('Observated data', 'YR forecast'))
axs[0].set(xlabel='Time', ylabel='Temperature')
axs[1].set(xlabel='Time', ylabel='Wind speed')


plt.show()
