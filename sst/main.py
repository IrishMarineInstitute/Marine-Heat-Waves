from anomalies import Anomalies
from datetime import datetime
from MHW import MarineHeatWaves
from ostia import OSTIA
from slider import Slider
from netCDF4 import Dataset
import numpy as np
import pickle
import json
import re

from log import set_logger, now
logger = set_logger()

def main():

    config = configuration()

    # Get buoy locations
    x_buoy, y_buoy = json.loads(config['lon']), json.loads(config['lat'])

    # Read coastline
    with open(config['coastfile'], 'rb') as f:
        coast = pickle.load(f)
        x_coast, y_coast = coast['longitude'], coast['latitude']

    # Read contour
    with open(config['bathymetry'], 'rb') as f:
        bathymetry = pickle.load(f)
        x_bathy, y_bathy = bathymetry['longitude'], bathymetry['latitude']

    # Read climatology
    f = config['clim']
    logger.info(f'{now()} Retrieving climatology from file {f}')
    clim = climatology(f)
    time_c, seas, pc90 = clim

    # Download sea surface temperature
    lon, lat, time, SST = OSTIA(config)

    # Calculate SST anomalies
    sst = (time, SST); clm = (time_c, seas, pc90)
    ANM = Anomalies(sst, clm)

    # Get Marine Heat Wave intensity
    marineHeatWaves = MarineHeatWaves(clm)

    # Fix data type
    lon, lat = np.round(lon.astype(np.float64), 3), np.round(lat.astype(np.float64), 3)
    SST, ANM = np.round(SST.astype(np.float64), 1), np.round(ANM.astype(np.float64), 1)
    marineHeatWaves = np.round(marineHeatWaves.astype(np.float64), 1)

    # Create SST figure
    logger.info(f'{now()} CREATING SEA SURFACE TEMPERATURE FIGURE...')
    colorscale = 'Portland'
    tickvals = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    contours=dict(start=5, end=20, size=1)
    try:
        sst = Slider(lon, lat, time, SST, (x_coast, y_coast), (x_buoy, y_buoy),
            (x_bathy, y_bathy), colorscale, tickvals, contours)
    except Exception as e:
        logging.critical(e, exc_info=True)

    # Create anomalies figure
    logger.info(f'{now()} CREATING ANOMALIES FIGURE...')
    colorscale = 'RdBu_r'
    tickvals = [-3, -2, -1, 0, 1, 2, 3]
    contours=dict(start=-3, end=3, size=.25)
    try:
        anm = Slider(lon, lat, time, ANM, (x_coast, y_coast), (x_buoy, y_buoy),
            (x_bathy, y_bathy), colorscale, tickvals, contours)
    except Exception as e:
        logging.critical(e, exc_info=True)

    # Create MHW figure
    logger.info(f'{now()} CREATING MHW FIGURE...')
    colorscale = 'Reds'
    tickvals = [0, 1, 2, 3]
    contours=dict(start=0, end=3, size=.25)
    try:
        mhw = Slider(lon, lat, time, marineHeatWaves, (x_coast, y_coast), (x_buoy, y_buoy),
            (x_bathy, y_bathy), colorscale, tickvals, contours)
    except Exception as e:
        logging.critical(e, exc_info=True)

    # Export figures to file
    logger.info(f'{now()} EXPORTING FIGURES TO FILES...')
    with open('/data/SST.pkl', 'wb') as f:
        pickle.dump({'SST': sst}, f)
    with open('/data/ANM.pkl', 'wb') as f:
        pickle.dump({'ANM': anm}, f)
    with open('/data/MHW.pkl', 'wb') as f:
        pickle.dump({'MHW': mhw}, f)

    logger.info(f'{now()} FINISHED...')

def configuration():
    ''' Read configuration file '''
    config = {}
    with open('config', 'r') as f:
        for line in f:
            if line[0] == '!': continue
            key, val = line.split()[0:2]
            # Save to dictionary
            config[key] = val
    return config

def climatology(file):
    ''' Read climatology from NetCDF file '''
       
    with Dataset(file, 'r') as nc:
        time = nc.variables['time'][:]
        # Read seasonal cycle (climatology)
        seas = nc.variables['seas'][:]
        # Read 90-th percentile (MHW threshold)
        pc90 = nc.variables['PCT90'][:]

    return time, seas, pc90

if __name__ == '__main__':
    main()
