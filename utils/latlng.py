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

def get_cardinal_direction(lat1, lng1, lat2, lng2):
    phi1 = deg2rad(lat1)
    phi2 = deg2rad(lat2)
    dsig = deg2rad(lng2 - lng1)
    x = math.cos(phi2) * math.sin(dsig)
    y = math.cos(phi1) * math.sin(phi2) - \
        math.sin(phi1) * math.cos(phi2) * math.cos(dsig)
    bearing = math.atan2(x, y)
    slot1 = ''
    slot2 = ''
    slot3 = ''
    mark = math.pi / 16
    if 7 * -mark < bearing and bearing <= 7 * mark:
        slot1 = 'N'
        if 3 * -mark < bearing and bearing <= 3 * mark:
            slot2 = 'N'
    elif bearing <= 9 * -mark or 9 * mark < bearing:
        slot1 = 'S'
        if bearing <= 13 * -mark or 13 * mark < bearing:
            slot2 = 'S'
    if mark < bearing and bearing <= 15 * mark:
        slot3 = 'E'
        if 5 * mark < bearing and bearing <= 11 * mark:
            slot2 = 'E'
    elif 15 * -mark < bearing and bearing <= -mark:
        slot3 = 'W'
        if 11 * -mark < bearing and bearing <= 5 * -mark:
            slot2 = 'W'

    if slot1 == '' or slot3 == '':
        slot2 = ''

    return '%s%s%s' % (slot1, slot2, slot3)

if __name__ == '__main__':
    None
