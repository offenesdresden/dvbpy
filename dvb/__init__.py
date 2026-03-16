"""
An unofficial Python module for querying Dresden's public transport system (VVO/DVB).
"""

__version__ = "3.0.0"

from .dvb import Client
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
    # Client
    "Client",
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
