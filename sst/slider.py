import plotly.graph_objects as go
import numpy as np
import plotly
import json

def Slider(lon, lat, time, data, coast, buoy, bathymetry, colorscale, tickvals, contours):
    ''' Create slider figure to display on portal '''

    # Coastline coordinates
    x_coast, y_coast = coast

    # Buoy(s) coordinates
    x_buoy,  y_buoy  = buoy

    # Bathymetry
    x_bathy, y_bathy = bathymetry

    # Initialize 1st trace: the 2-D contour data
    trace1 = []
    # Add traces, one for each slider step
    for i in range(len(time)):
        datos = data[i, :, :]
        trace1.append( go.Contour(
            z=datos, x=lon, y=lat,
            colorscale=colorscale,  
            hoverinfo='z', line_width=0, line_smoothing=0.85,
            colorbar=dict(
                title=dict(text='°C', font=dict(size=24)),
                tickvals=tickvals,
                tickfont=dict(size=24),
            ),
            contours=contours,
         ))

    # 2nd trace is the coastline
    trace2 = [ go.Scatter(
        x=x_coast, y=y_coast, 
        line={'color': 'black', 'width': 2}, 
        hoverinfo='none',
    ) ]            

    # 3rd trace is the buoys
    trace3 = [ go.Scatter(
        x=np.array(x_buoy), y=np.array(y_buoy), mode='markers+text', text=["Mace Head", "M2", "M3", "M4", "M5", "M6"], 
        textposition=["middle left", "bottom center", "bottom right", "top left", "bottom left", "bottom left"],
        marker={'size': 20, 'symbol': 'cross-thin', 'line': {'color': 'black', 'width': 1}}, 
        hoverinfo='none',
    ) ]            

    # Traces 4 is the bathymetry contour 
    trace4 = [go.Scatter(
        x=x_bathy, y=y_bathy, 
        line={'color': 'black', 'width': 1, 'dash': 'dash'}, 
        hoverinfo='none',
            )]
    
    # Create figure
    fig = go.Figure(data=trace1+trace2+trace3+trace4)

    # Create and add slider
    steps = []
    for i in range(len(time)):
        # Hide all traces
        step = dict(
            method='restyle',
            args = ['visible', [False] * len(fig.data)],
            label=time[i].strftime('%d %b'),
        )
  
        # Enable the traces we want to see
        step['args'][1][i] = True
        step['args'][1][-1] = True
        step['args'][1][-2] = True
        step['args'][1][-3] = True
    
        # Add step to step list
        steps.append(step)

    sliders = [dict(
        active=len(time)-1,
        currentvalue={"prefix": "", "xanchor": "center"},
        pad={"t": 50},
        len=1,
        steps=steps
    )]

    fig.update_layout(
        sliders=sliders
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
