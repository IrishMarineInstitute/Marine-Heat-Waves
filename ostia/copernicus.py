import copernicusmarine as cm
import os

from log import set_logger, now
logger = set_logger()

def Copernicus_Marine_Service_Download(user, pswd, dataset, 
        localpath, filename, lonmin, lonmax, latmin, latmax, idate, edate, var):
    
    '''
            This function downloads, as a NetCDF file, the variable from the
            specified dataset. 
    '''

    f = localpath + filename;
        
    for i in range(5): # Try up to 5 times to download from Copernicus Marine Service
    
        logger.info(f'{now()} Trial {i} to download SST data')

        cm.subset(
                username=user,
                password=pswd,
                dataset_id=dataset,
                output_directory=localpath,
                output_filename=filename,
                variables=[var],
                minimum_longitude=lonmin,
                maximum_longitude=lonmax,
                minimum_latitude=latmin,
                maximum_latitude=latmax,
                start_datetime=idate,
                end_datetime=edate,
                force_download=True
                )

        if os.path.isfile(f): # File downloaded successfully. Leave loop...
            logger.info(f'{now()}   Successfully downloaded file {f}'); break
        else: # Download failed. Retry...
            logger.info(f'{now()}   Download failed!'); continue
        
    if os.path.isfile(f):
        
        logger.info(f'{now()} Reading local NetCDF file...') 
        
    else: # If, after trying 5 times, file is still unavailable, return NaN
        
        logger.info(f'{now()} Unable to download Copernicus Marine Service file')
