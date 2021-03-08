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
@click.option('--sourceid', default='Frankfurt')
@click.option('--timeresolution', default='PT1H')
@click.option('--plotdata/--no-plotdata', default=True)
@click.option('--ploterror/--no-ploterror', default=False)
@click.option('--folder', default='/home/zetison/results/forecastData/')
@click.option('--startdate', default='') # in the format '2020-09-29 00:00:00'
@click.option('--enddate', default='')
def main(sourceid,folder,timeresolution,plotdata,ploterror,startdate,enddate):
    

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
    if not startdate:
        try:
            startdate = df_wrf['time'][0]
        except:
            startdate = df_YR['time'][0]
    else:
        startdate = pd.to_datetime(startdate)
    
    if not enddate:
        try:
            enddate = df_wrf['time'].iloc[-1]
        except:
            enddate = df_YR['time'][0]
    else:
        enddate = pd.to_datetime(enddate)

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
        df_obs['time'] = pd.to_datetime(df_obs['time'])
    elif sourceid == 'Frankfurt':
        df_obs = pd.read_csv(folder+'df_meteoblue_'+sourceid+'.csv', skiprows=9)
        df_obs['time'] = pd.to_datetime(df_obs['timestamp'])
        df_obs['air_temperature'] = df_obs['Airport Frankfurt Main Temperature [2 m elevation corrected]']
        df_obs['wind_speed'] = df_obs['Airport Frankfurt Main Wind Speed [10 m]']
        df_obs['wind_from_direction'] = df_obs['Airport Frankfurt Main Wind Direction [10 m]']

    df_obs = df_obs[df_obs.time >= startdate]
    df_obs = df_obs[df_obs.time <= enddate]
    if yrDataFound:
        df_YR = df_YR[df_YR.time >= startdate]
        df_YR = df_YR[df_YR.time <= enddate]
    if wrfDataFound:
        df_wrf = df_wrf[df_wrf.time >= startdate]
        df_wrf = df_wrf[df_wrf.time <= enddate]

    ########################################################################
    # Plot data
    sharex = True
    #fields = ['air_temperature','wind_speed', 'wind_from_direction']
    fields = np.array([['air_temperature','wind_speed'],
                           ['windDirX', 'windDirY']])
    ylabels = np.array([['Temperature [°C]', 'Wind speed [m/s]'], 
                            ['Wind direction - X','Wind direction - Y']])
    df_obs['windDirX'] = np.sin(np.radians(df_obs['wind_from_direction']))
    df_obs['windDirY'] = np.cos(np.radians(df_obs['wind_from_direction']))
    df_wrf['windDirX'] = np.sin(np.radians(df_wrf['wind_from_direction']))
    df_wrf['windDirY'] = np.cos(np.radians(df_wrf['wind_from_direction']))
    df_YR['windDirX'] = np.sin(np.radians(df_YR['wind_from_direction']))
    df_YR['windDirY'] = np.cos(np.radians(df_YR['wind_from_direction']))
    if plotdata:
        fig, axs = plt.subplots(2,2, sharex=sharex)
        mng = plt.get_current_fig_manager()
        #mng.resize(*mng.window.maxsize())
        mng.window.showMaximized()
        fig.suptitle('Weather forecast comparison between MetCoOp and WRF simulations at '+sourceid)
        for i in range(0,fields.shape[0]):
            for j in range(0,fields.shape[1]):
                if yrDataFound:
                    axs[i,j].plot(df_YR.time.to_numpy(),df_YR[fields[i,j]].to_numpy(),'g', label = 'MetCoOp forecast')
        
                if wrfDataFound:    
                    axs[i,j].plot(df_wrf.time.to_numpy(),df_wrf[fields[i,j]].to_numpy(),'b', label = 'WRF forecast')
        
                axs[i,j].plot(df_obs.time.to_numpy(),df_obs[fields[i,j]].to_numpy(),'r', label = 'Observation data')
    
                axs[i,j].legend()
                axs[i,j].set(xlabel='Time', ylabel=ylabels[i,j])
                axs[i,j].set_xlim(startdate,enddate)

        plt.show()
        fig.savefig(sourceid+'.png')


    ########################################################################
    # Plot error
    if ploterror:
        fig, axs = plt.subplots(2,2, sharex=sharex)
        mng = plt.get_current_fig_manager()
        #mng.resize(*mng.window.maxsize())
        mng.window.showMaximized()
        fig.suptitle('Weather forecast comparison between MetCoOp and WRF simulations at '+sourceid)
        df_YR_i = df_obs[fields[0,0]].copy() 
        df_wrf_i = df_obs[fields[0,0]].copy() 
        ylabels = np.array([['Relative temperature error [%]', 'Relative wind speed error [%]'],
                               ['Relative longitudinal wind direction error [%]', 'Relative latitudinal wind direction error [%]']])
        
        order = 2 # order of global norm
        for i in range(0,fields.shape[0]):
            for j in range(0,fields.shape[1]):
                df_YR_i[fields[i,j]] = np.interp(np.array(df_obs.time).astype(float),np.array(df_YR.time).astype(float),df_YR[fields[i,j]])
                df_wrf_i[fields[i,j]] = np.interp(np.array(df_obs.time).astype(float),np.array(df_wrf.time).astype(float),df_wrf[fields[i,j]])
                df_obs[fields[i,j]] = np.array(df_obs[fields[i,j]])

                diff_YR = df_YR_i[fields[i,j]]-df_obs[fields[i,j]]
                diff_wrf_i = df_wrf_i[fields[i,j]]-df_obs[fields[i,j]]
                if fields[i,j] == 'wind_from_direction':
                    phi_YR = np.mod(np.abs(diff_YR),360)
                    phi_wrf = np.mod(np.abs(diff_wrf_i),360)
                    diff_YR[phi_YR > 180] = 360 - phi_YR
                    diff_YR[phi_YR <= 180] = phi_YR
                    diff_wrf_i[phi_wrf > 180] = 360 - phi_wrf
                    diff_wrf_i[phi_wrf <= 180] = phi_wrf
    
                idx = np.isnan(np.array(df_obs[fields[i,j]]).astype(float)) == False
                yr_error = 100*np.linalg.norm(diff_YR[idx], ord=order)/np.linalg.norm(df_obs[fields[i,j]][idx], ord=order)
                wrf_error = 100*np.linalg.norm(diff_wrf_i[idx], ord=order)/np.linalg.norm(df_obs[fields[i,j]][idx], ord=order)
                axs[i,j].set_title(r'Relative $l_'+str(order)+'$-errors: MetCoOp: '+'{0:.1f}'.format(yr_error)+'%, WRF: '+'{0:.1f}'.format(wrf_error)+'%')
                yr_errors = 100*np.abs(diff_YR)/max(np.abs(df_obs[fields[i,j]]))
                wrf_errors = 100*np.abs(diff_wrf_i)/max(np.abs(df_obs[fields[i,j]]))
                axs[i,j].semilogy(df_obs.time.to_numpy(),yr_errors.to_numpy(),'g', label = 'MetCoOp')
                axs[i,j].semilogy(df_obs.time.to_numpy(),wrf_errors.to_numpy(),'b', label = 'WRF')
    
                axs[i,j].legend()
                axs[i,j].set_xlim(startdate,enddate)
                axs[i,j].set(xlabel='Time', ylabel=ylabels[i,j])

        plt.show()
        fig.savefig(sourceid+'_error.png')

    
if __name__ == '__main__':
    main()
    
    
    
    
