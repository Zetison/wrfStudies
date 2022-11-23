# Script based on https://frost.met.no/python_example.html
# Libraries needed (pandas is not standard and must be installed in Python)
from os.path import expanduser
from scipy.interpolate import interp1d 
import requests
import json
import sys
import pandas as pd
from netCDF4 import Dataset
import numpy as np
import wrf
import glob
from datetime import date
from os.path import expanduser
import click
from matplotlib.cm import get_cmap
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib as mpl
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from wrf import (getvar, interplevel, to_np, latlon_coords, get_cartopy,
                 cartopy_xlim, cartopy_ylim)
import shapely.geometry as sgeom
home = expanduser("~")
sys.path.insert(1, home+'/kode/colormaps')
from convert_json import fill_colormap 

def get_plot_element(infile):
    rootgroup = Dataset(infile, 'r')
    p = wrf.getvar(rootgroup, 'RAINNC')
    #lats, lons = wrf.latlon_coords(p)
    cart_proj = wrf.get_cartopy(p)
    xlim = wrf.cartopy_xlim(p)
    ylim = wrf.cartopy_ylim(p)
    rootgroup.close()
    return cart_proj, xlim, ylim

def linInterp(field,x):
    # This function performs a quadrilinear interpolation (on a hypercube) of a field at floating index x
    # Algorithm based on the trilinear interpolation algorithm: https://en.wikipedia.org/wiki/Trilinear_interpolation
    x0 = np.floor(x).astype(int)
    xd = x-x0
    n = x.shape[0]
    
    # Evaluate corner points of hypercube
    c = np.zeros((n,2,2,2,2))
    for i3 in range(0,2):
        for i2 in range(0,2):
            for i1 in range(0,2):
                for i0 in range(0,2):
                    c[:,i3,i2,i1,i0] = field[x0[:,3]+i3,x0[:,2]+i2,x0[:,1]+i1,x0[:,0]+i0]

    # Interpolate along the fourth dimension (time)
    c1 = np.zeros((n,2,2,2))
    for i2 in range(0,2):
        for i1 in range(0,2):
            for i0 in range(0,2):
                c1[:,i2,i1,i0] = c[:,0,i2,i1,i0]*(1-xd[:,3]) + c[:,1,i2,i1,i0]*xd[:,3]

    # Interpolate along the third dimension (height - z)
    c2 = np.zeros((n,2,2))
    for i1 in range(0,2):
        for i0 in range(0,2):
            c2[:,i1,i0] = c1[:,0,i1,i0]*(1-xd[:,2]) + c1[:,1,i1,i0]*xd[:,2]

    # Interpolate along the second dimension (Y - "lat")
    c3 = np.zeros((n,2))
    for i0 in range(0,2):
        c3[:,i0] = c2[:,0,i0]*(1-xd[:,1]) + c2[:,1,i0]*xd[:,1]

    # Interpolate along the first dimension (X - "lon")
    return c3[:,0]*(1-xd[:,0]) + c3[:,1]*xd[:,0]


# Insert your own client ID here
client_id = '24c65298-cf22-4c73-ad01-7c6b2c009626'

def getMetdata(endpoint, parameters, field):
    # Issue an HTTP GET request
    rObj = requests.get(endpoint, parameters, auth=(client_id,''))
    endpoint = rObj.url
    rObj = requests.get(endpoint, auth=(client_id,''))
    # Extract JSON data
    json = rObj.json()
    
    # Check if the request worked, print out any errors
    if rObj.status_code == 200:
        return json[field]
        print('Data retrieved from frost.met.no!')
    else:
        print('Error! Returned status code %s' % rObj.status_code)
        print('Message: %s' % json['error']['message'])
        print('Reason: %s' % json['error']['reason'])

def getYRdata(endpoint, parameters, field):
    # Issue an HTTP GET request
    headers = {
            'User-Agent': 'jonv',
            'From': 'jonvegard.venas@sintef.no'  # This is another valid field
    }

    rObj = requests.get(endpoint, parameters, headers=headers)
    # Check if the request worked, print out any errors
    if rObj.status_code == 200:
        return rObj.json()[field]
        print('Data retrieved from frost.met.no!')
    else:
        print('Error! Returned status code %s' % rObj.status_code)
        print('url: %s' % rObj.url)
        
