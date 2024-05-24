import pandas as pd
from urllib.request import urlopen
import json
with urlopen('https://robcapps.com/docs/justPopResult2.json') as resp:
    res = json.load(resp)
    center_pt = dict(zip(['lon', 'lat'], res['features'][0]['geometry']['coordinates']))
    coords = res['features'][1]['geometry']['coordinates']
    df = pd.DataFrame(coords, columns=['lon', 'lat'])
    # display(df.head())
    import plotly.express as px
    fig=px.scatter_mapbox(df, lat='lat', lon='lon', center=center_pt, mapbox_style='open-street-map', zoom=6,
                                                color_discrete_sequence=['rgba(122, 200, 255, 0.5)'])
    fig.update_geos(
            visible=True, scope='usa', showsubunits=True, showcountries=True,
        )
    fig.add_scattergeo(lat=[center_pt['lat']],lon=[center_pt['lon']], fillcolor='rgba(0, 0, 0, 1)')
    fig.show()
