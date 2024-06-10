from pyproj import Proj, transform


def convert_utm2latlon(easting, northing, zone=16, south=True, datum='WGS84'):
    utm_proj = Proj(proj='utm', zone=zone, south=south, ellps=datum)
    wgs84_proj = Proj(proj='latlong', datum=datum)
    lat, lon = transform(utm_proj, wgs84_proj, easting, northing)
    return {
        "lat": lat,
        "lon": lon
    }
