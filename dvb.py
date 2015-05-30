import requests
import json
import pyproj
from datetime import datetime


def monitor(stop, offset=0, limit=10, city='Dresden'):
    # VVO Online Monitor
    # (GET http://widgets.vvo-online.de/abfahrtsmonitor/Abfahrten.do)
    try:
        r = requests.get(
            url='http://widgets.vvo-online.de/abfahrtsmonitor/Abfahrten.do',
            params={
                'ort': city,
                'hst': stop,
                'vz': offset,
                'lim': limit,
            },
        )
        if r.status_code == 200:
            response = json.loads(r.content.decode('utf-8'))
        else:
            print('Failed to access VVO monitor. HTTP Error ' + r.status_code)
            response = None
    except requests.RequestException as e:
        print('Failed to access VVO monitor. Request Exception ' + e)
        response = None

    if response is None:
        return response
    else:
        return [
            {
                'line': line,
                'direction': direction,
                'arrival': int(arrival)
            } for line, direction, arrival in response
        ]


def process_single_trip(single_trip):
    def process_leg(leg):
        path = [convert_coords(a) for a in leg['path'].split(' ')] if 'path' in leg else None

        departure = {
            'stop': leg['points'][0]['nameWO'],
            'time': leg['points'][0]['dateTime']['time'],
            'coords': leg['points'][0]['ref']['coords']
        }

        arrival = {
            'stop': leg['points'][1]['nameWO'],
            'time': leg['points'][1]['dateTime']['time'],
            'coords': leg['points'][1]['ref']['coords']
        }

        return {
            'mode': leg['mode']['product'],
            'line': leg['mode']['number'],
            'direction': leg['mode']['destination'],
            'departure': departure,
            'arrival': arrival,
            'path': path
        }

    return {
        'departure': single_trip['legs'][0]['points'][0]['dateTime']['time'],
        'arrival': single_trip['legs'][-1]['points'][-1]['dateTime']['time'],
        'duration': single_trip['duration'],
        'interchange': int(single_trip['interchange']),
        'nodes': [process_leg(leg) for leg in single_trip['legs']]
    }


def route(origin, destination, city_origin='Dresden', city_destination='Dresden', time=0, deparr='dep', eduroam=False):
    # VVO Online EFA TripRequest
    # (GET http://efa.vvo-online.de:8080/dvb/XML_TRIP_REQUEST2)

    time = datetime.now() if time == 0 else datetime.fromtimestamp(int(datetime))

    url = 'http://efa.faplino.de/dvb/XML_TRIP_REQUEST2' if eduroam \
        else 'http://efa.vvo-online.de:8080/dvb/XML_TRIP_REQUEST2'

    try:
        r = requests.get(
            url=url,
            params={
                'sessionID': '0',
                'requestID': '0',
                'language': 'de',
                'execInst': 'normal',
                'command': '',
                'ptOptionsActive': '-1',
                'itOptionsActive': '',
                'itDateDay': time.day,
                'itDateMonth': time.month,
                'itDateYear': time.year,
                'place_origin': city_origin,
                'placeState_origin': 'empty',
                'type_origin': 'stop',
                'name_origin': origin,
                'nameState_origin': 'empty',
                'place_destination': city_destination,
                'placeState_destination': 'empty',
                'type_destination': 'stop',
                'name_destination': destination,
                'nameState_destination': 'empty',
                'itdTripDateTimeDepArr': deparr,
                'itdTimeHour': time.hour,
                'idtTimeMinute': time.minute,
                'outputFormat': 'JSON',
                'coordOutputFormat': 'WGS84',
                'coordOutputFormatTail': '0',
            },
            timeout=10
        )
        if r.status_code == 200:
            response = json.loads(r.content.decode('utf-8'))
        else:
            print('Failed to access VVO TripRequest. HTTP Error ' + r.status_code)
            response = None
    except requests.Timeout:
        print('Failed to access VVO TripRequest. Connection timed out. Are you connected to eduroam?')
        response = None
    except requests.RequestException as e:
        print('Failed to access VVO TripRequest. Request Exception ' + e)
        response = None

    if response is None:
        return response
    else:
        return {
            'origin': response['origin']['points']['point']['name'],
            'destination': response['destination']['points']['point']['name'],
            'trips': [
                process_single_trip(single_trip) for single_trip in response['trips']
            ]
        }


def find(search, eduroam=False):
    # VVO Online EFA Stopfinder
    # (GET http://efa.vvo-online.de:8080/dvb/XML_STOPFINDER_REQUEST)
    url = 'http://efa.faplino.de/dvb/XML_STOPFINDER_REQUEST' if eduroam \
        else 'http://efa.vvo-online.de:8080/dvb/XML_STOPFINDER_REQUEST'

    try:
        r = requests.get(
            url=url,
            params={
                'locationServerActive': '1',
                'outputFormat': 'JSON',
                'type_sf': 'any',
                'name_sf': search,
                'coordOutputFormat': 'WGS84',
                'coordOutputFormatTail': '0',
            },
            timeout=10
        )
        if r.status_code == 200:
            response = json.loads(r.content.decode('utf-8'))
        else:
            print('Failed to access VVO StopFinder. HTTP Error ' + r.status_code)
            response = None
    except requests.Timeout:
        print('Failed to access VVO StopFinder. Connection timed out. Are you connected to eduroam?')
        response = None
    except requests.RequestException as e:
        print('Failed to access VVO StopFinder. Request Exception ' + e)
        response = None

    if response is None:
        return response
    else:
        points = response['stopFinder']['points']
        return [
            # single result
            find_return_results(points['point'])
        ] if 'point' in points else [
            # multiple results
            find_return_results(stop)
            for stop in points
        ]


