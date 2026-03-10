from __future__ import annotations

import re
from datetime import datetime, timezone

import pyproj

from .models import Coords, Stop

# Thread-safe, reusable transformer instances
_gk4_to_wgs_transformer = pyproj.Transformer.from_crs("EPSG:5678", "EPSG:4326", always_xy=True)
_wgs_to_gk4_transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:5678", always_xy=True)

_DATE_RE = re.compile(r"/Date\((\d+)([+-]\d{4})\)/")


def parse_date(s: str) -> datetime:
    """Parse Microsoft JSON date format: /Date(milliseconds+timezone)/."""
    m = _DATE_RE.search(s)
    if not m:
        msg = f"Invalid date string: {s}"
        raise ValueError(msg)
    ms = int(m.group(1))
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def format_date(dt: datetime) -> str:
    """Format a datetime as Microsoft JSON date format: /Date(milliseconds-0000)/."""
    ms = int(dt.timestamp() * 1000)
    return f"/Date({ms}-0000)/"


def parse_point(s: str) -> Stop:
    """Parse a pipe-delimited point string into a Stop.

    Format: id|type|city|name|lat|lng|distance||shortcut
    """
    parts = s.split("|")
    stop_id = parts[0]
    city = parts[2] if len(parts) > 2 else ""
    name = parts[3] if len(parts) > 3 else ""
    lat_str = parts[4] if len(parts) > 4 else "0"
    lng_str = parts[5] if len(parts) > 5 else "0"

    coords = None
    if lat_str and lng_str and lat_str != "0" and lng_str != "0":
        if "." in lat_str or "." in lng_str:
            coords = Coords(lat=float(lat_str), lng=float(lng_str))
        else:
            coords = coords_gk4_to_wgs(int(lat_str), int(lng_str))

    return Stop(id=stop_id, name=name, city=city, coords=coords)


def coords_gk4_to_wgs(lat: int, lng: int) -> Coords:
    """Convert GK4 integer coordinates to WGS84."""
    wgs_lng, wgs_lat = _gk4_to_wgs_transformer.transform(lng, lat)
    return Coords(lat=wgs_lat, lng=wgs_lng)


def coords_wgs_to_gk4(lat: float, lng: float) -> tuple[int, int]:
    """Convert WGS84 coordinates to GK4 integers."""
    gk4_lng, gk4_lat = _wgs_to_gk4_transformer.transform(lng, lat)
    return int(gk4_lat), int(gk4_lng)
