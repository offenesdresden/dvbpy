from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Coords:
    lat: float
    lng: float


@dataclass(frozen=True, slots=True)
class Platform:
    name: str
    type: str


@dataclass(frozen=True, slots=True)
class Stop:
    id: str
    name: str
    city: str
    coords: Coords | None = None


@dataclass(frozen=True, slots=True)
class Departure:
    id: str
    line: str
    direction: str
    scheduled: datetime
    real_time: datetime | None = None
    state: str = ""
    platform: Platform | None = None
    mode: str = ""
    occupancy: str = "Unknown"


@dataclass(frozen=True, slots=True)
class RegularStop:
    id: str
    name: str
    city: str
    platform: Platform | None
    coords: Coords | None
    arrival: datetime | None
    departure: datetime | None
    arrival_real_time: datetime | None = None
    departure_real_time: datetime | None = None
    occupancy: str = "Unknown"


@dataclass(frozen=True, slots=True)
class PartialRoute:
    duration: int
    line: str
    mode: str
    direction: str
    stops: list[RegularStop]
    cancelled: bool = False
    changeover_endangered: bool = False
    path: list[Coords] | None = None


@dataclass(frozen=True, slots=True)
class Route:
    duration: int
    interchanges: int
    price: str
    fare_zones: str
    cancelled: bool
    legs: list[PartialRoute]
    session_id: str | None = None


@dataclass(frozen=True, slots=True)
class Pin:
    id: str
    name: str
    city: str
    coords: Coords | None
    type: str


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
    id: str
    title: str
    description: str
    type: str
    validity_periods: list[ValidityPeriod]
    lines: list[str]
