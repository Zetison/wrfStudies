from glob import glob
import pandas as pd
from os.path import expanduser
home = expanduser("~")
from datetime import datetime, timedelta
import click
@click.command()
@click.option('--sourceid', default='Frankfurt')
@click.option('--folder', default=home+'/results/forecastData/')
def main(sourceid,folder):
    WRFresultsFiles = glob(home+'/results/WRF/'+sourceid+'/20*/df_wrf_'+sourceid+'.csv')
    for f in WRFresultsFiles:
        dfSensor = pd.read_csv(f)
        mergedFile = folder+'df_wrf2_'+sourceid+'.csv'
        if isfile(mergedFile):
            dfSensor.to_csv(mergedFile,mode='a',index=False,header=False)
        else:
            dfSensor.to_csv(mergedFile,mode='a',index=False)


if __name__ == '__main__':
    main()

