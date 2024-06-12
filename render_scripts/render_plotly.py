import pandas as pd
import json


# render_plotly.py:
#   1. Load the json file
#   2. Convert the json to a pandas dataframe
#   3. Plot the dataframe using plotly express


def main():
    with open('/home/robertc/Git/rb-road-network/output/SavannaShoals.json', 'r') as resp:
        res = json.load(resp)
        center_pt = dict(zip(['lon', 'lat'], res['features']
                             [0]['geometry']['coordinates']))
        coords = res['features'][1]['geometry']['coordinates']
        df = pd.DataFrame(coords, columns=['lon', 'lat'])
        # display(df.head())
        import plotly.express as px
        fig = px.scatter_mapbox(
            df,
            lat='lat', lon='lon', center=center_pt,
            zoom=6,
            mapbox_style='open-street-map',
            color_discrete_sequence=['rgba(122, 200, 255, 0.5)']
        )
        fig.update_geos(
            visible=True, scope='usa', showsubunits=True, showcountries=True,
        )
        fig.add_scattergeo(lat=[center_pt['lat']], lon=[
            center_pt['lon']], fillcolor='rgba(0, 0, 0, 1)')
        fig.show()


if __name__ == '__main__':
    main()
