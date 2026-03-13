from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Coords:
    lat: float
    lng: float


@dataclass(frozen=True, slots=True)
class Platform:
    """A platform or track at a stop."""

    name: str
    type: str  # "Platform" for bus/tram stops, "Railtrack" for train stations


@dataclass(frozen=True, slots=True)
class Stop:
    id: str
    name: str
    city: str
    coords: Coords | None = None


@dataclass(frozen=True, slots=True)
class Departure:
    """A single upcoming departure from a stop."""

    id: str
    line: str
    direction: str  # destination name
    scheduled: datetime
    real_time: datetime | None = None
    state: str = ""  # real-time state, e.g. "InTime", "Delayed"
    platform: Platform | None = None
    mode: str = ""  # e.g. "Tram", "CityBus", "SuburbanRailway", "Ferry"
    occupancy: str = "Unknown"  # "Unknown", "ManySeats", "StandingOnly", "Full"


@dataclass(frozen=True, slots=True)
class RegularStop:
    """A stop along a trip or route leg, with scheduled and real-time arrival/departure data."""

    id: str
    name: str
    city: str
    platform: Platform | None
    coords: Coords | None
    arrival: datetime | None
    departure: datetime | None
    arrival_real_time: datetime | None = None
    departure_real_time: datetime | None = None
    occupancy: str = "Unknown"  # "Unknown", "ManySeats", "StandingOnly", "Full"


@dataclass(frozen=True, slots=True)
class PartialRoute:
    """A single leg of a planned route, e.g. one tram ride within a multi-transfer journey."""

    duration: int  # in minutes
    line: str
    mode: str  # e.g. "Tram", "CityBus", "Footpath", "StayForConnection"
    direction: str
    stops: list[RegularStop]
    cancelled: bool = False
    changeover_endangered: bool = False  # transfer to the next leg is at risk
    path: list[Coords] | None = None  # geographic polyline of this leg


@dataclass(frozen=True, slots=True)
class Route:
    """A complete planned journey from origin to destination, consisting of one or more legs."""

    duration: int  # total duration in minutes
    interchanges: int  # number of transfers
    price: str  # e.g. "2,30"
    fare_zones: str  # human-readable zone names, e.g. "TZ 10 (Dresden)"
    cancelled: bool
    legs: list[PartialRoute]
    session_id: str | None = None  # used to paginate earlier/later connections


@dataclass(frozen=True, slots=True)
class Pin:
    """A map marker, e.g. a stop, POI, bike rental station, or ticket machine."""

    id: str
    name: str
    city: str
    coords: Coords | None
    type: (
        str  # "Stop", "Platform", "Poi", "RentABike", "CarSharing", "TicketMachine", "ParkAndRide"
    )


@dataclass(frozen=True, slots=True)
class Line:
    name: str
    mode: str
    directions: list[str]


@dataclass(frozen=True, slots=True)
class ValidityPeriod:
    begin: datetime
    end: datetime


@dataclass(frozen=True, slots=True)
class RouteChange:
    """A service disruption or planned route change affecting one or more lines."""

    id: str
    title: str
    description: str  # may contain HTML
    type: str  # e.g. "Scheduled" for planned changes
    validity_periods: list[ValidityPeriod]
    lines: list[str]
