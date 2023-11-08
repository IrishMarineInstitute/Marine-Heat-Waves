'''
    This script merges the daily SST files into a single, multi-year NetCDF
    file. Use this script after downloading and cropping the files with the
    bash scripts provided with this repository.
    
    After running this script, a new, multi-year NetCDF file will be produced.
    This NetCDF file has an unlimited time dimension. This is very important,
    so that new daily SST layers will be later appended to this file as a 
    result of the daily routine operations of this application. 
    
    The name of the resulting NetCDF file is "OSTIA-UNLIMITED.nc". A 
    mini-example of this dataset containing just the month of January of 1982
    is provided with the repository. However, it is recommended that an updated
    dataset, containing >40 years of data, is used to launch the application.
    These are the steps to be followed:
        
        1. Run the bash script "download.sh" to download global SST files from
           the Copernicus Marine Service.
           
        2. Run the bash script "crop.sh" to extract your area of interest. 
        
        3. Run this script "merge.py" to join the files into a single, multi-year
           NetCDF dataset with an unlimited time dimension: "OSTIA-UNLIMITED.nc"
           
        4. Place this file "OSTIA-UNLIMITED.nc" and the climatology 
           "OSTIA-Climatology.nc" in the "ostia" container before building.
'''

from netCDF4 import Dataset, num2date
import numpy as np
import glob


# Path of the SST files downloaded (and cropped) from the Copernicus Marine 
# Service. Change as required.
files = './OSTIA/*.nc'

''' NO NEED TO MODIFY THE LINES BELOW '''

# Output NetCDF file name
ncname = 'OSTIA-UNLIMITED.nc'

# Get list of files
filelist = glob.glob(files)

# Read dimensions from first file
with Dataset(filelist[0], 'r') as nc:
    # Read longitude
    lon = nc.variables['lon'][:]; L = len(lon)
    # Read latitude
    lat = nc.variables['lat'][:]; M = len(lat)
    # Read mask
    mask = nc.variables['mask'][:]

# Open new dataset to create NetCDF structure
with Dataset(ncname, 'w', format='NETCDF4') as nc:
    # Create dimensions
    nc.createDimension('longitude', L)
    nc.createDimension('latitude',  M)
    nc.createDimension('time', None)      # UNLIMITED TIME DIMENSION
    
    # Longitude
    lonvar = nc.createVariable('longitude', 'f4', dimensions=('longitude'))
    lonvar.standard_name = 'longitude'
    lonvar.units = 'degree_east'
    # Write longitude
    lonvar[:] = lon

    # Latitude
    latvar = nc.createVariable('latitude', 'f4', dimensions=('latitude'))
    latvar.standard_name = 'latitude'
    latvar.units = 'degree_north'
    # Write latitude
    latvar[:] = lat
    
    # Mask
    maskvar = nc.createVariable('mask', 'i4', dimensions=('latitude', 'longitude'))
    maskvar.long_name = 'land sea ice lake bit mask'
    # Write mask
    maskvar[:] = mask
    
    # Time
    timevar = nc.createVariable('time', 'f8', dimensions=('time'))
    timevar.standard_name = 'time'
    timevar.units = 'seconds since 1981-1-1 00:00:00'
    
    # SST
    sstvar = nc.createVariable('analysed_sst', 'f4', dimensions=('time', 'latitude', 'longitude'))
    sstvar.standard_name = 'sea_surface_foundation_temperature'
    sstvar.units = 'kelvin'
    
# Open NetCDF to write SST day by day
with Dataset(ncname, 'a') as nc:
    # Access time variable
    timevar = nc.variables['time']
    # Access SST variables
    sstvar = nc.variables['analysed_sst']
    
    # Iterate along the daily downloaded (and cropped) files
    for i, file in enumerate(filelist):
        # Open daily file
        with Dataset(file, 'r') as cdf:
            # Read time
            time = cdf.variables['time'][:]
            # Convert to an actual date to display progress
            date = num2date(time, 'seconds since 1981-1-1 00:00:00').data[0]
            # Display progress
            print(date.strftime('%Y-%m-%d'))
            # Read SST
            sst = cdf.variables['analysed_sst'][:]
            
        # Append time
        timevar[i] = time
        # Append SST
        sstvar[i, :, :] = sst
        
# OPTIONAL. Check that the resulting dataset has a well-behaved time series
# (e.g. a time series with a constant step of 86400 seconds).

with Dataset(ncname, 'r') as nc:
    # Read time
    time = nc.variables['time'][:]
# Get time step
DT = np.unique(time[1::]-time[0:-1])[0]

try:
    assert(DT == 86400)
except AssertionError:
    raise AssertionError("The time step is not constant or not equal to 1 day. " + \
                         "Check that the daily files do not overlap in time")