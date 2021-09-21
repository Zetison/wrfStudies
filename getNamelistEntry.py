import f90nml
import click
from os.path import expanduser
home = expanduser("~")
@click.command()
@click.argument('inputnamelist', type=click.File('r'), default=home+'/kode/wrfStudies/studies/debug.nml')
@click.option('--namelist', default='share')
@click.option('--subnamelist', default='max_dom')
def main(inputnamelist,namelist,subnamelist):
    nml = f90nml.read(inputnamelist)
    print(nml[namelist][subnamelist])
    return 0

if __name__ == '__main__':
    main()
