from datetime import date, timedelta
from ostia import OSTIA
from netCDF4 import Dataset, num2date
import shutil
import os

from log import set_logger, now
logger = set_logger()

def cf2date(cf):
    return date(cf.year, cf.month, cf.day)

def main():

    logger.info(f'{now()} STARTING OSTIA OPERATIONS...')

    today = date.today()

    config = configuration()

    # Get path to NetCDF files in shared volume
    ncpath = config['ncpath']
    if not os.path.isdir(ncpath):
        os.mkdir(ncpath)

    # Get local database file name
    file = config['SST']; logger.info(f'{now()} Local database is {file}...')

    fullpath = ncpath + file

    # Move local database to shared volume if not moved yet
    if os.path.isfile(file) and not os.path.isfile(fullpath):
        shutil.move(file, fullpath)
    if not os.path.isfile(fullpath):
        raise FileNotFoundError(f'ERROR: Local database file {file} not found! ' + \
                'Please make sure the NetCDF file is at the base directory '     + \
                'during build time or it is already located at the shared volume.')

    # Get climatology file name
    climfile = config['climnc']; fullclimpath = ncpath + climfile

    # Move climatology to shared volume if not moved yet
    if os.path.isfile(climfile) and not os.path.isfile(fullclimpath):
        shutil.move(climfile, fullclimpath)
    if not os.path.isfile(fullclimpath):
        raise FileNotFoundError(f'ERROR: Climatology file {climfile} not found! ' + \
                'Please make sure the NetCDF file is at the base directory '     + \
                'during build time or it is already located at the shared volume.')

    with Dataset(fullpath, 'r') as nc:
        series = num2date(nc.variables['time'], nc.variables['time'].units)
        # Get last index of historical time series
        lastIndex = len(series) - 1 
    ind, end = cf2date(series[0]), cf2date(series[-1])
    # Convert time to string for logging
    istr, estr = ind.strftime('%Y-%b-%d'), end.strftime('%Y-%b-%d')
    logger.info(f'{now()} HISTORICAL dataset runs from {istr} to {estr}')
    
    idate = end + timedelta(days=1)
    if idate == today:
        logger.info(f'{now()} Yesterday SST already downloaded. Exiting...')
        return
    else:
        logger.info(f'{now()} Starting download from {idate.strftime("%Y-%b-%d")} onward...')
        file = OSTIA(config, idate)

    if not os.path.isfile(file): # File could not be downloaded
        logger.info(f'{now()} File could not be downloaded from Copernicus. Exiting...')
        return

    # Read TMP dataset
    with Dataset(file) as nc:
        # Read time
        timestamp = nc.variables['time'][:]
        # Convert time to date
        time = num2date(timestamp, nc.variables['time'].units)
        # Read SST. Convert to Celsius
        sst = nc.variables['analysed_sst'][:] 

    os.remove(file) # Delete temporal file

    # Convert to datetime
    start, fin = cf2date(time[0]), cf2date(time[-1])
    # Convert to string for logging
    startstr, endstr = start.strftime('%Y-%b-%d'), fin.strftime('%Y-%b-%d')
    logger.info(f'{now()} TMP dataset runs from {startstr} to {endstr}')

    # Find out the difference [days] between latest date in local database
    # and earliest date in the temporal NetCDF file just downloaded
    DT = (start - end).days
    logger.info(f'{now()} time difference between END of HISTORICAL and ' + \
            f'START of TMP is {DT} day')

    logger.info(f'{now()} Last HISTORICAL time index is {lastIndex}')
    # Get start writing index
    wrtstart = lastIndex + DT 
    # Get end writing index
    wrtend = wrtstart + len(time); 
    logger.info(f'{now()} Write from {startstr} ({wrtstart}) to {endstr} ({wrtend})')

    with Dataset(fullpath, 'a') as nc:
        logger.info(f'{now()} Writing time...')
        nc.variables['time'][wrtstart:wrtend] = timestamp
        logger.info(f'{now()} Writing SST...')
        nc.variables['analysed_sst'][wrtstart:wrtend, :, :] = sst 

    logger.info(f'{now()} FINISHED...')

    return

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

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error('ERROR: %s', e)
