import glob
import os

def clean():
    ''' Clean NetCDF directory. Remove partition files '''

    files = glob.glob('/data/netcdf/Cut_*.nc');
    for f in files:
        os.remove(f)

if __name__ == '__main__':
    clean()
