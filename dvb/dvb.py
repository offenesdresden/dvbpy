"""DVB/VVO public transport API client using the VVO WebAPI."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests

from ._utils import coords_gk4_to_wgs, coords_wgs_to_gk4, parse_date, parse_point
from .exceptions import APIError
from .exceptions import ConnectionError as DVBConnectionError
from .models import (
    Coords,
    Departure,
    Line,
    PartialRoute,
    Pin,
    Platform,
    RegularStop,
    Route,
    RouteChange,
    Stop,
    ValidityPeriod,
)

BASE_URL = "https://webapi.vvo-online.de"
_TIMEOUT = 15


def _post(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    """POST to a WebAPI endpoint and return the parsed JSON response."""
    payload["format"] = "json"
    try:
        r = requests.post(
            f"{BASE_URL}/{endpoint}",
            json=payload,
            headers={"Content-Type": "application/json; charset=UTF-8"},
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        raise DVBConnectionError(str(e)) from e

    data: dict[str, Any] = r.json()
    status = data.get("Status", {}).get("Code", "")
    if status != "Ok":
        msg = f"API returned status: {status}"
        raise APIError(msg)
    return data


def _get(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    """GET from a WebAPI endpoint and return the parsed JSON response."""
    params["format"] = "json"
    try:
        r = requests.get(
            f"{BASE_URL}/{endpoint}",
            params=params,
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        raise DVBConnectionError(str(e)) from e

    data: dict[str, Any] = r.json()
    status = data.get("Status", {}).get("Code", "")
    if status != "Ok":
        msg = f"API returned status: {status}"
        raise APIError(msg)
    return data


def _resolve_stop_id(stop: str) -> str:
    """Resolve a stop name to its numeric ID. Returns as-is if already numeric."""
    if stop.isdigit():
        return stop
    results = find(stop)
    if not isinstance(results, list) or not results:
        msg = f"No stops found for query: {stop}"
        raise APIError(msg)
    return results[0].id


def _parse_platform(data: dict[str, Any] | None) -> Platform | None:
    """Parse a Platform object from API response data."""
    if not data:
        return None
    return Platform(name=data.get("Name", ""), type=data.get("Type", ""))


def _parse_regular_stop(data: dict[str, Any]) -> RegularStop:
    """Parse a RegularStop from a trip/departure response."""
    coords = None
    lat = data.get("Latitude")
    lng = data.get("Longitude")
    if lat and lng:
        coords = coords_gk4_to_wgs(int(lat), int(lng))

    arrival = _try_parse_date(data.get("ArrivalTime") or data.get("Time"))
    departure = _try_parse_date(data.get("DepartureTime") or data.get("Time"))
    arrival_rt = _try_parse_date(data.get("ArrivalRealTime") or data.get("RealTime"))
    departure_rt = _try_parse_date(data.get("DepartureRealTime") or data.get("RealTime"))

    return RegularStop(
        id=data.get("DataId") or data.get("Id", ""),
        name=data.get("Name", ""),
        city=data.get("Place", ""),
        platform=_parse_platform(data.get("Platform")),
        coords=coords,
        arrival=arrival,
        departure=departure,
        arrival_real_time=arrival_rt,
        departure_real_time=departure_rt,
        occupancy=data.get("Occupancy", "Unknown"),
    )


def _try_parse_date(s: str | None) -> datetime | None:
    """Parse a date string, returning None if input is None or invalid."""
    if not s:
        return None
    try:
        return parse_date(s)
    except ValueError:
        return None


def _parse_route(route_data: dict[str, Any], session_id: str | None = None) -> Route:
    """Parse a Route from a trips response."""
    legs: list[PartialRoute] = []
    for pr in route_data.get("PartialRoutes", []):
        mot = pr.get("Mot", {})
        stops = [_parse_regular_stop(rs) for rs in pr.get("RegularStops", [])]

        path: list[Coords] | None = None
        map_data_index = pr.get("MapDataIndex")
        route_map_data = route_data.get("MapData", [])
        if map_data_index is not None and map_data_index < len(route_map_data):
            path = _parse_map_data(route_map_data[map_data_index])

        legs.append(
            PartialRoute(
                duration=pr.get("Duration", 0),
                line=mot.get("Name", ""),
                mode=mot.get("Type", ""),
                direction=mot.get("Direction", "").strip(),
                stops=stops,
                cancelled=pr.get("TripCancelled", False),
                changeover_endangered=pr.get("ChangeoverEndangered", False),
                path=path,
            )
        )

    return Route(
        duration=route_data.get("Duration", 0),
        interchanges=route_data.get("Interchanges", 0),
        price=route_data.get("Price", ""),
        fare_zones=route_data.get("FareZoneNames", ""),
        cancelled=route_data.get("RouteCancelled", False),
        legs=legs,
        session_id=session_id,
    )


def _parse_map_data(map_str: str) -> list[Coords]:
    """Parse pipe-delimited GK4 map data into Coords list."""
    parts = map_str.split("|")
    # First element is the transport mode, then alternating lat/lng pairs
    coords: list[Coords] = []
    i = 1
    while i + 1 < len(parts):
        try:
            lat = int(parts[i])
            lng = int(parts[i + 1])
            coords.append(coords_gk4_to_wgs(lat, lng))
        except (ValueError, IndexError):
            pass
        i += 2
    return coords


# --- Public API functions ---


def find(query: str, *, raw: bool = False) -> list[Stop] | dict[str, Any]:
    """Find stops by name.

    Args:
        query: Search query string.
        raw: If True, return the raw API response dict.

    Returns:
        List of Stop objects, or raw dict if raw=True.

    Raises:
        APIError: If the API returns an error status.
        ConnectionError: If the request fails.
    """
    data = _get("tr/pointfinder", {"query": query, "stopsOnly": "true"})

    if raw:
        return data

    points = data.get("Points", [])
    return [parse_point(p) for p in points if p]


def monitor(
    stop: str,
    *,
    offset: int = 0,
    limit: int = 10,
    raw: bool = False,
) -> list[Departure] | dict[str, Any]:
    """Get departures from a stop.

    Args:
        stop: Stop name or numeric stop ID.
        offset: Time offset in minutes (not currently used by WebAPI, reserved).
        limit: Maximum number of departures to return.
        raw: If True, return the raw API response dict.

    Returns:
        List of Departure objects, or raw dict if raw=True.

    Raises:
        APIError: If the API returns an error or stop not found.
        ConnectionError: If the request fails.
    """
    stop_id = _resolve_stop_id(stop)
    payload: dict[str, Any] = {"stopid": stop_id, "limit": limit}
    if offset:
        now = datetime.now(tz=timezone.utc)
        payload["time"] = now.isoformat()

    data = _post("dm", payload)

    if raw:
        return data

    departures: list[Departure] = []
    for dep in data.get("Departures", []):
        scheduled = parse_date(dep["ScheduledTime"])
        real_time = _try_parse_date(dep.get("RealTime"))

        departures.append(
            Departure(
                id=dep.get("Id", ""),
                line=dep.get("LineName", ""),
                direction=dep.get("Direction", ""),
                scheduled=scheduled,
                real_time=real_time,
                state=dep.get("State", ""),
                platform=_parse_platform(dep.get("Platform")),
                mode=dep.get("Mot", ""),
                occupancy=dep.get("Occupancy", "Unknown"),
            )
        )

    return departures


def route(
    origin: str,
    destination: str,
    *,
    time: datetime | None = None,
    arrival: bool = False,
    raw: bool = False,
) -> list[Route] | dict[str, Any]:
    """Plan a trip between two stops.

    Args:
        origin: Origin stop name or ID.
        destination: Destination stop name or ID.
        time: Departure or arrival time. Defaults to now.
        arrival: If True, interpret time as arrival time.
        raw: If True, return the raw API response dict.

    Returns:
        List of Route objects, or raw dict if raw=True.

    Raises:
        APIError: If the API returns an error or stops not found.
        ConnectionError: If the request fails.
    """
    origin_id = _resolve_stop_id(origin)
    dest_id = _resolve_stop_id(destination)

    if time is None:
        time = datetime.now(tz=timezone.utc)

    payload: dict[str, Any] = {
        "origin": origin_id,
        "destination": dest_id,
        "time": time.isoformat(),
        "isarrivaltime": arrival,
        "shorttermchanges": True,
    }

    data = _post("tr/trips", payload)

    if raw:
        return data

    session_id = data.get("SessionId")
    return [_parse_route(r, session_id) for r in data.get("Routes", [])]


def pins(
    sw_lat: float,
    sw_lng: float,
    ne_lat: float,
    ne_lng: float,
    *,
    pin_types: tuple[str, ...] = ("Stop",),
    raw: bool = False,
) -> list[Pin] | dict[str, Any]:
    """Get map pins within a bounding box.

    Args:
        sw_lat: Southwest latitude (WGS84).
        sw_lng: Southwest longitude (WGS84).
        ne_lat: Northeast latitude (WGS84).
        ne_lng: Northeast longitude (WGS84).
        pin_types: Types of pins to include (e.g. "Stop", "Platform", "Poi").
        raw: If True, return the raw API response dict.

    Returns:
        List of Pin objects, or raw dict if raw=True.

    Raises:
        APIError: If the API returns an error status.
        ConnectionError: If the request fails.
    """
    sw_gk4_lat, sw_gk4_lng = coords_wgs_to_gk4(sw_lat, sw_lng)
    ne_gk4_lat, ne_gk4_lng = coords_wgs_to_gk4(ne_lat, ne_lng)

    payload: dict[str, Any] = {
        "swlat": str(sw_gk4_lat),
        "swlng": str(sw_gk4_lng),
        "nelat": str(ne_gk4_lat),
        "nelng": str(ne_gk4_lng),
        "pintypes": list(pin_types),
    }

    data = _post("map/pins", payload)

    if raw:
        return data

    result: list[Pin] = []
    for pin_str in data.get("Pins", []):
        if not pin_str:
            continue
        parts = pin_str.split("|")
        pin_id = parts[0] if parts else ""
        city = parts[2] if len(parts) > 2 else ""
        name = parts[3] if len(parts) > 3 else ""

        coords = None
        if len(parts) > 5:
            lat_str = parts[4]
            lng_str = parts[5]
            if lat_str and lng_str and lat_str != "0" and lng_str != "0":
                coords = coords_gk4_to_wgs(int(lat_str), int(lng_str))

        # Determine type from ID prefix
        pin_type = _pin_type_from_id(pin_id)

        result.append(Pin(id=pin_id, name=name, city=city, coords=coords, type=pin_type))

    return result


def _pin_type_from_id(pin_id: str) -> str:
    """Determine pin type from its ID prefix."""
    if pin_id.isdigit():
        return "Stop"
    prefixes = {
        "pf:": "Platform",
        "pr:": "ParkAndRide",
        "p:": "Poi",
        "r:": "RentABike",
        "t:": "TicketMachine",
        "c:": "CarSharing",
        "w:": "Footpath",
    }
    for prefix, pin_type in prefixes.items():
        if pin_id.startswith(prefix):
            return pin_type
    return "Unknown"


def address(
    lat: float,
    lng: float,
    *,
    raw: bool = False,
) -> Stop | None | dict[str, Any]:
    """Reverse geocode coordinates to the nearest stop.

    Args:
        lat: Latitude (WGS84).
        lng: Longitude (WGS84).
        raw: If True, return the raw API response dict.

    Returns:
        The nearest Stop, None if not found, or raw dict if raw=True.

    Raises:
        APIError: If the API returns an error status.
        ConnectionError: If the request fails.
    """
    gk4_lat, gk4_lng = coords_wgs_to_gk4(lat, lng)
    data = _get(
        "tr/pointfinder",
        {"query": f"coord:{gk4_lng}:{gk4_lat}", "assignedstops": "true"},
    )

    if raw:
        return data

    points = data.get("Points", [])
    if not points:
        return None

    return parse_point(points[0])


def lines(
    stop: str,
    *,
    raw: bool = False,
) -> list[Line] | dict[str, Any]:
    """Get lines servicing a stop.

    Args:
        stop: Stop name or numeric stop ID.
        raw: If True, return the raw API response dict.

    Returns:
        List of Line objects, or raw dict if raw=True.

    Raises:
        APIError: If the API returns an error or stop not found.
        ConnectionError: If the request fails.
    """
    stop_id = _resolve_stop_id(stop)
    data = _post("stt/lines", {"stopid": stop_id})

    if raw:
        return data

    result: list[Line] = []
    for line_data in data.get("Lines", []):
        directions = [d["Name"] for d in line_data.get("Directions", [])]
        result.append(
            Line(
                name=line_data.get("Name", ""),
                mode=line_data.get("Mot", ""),
                directions=directions,
            )
        )

    return result


def route_changes(*, raw: bool = False) -> list[RouteChange] | dict[str, Any]:
    """Get current route changes and disruptions.

    Args:
        raw: If True, return the raw API response dict.

    Returns:
        List of RouteChange objects, or raw dict if raw=True.

    Raises:
        APIError: If the API returns an error status.
        ConnectionError: If the request fails.
    """
    data = _post("rc", {"shortterm": True})

    if raw:
        return data

    result: list[RouteChange] = []
    for change in data.get("Changes", []):
        validity_periods = []
        for vp in change.get("ValidityPeriods", []):
            begin = _try_parse_date(vp.get("Begin"))
            end = _try_parse_date(vp.get("End"))
            if begin and end:
                validity_periods.append(ValidityPeriod(begin=begin, end=end))

        result.append(
            RouteChange(
                id=change.get("Id", ""),
                title=change.get("Title", ""),
                description=change.get("Description", ""),
                type=change.get("Type", ""),
                validity_periods=validity_periods,
                lines=change.get("LineIds", []),
            )
        )

    return result


def trip_details(
    trip_id: str,
    time: str,
    stop_id: str,
    *,
    raw: bool = False,
) -> list[RegularStop] | dict[str, Any]:
    """Get all stops for a specific trip/departure.

    Args:
        trip_id: The departure ID from a monitor response.
        time: Timestamp in /Date(...)/ format from the departure response.
        stop_id: ID of a stop on the route.
        raw: If True, return the raw API response dict.

    Returns:
        List of RegularStop objects, or raw dict if raw=True.

    Raises:
        APIError: If the API returns an error status.
        ConnectionError: If the request fails.
    """
    data = _post(
        "dm/trip",
        {"tripid": trip_id, "time": time, "stopid": stop_id, "mapdata": True},
    )

    if raw:
        return data

    return [_parse_regular_stop(s) for s in data.get("Stops", [])]


def earlier_later(
    origin: str,
    destination: str,
    session_id: str,
    *,
    previous: bool = True,
    raw: bool = False,
) -> list[Route] | dict[str, Any]:
    """Paginate trip results using a session ID from a previous route() call.

    Args:
        origin: Origin stop name or ID.
        destination: Destination stop name or ID.
        session_id: Session ID from a previous route() response.
        previous: If True, get earlier connections; if False, get later ones.
        raw: If True, return the raw API response dict.

    Returns:
        List of Route objects, or raw dict if raw=True.

    Raises:
        APIError: If the API returns an error or stops not found.
        ConnectionError: If the request fails.
    """
    origin_id = _resolve_stop_id(origin)
    dest_id = _resolve_stop_id(destination)

    payload: dict[str, Any] = {
        "origin": origin_id,
        "destination": dest_id,
        "sessionId": session_id,
        "previous": previous,
    }

    data = _post("tr/prevnext", payload)

    if raw:
        return data

    new_session_id = data.get("SessionId")
    return [_parse_route(r, new_session_id) for r in data.get("Routes", [])]
