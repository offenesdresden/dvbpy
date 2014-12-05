import requests
import json
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
    except requests.exceptions.RequestException as e:
        print('Failed to access VVO monitor. Request Exception ' + e)
        response = None

    if response is None:
        return response
    else:
        connections = [{
            'line': line,
            'direction': direction,
            'arrival': arrival
        } for line, direction, arrival in response]
        return connections


def route(origin, destination, city_origin='Dresden', city_destination='Dresden', time=0, deparr='dep', eduroam=False):
    # VVO Online EFA TripRequest
    # (GET http://efa.vvo-online.de:8080/dvb/XML_TRIP_REQUEST2)

    if time == 0:
        time = datetime.now()
    else:
        time = datetime.fromtimestamp(int(datetime))

    if eduroam:
        url = 'http://efa.faplino.de/dvb/XML_TRIP_REQUEST2'
    else:
        url = 'http://efa.vvo-online.de:8080/dvb/XML_TRIP_REQUEST2'
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
    except requests.exceptions.Timeout:
        print('Failed to access VVO TripRequest. Connection timed out. Are you in Eduroam?')
        response = None
    except requests.exceptions.RequestException as e:
        print('Failed to access VVO TripRequest. Request Exception ' + e)
        response = None

    if response is None:
        return response
    else:
        found_trips = {
            'origin': response['origin']['points']['point']['name'],
            'destination': response['destination']['points']['point']['name'],
            'trips': []
        }

        # iterate over all trips
        for single_trip in response['trips']:
            departure = single_trip['legs'][0]['points'][0]['dateTime']['time']
            arrival = single_trip['legs'][-1]['points'][-1]['dateTime']['time']
            duration = single_trip['duration']
            interchange = int(single_trip['interchange'])

            trip = {
                'departure': departure,
                'arrival': arrival,
                'duration': duration,
                'interchange': interchange,
                'nodes': []
            }

            # iterate over single elements of this trip (e.g. bus -> tram -> bus -> on foot etc.)
            for leg in single_trip['legs']:
                mode = leg['mode']['product']
                line = leg['mode']['number']
                direction = leg['mode']['destination']

                if 'path' in leg:
                    path = leg['path']
                    path = path.split(' ')

                    for i in range(len(path)):
                        path[i] = convert_coords(path[i])

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

                node = {
                    'mode': mode,
                    'line': line,
                    'direction': direction,
                    'departure': departure,
                    'arrival': arrival,
                    'path': path
                }

                # TODO: Cleanup both evil appends.
                trip['nodes'].append(node)

            found_trips['trips'].append(trip)

        return found_trips


def find(search, eduroam=False):
    # VVO Online EFA Stopfinder
    # (GET http://efa.vvo-online.de:8080/dvb/XML_STOPFINDER_REQUEST)
    if eduroam:
        url = 'http://efa.faplino.de/dvb/XML_STOPFINDER_REQUEST'
    else:
        url = 'http://efa.vvo-online.de:8080/dvb/XML_STOPFINDER_REQUEST'
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
    except requests.exceptions.Timeout:
        print('Failed to access VVO StopFinder. Connection timed out. Are you in Eduroam?')
        response = None
    except requests.exceptions.RequestException as e:
        print('Failed to access VVO StopFinder. Request Exception ' + e)
        response = None

    if response is None:
        return response
    else:
        points = response['stopFinder']['points']
        results = [
            # single result
            find_return_results(points['point'])
        ] if 'point' in points else [
            # multiple results
            find_return_results(stop)
            for stop in points
        ]
        return results


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
    coords = coords.split(',')
    for i in range(len(coords)):
        coords[i] = int(coords[i])
        coords[i] /= 1000000
    return coords
