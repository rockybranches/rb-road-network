"""The fully detailed result: every reached cell, as the legacy program wrote it.

The C++ program saved its result as GeoJSON with two features: the start
point (`StartPoint`) and one MultiPoint (`AccessibleArea`) holding the centre
of every grid square it could reach. The QGIS script in
`scripts/qgis_scripts/` and other existing tools read that layout, so the
detailed result keeps it: the same feature names, order and marker styles.

What differs is the grid: one point per reached 250 m road cell of the
national grid, where the legacy grid squares were about 1.3 km. A few
properties are added to describe the result; the legacy tools ignore them.

The coarse map copy (`area.py`) is small enough to keep with every analysis.
This is not: a 75 km search reaches on the order of 100,000 cells, a few
megabytes of GeoJSON, so the Worker builds it in the background on request
and keeps it in object storage.

Pure standard library and free of Cloudflare imports.
"""

import json

from . import grid as g

COORD_DIGITS = 5  # about 1 m, against 250 m cells
START_STYLE = {"marker-color": "#ff0000", "marker-size": "large", "marker-symbol": "circle"}
AREA_STYLE = {"marker-color": "#0000ff", "marker-size": "small", "marker-symbol": "circle"}


def _coord(lon, lat):
    return f"[{lon:.{COORD_DIGITS}f},{lat:.{COORD_DIGITS}f}]"


def to_geojson(analysis, request, datasets, analysis_id=None):
    """The detailed result as GeoJSON text.

    `analysis` comes from `analyze(..., keep_cells=True)`; `request` is the
    analysis's request (lat, lon, radius_m, ...) and `datasets` the road and
    county dataset labels it was run against. Built as text rather than
    through json.dumps: a list of a million coordinate pairs would cost
    several times the memory of the finished string.
    """
    cells = analysis.cells
    if cells is None:
        raise ValueError("analysis was run without keep_cells")

    start = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            # The point as given, like the legacy file. The search starts at
            # the nearest road cell, given below when it differs.
            "coordinates": [request["lon"], request["lat"]],
        },
        "properties": {
            "name": "StartPoint",
            **START_STYLE,
            "analysis_id": analysis_id,
            "label": request.get("label", ""),
            "search_start": [
                round(analysis.start_lon, COORD_DIGITS),
                round(analysis.start_lat, COORD_DIGITS),
            ],
            "moved_to_nearest_road": analysis.snapped,
        },
    }
    area_props = {
        "name": "AccessibleArea",
        **AREA_STYLE,
        "points": len(cells),
        "cell_m": g.CELL_M,
        "radius_m": request["radius_m"],
        "reached_km2": round(analysis.reached_km2, 1),
        "datasets": datasets,
    }

    to_lonlat = g.xy_to_lonlat
    x0 = g.X0 + 0.5 * g.CELL_M
    y0 = g.Y0 + 0.5 * g.CELL_M
    size = g.CELL_M
    points = ",".join(
        _coord(*to_lonlat(x0 + c * size, y0 + r * size))
        for c, r in zip(cells.cols, cells.rows)
    )
    return (
        '{"type":"FeatureCollection","features":['
        + json.dumps(start, separators=(",", ":"))
        + ',{"type":"Feature","geometry":{"type":"MultiPoint","coordinates":['
        + points
        + ']},"properties":'
        + json.dumps(area_props, separators=(",", ":"))
        + "}]}\n"
    )


def object_key(analysis_id):
    """Where an analysis's detailed result is kept in object storage."""
    return f"details/{analysis_id}.geojson"
