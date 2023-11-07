from netCDF4 import Dataset, num2date
import shutil
import wget
import os

from log import set_logger, now
logger = set_logger()

def erddap():
    ''' Download data from ERDDAP '''

    # Start date to download
    idate = '1980-01-01'

    ''' Download from Irish Weather Buoy Network '''
    # Buoys
    M = ('M2', 'M3', 'M4', 'M5', 'M6')

    root = "https://erddap.marine.ie/erddap/tabledap/IWBNetwork.nc?"       + \
               "station_id%2Ctime%2CSeaTemperature%2CQC_Flag" + \
               "&station_id=%22"
               
    suffix = "%22&time%3E="

    if not os.path.isdir('/data/csv/'):
        os.mkdir('/data/csv')
        
    for i in M:
        logger.info(f'{now()} Downloading {i}')
        f = root + i + suffix + idate
        # Download
        f = wget.download(f)
        # Move
        shutil.move(f, f'/data/netcdf/{i}.nc')

        logger.info(f'{now()} Masking temperature for {i}')
        # Open file 
        with Dataset(f'/data/netcdf/{i}.nc', 'a') as nc:
            # Read temperature
            temp = nc.variables['SeaTemperature'][:]
            # Mask values with 0.0 seawater temperature 
            temp.mask[temp == 0] = True
            # Write temperature with masked 0.0 values
            nc.variables['SeaTemperature'][:] = temp
            # Read time
            time = num2date(nc.variables['time'][:],
                    nc.variables['time'].units)
            # Read QC
            QC = nc.variables['QC_Flag'][:]

        # Set CSV file name
        filename = f'/data/csv/{i}.csv'

        logger.info(f'{now()} Creating CSV file {filename}')
        with open(filename, 'w') as f:
            # Write header
            f.write(f'Seawater temperature at {i}\n')
            f.write('QC flag values: 0, 1, 9\n')
            f.write('QC flag meanings: unknown, good, missing\n\n')
            f.write('Date,in-situ seawater temperature (ºC),quality flag\n')
            # Write data line by line
            for t, T, qc in zip(time, temp, QC):
                f.write(f'%s,%.2f,%d\n' % (t.strftime('%Y-%m-%d %H:%M'), T, qc))

    ''' Download from Mace Head '''

    f = "https://erddap.marine.ie/erddap/tabledap/compass_mace_head.nc?" + \
           f"time%2Clatitude%2Clongitude%2Csbe_temp_avg&time%3E={idate}"

    logger.info(f'{now()} Downloading Mace Head...')
    # Download
    f = wget.download(f)
    # Move
    shutil.move(f, f'/data/netcdf/Mace-Head.nc')

    # Open file 
    with Dataset(f'/data/netcdf/Mace-Head.nc', 'r') as nc:
        # Read temperature
        temp = nc.variables['sbe_temp_avg'][:]
        # Read time
        time = num2date(nc.variables['time'][:],
                nc.variables['time'].units)

    # Set CSV file name
    filename = f'/data/csv/Mace-Head.csv'

    logger.info(f'{now()} Creating CSV file {filename}')
    with open(filename, 'w') as f:
        # Write header
        f.write(f'Seawater temperature at Mace Head\n\n')
        f.write('Date,in-situ seawater temperature (ºC)\n')
        # Write data line by line
        for t, T in zip(time, temp):
            f.write(f'%s,%.2f\n' % (t.strftime('%Y-%m-%d %H:%M'), T))

    logger.info(f'{now()} FINISHED...')

if __name__ == '__main__':
    erddap()
