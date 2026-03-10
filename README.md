# dvbpy

An unofficial Python module for querying Dresden's public transport system (VVO/DVB).

Want something like this for another language? Look [here](https://github.com/kiliankoe/vvo#libraries).

```shell
pip install dvb
```

```python
import dvb
```

## Find stops

```python
dvb.find("Helmholtzstraße")
```

```python
[
    Stop(id='33000742', name='Helmholtzstraße', city='', coords=Coords(lat=51.03, lng=13.73)),
    Stop(id='36030083', name='Helmholtzstr', city='Chemnitz', coords=Coords(lat=50.83, lng=12.93)),
    ...
]
```

## Monitor a stop

```python
dvb.monitor("Helmholtzstraße", limit=2)
```

```python
[
    Departure(
        id='voe:11003: :H:j26',
        line='3',
        direction='Wilder Mann',
        scheduled=datetime(2025, 2, 22, 14, 41),
        real_time=datetime(2025, 2, 22, 14, 43, 50),
        state='Delayed',
        platform=Platform(name='1', type='Platform'),
        mode='Tram',
        occupancy='ManySeats',
    ),
    ...
]
```

Stop names are automatically resolved to IDs. You can also pass a numeric stop ID directly.

## Plan a route

```python
dvb.route("Helmholtzstraße", "Postplatz")
```

```python
[
    Route(
        duration=11,
        interchanges=0,
        price='2,30',
        fare_zones='TZ 10 (Dresden)',
        cancelled=False,
        legs=[
            PartialRoute(
                duration=11,
                line='3',
                mode='Tram',
                direction='Btf Trachenberge',
                stops=[...],
            )
        ],
        session_id='367417461:efa4',
    ),
    ...
]
```

Use the `session_id` to paginate with `dvb.earlier_later()`.

## Map pins

Search for stops, POIs, and other points of interest within a bounding box.

```python
dvb.pins(51.04, 13.70, 51.05, 13.72, pin_types=("Stop", "Platform"))
```

```python
[
    Pin(id='33000028', name='Hauptbahnhof', city='Dresden', coords=Coords(...), type='Stop'),
    Pin(id='pf:1234', name='Hauptbahnhof Gleis 3', city='Dresden', coords=Coords(...), type='Platform'),
    ...
]
```

## Lines at a stop

```python
dvb.lines("33000742")
```

```python
[
    Line(name='3', mode='Tram', directions=['Dresden Wilder Mann', 'Dresden Coschütz']),
    Line(name='66', mode='CityBus', directions=['Dresden Lockwitz']),
    ...
]
```

## Route changes

```python
dvb.route_changes()
```

```python
[
    RouteChange(
        id='511595',
        title='Dresden - Mengsstraße, Vollsperrung',
        description='<p>...</p>',
        type='Scheduled',
        validity_periods=[ValidityPeriod(begin=..., end=...)],
        lines=['428296'],
    ),
    ...
]
```

## Trip details

Get all stops for a specific departure (using the ID from a monitor response).

```python
dvb.trip_details(trip_id="71313709", time="/Date(1512563081000+0100)/", stop_id="33000077")
```

## Reverse geocoding

```python
dvb.address(51.04373, 13.70320)
```

```python
Stop(id='33000144', name='Tharandter Straße', city='Dresden', coords=Coords(...))
```

## Raw responses

All functions accept `raw=True` to get the unprocessed API response as a dict:

```python
dvb.monitor("Helmholtzstraße", raw=True)
# Returns the raw JSON dict from the WebAPI
```

## Error handling

```python
from dvb import APIError, ConnectionError

try:
    dvb.monitor("Helmholtzstraße")
except ConnectionError:
    print("Network error or timeout")
except APIError:
    print("API returned an error")
```

## Migrating from 1.x

dvb 2.0 is a complete rewrite with breaking changes:

- All functions return frozen dataclasses instead of dicts/lists
- Functions raise `APIError`/`ConnectionError` instead of printing errors and returning `None`
- Migrated from legacy widget/EFA endpoints to the VVO WebAPI
- Removed `poi_coords()` (use `find()`), `interchange_prediction()`, `city`/`eduroam`/`deparr` parameters
- `route()` uses `arrival=True/False` instead of `deparr="arr"/"dep"`, `pins()` uses `pin_types=("Stop",)` instead of `pintypes="stop"`
- Dropped `numpy`
- Requires Python >= 3.10

## Development

```bash
uv sync --group dev
uv run ruff check .
uv run ruff format --check .
uv run mypy dvb/
uv run pytest
```