@click.command()
@click.option('--folder', default=home+'/results/WRF/Frankfurt/modeS/2021-07-10/')
@click.option('--wrffolder', default=home+'/results/WRF/Frankfurt_10800/2021071018')
@click.option('--sourceid', default='3965B1')
@click.option('--append/--no-append', default=True)
@click.option('--plotcurves/--no-plotcurves', default=True)
@click.option('--plotmap/--no-plotmap', default=True)
@click.option('--plotcontour/--no-plotcontour', default=True)
@click.option('--plotcontourf/--no-plotcontourf', default=False)
@click.option('--plotbarbs/--no-plotbarbs', default=True)
@click.option('--resol', default='50m')
def main(folder,wrffolder,append,sourceid,plotmap,plotcurves,plotcontour,plotcontourf,plotbarbs,resol): 
    #z_unit = 'km'
    z_unit = 'dm'
    z_unitStr = 'dam'
    #u_unit = 'm s-1'
    u_unit = 'kt'
    w_unit = u_unit
    w_unitStr = 'm/s'
    w_unitStr = 'kt'
    p_unit = 'hPa'
    df_obs = pd.read_csv(folder+sourceid+'_json.txt',delimiter='\t')
    df_obs['time'] = pd.to_datetime(df_obs['CurrentTime'],unit='s')
    df_obs['air_temperature'] = df_obs['Temperature']
    df_obs['pressure'] = df_obs['Barometric Pressure']
    df_obs['wind_speed'] = df_obs['Wind Speed']*1.852/3.6 # Convert from knots to m/s
    if z_unit == "km":
        feetScale = 0.3048/1000
    elif z_unit == "m":
        feetScale = 0.3048
    elif z_unit == "dm":
        feetScale = 0.3048/10

    df_obs['z'] = df_obs['Alt'].to_numpy()*feetScale # Convert from feet to decameters (dam)
    # Get data from WRF file
    i_domain = 10
    isOutside = True
    while isOutside:
        if i_domain < 0:
            print('Parts of the flightpath for '+str(sourceid)+' is not inside the solution domain')
            break

        i_domain -= 1
        try:
            ncfile = Dataset(glob.glob(wrffolder+'/wrfout_d0'+str(i_domain)+'*.nc')[0])
        except:
            continue

        fields = ['T','wind_speed','wind_from_direction']
        lat_e = df_obs['Latitude'].to_numpy()
        lon_e = df_obs['Longitude'].to_numpy()
        z_e = df_obs['z'].to_numpy()
        time_e = df_obs['time'].to_numpy()
        dummy = pd.DataFrame({'time': wrf.getvar(ncfile, 'Times', wrf.ALL_TIMES)})
        time = dummy['time'].to_numpy()
        indices = (time[0] <= time_e) & (time_e <= time[-1])
        #if not np.any(indices):
            #raise OutOfRange('The mode-S data is out of range')

        lat_e = lat_e[indices]
        lon_e = lon_e[indices]
        z_e = z_e[indices]
        time_e = time_e[indices]

        x = np.zeros((lat_e.shape[0],4))
        xy = wrf.ll_to_xy(ncfile,lat_e,lon_e,as_int=False,meta=False)
        if ncfile.MAP_PROJ_CHAR == 'Cylindrical Equidistant' and i_domain == 1:
            xy[0] += 360/0.25

        x[:,0] = xy[0]
        x[:,1] = xy[1]
        e_we = ncfile.dimensions['west_east'].size
        e_sn = ncfile.dimensions['south_north'].size
        if np.any(xy < 0) or np.any(xy[0] > e_we-1) or np.any(xy[1] > e_sn-1):
            print('Part of the flight path is outside domain d0'+str(i_domain))
            continue
        else:
            print('Extracting WRF-data from domain d0'+str(i_domain))

        if plotcurves:
            xy2 = np.zeros(xy.T.shape)
            xy2[:,:] = xy[:,:].T
            #zgrid = wrf.interp2dxy(wrf.getvar(ncfile,'z',units=z_unit),xy2,meta=False)
            zgrid = wrf.interp2dxy(wrf.g_geoht.get_height(ncfile,units=z_unit),xy2,meta=False) # Get geopotential height
            for i in range(0,len(z_e)):
                f_time = interp1d(zgrid[:,i], range(0,zgrid.shape[0]), kind='linear')
                x[i,2] = f_time(z_e[i])
                
            f_time = interp1d(time.astype('int'), range(0,len(time)), kind='linear')
            x[:,3] = f_time(time_e.astype('int')) 
            df_wrf = pd.DataFrame()
            df_wrf['time'] = time_e 
            df_wrf['air_temperature'] = linInterp(wrf.getvar(ncfile,'tc',wrf.ALL_TIMES,meta=False),x)
            df_wrf['pressure'] = linInterp(wrf.g_pressure.get_pressure(ncfile,wrf.ALL_TIMES,meta=False,units=p_unit),x)
            df_wrf['wind_speed'] = linInterp(wrf.g_wind.get_destag_wspd(ncfile,wrf.ALL_TIMES,meta=False),x)
            df_wrf['wind_from_direction'] = linInterp(wrf.g_wind.get_destag_wdir(ncfile,wrf.ALL_TIMES,meta=False),x)

            if df_wrf.isnull().values.any():
                print('Some points are outside the domain '+str(i_domain))
                continue
            else:
                isOutside = False
        else:
            isOutside = False
                
    if plotcurves:
        # Plot data
        sharex = True
        #fields = np.array([['air_temperature','wind_speed','pressure'],
        #                       ['windDirX', 'windDirY','z']])
        #ylabels = np.array([['Temperature [°C]', 'Wind speed [m/s]', 'Pressure ['+p_unit+']'], 
        #                        ['Wind direction - X','Wind direction - Y', 'Altitude ['+z_unitStr+']']])
        fields = np.array([['air_temperature','wind_speed'],
                               ['windDirX', 'windDirY']])
        ylabels = np.array([['Temperature [°C]', 'Wind speed [m/s]'], 
                                ['Wind direction - X','Wind direction - Y']])
        df_obs['windDirX'] = np.cos(np.radians(df_obs['Wind Direction']))
        df_obs['windDirY'] = np.sin(np.radians(df_obs['Wind Direction']))
        df_wrf['windDirX'] = np.cos(np.radians(df_wrf['wind_from_direction']))
        df_wrf['windDirY'] = np.sin(np.radians(df_wrf['wind_from_direction']))
        df_wrf['z'] = z_e 
        
        fig, axs = plt.subplots(fields.shape[0],fields.shape[1], sharex=sharex)
        mng = plt.get_current_fig_manager()
        #mng.resize(*mng.window.maxsize())
        #mng.frame.Maximize(True)
        mng.window.showMaximized()
        title = 'Comparison between Mode-S data and WRF simulations for flight '+sourceid
        if plotcurves:
            title += '. WRF data from domain d0'+str(i_domain)+' with grid resolution {:.1f} km'.format(max(ncfile.DX,ncfile.DY)/1000)
        fig.suptitle(title)
        for i in range(0,fields.shape[0]):
            for j in range(0,fields.shape[1]):
                axs[i,j].plot(df_wrf.time.to_numpy(),df_wrf[fields[i,j]].to_numpy(),'b', label = 'WRF forecast')
                axs[i,j].plot(df_obs.time.to_numpy(),df_obs[fields[i,j]].to_numpy(),'r', label = 'Observation data')

                axs[i,j].legend()
                axs[i,j].set(xlabel='Time', ylabel=ylabels[i,j])
                axs[i,j].set_xlim(time_e[0],time_e[-1])
        axs[1,0].set_ylim(-1,1)
        axs[1,1].set_ylim(-1,1)
        plt.show()
        fig.savefig(folder+'/'+sourceid+'_curves.png', dpi=400)

    if plotmap:
        # Extract the pressure, geopotential height, and wind variables
        ncfile = Dataset(wrffolder+'/wrfout_d01.nc')
        p = wrf.g_pressure.get_pressure(ncfile,units=p_unit)
        #p = getvar(ncfile, "pressure",units=p_unit)
        z = getvar(ncfile, "z", units=z_unit)
        ua = getvar(ncfile, "ua", units=u_unit)
        va = getvar(ncfile, "va", units=u_unit)
        wspd = getvar(ncfile, "wspd_wdir", units=w_unit)[0,:]

        # Interpolate geopotential height, u, and v winds to 500 hPa
        ht_500 = interplevel(z, p, 500)
        u_500 = interplevel(ua, p, 500)
        v_500 = interplevel(va, p, 500)
        wspd_500 = interplevel(wspd, p, 500)

        # Get the lat/lon coordinates
        lats, lons = latlon_coords(ht_500)

        # Get the map projection information
        cart_proj = get_cartopy(ht_500)

        # Create the figure
        fig = plt.figure(figsize=(12,9))
        ax = plt.axes(projection=cart_proj)

        # Download and add the states and coastlines
        name = 'admin_0_boundary_lines_land'
        #name = 'admin_1_states_provinces_lines'
        #name = "admin_1_states_provinces_shp"
        bodr = cfeature.NaturalEarthFeature(category='cultural',
            name=name, scale=resol, facecolor='none')
        land = cfeature.NaturalEarthFeature('physical', 'land', \
            scale=resol, edgecolor='k', facecolor=cfeature.COLORS['land'])
        ocean = cfeature.NaturalEarthFeature('physical', 'ocean', \
            scale=resol, edgecolor='none', facecolor=cfeature.COLORS['water'])
        lakes = cfeature.NaturalEarthFeature('physical', 'lakes', \
            scale=resol, edgecolor='b', facecolor=cfeature.COLORS['water'])
        rivers = cfeature.NaturalEarthFeature('physical', 'rivers_lake_centerlines', \
            scale=resol, edgecolor='b', facecolor='none')

        ax.add_feature(land, facecolor='beige',zorder=0)
        ax.add_feature(ocean, linewidth=0.2,zorder=0)
        ax.add_feature(lakes, linewidth=0.2,zorder=1)
        ax.add_feature(bodr, edgecolor='k',zorder=1,linewidth=0.5)
        #ax.add_feature(rivers, linewidth=0.5,zorder=1)
        if plotcontour:
            # Add the 500 hPa geopotential height contour
            levels = np.arange(100., 2000., 10.)
            contours = plt.contour(to_np(lons), to_np(lats), to_np(ht_500),
                                   levels=levels, colors="forestgreen",linewidths=1,
                                   transform=ccrs.PlateCarree(),zorder=3)
            plt.clabel(contours, inline=1, fontsize=10, fmt="%i")

        if plotcontourf:
            try:
                with open(home+'/kode/colormaps/SINTEF1.json') as f:
                    json_data = json.load(f)
                SINTEF1 = np.reshape(json_data[0]['RGBPoints'],(-1,4))
                cmap = ListedColormap(fill_colormap(SINTEF1))
            except:
                print('SINTEF1 colormap not found (can be found at https://github.com/Zetison/colormaps.git)')
                cmap = get_cmap("rainbow")

            # Add the wind speed contours
            levels = np.linspace(20,120,101)
            wspd_contours = plt.contourf(to_np(lons), to_np(lats), to_np(wspd_500),
                                         levels=levels,
                                         cmap=cmap,
                                         alpha=0.7,
                                         antialiased=True,
                                         transform=ccrs.PlateCarree(),zorder=2)
            cbar_wspd = plt.colorbar(wspd_contours, ax=ax, orientation="horizontal", pad=.05,shrink=0.5,aspect=30,ticks=range(10,110,10))
            cbar_wspd.ax.set_xlabel('Wind speeds ['+w_unitStr+'] at 500 mbar height')
        # Add the 500 hPa wind barbs, only plotting every nthb data point.
        nthb = 10
        if plotbarbs:
            plt.barbs(to_np(lons[::nthb,::nthb]), to_np(lats[::nthb,::nthb]),
                      to_np(u_500[::nthb, ::nthb]), to_np(v_500[::nthb, ::nthb]),
                      transform=ccrs.PlateCarree(), length=6,zorder=3)

        track = sgeom.LineString(zip(df_obs['Longitude'].to_numpy(),df_obs['Latitude'].to_numpy()))
        fullFlightPath = ax.add_geometries([track],
                      ccrs.PlateCarree(),
                      facecolor='none',zorder=4,
                      edgecolor='red',
                      linewidth=2,label='Flight path')
        track = sgeom.LineString(zip(lon_e,lat_e))
        flightPath = ax.add_geometries([track],
                      ccrs.PlateCarree(),
                      facecolor='none',zorder=4,
                      linestyle=':',
                      edgecolor='green',
                      linewidth=2,label='Extracted flight path')
        #plt.legend(handles=[fullFlightPath])
        #blue_line = mlines.Line2D([], [], color='red',linestyle='--', label='Flight path',linewidth=2)
        #plt.legend(handles=[blue_line])
        # Set the map bounds
        ax.set_xlim(cartopy_xlim(ht_500))
        ax.set_ylim(cartopy_ylim(ht_500))

        #ax.gridlines(draw_labels=True)
        ax.gridlines()
        startdate = pd.to_datetime(str(time_e[0])).strftime("%Y-%m-%d %H:%M:%S")
        plt.title('Flight '+sourceid+', with visualization of WRF simulation ('+startdate+') at 500 mbar Height ('+z_unitStr+'), Wind Speed ('+w_unitStr+'), Barbs ('+w_unitStr+')')

        # Plot domain boundaries
        infile_d01 = wrffolder+'/wrfout_d01.nc'
        cart_proj, xlim_d01, ylim_d01 = get_plot_element(infile_d01)
         
        infile_d02 = wrffolder+'/wrfout_d02.nc'
        _, xlim_d02, ylim_d02 = get_plot_element(infile_d02)
         
        infile_d03 = wrffolder+'/wrfout_d03.nc'
        _, xlim_d03, ylim_d03 = get_plot_element(infile_d03)
         
        infile_d04 = wrffolder+'/wrfout_d04.nc'
        _, xlim_d04, ylim_d04 = get_plot_element(infile_d04)

        # d01
        ax.set_xlim([xlim_d01[0]-(xlim_d01[1]-xlim_d01[0])/15, xlim_d01[1]+(xlim_d01[1]-xlim_d01[0])/15])
        ax.set_ylim([ylim_d01[0]-(ylim_d01[1]-ylim_d01[0])/15, ylim_d01[1]+(ylim_d01[1]-ylim_d01[0])/15])
         
        # d01 box
        textSize=10
        colors=['blue','orange','brown','deepskyblue']
        linewidth=1
        txtscale=0.003
        ax.add_patch(mpl.patches.Rectangle((xlim_d01[0], ylim_d01[0]), xlim_d01[1]-xlim_d01[0], ylim_d01[1]-ylim_d01[0],
                     fill=None, lw=linewidth, edgecolor=colors[0], zorder=10))
        ax.text(xlim_d01[0], ylim_d01[0]+(ylim_d01[1]-ylim_d01[0])*(1+txtscale), 'd01',
                size=textSize, color=colors[0], zorder=10)
         
        # d02 box
        ax.add_patch(mpl.patches.Rectangle((xlim_d02[0], ylim_d02[0]), xlim_d02[1]-xlim_d02[0], ylim_d02[1]-ylim_d02[0],
                     fill=None, lw=linewidth, edgecolor=colors[1], zorder=10))
        ax.text(xlim_d02[0], ylim_d02[0]+(ylim_d02[1]-ylim_d02[0])*(1+txtscale*3), 'd02',
                size=textSize, color=colors[1], zorder=10)
         
        # d03 box
        ax.add_patch(mpl.patches.Rectangle((xlim_d03[0], ylim_d03[0]), xlim_d03[1]-xlim_d03[0], ylim_d03[1]-ylim_d03[0],
                     fill=None, lw=linewidth, edgecolor=colors[2], zorder=10))
        ax.text(xlim_d03[0], ylim_d03[0]+(ylim_d03[1]-ylim_d03[0])*(1+txtscale*3**2), 'd03',
        size=textSize, color=colors[2], zorder=10)

        # d04 box
        ax.add_patch(mpl.patches.Rectangle((xlim_d04[0], ylim_d04[0]), xlim_d04[1]-xlim_d04[0], ylim_d04[1]-ylim_d04[0],
                     fill=None, lw=linewidth, edgecolor=colors[3], zorder=10))
        ax.text(xlim_d04[0], ylim_d04[0]+(ylim_d04[1]-ylim_d04[0])*(1+txtscale*3**3), 'd04',
        size=textSize, color=colors[3], zorder=10)
            
        plt.show()
        fig.savefig(folder+'/'+sourceid+'_map.png', dpi=400)
        
if __name__ == '__main__':
    main()
