import requests
import json
import time


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
        connections = [
        {
            'line': line,
            'direction': direction,
            'arrival': arrival
        } for line, direction, arrival in response]
        return connections


def find(search, eduroam=False):
    # VVO Online EFA Stopfinder
    # (GET http://efa.vvo-online.de:8080/dvb/XML_STOPFINDER_REQUEST)
    try:
        if eduroam:
            url = 'http://efa.faplino.de/dvb/XML_STOPFINDER_REQUEST'
        else:
            url = 'http://efa.vvo-online.de:8080/dvb/XML_STOPFINDER_REQUEST'
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
            timeout=5
        )
        if r.status_code == 200:
            response = json.loads(r.content.decode('utf-8'))
        else:
            print('Failed to access VVO monitor. HTTP Error ' + r.status_code)
            response = None
    except requests.exceptions.Timeout:
        print('Failed to access VVO monitor. Connection timed out. Are you in Eduroam?')
        response = None
    except requests.exceptions.RequestException as e:
        print('Failed to access VVO monitor. Request Exception ' + e)
        response = None

    if response is None:
        return response
    else:
        results = []
        # there's only a single result
        if 'point' in response['stopFinder']['points']:
            stop = response['stopFinder']['points']['point']
            if 'object' in stop:
                    results.append({
                        'name': stop['object'],
                        'city': stop['posttown'],
                        'coords': convert_coords(stop['ref']['coords'])
                    })
            else:
                results.append({
                    'name': stop['name'],
                    'coords': convert_coords(stop['ref']['coords'])
                })
        # multiple results
        else:
            for stop in response['stopFinder']['points']:
                if 'object' in stop:
                    results.append({
                        'name': stop['object'],
                        'city': stop['posttown'],
                        'coords': convert_coords(stop['ref']['coords'])
                    })
                else:
                    results.append({
                        'name': stop['name'],
                        'coords': convert_coords(stop['ref']['coords'])
                    })

        return results


def convert_coords(coords):
    coords = coords.split(',')
    for i in range(len(coords)):
        coords[i] = int(coords[i])
        coords[i] /= 1000000
    return coords
