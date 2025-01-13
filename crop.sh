#!/bin/bash

: <<'END'

This script crops the downloaded GLOBAL dataset to select
your area of interest. 

First, make sure this script is executable with:

$ chmod +x crop.sh

Then, call this script from the command line as:

$ bash ./crop.sh {FOLDER} {WEST} {EAST} {SOUTH} {NORTH}

  where {FOLDER} is the folder where the SST files have
                 been downloaded.

        {WEST} western boundary (longitude)

        {EAST} eastern boundary (longitude)

        {SOUTH} southern boundary (latitude)
  
        {NORTH} northern boundary (latitude)

Both the Reprocessed (REP) and Near-Real-Time (NRT) datasets
are processed here. At the end, a collection of *_crop.nc 
NetCDF files will have been produced, containing only the
selected area. Now, move these files to a separate folder,
MAKING SURE THAT THE TWO DATASETS DO NOT OVERLAP IN TIME.
For overlapping times, you will have to choose files from 
one or the other dataset (either REP or NRT). Then, run
"merge.py" to obtain single, multi-year NetCDF file that
can be used to start the "ostia" container.

END

for file in $(ls $1*-UKMO-L4_GHRSST-SSTfnd-OSTIA-GLOB_REP-v02.0-fv02.0.nc) 
    do
	    cdo sellonlatbox,$2,$3,$4,$5 $file ${file%???}_crop.nc;
    done

for file in $(ls $1*-UKMO-L4_GHRSST-SSTfnd-OSTIA-GLOB-v02.0-fv02.0.nc) 
    do 
	    cdo sellonlatbox,$2,$3,$4,$5 $file ${file%???}_crop.nc;
    done
