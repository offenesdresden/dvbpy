dvbpy
-----

An unofficial python module giving you a few options to query a
collection of publicly accessible API methods for Dresden's public
transport system.

In case you're looking for something like this for node.js, check out
`dvbjs <https://github.com/kiliankoe/dvbjs>`__.

dvbpy is not available on PyPI for the time being. Please download it
yourself and import it to get started.

.. code:: python

    import dvb

Requirements
~~~~~~~~~~~~

dvbpy needs **requests** for HTTP-Communication and **pyproj** for
geocoordinate transformations \* ``pip install requests`` \*
``pip install pyproj``

Monitor a single stop
~~~~~~~~~~~~~~~~~~~~~

Monitor a single stop to see every bus or tram leaving this stop after
the specified time offset.

.. code:: python

    import dvb

    stop = 'Helmholtzstraße'
    time_offset = 0 # how many minutes in the future, 0 for now
    num_results = 2
    city = 'Dresden'

    dvb.monitor(stop, time_offset, num_results, city)

.. code:: python

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

You can also call ``monitor()`` without city, num\_results or
time\_offset. City will default to Dresden.

Find routes
~~~~~~~~~~~

Query the server for possible routes from one stop to another. Returns
multiple possible trips, the bus-/tramlines to be taken, the single
stops, their arrival and departure times and their GPS coordinates.

.. code:: python

    import dvb
    import time

    origin = 'Zellescher Weg'
    city_origin = 'Dresden'
    destination = 'Postplatz'
    city_destination = 'Dresden'
    time = int(time.time()) # a unix timestamp is wanted here
    deparr = 'dep'  # set to 'arr' for arrival time, 'dep' for departure time

    dvb.route(origin, destination, city_origin, city_destination, time, deparr)

.. code:: python

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

Everything besides origin and destination is optional and only needs to
be included if necessary. City for origin and destination defaults to
Dresden, time to now and is handled as the departure time.

The path property contains a list consisting of all the coordinates
describing the path of this node. Useful for example if you want to draw
it on a map.

Find stops by name
~~~~~~~~~~~~~~~~~~

Search for a single stop in the network of the DVB.

.. code:: python

    import dvb

    dvb.find('zellesch')

.. code:: python

    [{
        'name': 'Zellescher Weg',
        'city': 'Dresden',
        'coords': [51.028366, 13.745847]
    }]

The fields ``city`` and ``coords`` are optional as they are not
available for every stop. So don't forget to check for their existence
first.

.. code:: python

    [stop for stop in dvb.find('Post') if 'city' in stop if stop['city'] == 'Dresden']

Find other POIs with coordinates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Search for all kinds of POIs inside a given square.

.. code:: python

    import dvb

    southwest_lat = 51.04120
    southwest_lng = 13.70106
    northeast_lat = 51.04615
    northeast_lng = 13.71368

    pintypes = 'stop'
    # can be poi, platform, rentabike, ticketmachine, parkandride, carsharing or stop

    dvb.pins(southwest_lat, southwest_lng, northeast_lat, northeast_lng, pintypes)

``pintypes`` defaults to 'stop' if no other input is given.

.. code:: python

    [  
       {  
          "connections":"1:7~8~9~10~11~12",
          "coords":{  
             "lat":51.04373256804444,
             "lng":13.70625638110702
          },
          "id":33000143,
          "name":"Saxoniastraße"
       },
       {  
          "connections":"2:61~90",
          "coords":{  
             "lat":51.04159705545878,
             "lng":13.7053650905211
          },
          "id":33000700,
          "name":"Ebertplatz"
       },
       {  
          "connections":"1:6~7~8~9~10~11~12#2:61~63~90~A#3:333",
          "coords":{  
             "lat":51.04372841952444,
             "lng":13.703461228676069
          },
          "id":33000144,
          "name":"Tharandter Straße"
       }, ...
    ]

Look up coordinates for POI
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Find the coordinates for a given POI id.

.. code:: python

    import dvb

    dvb.poi_coords(33000755)

.. code:: python

    {'lat': 51.018745307424005, 'lng': 13.758700156062707}

Address for coordinates - WIP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Look up the address for a given set of coordinates.

.. code:: python

    import dvb

    lat = 51.04373
    lng = 13.70320

    dvb.address(lat, lng)

.. code:: python

    {
        'city': u'Dresden',
        'address': u'Kesselsdorfer Straße 1'
    }

Other stuff
~~~~~~~~~~~

Stop names in queries are very forgiving. As long as the server sees it
as a unique hit, it'll work. 'Helmholtzstraße' finds the same data as
'helmholtzstrasse', 'Nürnberger Platz' = 'nuernbergerplatz' etc.

One last note, be sure not to run whatever it is you're building from
inside the network of the TU Dresden. Calls to ``dvb.route()`` and
``dvb.find()`` will time out. This is unfortunately expected behavior as
API calls from these IP ranges are blocked.
