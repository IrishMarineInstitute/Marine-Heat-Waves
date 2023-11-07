from flask import render_template, request, url_for, redirect, send_file
from mhw_historical import mhw_historical
from pickle import load
from app import app
import json

def buoys():
    # Define buoy NetCDF properties 

    return dict(
            lon=(-5.4302, -10.5483, -9.9991, -6.7043, -15.88135, -9.9326),
            lat=(53.4836, 51.2160, 55.0000, 51.6904, 53.0748, 53.3306),
            nc=('M2', 'M3', 'M4', 'M5', 'M6', 'Mace-Head'),
            temp=('SeaTemperature', 'SeaTemperature', 'SeaTemperature',
                  'SeaTemperature', 'SeaTemperature', 'sbe_temp_avg'))

def dataload(pkl, dic):
    ''' Load data from container. Update dictionary '''
    try:
        with open(pkl, 'rb') as f:
            var = load(f)
    except FileNotFoundError:
        var = {}
    return {**dic, **var}


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':

        if "SSTMAP" in request.form:
            data = dataload('/data/SST.pkl', {})
            return render_template('sst.html', **data)

        if "ANMMAP" in request.form:
            data = dataload('/data/ANM.pkl', {})
            return render_template('anm.html', **data)

        if "MHWMAP" in request.form:
            data = dataload('/data/MHW.pkl', {})
            return render_template('mhw.html', **data)

        for key in request.form:
            if 'csv' in key:
                return send_file(key, as_attachment=True)

        # Get position selected on the map 
        lon, lat = float(request.form['longitude']), float(request.form['latitude'])

        # Check marker is inside SST domain
        if lon < -25 or lon > -5 or lat < 46 or lat > 58 :
            error = 'SITE MUST BE WITHIN THE RECTANGLE (46ºN, 25ºW) TO (58ºN, 05ºW). SITE MUST BE AT SEA.'
            return render_template('index.html', latitude=52, longitude=-15,
                polygon=json.dumps([[46,-25],[58,-25],[58,-5],[46,-5]]), error=error) 

        ''' Find out if the seleted position matches any of the buoys '''
        # Load dictionary with buoy positions, NetCDF names and temperature 
        buoydict, buoy = buoys(), False
        # Coordinates of buoys     
        lons, lats = buoydict.get('lon'), buoydict.get('lat') 
        # NetCDF file names and temperature variables names for each buoy
        ncs, temps = buoydict.get('nc'),  buoydict.get('temp')

        insitu = False
        for i, j, nc, temp in zip(lons, lats, ncs, temps):
            if ( i == lon ) and ( j == lat ):
                buoy = (nc, temp); insitu = True; break # Use this NetCDF 

        MHW, CS = False, False
        if 'MHW' in request.form:
            MHW = True
        if 'CS' in request.form:
            CS = True

        # Produce figure 
        try:
            fig, csvsst, csvclim, csvmhw, csvcs, csvinsitu = mhw_historical(lon, lat, MHW, CS, buoy=buoy)
        except RuntimeError:
            error = 'SITE MUST BE AT SEA.'
            return render_template('index.html', latitude=52, longitude=-15,
                polygon=json.dumps([[46,-25],[58,-25],[58,-5],[46,-5]]), error=error) 
   
        # Return figure
        return render_template('figure.html', fig=fig, MHW=MHW, CS=CS, insitu=insitu,
                csvsst=csvsst, csvclim=csvclim, csvmhw=csvmhw, csvcs=csvcs, csvinsitu=csvinsitu)

    else:

        return render_template('index.html', latitude=52, longitude=-15,
            polygon=json.dumps([[46,-25],[58,-25],[58,-5],[46,-5]])) 
