from glob import glob
import pandas as pd
from os.path import expanduser, isfile
home = expanduser("~")
import numpy as np
from datetime import datetime, timedelta
import click
import copy
@click.command()
@click.option('--sourceidlist', default='424242')
@click.option('--folder', default=home+'/results/forecastData/')
@click.option('--CASE', 'CASE',default='Frankfurt')
def main(sourceidlist,folder,CASE):
    wrffolder=home+'/results/WRF/'+CASE+'/'
    if sourceidlist:
        sourceIDlist = sourceidlist.split(' ')
    else:
        #sourceIDlist = ["424242"]
        sourceIDlist = ['424242', #Frankfurt airport
                        '2925507', #Fränkisch-Crumbach
                        '2926120', #Flörsheim
                        '2925533', #Frankfurt am Main
                        '2926300', #Fleisbach
                        '7290400', #Airport Frankfurt Main
                        '2926419', #Flacht
                        '2925550', #Frankenthal
                        '3220966', #Landkreis Darmstadt-Dieburg
                        '2925665', #Frammersbach
                        '7290401'] #Niederrad
        #sourceIDlist = ["SN18700", # OSLO - BLINDERN          
        #                "SN6700",  # RV3 Svingen - Elverum
        #                "SN71900", # Bessaker
        #                "SN71990", # Buholmråsa fyr
        #                "SN76914", # ITASMOBAWS1 - Rikshospitalet i Oslo
        #                "424242"] # Frankfurt airport
    for sourceid in sourceIDlist:
        WRFresultsFiles = glob(wrffolder+'20*/df_wrf_'+sourceid+'.csv')
        df = pd.DataFrame()
        for f in WRFresultsFiles:
            row = pd.read_csv(f)
            df = pd.concat([df,row])
            rowNan = copy.deepcopy(df.iloc[-1])
            for col in df.columns:
                if not col == 'time' and not col == 'index':
                    rowNan[col] = np.NaN
            df = pd.concat([df,rowNan], ignore_index=True)

        df['time'] = pd.to_datetime(df['time'])

        df = df.reset_index(drop=True)
        df.drop(df.tail(1).index,inplace=True)
        mergedFile = folder+'df_wrf_'+sourceid+'.csv'
        df.to_csv(mergedFile,index=False)


if __name__ == '__main__':
    main()