def find_return_results(stop):
    if 'object' in stop and 'coords' in stop['ref']:
        # city and coords
        return {
            'name': stop['object'],
            'city': stop['posttown'],
            'coords': convert_coords(stop['ref']['coords'])
        }
    elif 'object' in stop:
        # only city, no coords
        return {
            'name': stop['object'],
            'city': stop['posttown']
        }
    elif 'coords' in stop['ref']:
        # only coords, no city
        return {
            'name': stop['name'],
            'coords': convert_coords(stop['ref']['coords'])
        }
    else:
        # neither city or coords
        return {
            'name': stop['name']
        }


def convert_coords(coords):
    # for i in coords.split(','):
    #     yield int(i) / 1000000
    coords = coords.split(',')
    for i in range(len(coords)):
        coords[i] = int(coords[i])
        coords[i] /= 1000000
    return coords


def pins(swlat, swlng, nelat, nelng, pintypes='stop'):
    # DVB Map Pins (GET https://www.dvb.de/apps/map/pins)
    try:
        swlat, swlng = wgs_to_gk4(swlat, swlng)
        nelat, nelng = wgs_to_gk4(nelat, nelng)
        r = requests.get(
            url='https://www.dvb.de/apps/map/pins',
            params={
                'showlines': 'true',
                'swlat': swlat,
                'swlng': swlng,
                'nelat': nelat,
                'nelng': nelng,
                'pintypes': pintypes,
            },
        )
        if r.status_code == 200:
            response = json.loads(r.content.decode('utf-8'))
        else:
            print('Failed to access DVB map pins app. HTTP Error ' + r.status_code)
            response = None
    except requests.RequestException as e:
        print('Failed to access DVB map pins app. Request Exception ' + e)
        response = None

    if response is None:
        return response
    else:
        return [pins_return_results(line, pintypes) for line in response]


def pins_return_results(line, pintypes):
    if pintypes == 'stop':
        return {
            'id': int(line.split('|||')[0]),
            'name': line.split('||')[1].split('|')[1],
            'coords': pincoords_to_object(
                int(line.split('||')[1].split('|')[2]),
                int(line.split('||')[1].split('|')[3])
            ),
            'connections': line.split('||')[2]
        }
    elif pintypes == 'platform':
        return {
            'name': line.split('||')[1].split('|')[0],
            'coords': pincoords_to_object(
                int(line.split('||')[1].split('|')[1]),
                int(line.split('||')[1].split('|')[2])
            ),
            '?': line.split('||')[1].split('|')[3]
        }
    elif pintypes == 'poi' or pintypes == 'rentabike' or pintypes == 'ticketmachine' \
            or pintypes == 'carsharing' or pintypes == 'parkandride':
        return {
            'id': ':'.join(line.split('||')[0].split(':')[:3]),
            'name': line.split('||')[1].split('|')[0],
            'coords': pincoords_to_object(
                int(line.split('||')[1].split('|')[1]),
                int(line.split('||')[1].split('|')[2])
            )
        }


def poi_coords(poi_id):
    # DVB Map Coordinates (GET https://www.dvb.de/apps/map/coordinates)
    try:
        r = requests.get(
            url='https://www.dvb.de/apps/map/coordinates',
            params={
                'id': poi_id,
            },
        )
        if r.status_code == 200:
            response = json.loads(r.content.decode('utf-8'))
        else:
            print('Failed to access DVB map coordinates app. HTTP Error ' + r.status_code)
            response = None
    except requests.RequestException as e:
        print('Failed to access DVB map coordinates app. Request Exception ' + e)
        response = None

    if response is None:
        return response
    else:
        coords = [int(i) for i in response.split('|')]
        lat, lng = gk4_to_wgs(coords[0], coords[1])
        return {
            'lat': lat,
            'lng': lng
        }


def address(lat, lng):
    # DVB Map Address (GET https://www.dvb.de/apps/map/address)
    try:
        lat, lng = wgs_to_gk4(lat, lng)
        r = requests.get(
            url='https://www.dvb.de/apps/map/address',
            params={
                'lat': lat,
                'lng': lng,
            },
        )
        if r.status_code == 200:
            response = json.loads(r.content.decode('utf-8'))
        else:
            print('Failed to access DVB map address app. HTTP Error ' + r.status_code)
            response = None
    except requests.RequestException as e:
        print('Failed to access DVB map address app. Request Exception ' + e)
        response = None

    if response is None:
        return response
    else:
        return process_address(response)


def process_address(line):
    try:
        return {
            'city': line.split('|')[0],
            'address': line.split('|')[1]
        }
    except Exception as e:
        print('Address not found. Error: ' + e.__str__())
        return None

def wgs_to_gk4(lat, lng):
    #transforms coordinates from WGS84 to Gauss-Kruger zone 4
    wgs = pyproj.Proj(init='epsg:4326')
    gk4 = pyproj.Proj(init='epsg:5678')
    lngOut, latOut = pyproj.transform(wgs,gk4,lng,lat)
    return int(latOut), int(lngOut)

def gk4_to_wgs(lat, lng):
    #transforms coordinates from Gauss-Kruger zone 4 to WGS84
    wgs = pyproj.Proj(init='epsg:4326')
    gk4 = pyproj.Proj(init='epsg:5678')
    lngOut, latOut = pyproj.transform(gk4,wgs,lng,lat)
    return latOut, lngOut

def pincoords_to_object (lat, lng):
    lat, lng = gk4_to_wgs(lat, lng)
    return {
        'lat': lat,
        'lng': lng
    }

