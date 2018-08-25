#source https://en.wikipedia.org/wiki/Haversine_formula
import math

#hav(θ) = sin²(θ/2)
def haversine(latLong2, latLong1):
    d = math.radians(latLong2-latLong1)
    return math.pow(math.sin(d/2),2)

#distance = 2*r*arcsin(x¹/²)
def distance(origin, destination):
    lat1 = origin['lat']
    lon1 = origin['lon']
    lat2 = destination['lat']
    lon2 = destination['lon']
    radius = 6371 #earth radius

    havLat = haversine(lat2, lat1)
    havLon = haversine(lon2, lon1)

    #hav(Θ) = hav(latitudes) + cos(lat1)*cos(lat2)*hav(longitudes)
    hav = havLat + (math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))) * havLon

    #2*r*arcsin(x¹/²)
    distance = 2 * radius * math.asin(math.sqrt(hav))

    return distance