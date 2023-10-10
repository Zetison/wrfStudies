import requests
import pandas as pd
from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import click
from os.path import expanduser
home = expanduser("~")
import sys
sys.path.insert(1, home+'/kode/ham_windsim_2021/Frankfurt/data_prep')
from read_wrf_data import string_to_time

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
@click.option('--CASE', 'CASE', default='Trondheim')
@click.option('--sourceid', default='SN68860')
@click.option('--timeresolution', default='PT1H')
@click.option('--plotdata/--no-plotdata', default=True)
@click.option('--ploterror/--no-ploterror', default=True)
@click.option('--folder', default=home+'/results/forecastData/')
@click.option('--meteobluefile', default=home+'/results/WRF/Frankfurt/meteoblue/AirportFrankfurtMain.csv')
@click.option('--startdate', default='') # in the format '2020-09-29 00:00:00'
@click.option('--enddate', default='')
@click.option('--filetype', default='png', help='File type (png,pdf,...) for exporting graphics')
def main(CASE,sourceid,timeresolution,plotdata,ploterror,folder,meteobluefile,startdate,enddate,filetype):
    

    ########################################################################
    # Get YR/OMW/wrf data
    try:
        df_DWD = pd.read_csv(folder+'df_dwd_'+sourceid+'.csv')
        df_DWD['time'] = pd.to_datetime(df_DWD['time'])
        print('Observation data found')
        dwdDataFound = True
    except:
        dwdDataFound = False
    
    try:
        df_open_meteo = pd.read_csv(folder+'df_open_meteo_'+sourceid+'.csv')
        df_open_meteo['time'] = pd.to_datetime(df_open_meteo['time'])
        print('Observation data found')
        open_meteoDataFound = True
    except:
        open_meteoDataFound = False
    
    try:
        df_YR = pd.read_csv(folder+'df_YR_'+sourceid+'.csv')
        df_YR['time'] = pd.to_datetime(df_YR['time'])
        yrDataFound = True
        print('YR data found')
    except:
        yrDataFound = False
    
    try:
        df_wrf = pd.read_csv(folder+'df_wrf_'+sourceid+'.csv')
        df_wrf['time'] = pd.to_datetime(df_wrf['time'])
        wrfDataFound = True
        print('wrf data found')
    except:
        wrfDataFound = False
    
    try:
        df_wrf2 = pd.read_csv(folder+'df_wrf2_'+sourceid+'.csv')
        df_wrf2['time'] = pd.to_datetime(df_wrf2['time'])
        wrf2DataFound = True
        print('wrf2 data found')
    except:
        wrf2DataFound = False
    
    ########################################################################
    ## Get observation data
    # Define endpoint and parameters
    if not startdate:
        if wrfDataFound:
            startdate = df_wrf['time'].min()
        elif wrf2DataFound:
            startdate = df_wrf2['time'].min()
        elif open_meteoDataFound:
            startdate = df_open_meteo['time'].min()
        else:
            startdate = df_YR['time'].min()
    else:
        startdate = pd.to_datetime(startdate)
    
    if not enddate:
        if wrfDataFound:
            enddate = df_wrf['time'].max()
        elif wrf2DataFound:
            enddate = df_wrf2['time'].max()
        elif open_meteoDataFound:
            enddate = df_open_meteo['time'].max()
        else:
            enddate = df_YR['time'].max()
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
            df = pd.concat([df,row])
        
        df = df.reset_index()
        
        # These additional columns will be kept
        df_obs = df[fields].copy()
        # Convert the time value to something Python understands
        df_obs['time'] = pd.to_datetime(df_obs['time']).dt.tz_localize(None)
    elif sourceid == '424242':
        df_obs = pd.read_csv(meteobluefile, skiprows=9)
        df_obs['time'] = pd.to_datetime(df_obs['timestamp'])
        df_obs['air_temperature'] = df_obs['Airport Frankfurt Main Temperature [2 m elevation corrected]']
        df_obs['wind_speed'] = df_obs['Airport Frankfurt Main Wind Speed [10 m]']
        df_obs['wind_from_direction'] = df_obs['Airport Frankfurt Main Wind Direction [10 m]']
    else:
        try:
            df_obs = pd.read_csv(home+'/results/forecastData/df_OWM_'+sourceid+'.csv')
            df_obs['time'] = pd.to_datetime(df_obs['time']) + timedelta(seconds=df_obs.timezone.to_numpy()[0])
            df_obs['air_temperature'] = df_obs['temp']
            df_obs['wind_speed'] = df_obs['speed']
            df_obs['wind_from_direction'] = df_obs['deg']
        except:
            df_obs = pd.read_csv(home+'/results/forecastData/df_obs_'+sourceid+'.csv')
            df_obs['time'] = pd.to_datetime(df_obs['time'])


    df_obs = df_obs[df_obs.time >= startdate]
    df_obs = df_obs[df_obs.time <= enddate]
    if dwdDataFound:
        df_DWD = df_DWD[df_DWD.time >= startdate]
        df_DWD = df_DWD[df_DWD.time <= enddate]
        if df_DWD.empty:
            dwdDataFound = False

    if open_meteoDataFound:
        df_open_meteo = df_open_meteo[df_open_meteo.time >= startdate]
        df_open_meteo = df_open_meteo[df_open_meteo.time <= enddate]
        if df_open_meteo.empty:
            open_meteoDataFound = False

    if yrDataFound:
        df_YR = df_YR[df_YR.time >= startdate]
        df_YR = df_YR[df_YR.time <= enddate]
        if df_YR.empty:
            yrDataFound = False

    if wrfDataFound:
        df_wrf = df_wrf[df_wrf.time >= startdate]
        df_wrf = df_wrf[df_wrf.time <= enddate]

    if wrf2DataFound:
        df_wrf2 = df_wrf2[df_wrf2.time >= startdate]
        df_wrf2 = df_wrf2[df_wrf2.time <= enddate]

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
    if wrfDataFound:
        df_wrf['windDirX'] = np.sin(np.radians(df_wrf['wind_from_direction']))
        df_wrf['windDirY'] = np.cos(np.radians(df_wrf['wind_from_direction']))

    if wrf2DataFound:
        df_wrf2['windDirX'] = np.sin(np.radians(df_wrf2['wind_from_direction']))
        df_wrf2['windDirY'] = np.cos(np.radians(df_wrf2['wind_from_direction']))

    if dwdDataFound:
        df_DWD['windDirX'] = np.sin(np.radians(df_DWD['wind_from_direction']))
        df_DWD['windDirY'] = np.cos(np.radians(df_DWD['wind_from_direction']))

    if open_meteoDataFound:
        df_open_meteo['windDirX'] = np.sin(np.radians(df_open_meteo['wind_from_direction']))
        df_open_meteo['windDirY'] = np.cos(np.radians(df_open_meteo['wind_from_direction']))

    if yrDataFound:
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
                if dwdDataFound:
                    axs[i,j].plot(df_DWD.time.to_numpy(),df_DWD[fields[i,j]].to_numpy(),'o', label = 'DWD')

                if open_meteoDataFound:
                    axs[i,j].plot(df_open_meteo.time.to_numpy(),df_open_meteo[fields[i,j]].to_numpy(),color='m', label = 'Open-Meteo')

                if yrDataFound:
                    axs[i,j].plot(df_YR.time.to_numpy(),df_YR[fields[i,j]].to_numpy(),'g', label = 'MetCoOp forecast')
        
                if wrfDataFound:    
                    axs[i,j].plot(df_wrf.time.to_numpy(),df_wrf[fields[i,j]].to_numpy(),'b', label = 'WRF forecast')
                if wrf2DataFound:    
                    axs[i,j].plot(df_wrf2.time.to_numpy(),df_wrf2[fields[i,j]].to_numpy(),'c', label = 'WRF highres forecast')
        
                axs[i,j].plot(df_obs.time.to_numpy(),df_obs[fields[i,j]].to_numpy(),'r', label = 'Observation data')
    
                axs[i,j].legend()
                axs[i,j].set(xlabel='Time', ylabel=ylabels[i,j])
                axs[i,j].set_xlim(startdate,enddate)

        plt.show()
        fig.savefig(home+'/results/WRF/'+CASE+'/Comparison.'+filetype)


    ########################################################################
    # Plot error
    if ploterror:
        fig, axs = plt.subplots(2,2, sharex=sharex)
        mng = plt.get_current_fig_manager()
        #mng.resize(*mng.window.maxsize())
        mng.window.showMaximized()
        fig.suptitle('Weather forecast comparison between MetCoOp and WRF simulations at '+sourceid)
        df_DWD_i = df_obs[fields[0,0]].copy() 
        df_open_meteo_i = df_obs[fields[0,0]].copy() 
        df_YR_i = df_obs[fields[0,0]].copy() 
        df_wrf_i = df_obs[fields[0,0]].copy() 
        df_wrf2_i = df_obs[fields[0,0]].copy() 
        ylabels = np.array([['Relative temperature error [%]', 'Relative wind speed error [%]'],
                               ['Relative longitudinal wind direction error [%]', 'Relative latitudinal wind direction error [%]']])
        
        order = 2 # order of global norm
        for i in range(0,fields.shape[0]):
            for j in range(0,fields.shape[1]):
                df_obs[fields[i,j]] = np.array(df_obs[fields[i,j]])
                idx = np.isnan(np.array(df_obs[fields[i,j]]).astype(float)) == False
                title = 'Relative $l_'+str(order)+'$-errors: '
                if dwdDataFound:
                    df_DWD_i[fields[i,j]] = np.interp(np.array(df_obs.time).astype(float),np.array(df_DWD.time).astype(float),df_DWD[fields[i,j]])
                    diff_DWD = df_DWD_i[fields[i,j]]-df_obs[fields[i,j]]
                    dwd_error = 100*np.linalg.norm(diff_DWD[idx], ord=order)/np.linalg.norm(df_obs[fields[i,j]][idx], ord=order)
                    dwd_errors = 100*np.abs(diff_DWD)/max(np.abs(df_obs[fields[i,j]]))
                    axs[i,j].semilogy(df_obs.time.to_numpy(),dwd_errors.to_numpy(),'o', label = 'DWD')
                    title += 'DWD: '+'{0:.2f}'.format(dwd_error)+'%, '

                if open_meteoDataFound:
                    df_open_meteo_i[fields[i,j]] = np.interp(np.array(df_obs.time).astype(float),np.array(df_open_meteo.time).astype(float),df_open_meteo[fields[i,j]])
                    diff_open_meteo = df_open_meteo_i[fields[i,j]]-df_obs[fields[i,j]]
                    open_meteo_error = 100*np.linalg.norm(diff_open_meteo[idx], ord=order)/np.linalg.norm(df_obs[fields[i,j]][idx], ord=order)
                    open_meteo_errors = 100*np.abs(diff_open_meteo)/max(np.abs(df_open_meteo[fields[i,j]]))
                    axs[i,j].semilogy(df_obs.time.to_numpy(),open_meteo_errors.to_numpy(),color='m', label = 'Open-Meteo')
                    title += 'Open-Meteo: '+'{0:.2f}'.format(open_meteo_error)+'%, '

                if yrDataFound:
                    df_YR_i[fields[i,j]] = np.interp(np.array(df_obs.time).astype(float),np.array(df_YR.time).astype(float),df_YR[fields[i,j]])
                    diff_YR = df_YR_i[fields[i,j]]-df_obs[fields[i,j]]
                    yr_error = 100*np.linalg.norm(diff_YR[idx], ord=order)/np.linalg.norm(df_obs[fields[i,j]][idx], ord=order)
                    yr_errors = 100*np.abs(diff_YR)/max(np.abs(df_obs[fields[i,j]]))
                    axs[i,j].semilogy(df_obs.time.to_numpy(),yr_errors.to_numpy(),'g', label = 'MetCoOp')
                    title += 'MetCoOp: '+'{0:.2f}'.format(yr_error)+'%, '

                if wrfDataFound:
                    df_wrf_i[fields[i,j]] = np.interp(np.array(df_obs.time).astype(float),np.array(df_wrf.time).astype(float),df_wrf[fields[i,j]])
                    diff_wrf_i = df_wrf_i[fields[i,j]]-df_obs[fields[i,j]]
                    wrf_error = 100*np.linalg.norm(diff_wrf_i[idx], ord=order)/np.linalg.norm(df_obs[fields[i,j]][idx], ord=order)
                    wrf_errors = 100*np.abs(diff_wrf_i)/max(np.abs(df_obs[fields[i,j]]))
                    axs[i,j].semilogy(df_obs.time.to_numpy(),wrf_errors.to_numpy(),'b', label = 'WRF')
                    title += 'WRF: '+'{0:.2f}'.format(wrf_error)+'%, '

                if wrf2DataFound:
                    df_wrf2_i[fields[i,j]] = np.interp(np.array(df_obs.time).astype(float),np.array(df_wrf2.time).astype(float),df_wrf2[fields[i,j]])
                    diff_wrf2_i = df_wrf2_i[fields[i,j]]-df_obs[fields[i,j]]
                    wrf2_error = 100*np.linalg.norm(diff_wrf2_i[idx], ord=order)/np.linalg.norm(df_obs[fields[i,j]][idx], ord=order)
                    wrf2_errors = 100*np.abs(diff_wrf2_i)/max(np.abs(df_obs[fields[i,j]]))
                    axs[i,j].semilogy(df_obs.time.to_numpy(),wrf2_errors.to_numpy(),'c', label = 'WRF highres')
                    title += 'WRF2: '+'{0:.2f}'.format(wrf2_error)+'%, '


                axs[i,j].set_title(title)
    
                axs[i,j].legend()
                axs[i,j].set_xlim(startdate,enddate)
                axs[i,j].set(xlabel='Time', ylabel=ylabels[i,j])

        plt.show()
        fig.savefig(home+'/results/WRF/'+CASE+'/Comparison_error.'+filetype)

    
if __name__ == '__main__':
    main()
