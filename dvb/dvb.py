import requests
import json
import pyproj
from datetime import datetime
import numpy as np

WEBAPI_BASE_URL = 'https://webapi.vvo-online.de/'
ALL_TRANSPORT_MODES = [
    'Tram',
    'CityBus',
    'IntercityBus',
    'SuburbanRailway',
    'Train',
    'Cableway',
    'Ferry',
    'HailedSharedTaxi'
]


def find(query):
    data = {
        'limit': 0,
        'query': query,
        'stopsOnly': True,
        'dvb': True,
    }
    response = _send_post_request(WEBAPI_BASE_URL + 'tr/pointfinder', data)

    points = [_parse_stopstring(stopstring) for stopstring in response['Points']]
    response['Points'] = points

    return response


def monitor(stopid, timestamp=datetime.now(), is_arrival=False, allowed_modes=ALL_TRANSPORT_MODES):
    data = {
        'stopid': stopid,
        'timestamp': timestamp.isoformat(),
        'isarrival': is_arrival,
        'limit': 0,
        'shorttermchanges': True,
        'mot': allowed_modes
    }
    response = _send_post_request(WEBAPI_BASE_URL + 'dm', data)

    departures = []
    for departure in response['Departures']:
        if 'RealTime' in departure:
            departure['RealTime'] = _parse_datestring(departure['RealTime'])
        departure['ScheduledTime'] = _parse_datestring(departure['ScheduledTime'])
        departures.append(departure)
    response['Departures'] = departures

    return response


def route_changes():
    data = {
        'shortterm': True
    }
    response = _send_post_request(WEBAPI_BASE_URL + 'rc', data)

    # omfg, this is a stupid approach
    changes = []
    for change in response['Changes']:
        change['PublishDate'] = _parse_datestring(change['PublishDate'])
        validity_periods = []
        for period in change['ValidityPeriods']:
            period['Begin'] = _parse_datestring(period['Begin'])
            if 'End' in period:
                period['End'] = _parse_datestring(period['End'])
            validity_periods.append(period)
        change['ValidityPeriods'] = validity_periods
        changes.append(change)
    response['Changes'] = changes

    return response


def _send_post_request(url, data):
    try:
        r = requests.post(url, json=data)
        if r.status_code == 200:
            response = json.loads(r.content.decode('utf-8'))
            response['ExpirationTime'] = _parse_datestring(response['ExpirationTime'])
            return response
        else:
            raise requests.HTTPError('HTTP Status: {}'.format(r.status_code))

    except requests.RequestException as e:
        print('Failed to access {}. Request exception: {}'.format(url, e))
        return None


def _parse_stopstring(stopstring):
    components = stopstring.split('|')
    return {
        'id': components[0],
        'region': components[2],
        'name': components[3],
        'coords': gk4_to_wgs(components[4], components[5])
    }


def _parse_datestring(datestring):
    millis = float(datestring.replace('/Date(', '').replace(')/', '').split('+')[0])
    return datetime.fromtimestamp(millis / 1000)


class InterPos():
    NO = None
    FRONT = 0
    MIDDLE = 1
    BACK = 2


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


def route(origin, destination, city_origin='Dresden', city_destination='Dresden', time=None,
          deparr='dep', eduroam=False, recommendations=False, *, raw=False):
    """
    VVO Online EFA TripRequest
    (GET http://efa.vvo-online.de:8080/dvb/XML_TRIP_REQUEST2)

    :param origin: Origin of route
    :param destination: Destination of route
    :param city_origin: City of origin
    :param city_destination: City of destination
    :param time: Unix timestamp of departure
    :param deparr: 'dep' for departure time (default), or 'arr' for arrival
    :param eduroam: Request from eduroam
    :param recommendations: Recommendations for interchange
    :param raw: Return raw response
    :return: List of single trips
    """

    assert deparr == 'dep' or deparr == 'arr'

    time = datetime.now() if time is None else datetime.fromtimestamp(int(time))

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
            raise requests.HTTPError('HTTP Status: {}'.format(r.status_code))
    except requests.Timeout:
        print('Failed to access VVO TripRequest. Connection timed out. Are you connected to eduroam?')
        response = None
    except requests.RequestException as e:
        print('Failed to access VVO TripRequest. Request Exception', e)
        response = None

    if response is None:
        return None

    if raw:
        return response

    prettified = {
        'origin': response['origin']['points']['point']['name'],
        'destination': response['destination']['points']['point']['name'],
        'trips': [
            process_single_trip(single_trip) for single_trip in response['trips']
            ]
    }

    if recommendations:
        prettified['trips'] = [interchange_prediction(trip) for trip in prettified['trips']]

    return prettified

