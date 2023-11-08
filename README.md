# Marine-Heat-Waves

This project is an uWSGI-Nginx-Flask (https://github.com/tiangolo/uwsgi-nginx-flask-docker) web application that provides rapid access to Marine Heat Waves (MHW) analysis over an area of interest. After the application is deployed, the user can select a point on a map and obtain the time series of Sea Surface Temperature (SST) at the selected site, together with the climatological values and an anaysis of the occurrence of MHW. This information is presented using an interactive figure with a slider that allows the user to select different years in the time series. This project uses the mhw-detect package (https://pypi.org/project/mhw-detect) for detection of Marine Heat Waves.

The source of SST data is the Operational Sea Surface Temperature and Ice Analysis run by Met Office and delivered by IFREMER (https://doi.org/10.48670/moi-00165). This is a global-coverage product. Therefore, with minimal changes in the code, this application should be adaptable to any area of interest. The application distributed with this repository has been applied to the Irish EEZ (46ºN 25ºW to 58ºN 5ºW).

It is also possible to include in-situ measurements of seawater temperature from oceanographic moorings. This application also includes in-situ observations from the Irish Marine Data Buoy Observation Network (IMDBON) and the Mace Head buoy deployed under the framework of the Interreg COMPASS project. The in-situ data is accessed from the Marine Institute ERDDAP Server (https://erddap.marine.ie). 

The instructions below provide details on how to deploy this application for your area of interest.

## Structure




