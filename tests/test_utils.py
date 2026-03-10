from datetime import datetime, timezone

import pytest

from dvb._utils import coords_gk4_to_wgs, coords_wgs_to_gk4, format_date, parse_date, parse_point
from dvb.models import Coords


class TestParseDate:
    def test_basic(self) -> None:
        dt = parse_date("/Date(1487778279147+0100)/")
        assert dt.year == 2017
        assert dt.month == 2
        assert dt.day == 22

    def test_negative_offset(self) -> None:
        dt = parse_date("/Date(1512769800000-0000)/")
        assert dt.year == 2017

    def test_invalid(self) -> None:
        with pytest.raises(ValueError, match="Invalid date string"):
            parse_date("not a date")

    def test_embedded_in_string(self) -> None:
        dt = parse_date('{"time": "/Date(1487778279147+0100)/"}')
        assert dt.year == 2017


class TestFormatDate:
    def test_basic(self) -> None:
        dt = datetime(2017, 12, 6, 13, 24, 41, tzinfo=timezone.utc)
        result = format_date(dt)
        assert result.startswith("/Date(")
        assert result.endswith(")/")

    def test_round_trip(self) -> None:
        dt = datetime(2017, 12, 6, 13, 24, 41, tzinfo=timezone.utc)
        formatted = format_date(dt)
        parsed = parse_date(formatted)
        assert abs((parsed - dt).total_seconds()) < 1


class TestParsePoint:
    def test_stop_with_gk4_coords(self) -> None:
        stop = parse_point("33000742|||Helmholtzstraße|5655904|4621157|0||")
        assert stop.id == "33000742"
        assert stop.name == "Helmholtzstraße"
        assert stop.city == ""
        assert stop.coords is not None
        assert abs(stop.coords.lat - 51.0) < 0.1
        assert abs(stop.coords.lng - 13.7) < 0.1

    def test_stop_with_city(self) -> None:
        stop = parse_point("36030083||Chemnitz|Helmholtzstr|5635837|4566835|0||")
        assert stop.city == "Chemnitz"
        assert stop.name == "Helmholtzstr"

    def test_stop_without_coords(self) -> None:
        stop = parse_point("9022020||Bonn|Helmholtzstraße|0|0|0||")
        assert stop.coords is None

    def test_street_id(self) -> None:
        point_str = (
            "streetID:123:42a:0:-1:Musterstr:Dresden:Musterstr:"
            ":Musterstr:01067:ANY:DIVA_SINGLEHOUSE:0:0:NAV4:VVO"
            "|a||Musterstr 42a|5655000|4621000|0||"
        )
        stop = parse_point(point_str)
        assert "streetID" in stop.id


class TestCoordsConversion:
    def test_gk4_to_wgs(self) -> None:
        coords = coords_gk4_to_wgs(5655904, 4621157)
        assert abs(coords.lat - 51.03) < 0.01
        assert abs(coords.lng - 13.73) < 0.01

    def test_wgs_to_gk4(self) -> None:
        lat, lng = coords_wgs_to_gk4(51.03, 13.73)
        assert abs(lat - 5655904) < 1000
        assert abs(lng - 4621157) < 1000

    def test_round_trip(self) -> None:
        original = Coords(lat=51.0504, lng=13.7373)
        gk4_lat, gk4_lng = coords_wgs_to_gk4(original.lat, original.lng)
        result = coords_gk4_to_wgs(gk4_lat, gk4_lng)
        assert abs(result.lat - original.lat) < 0.001
        assert abs(result.lng - original.lng) < 0.001
