## dvbpy

An unofficial python module giving you a few options to query Dresden's public transport system for current bus- and tramstop data.

Install and import the module to get started.

```sh
$ pip install dvbpy
```

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
    'arrival': '5'
},
{
    'line': '85',
    'direction': 'Löbtau Süd',
    'arrival': '7'
}]
```

You can also call `monitor()` without city, num_results or time_offset. City will default to Dresden.


### Find routes - WIP

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


### Find stops

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

The fields `city` and `coords` are optional as they are not available for every stop. So don't forget to check for their existance first.

```python
[stop for stop in dvb.find('Post') if 'city' in stop if stop['city'] == 'Dresden']
```

### Other stuff

Stop names in queries are very forgiving. As long as the server sees it as a unique hit, it'll work. 'Helmholtzstraße' finds the same data as 'helmholtzstrasse', 'Nürnberger Platz' = 'nuernbergerplatz' etc.

One last note, be sure not to run whatever it is you're building from inside the network of the TU Dresden. Calls to everything but `dvb.monitor()` will time out. This is unfortunately expected behavior as API calls from these IP ranges are blocked.
