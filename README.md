## dvbpy

An unofficial python module giving you a few options to query a collection of publicly accessible API methods for Dresden's public transport system.

In case you're looking for something like this for node.js, check out [dvbjs](https://github.com/kiliankoe/dvbjs).

dvbpy is not available on PyPI for the time being. Please download it yourself and import it to get started.

```python
import dvb
```


### Monitor a single stop

Monitor a single stop to see every bus or tram leaving this stop after the specified time offset.

```python
import dvb

stop = 'Helmholtzstraße'
time_offset = 0 # how many minutes in the future, 0 for now
num_results = 2
city = 'Dresden'

dvb.monitor(stop, time_offset, num_results, city)
```

```python
[{
    'line': '85',
    'direction': 'Striesen',
    'arrival': 5
},
{
    'line': '85',
    'direction': 'Löbtau Süd',
    'arrival': 7
}]
```

You can also call `monitor()` without city, num_results or time_offset. City will default to Dresden.


### Find routes

Query the server for possible routes from one stop to another. Returns multiple possible trips, the bus-/tramlines to be taken, the single stops, their arrival and departure times and their GPS coordinates.

```python
import dvb
import time

origin = 'Zellescher Weg'
city_origin = 'Dresden'
destination = 'Postplatz'
city_destination = 'Dresden'
time = int(time.time()) # a unix timestamp is wanted here
deparr = 'dep'  # set to 'arr' for arrival time, 'dep' for departure time

dvb.route(origin, destination, city_origin, city_destination, time, deparr)
```

```python
{
    'trips': [{
        'interchange': 0,
        'nodes': [{
            'line': '11',
            'mode': 'Straßenbahn',
            'direction': 'Dresden Bühlau Ullersdorfer Platz',
            'path': [
                [13.745754, 51.02816],
                [13.745848, 51.028393],
                ...
            ],
            'departure': {
                'time': '18:01',
                'stop': 'Zellescher Weg',
                'coords': '13745754,51028160'
            },
            'arrival': {
                'time': '18:14',
                'stop': 'Postplatz',
                'coords': '13733717,51050544'
            }
        }],
        'duration': '00:13',
        'departure': '18:01',
        'arrival': '18:14'
    },
    ...
    }],
    'origin': 'Dresden, Zellescher Weg',
    'destination': 'Dresden, Postplatz'
}
```

Everything besides origin and destination is optional and only needs to be included if necessary. City for origin and destination defaults to Dresden, time to now and is handled as the departure time.

The path property contains a list consisting of all the coordinates describing the path of this node. Useful for example if you want to draw it on a map.


### Find stops by name

Search for a single stop in the network of the DVB.

```python
import dvb

dvb.find('zellesch')
```

```python
[{
    'name': 'Zellescher Weg',
    'city': 'Dresden',
    'coords': [51.028366, 13.745847]
}]
```

The fields `city` and `coords` are optional as they are not available for every stop. So don't forget to check for their existence first.

```python
[stop for stop in dvb.find('Post') if 'city' in stop if stop['city'] == 'Dresden']
```


### Find other POIs with coordinates - WIP

Search for all kinds of POIs inside a given square.
```python
import dvb

southwest_lat = 5654791
southwest_lng = 4620310
northeast_lat = 5657216
northeast_lng = 4623119

pintypes = 'stop'
# can be poi, platform, rentabike, ticketmachine, parkandride, carsharing or stop

dvb.pins(southwest_lat, southwest_lng, northeast_lat, northeast_lng, pintypes)
```

`pintypes` defaults to 'stop' if no other input is given.

```python
[{
    'id': 33000732,
    'name': 'Mommsenstraße',
    'coords': [5656132, 4621567],
    'connections': '2:66#3:352~360~366'
}, {
    'id': 33000512,
    'name': 'Stadtgutstraße',
    'coords': [5655763, 4621918],
    'connections': '2:85'
}, {
    'id': 33000728,
    'name': 'Staats- und Universitätsbibliothek',
    'coords': [5656319, 4622011],
    'connections': '2:61~63'
},...]
```

Unfortunately the coordinates (both input and output) are in a format called MDV which appears to be based on Gauß-Krüger, but are pretty much useless in this format. Hopefully this module will soon be able to convert them to something a little more useable.


### Look up coordinates for POI - WIP

Find the coordinates for a given POI id.
```python
import dvb

dvb.poi_coords(33000755)
```

```python
[5655203, 4623508]
```

Same coordinates issue as above.


### Address for coordinates - WIP

Look up the address for a given set of coordinates.
```python
import dvb

lat = 5656350
lng = 4622580

dvb.address(lat, lng)
```

```python
{
    'address': 'Ackermannstraße 20',
    'city': 'Dresden'
}
```

Same coordinates issue as above


### Other stuff

Stop names in queries are very forgiving. As long as the server sees it as a unique hit, it'll work. 'Helmholtzstraße' finds the same data as 'helmholtzstrasse', 'Nürnberger Platz' = 'nuernbergerplatz' etc.

One last note, be sure not to run whatever it is you're building from inside the network of the TU Dresden. Calls to `dvb.route()` and `dvb.find()` will time out. This is unfortunately expected behavior as API calls from these IP ranges are blocked.
