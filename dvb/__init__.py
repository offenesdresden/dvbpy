"""
An unofficial Python module for querying Dresden's public transport system (VVO/DVB).
"""

__version__ = "2.0.0"

from .dvb import (
    address,
    earlier_later,
    find,
    lines,
    monitor,
    pins,
    route,
    route_changes,
    trip_details,
)
from .exceptions import APIError, ConnectionError, DVBError
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

__all__ = [
    # Functions
    "address",
    "earlier_later",
    "find",
    "lines",
    "monitor",
    "pins",
    "route",
    "route_changes",
    "trip_details",
    # Exceptions
    "APIError",
    "ConnectionError",
    "DVBError",
    # Models
    "Coords",
    "Departure",
    "Line",
    "PartialRoute",
    "Pin",
    "Platform",
    "RegularStop",
    "Route",
    "RouteChange",
    "Stop",
    "ValidityPeriod",
]
