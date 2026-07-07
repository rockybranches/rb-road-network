import argparse
import json
import sys

import pandas as pd


# render_plotly.py:
#   1. Load the json file
#   2. Convert the json to a pandas dataframe
#   3. Plot the dataframe using plotly express
#   Optional: save the figure to a PNG file with --output


def render(json_file, output=None):
    import plotly.express as px

    with open(json_file, 'r') as resp:
        res = json.load(resp)
    center_pt = dict(zip(['lon', 'lat'], res['features']
                         [0]['geometry']['coordinates']))
    coords = res['features'][1]['geometry']['coordinates']
    df = pd.DataFrame(coords, columns=['lon', 'lat'])
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

    if output:
        fig.write_image(output)
        print(f'Saved map image to: {output}')
    else:
        fig.show()


def main(args=None):
    parser = argparse.ArgumentParser(
        description='Render a roads-to-population JSON result as a Plotly map.')
    parser.add_argument('json_file', help='Path to the justPop JSON output file.')
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Save the figure to this path (e.g. result.png) instead of opening a browser.',
    )
    parsed = parser.parse_args(args)
    render(parsed.json_file, output=parsed.output)


if __name__ == '__main__':
    main()
