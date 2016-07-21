import math

def deg2rad(deg):
    return deg * math.pi / 180

def rad2deg(rad):
    return rad * 180 / math.pi

# phi = lat in radians
# sig = lng in radians
# dfoo = delta foo
def latlng_distance(lat1, lng1, lat2, lng2):
    r = 6371000                 # earth radius, meters
    phi1 = deg2rad(lat1)
    phi2 = deg2rad(lat2)
    dphi = deg2rad(lat2 - lat1)
    dsig = deg2rad(lng2 - lng1)
    a = (math.sin(dphi / 2) * math.sin(dphi / 2) +
         math.cos(phi1) * math.cos(phi1) *
         math.sin(dsig / 2) * math.sin(dsig / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c

# given a point, find the latlng bounds that create a square that is
# 2 * radius in width and height
#
# solves the algorithm in latlng_distance going the other way
def find_bounds(lat, lng, radius):
    r = 6371000                 # earth radius, meters
    c = float(radius) / r
    c2 = c / 2
    c3 = math.tan(c2)
    c4 = c3 * c3
    a = c4 / (1 - c4)

    a2 = math.sqrt(a)
    a3 = math.asin(a2)
    dphi = a3 * 2
    dlat = rad2deg(dphi)

    phi = deg2rad(lat)
    a4 = a / (math.cos(phi) * math.cos(phi))
    a5 = math.sqrt(a4)
    a6 = math.asin(a5)
    dsig = a6 * 2
    dlng = rad2deg(dsig)
    return (
        (lat - dlat, lng - dlng),
        (lat + dlat, lng + dlng)
    )
