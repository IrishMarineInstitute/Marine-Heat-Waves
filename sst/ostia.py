from datetime import date, timedelta
from netCDF4 import Dataset, num2date
from subset_sst import subset_sst
from math import nan
import copernicus
import os

from log import set_logger, now
logger = set_logger()

def OSTIA(config):

    ''' Download OSTIA '''

    # Copernicus credentials
    USER, PSWD = config['USERNAME'], config['PASSWORD']
        
    # Geographical boundaries
    w, e = float(config['w']), float(config['e'])
    s, n = float(config['s']), float(config['n'])
        
    # OSTIA associated product and service ID's
    copernicus_dataset = config['dataset-id']

    # Number of days back in time to download
    N = int(config['N'])

    # Set local directory to download NetCDF files to 
    path = '/data/SST/'     
    if not os.path.isdir(path):
        os.makedirs(path)

    # Set variable to download
    var = 'analysed_sst'

    # Date range to download  
    idate, edate = date.today() - timedelta(days=N+4), date.today()

    # File name to download 
    file = 'OSTIA-MHW.nc'
    if os.path.isfile(path + file):
        os.remove(path + file)

    # Download
    copernicus.Copernicus_Marine_Service_Download(USER, PSWD, copernicus_dataset, 
            path, file, w, e, s, n, idate.strftime('%Y-%m-%dT%H:%M:%S'), 
            edate.strftime('%Y-%m-%dT%H:%M:%S'), var)

    subset_sst() # Subset from MHW file (N + 4 days) to new file (N days)

    # File name to read from 
    file = 'OSTIA.nc'

    # Read SST
    with Dataset(path + file) as nc:
        # Read coordinates
        lon, lat = nc.variables['lon'][:], nc.variables['lat'][:]
        # Read time
        time = num2date(nc.variables['time'][:], nc.variables['time'].units)
        # Read SST. Convert to Celsius
        sst = nc.variables['analysed_sst'][:] - 273.15

    # Mask missing values
    sst = sst.filled(nan)

    return lon, lat, time, sst 
