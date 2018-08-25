import requests, json
from datetime import timedelta, datetime
from collections import namedtuple
import haversine

airportsURL = 'http://stub.2xt.com.br/air/airports/oKexeaxSLvOqwGGq9DiDKEKaEQMmgAv3'
searchURL = 'http://stub.2xt.com.br/air/search/oKexeaxSLvOqwGGq9DiDKEKaEQMmgAv3'
auth = ('arthur', 'rHaxea')

#sum 40 days from current date
departureDate = datetime.now() + timedelta(days=40)
departureDate = departureDate.strftime("%Y-%m-%d")

#generic get request, return python object
def doGetRequest(url, auth, name):
    #Found at question 6578986 stack overflow
    def _json_object_hook(d): return namedtuple(name, d.keys())(*d.values())
    def json2obj(data): return json.loads(data, object_hook=_json_object_hook)
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        jsonResponse = response.text
        jsonResponse = jsonResponse.replace('from', 'fromAirport')
        return json2obj(jsonResponse)
    else:
        response.raise_for_status()

#build search URL based in airports and departure date
def buildSearchURL(departure, arrival, date):
    returnURL = searchURL + '/'  + departure + '/' + arrival + '/' + date
    return returnURL

#use Haversine to calculate distance between two airports
def getDistanceByLatLong(departure, arrival):
    return haversine.distance(departure, arrival)    


#json with all airport data
airports = doGetRequest(airportsURL, auth, 'airport')

for departureAirport in airports:
    for arrivalAirport in airports:
        #do it for all airport x airport combination, except if both it's the same
        if(departureAirport.iata != arrivalAirport.iata):
            url = buildSearchURL(departureAirport.iata, arrivalAirport.iata, departureDate)
            flightSearch = doGetRequest(url, auth, 'search')

            arrivalLatlong = {
                'lat': arrivalAirport.lat,
                'lon': arrivalAirport.lon,
            }

            departureLatlong = {
                'lat': departureAirport.lat,
                'lon': departureAirport.lon,
            }

            distance = round(getDistanceByLatLong(departureLatlong, arrivalLatlong))






