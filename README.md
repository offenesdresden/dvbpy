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

origin = 'Zellescher Weg'
destination = 'Postplatz'
time = int(time.time())
deparr = 'dep'  # set to 'arr' for arrival time, 'dep' for departure time

dvb.route(origin, destination, time, deparr)
```

```python

```

The path property contains a list consisting of all the coordinates describing the path of this node. Useful for example to draw on a map.


### Find stops

Search for a single stop in the network of the DVB. Returns an array of all possible hits including their GPS coordinates.

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
