from glob import glob
import pandas as pd
from os.path import expanduser, isfile
home = expanduser("~")
from datetime import datetime, timedelta
import click
@click.command()
@click.option('--sourceid', default='Frankfurt')
@click.option('--folder', default=home+'/results/forecastData/')
def main(sourceid,folder):
    WRFresultsFiles = glob(home+'/results/WRF/'+sourceid+'/20*_highres/df_wrf_'+sourceid+'.csv')
    df = pd.DataFrame()
    for f in WRFresultsFiles:
        row = pd.read_csv(f)
        df = df.append(row)

    df['time'] = pd.to_datetime(df['time'])

    df = df.sort_values(by='time')
    df = df.reset_index()
    mergedFile = folder+'df_wrf2_'+sourceid+'.csv'
    df.to_csv(mergedFile,index=False)


if __name__ == '__main__':
    main()

