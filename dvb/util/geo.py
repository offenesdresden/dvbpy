import pyproj


def wgs_to_gk4(lat, lng):
    """transforms coordinates from WGS84 to Gauss-Krüger zone 4"""
    wgs = pyproj.Proj(init='epsg:4326')
    gk4 = pyproj.Proj(init='epsg:5678')
    lng_out, lat_out = pyproj.transform(wgs, gk4, lng, lat)
    return int(lat_out), int(lng_out)


def gk4_to_wgs(lat, lng):
    """transforms coordinates from Gauss-Krüger zone 4 to WGS84"""
    wgs = pyproj.Proj(init='epsg:4326')
    gk4 = pyproj.Proj(init='epsg:5678')
    lng_out, lat_out = pyproj.transform(gk4, wgs, lng, lat)
    return lat_out, lng_out
