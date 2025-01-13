#!/bin/bash

: <<'END'

This script downloads the Operational Sea Surface Tempearature
and Ice Analysis run by Met Office and delivered by IFREMER
(https://doi.org/10.48670/moi-00165). At the time this script
is developed, this dataset is split into a "Reprocessed" (REP)
dataset, from Oct-1981 to May-2022, and a "Near-Real-Time" (NRT)
dataset. These datasets have to be downloaded separately.

The lines below download the entire dataset from 1982 until
present, with GLOBAL coverage. Later, use the "crop.sh" script
to select your are of interest and save into separate files.
Finally, use "merge.py" to join the daily files into a single,
multi-year NetCDF "OSTIA-UNLIMITED.nc" and move it to the 
"ostia" container.

First, make sure this script is executable with:

$ chmod +x download.sh

Then, call this script from the command line as:

$ bash ./download.sh {USERNAME} {PASSWORD} {FOLDER}

where {USERNAME} is your Copernicus Marine Service username,

      {PASSWORD} is your Copernicus Marine Service password,

  and {FOLDER} is the folder you wish to have the files 
               downloaded to.

END

sudo wget -m -nd -np -r --ftp-user=$1 --ftp-password=$2 ftp://my.cmems-du.eu/Core/SST_GLO_SST_L4_REP_OBSERVATIONS_010_011/METOFFICE-GLO-SST-L4-REP-OBS-SST/198{2,3,4,5,6,7,8,9}/{01,02,03,04,05,06,07,08,09,10,11,12}/ -P $3
sudo wget -m -nd -np -r --ftp-user=$1 --ftp-password=$2 ftp://my.cmems-du.eu/Core/SST_GLO_SST_L4_REP_OBSERVATIONS_010_011/METOFFICE-GLO-SST-L4-REP-OBS-SST/199{0,1,2,3,4,5,6,7,8,9}/{01,02,03,04,05,06,07,08,09,10,11,12}/ -P $3
sudo wget -m -nd -np -r --ftp-user=$1 --ftp-password=$2 ftp://my.cmems-du.eu/Core/SST_GLO_SST_L4_REP_OBSERVATIONS_010_011/METOFFICE-GLO-SST-L4-REP-OBS-SST/200{0,1,2,3,4,5,6,7,8,9}/{01,02,03,04,05,06,07,08,09,10,11,12}/ -P $3
sudo wget -m -nd -np -r --ftp-user=$1 --ftp-password=$2 ftp://my.cmems-du.eu/Core/SST_GLO_SST_L4_REP_OBSERVATIONS_010_011/METOFFICE-GLO-SST-L4-REP-OBS-SST/201{0,1,2,3,4,5,6,7,8,9}/{01,02,03,04,05,06,07,08,09,10,11,12}/ -P $3
sudo wget -m -nd -np -r --ftp-user=$1 --ftp-password=$2 ftp://my.cmems-du.eu/Core/SST_GLO_SST_L4_REP_OBSERVATIONS_010_011/METOFFICE-GLO-SST-L4-REP-OBS-SST/202{0,1,2,3,4,5,6,7,8,9}/{01,02,03,04,05,06,07,08,09,10,11,12}/ -P $3
sudo wget -m -nd -np -r --ftp-user=$1 --ftp-password=$2 ftp://nrt.cmems-du.eu/Core/SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001/METOFFICE-GLO-SST-L4-NRT-OBS-SST-V2/202{0,1,2,3,4,5,6,7,8,9}/{01,02,03,04,05,06,07,08,09,10,11,12}/ -P $3
