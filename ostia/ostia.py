from datetime import date
import copernicus

def OSTIA(config, idate):

    ''' Download OSTIA '''

    # Copernicus credentials
    USER, PSWD = config['USERNAME'], config['PASSWORD']

    # Geographical boundaries
    w, e = float(config['w']), float(config['e'])
    s, n = float(config['s']), float(config['n'])
        
    # OSTIA associated product and service ID's
    copernicus_dataset = config['dataset-id']


    # Set local directory to download NetCDF files to 
    path = '/tmp/'     

    # Set variable to download 
    var = 'analysed_sst'

    # If possible, download until today
    edate = date.today()

    # File name to download 
    file = 'OSTIA-TMP.nc'

    # Convert dates to strings
    idate = idate.strftime('%Y-%m-%dT%H:%M:%S')
    edate = edate.strftime('%Y-%m-%dT%H:%M:%S')

    # Download
    copernicus.Copernicus_Marine_Service_Download(USER, PSWD, copernicus_dataset, 
        path, file, w, e, s, n, idate, edate, var)

    return path + file
