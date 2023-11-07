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
    PRODUCT, SERVICE = config['product-id'], config['service-id']

    # Set local directory to download NetCDF files to 
    path = '/tmp/'     

    # Set variable to download and mode to Near-Real-Time
    var, mode = 'analysed_sst', 'nrt'

    # If possible, download until today
    edate = date.today()

    # File name to download 
    file = 'OSTIA-TMP.nc'

    # Download
    copernicus.Copernicus_Marine_Service(USER, PSWD, PRODUCT, SERVICE,
        path, file, w, e, s, n, idate, edate, var, mode)

    return path + file
