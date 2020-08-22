import pandas as pd
import matplotlib.pyplot as plt

client_id = '24c65298-cf22-4c73-ad01-7c6b2c009626'
#sourceID = "SN18703" # OSLO - BLINDERN TESTFELT
sourceID = "SN18700" # OSLO - BLINDERN
#sourceID = "SN18701" # OSLO - BLINDERN PLU
#sourceID = "SN76914" # ITASMOBAWS1
startdate = "2020-08-17T16:00:00.000Z"

df_YR = pd.read_csv('df_YR_'+sourceID+'_'+startdate+'.csv')
df_obs = pd.read_csv('df_obs_'+sourceID+'_'+startdate+'.csv')
df_wrf = pd.read_csv('df_wrf_'+sourceID+'_'+startdate+'.csv')
df_obs['referenceTime'] = pd.to_datetime(df_obs['referenceTime'])
df_YR['time'] = pd.to_datetime(df_YR['time'])
df_wrf['time'] = pd.to_datetime(df_wrf['time'])

# Plot data
fig, axs = plt.subplots(2)
lines = axs[0].plot(df_obs.referenceTime,df_obs.air_temperature,'r',df_YR.time,df_YR.air_temperature,'g',df_wrf.time,df_wrf.air_temperature,'b')
lines2 = axs[1].plot(df_obs.referenceTime,df_obs.wind_speed,'r',df_YR.time,df_YR.wind_speed,'g',df_wrf.time,df_wrf.wind_speed,'b')
axs[0].legend(('Observated data', 'YR forecast', 'WRF forecast'))
axs[1].legend(('Observated data', 'YR forecast', 'WRF forecast'))
axs[0].set(xlabel='Time', ylabel='Temperature [°C]')
axs[1].set(xlabel='Time', ylabel='Wind speed [m/s]')
axs[0].set_xlim(pd.to_datetime(startdate),pd.to_datetime('2020-08-21 00:00:00+00:00'))
axs[1].set_xlim(pd.to_datetime(startdate),pd.to_datetime('2020-08-21 00:00:00+00:00'))
plt.show()



















