"""Fixed analysis grid shared by the Worker and the offline ingest tools.

Everything is laid out on one national grid in EPSG:5070 (NAD83 / CONUS Albers
equal-area), so a cell is the same size on the ground wherever it is and a
tile key means the same thing in every dataset version.

Pure standard library: this module is imported inside the Python Worker
(Pyodide) and by the local ingest tools.
"""

import math

# --- grid layout -----------------------------------------------------------

CELL_M = 250.0  # ground size of one cell
TILE = 128  # cells per tile side (one tile = 32 km)
TILE_M = CELL_M * TILE

# Grid origin (lower-left corner of cell 0,0) in EPSG:5070 metres. Chosen as a
# whole number of tiles south-west of the contiguous US, so tile indices are
# small non-negative integers across CONUS.
X0 = -2_432_000.0
Y0 = 192_000.0

# Road-class bit flags stored in each cell of the "roads" layer.
CLASS_MAJOR = 1  # motorway, trunk (+ links)
CLASS_ARTERIAL = 2  # primary, secondary (+ links)
CLASS_LOCAL = 4  # tertiary, unclassified, residential, living_street
CLASS_MINOR = 8  # service, track, busway, unknown

FCLASS_BITS = {
    "motorway": CLASS_MAJOR,
    "motorway_link": CLASS_MAJOR,
    "trunk": CLASS_MAJOR,
    "trunk_link": CLASS_MAJOR,
    "primary": CLASS_ARTERIAL,
    "primary_link": CLASS_ARTERIAL,
    "secondary": CLASS_ARTERIAL,
    "secondary_link": CLASS_ARTERIAL,
    "tertiary": CLASS_LOCAL,
    "tertiary_link": CLASS_LOCAL,
    "unclassified": CLASS_LOCAL,
    "residential": CLASS_LOCAL,
    "living_street": CLASS_LOCAL,
    "service": CLASS_MINOR,
    "track": CLASS_MINOR,
    "track_grade1": CLASS_MINOR,
    "track_grade2": CLASS_MINOR,
    "track_grade3": CLASS_MINOR,
    "track_grade4": CLASS_MINOR,
    "track_grade5": CLASS_MINOR,
    "busway": CLASS_MINOR,
    "unknown": CLASS_MINOR,
}
# Deliberately absent (not drivable): footway, path, cycleway, pedestrian,
# bridleway, steps.

# --- EPSG:5070 projection (Snyder, "Map Projections: A Working Manual") ------

_A = 6378137.0  # GRS80 semi-major axis
_F = 1.0 / 298.257222101
_E2 = 2.0 * _F - _F * _F
_E = math.sqrt(_E2)
_LAT1 = math.radians(29.5)
_LAT2 = math.radians(45.5)
_LAT0 = math.radians(23.0)
_LON0 = math.radians(-96.0)


def _q(phi):
    s = math.sin(phi)
    return (1.0 - _E2) * (
        s / (1.0 - _E2 * s * s)
        - (1.0 / (2.0 * _E)) * math.log((1.0 - _E * s) / (1.0 + _E * s))
    )


def _m(phi):
    s = math.sin(phi)
    return math.cos(phi) / math.sqrt(1.0 - _E2 * s * s)


_N = (_m(_LAT1) ** 2 - _m(_LAT2) ** 2) / (_q(_LAT2) - _q(_LAT1))
_C = _m(_LAT1) ** 2 + _N * _q(_LAT1)
_RHO0 = _A * math.sqrt(_C - _N * _q(_LAT0)) / _N


def lonlat_to_xy(lon, lat):
    """WGS84/NAD83 degrees -> EPSG:5070 metres."""
    rho = _A * math.sqrt(_C - _N * _q(math.radians(lat))) / _N
    theta = _N * (math.radians(lon) - _LON0)
    return rho * math.sin(theta), _RHO0 - rho * math.cos(theta)


def xy_to_lonlat(x, y):
    """EPSG:5070 metres -> WGS84/NAD83 degrees."""
    dy = _RHO0 - y
    rho = math.hypot(x, dy)
    theta = math.atan2(x, dy)
    q = (_C - (rho * _N / _A) ** 2) / _N
    phi = math.asin(q / 2.0)
    for _ in range(8):
        s = math.sin(phi)
        t = 1.0 - _E2 * s * s
        dphi = (t * t / (2.0 * math.cos(phi))) * (
            q / (1.0 - _E2)
            - s / t
            + (1.0 / (2.0 * _E)) * math.log((1.0 - _E * s) / (1.0 + _E * s))
        )
        phi += dphi
        if abs(dphi) < 1e-12:
            break
    return math.degrees(_LON0 + theta / _N), math.degrees(phi)


# --- cell / tile arithmetic -------------------------------------------------


def xy_to_cell(x, y):
    """Projected metres -> (col, row) of the containing cell."""
    return math.floor((x - X0) / CELL_M), math.floor((y - Y0) / CELL_M)


def cell_center_xy(col, row):
    return X0 + (col + 0.5) * CELL_M, Y0 + (row + 0.5) * CELL_M


def cell_to_tile(col, row):
    return col // TILE, row // TILE