def interchange_prediction(trip):

    proj = pyproj.Proj(init='epsg:4326')

    # getting all intersections (interchanges), contains exactly three points
    interchanges = [(incoming['path'][-3], # second to last point en route of the arriving route
                [int(x) / 1000000 for x in incoming['arrival']['coords'].split(',')], # stop point of the arriving route
                [int(x) / 1000000 for x in outgoing['departure']['coords'].split(',')]) # start point of the departing route
                for incoming, outgoing in zip(trip['nodes'][:-1], trip['nodes'][1:])]

    # projecting into x/y
    interchanges = [[proj(*point) for point in path] for path in interchanges]

    for i, interchange in enumerate(interchanges):
        a = np.subtract(interchange[1], interchange[0]) # direction of the arriving route

        b = np.subtract(interchange[2], interchange[1]) # direction of the walk to the departing route

        if not np.any(b):
            # same point for interchange, so why do you even care?
            trip['nodes'][i]['recommendation'] = InterPos.MIDDLE
        else:
            b = b / np.linalg.norm(b)
            a = a / np.linalg.norm(a)

            # angle between the two directions, 0° - 180°
            deg = np.degrees(np.arccos(np.dot(a,b)))

            if deg > 90:
                # departing route is "behind" your arrriving route
                trip['nodes'][i]['recommendation'] = InterPos.BACK
            else:
                # departing route is "in front" of your arriving route
                trip['nodes'][i]['recommendation'] = InterPos.FRONT

    return trip


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


def pins(swlat, swlng, nelat, nelng, pintypes='stop', *, raw=False):
    """
    DVB Map Pins
    (GET https://www.dvb.de/apps/map/pins)

    :param swlat: South-West Bounding Box Latitude
    :param swlng: South-West Bounding Box Longitude
    :param nelat: North-East Bounding Box Latitude
    :param nelng: North-East Bounding Box Longitude
    :param pintypes: Types to search for, defaults to 'stop'
    :param raw: Return raw response
    :return:
    """
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
            raise requests.HTTPError('HTTP Status: {}'.format(r.status_code))
    except requests.RequestException as e:
        print('Failed to access DVB map pins app. Request Exception', e)
        response = None

    if response is None:
        return None

    return response if raw else [pins_return_results(line, pintypes) for line in response]


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


def poi_coords(poi_id, *, raw=False):
    """
    DVB Map Coordinates
    (GET https://www.dvb.de/apps/map/coordinates)

    :param poi_id: Id of poi
    :param raw: Return raw response
    :return: Coordinates of poi
    """
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
            raise requests.HTTPError('HTTP Status: {}'.format(r.status_code))
    except requests.RequestException as e:
        print('Failed to access DVB map coordinates app. Request Exception', e)
        response = None

    if response is None or raw:
        return response

    coords = [int(i) for i in response.split('|')]
    lat, lng = gk4_to_wgs(coords[0], coords[1])
    return {
        'lat': lat,
        'lng': lng
    }


def address(lat, lng, *, raw=False):
    """
    DVB Map Address
    (GET https://www.dvb.de/apps/map/address)

    :param lat: Latitude
    :param lng: Longitude
    :param raw: Return raw response
    :return: Dict of address
    """
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
            raise requests.HTTPError('HTTP Status: {}'.format(r.status_code))
    except requests.RequestException as e:
        print('Failed to access DVB map address app. Request Exception', e)
        response = None

    if response is None:
        return None
    return response if raw else process_address(response)


def process_address(line):
    try:
        return {
            'city': line.split('|')[0],
            'address': line.split('|')[1]
        }
    except Exception as e:
        print('Address not found. Error:', e)
        return None


def wgs_to_gk4(lat, lng):
    # transforms coordinates from WGS84 to Gauss-Kruger zone 4
    wgs = pyproj.Proj(init='epsg:4326')
    gk4 = pyproj.Proj(init='epsg:5678')
    lngOut, latOut = pyproj.transform(wgs, gk4, lng, lat)
    return int(latOut), int(lngOut)


def gk4_to_wgs(lat, lng):
    # transforms coordinates from Gauss-Kruger zone 4 to WGS84
    wgs = pyproj.Proj(init='epsg:4326')
    gk4 = pyproj.Proj(init='epsg:5678')
    lngOut, latOut = pyproj.transform(gk4, wgs, lng, lat)
    return latOut, lngOut


def pincoords_to_object(lat, lng):
    lat, lng = gk4_to_wgs(lat, lng)
    return {
        'lat': lat,
        'lng': lng
    }
