import requests, json
from peewee import *
from datetime import timedelta, datetime
from collections import namedtuple
import haversine

database = PostgresqlDatabase('desafio_2xt', user='postgres', password='admin')
class BaseModel(Model):
    class Meta:
        database = database
    
class Airport(BaseModel):
    iata = CharField(unique=True, max_length=3, primary_key=True)
    city = CharField(max_length = 200)
    lat = CharField(max_length = 15)
    lon = CharField(max_length = 15)
    state = CharField(max_length = 2)

class Aircraft(BaseModel):
    nrseqaircraft = IntegerField(unique=True, primary_key=True)
    model = CharField(max_length = 20)
    manufacturer = CharField(max_length = 100)

class Trip(BaseModel):
    nrseqtrip = IntegerField(unique=True, primary_key=True)
    iatadeparture = ForeignKeyField(Airport, backref='departure')
    iataarrival   = ForeignKeyField(Airport, backref='arrival')
    currency = CharField(max_length = 3)
    distance = IntegerField()
    searchurl = CharField(max_length = 90)
    cheapestprice = FloatField(null = True)
    cheapestflightaircraft = ForeignKeyField(Aircraft, backref='aircraft', null = True)

class Flight(BaseModel):
    nrseqtrip = ForeignKeyField(Trip, backref='trip')
    nrseqaircraft   = ForeignKeyField(Aircraft, backref='aircraft')
    departuretime = DateTimeField()
    arrivaltime = DateTimeField()
    fareprice = FloatField()
    priceperkm = FloatField()
    flighthours = FloatField()
    flightspeed = FloatField()

database.create_tables([Airport, Aircraft, Trip, Flight])

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
        #fixes tuple's field name problem
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

def toDateTime(str):
    return datetime.strptime(str, '%Y-%m-%dT%H:%M:%S')

#subtract dates, return difference in hours
def subtractDate(date1, date2):
    date2 = toDateTime(date2)
    date1 = toDateTime(date1)
    diff = date2 - date1
    return (diff.total_seconds() / 3600)


#json with all airport data
airports = doGetRequest(airportsURL, auth, 'airport')

#insert the airports
for airport in airports:
    try:
        Airport.get(Airport.iata == airport.iata)
    except Airport.DoesNotExist:
        (Airport.create(iata = airport.iata, city = airport.city, lat = airport.lat, lon = airport.lon, state = airport.state))

nrseqtrip = 0
nrseqaircraft = 0
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
            #haversine
            distance = round(getDistanceByLatLong(departureLatlong, arrivalLatlong))
            
            #insert trip
            try:
                trip = Trip.get(Trip.iatadeparture == departureAirport.iata, Trip.iataarrival == arrivalAirport.iata)
                #if this trip already exists, update pk
                nrseqtrip = trip.nrseqtrip+1
            except Trip.DoesNotExist:
                trip = Trip.create(nrseqtrip = nrseqtrip, currency = flightSearch.summary.currency, distance = distance, searchurl = searchURL, iatadeparture = departureAirport.iata, iataarrival = arrivalAirport.iata)
                #else, sum
                nrseqtrip += 1

            #loop into flight options, searching the cheapest one
            cheapestPrice = None
            cheapestAircraft = None
            for flight in flightSearch.options:
                #speed in km/hour
                hoursOfFlight = subtractDate(flight.departure_time, flight.arrival_time)
                flightSpeed = distance / hoursOfFlight

                #price
                price = flight.fare_price
                pricePerKm = price / distance

                #insert aircraft
                try:
                    aircraft = Aircraft.get(Aircraft.model == flight.aircraft.model and Aircraft.manufacturer == flight.aircraft.manufacturer)
                    #if this trip already exists, update pk
                    nrseqaircraft = aircraft.nrseqaircraft+1
                except Aircraft.DoesNotExist:
                    aircraft = Aircraft.create(nrseqaircraft = nrseqaircraft, model = flight.aircraft.model, manufacturer = flight.aircraft.manufacturer)
                    #else, sum
                    nrseqaircraft += 1
                
                cheapestPrice = price if (cheapestPrice == None or price < cheapestPrice) else cheapestPrice
                cheapestAircraft = aircraft.nrseqaircraft if (cheapestPrice == price) else cheapestAircraft
                
                #insert flight
                Flight.create(nrseqtrip = trip.nrseqtrip, nrseqaircraft = aircraft.nrseqaircraft, departuretime = toDateTime(flight.departure_time), arrivaltime = toDateTime(flight.arrival_time), fareprice = flight.fare_price, priceperkm = pricePerKm, flighthours = hoursOfFlight, flightspeed = flightSpeed)

            trip.cheapestprice = cheapestPrice
            trip.cheapestflightaircraft = cheapestAircraft

            trip.save()


                
                
                










