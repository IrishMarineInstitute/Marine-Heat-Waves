from datetime import datetime
import pyarrow.parquet as pa
from netCDF4 import Dataset
import numpy as np
import shutil
import os

from log import set_logger, now
logger = set_logger()

def to_timestamp(time):
    ''' Convert datetime list to time stamp '''
    
    return np.array([datetime.strptime(i, '%Y-%m-%d').timestamp() for i in time])

def parquet2cdf(pqt):
    ''' Convert parquet file to NetCDF '''

    logger.info(f'{now()} STARTING PARQUET-TO-CDF OPERATIONS...')

    ''' Read parquet file '''
    # Read table
    df = pa.read_table(pqt)
    # Convert to pandas data frame
    df = df.to_pandas()

    # Subset longitude and latitude
    lon, lat = df['lon'].to_numpy(), df['lat'].to_numpy()

    # Get number of events
    n = len(lon); 

    # Read MHW start time
    logger.info(f'{now()} Converting idates to timestamps...')
    t0 = to_timestamp(df['time_deb'].to_numpy())
    # Read MHW end time
    logger.info(f'{now()} Converting edates to timestamps...')
    t1 = to_timestamp(df['time_end'].to_numpy())
    # Read MHW duration
    duration = df['duration'].to_numpy()
    # Read MHW intensity
    intensity = df['imax'].to_numpy()    
    # Read MHW category
    categ = df['categ'].to_numpy()    

    ''' Create NetCDF '''
    # Set NetCDF file name
    if 'mhw' in pqt:
        ncname = 'mhw.nc'
    elif 'cs' in pqt:
        ncname = 'cs.nc'

    logger.info(f'{now()} NetCDF file name is {ncname}')

    # Open new NetCDF
    logger.info(f'{now()} Opening new NetCDF {ncname}')
    with Dataset(ncname, 'w', format='NETCDF4') as nc:
        # Create dimensions
        nc.createDimension('N', n)       # Number of events      

        # Longitude
        lonvar = nc.createVariable('longitude', 'f4', dimensions=('N'))
        lonvar.standard_name = 'longitude'
        lonvar.units = 'degree_east'
        # Write longitude
        lonvar[:] = lon

        # Latitude
        latvar = nc.createVariable('latitude', 'f4', dimensions=('N'))
        latvar.standard_name = 'latitude'
        latvar.units = 'degree_north'
        # Write latitude
        latvar[:] = lat

        # Start times
        t0var = nc.createVariable('idate', 'f8', dimensions=('N'))
        t0var.long_name = 'start date of events'
        t0var.units = 'seconds since 1970-01-01'
        # Write start times
        t0var[:] = t0
        
        # End times
        t1var = nc.createVariable('edate', 'f8', dimensions=('N'))
        t1var.long_name = 'end date of events'
        t1var.units = 'seconds since 1970-01-01'
        # Write end times
        t1var[:] = t1

        # Duration
        durationvar = nc.createVariable('duration', 'f8', dimensions=('N'))
        durationvar.long_name = 'duration of events'
        durationvar.units = 'day'
        # Write duration
        durationvar[:] = duration

        # Intensity
        intensityvar = nc.createVariable('intensity', 'f8', dimensions=('N'))
        intensityvar.long_name = 'maximum intensity of events'
        intensityvar.units = 'ºC'
        # Write intensity
        intensityvar[:] = intensity

        # Category
        categvar = nc.createVariable('category', 'u4', dimensions=('N'))
        categvar.long_name = 'category of events'
        # Write category
        categvar[:] = categ

    if os.path.isfile(f'/data/{ncname}'):
        logger.info(f'{now()} Deleting previous file {ncname}...')
        os.remove(f'/data/{ncname}')
    logger.info(f'{now()} Moving {ncname} to shared volume...')
    shutil.move(ncname, f'/data/{ncname}')

    logger.info(f'{now()} Finished converting {pqt} to {ncname}')

def pqt2cdf():
    # Name of files
    mhw, cs = '/data/mhw.parquet', '/data/cs.parquet' 
    # Convert Marine Heat Waves
    parquet2cdf(mhw); os.remove(mhw)
    # Convert cold spells
    parquet2cdf(cs);  os.remove(cs)
