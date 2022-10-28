from bs4 import BeautifulSoup
import click
import os
@click.command()
@click.option('--filestr', type=str, default='wrfout_d05')
@click.option('--timeshift', type=int, default=0)

def main(filestr,timeshift): 
    directory = os.getcwd()
    counter = 1
    for filename in sorted(os.listdir(directory)):
        split_tup = os.path.splitext(filename)
        if (not split_tup[1] == '.pvd') or filename == filestr+'.pvd':
            continue
        if not filestr in filename:
            continue

        with open(os.path.join(directory, filename), 'r') as f:
            data = f.read()

        bs_data = BeautifulSoup(data,'xml')
        if counter == 1:
            for dataSet in bs_data.find_all('Collection')[0].find_all('DataSet'):
                dataSet['timestep'] = str(round(float(dataSet['timestep'])+timeshift))

            bs_dataMerged = bs_data.__copy__()
        else:
            for dataSet in bs_data.find_all('Collection')[0].find_all('DataSet'):
                dataSet['timestep'] = str(round(float(dataSet['timestep'])+timeshift))
                bs_dataMerged.find_all('Collection')[0].append(dataSet)

        counter += 1

    if counter == 1:
        print('Did not found any .pvd files with name '+filestr+' or could write to file')
    else:
        f = open(filestr+'.pvd', "w")
        f.write(bs_dataMerged.prettify())
        f.close()

if __name__ == '__main__':
    main()
