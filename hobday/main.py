from parquet2cdf import pqt2cdf
from mhw import extreme_events
from clean import clean
from cut import cut

def main():
    # Partition SST dataset for parallel processing
    cut('config')
    # Marine Heat Waves analysis
    extreme_events('config', 'mhw.parquet') 
    # Cold Spells analysis
    extreme_events('csnfig', 'cs.parquet') 
    # Clean NetCDF directory (remove partition files)
    clean() 
    # Convert PARQUET files to NetCDF
    pqt2cdf()

if __name__ == '__main__':
    main()
