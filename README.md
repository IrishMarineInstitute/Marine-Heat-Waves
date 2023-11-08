# Marine-Heat-Waves
This project is an **uWSGI-Nginx-Flask** (https://github.com/tiangolo/uwsgi-nginx-flask-docker) web application that provides rapid access to Marine Heat Waves (MHW) analysis over an area of interest. After the application is deployed, the user can select a point on a map and obtain the time series of Sea Surface Temperature (SST) at the selected site, together with the climatological values and an anaysis of the occurrence of MHW. This information is presented using an interactive figure with a slider that allows the user to select different years in the time series. This project uses the **mhw-detect** package (https://pypi.org/project/mhw-detect) for detection of Marine Heat Waves.

The source of SST data is the **Operational Sea Surface Temperature and Ice Analysis** run by Met Office and delivered by IFREMER (https://doi.org/10.48670/moi-00165). This is a global-coverage product. Therefore, with minimal changes in the code, this application should be adaptable to any area of interest. The application distributed with this repository has been applied to the Irish EEZ (46ºN 25ºW to 58ºN 5ºW).

It is also possible to include in-situ measurements of seawater temperature from oceanographic moorings. This application also includes in-situ observations from the **Irish Marine Data Buoy Observation Network (IMDBON)** and the Mace Head buoy deployed under the framework of the **Interreg COMPASS** project. The in-situ data is accessed from the **Marine Institute ERDDAP Server** (https://erddap.marine.ie). 

The instructions below provide details on how to deploy this application for your area of interest.

## Structure
The code is structured in five containerized applications that communicate to each other through a Docker volume. These containers are: **ostia**, **hobday**, **erddap**, **sst** and **webapp**. This last container (**webapp**) produces the front-end part of the application, while the other containers run the back-end part of the application:

  1. **ostia**: This container maintains and updates a local, multi-year dataset of SST. Every day, it downloads and appends a new SST layer to the local dataset.
  2. **hobday**: This container reads this local SST dataset and applies the **mhw-detect** algorithms (Hobday *et al.,* 2016) to determine the occurrence of marine heat waves and cold spells in the area.
  3. **erddap**: This container accesses and processes in-situ seawater temperature measurements from the Marine Institute ERDDAP.
  4. **sst**: In addition to the main workflow, which focuses on time-series analysis, this container produces 2-D maps of the sea surface tempeature, anomalies and marine heat waves occurring in the area of interest in the last two weeks.
  5. **webapp**: This container produces a web application to visualize data produced by the other containers.

In addition, some scripts are provided at the root of the repository for the pre-processing steps. More details below.

## Preparing the system
Before deploying the containers, two pre-processing steps are required:

  1. First, the SST dataset must be downloaded, ideally to the latest date available. The **ostia** container has been designed to update the local dataset to the current date, but it is not expected to initialize the dataset from scratch or to update the dataset several years at once.

Different tools are provided to help to build this dataset. A miniature example of how this dataset should like is provided under the **ostia** container. This file is **OSTIA-UNLIMITED.nc**. It consists of a NetCDF file with an unlimited time dimension, so that new daily layers can be later appended. 

To start downloading the dataset from the Copernicus Marine Service, run the **download.sh** script at the root directory, by providing your Copernicus Marine Service username and password, together with the local directry you wish to have the files downloaded to, as follows:

```
$ bash ./download.sh {USERNAME} {PASSWORD} {FOLDER}
```

## References
Hobday, A. J., Alexander, L. V., Perkins, S. E., Smale, D. A., Straub, S. C., Oliver, E. C., ... & Wernberg, T. (2016). A hierarchical approach to defining marine heatwaves. Progress in Oceanography, 141, 227-238.

 

