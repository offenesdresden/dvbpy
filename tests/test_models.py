from datetime import datetime, timezone

import pytest

from dvb.models import (
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


class TestCoords:
    def test_construction(self) -> None:
        c = Coords(lat=51.0, lng=13.7)
        assert c.lat == 51.0
        assert c.lng == 13.7

    def test_equality(self) -> None:
        assert Coords(lat=1.0, lng=2.0) == Coords(lat=1.0, lng=2.0)
        assert Coords(lat=1.0, lng=2.0) != Coords(lat=1.0, lng=3.0)

    def test_frozen(self) -> None:
        c = Coords(lat=1.0, lng=2.0)
        with pytest.raises(AttributeError):
            c.lat = 3.0  # type: ignore[misc]


class TestPlatform:
    def test_construction(self) -> None:
        p = Platform(name="3", type="Platform")
        assert p.name == "3"
        assert p.type == "Platform"


class TestStop:
    def test_with_coords(self) -> None:
        s = Stop(id="33000742", name="Helmholtzstraße", city="Dresden", coords=Coords(51.0, 13.7))
        assert s.id == "33000742"
        assert s.coords is not None

    def test_without_coords(self) -> None:
        s = Stop(id="33000742", name="Helmholtzstraße", city="Dresden")
        assert s.coords is None

    def test_frozen(self) -> None:
        s = Stop(id="1", name="Test", city="City")
        with pytest.raises(AttributeError):
            s.name = "Other"  # type: ignore[misc]


class TestDeparture:
    def test_construction(self) -> None:
        t = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
        d = Departure(
            id="voe:11003: :H:j26",
            line="3",
            direction="Wilder Mann",
            scheduled=t,
            real_time=t,
            state="InTime",
            platform=Platform(name="3", type="Platform"),
            mode="Tram",
            occupancy="ManySeats",
        )
        assert d.line == "3"
        assert d.occupancy == "ManySeats"

    def test_defaults(self) -> None:
        t = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
        d = Departure(id="x", line="1", direction="A", scheduled=t)
        assert d.real_time is None
        assert d.state == ""
        assert d.occupancy == "Unknown"


class TestRegularStop:
    def test_construction(self) -> None:
        t = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
        rs = RegularStop(
            id="33000028",
            name="Hauptbahnhof",
            city="Dresden",
            platform=Platform(name="3", type="Railtrack"),
            coords=Coords(51.0, 13.7),
            arrival=t,
            departure=t,
        )
        assert rs.name == "Hauptbahnhof"
        assert rs.arrival_real_time is None


class TestPartialRoute:
    def test_construction(self) -> None:
        pr = PartialRoute(
            duration=11,
            line="3",
            mode="Tram",
            direction="Btf Trachenberge",
            stops=[],
        )
        assert pr.cancelled is False
        assert pr.path is None


class TestRoute:
    def test_construction(self) -> None:
        r = Route(
            duration=11,
            interchanges=0,
            price="2,30",
            fare_zones="TZ 10 (Dresden)",
            cancelled=False,
            legs=[],
            session_id="12345:efa4",
        )
        assert r.session_id == "12345:efa4"


class TestPin:
    def test_construction(self) -> None:
        p = Pin(
            id="33000028",
            name="Hauptbahnhof",
            city="Dresden",
            coords=Coords(51.0, 13.7),
            type="Stop",
        )
        assert p.type == "Stop"


class TestLine:
    def test_construction(self) -> None:
        ln = Line(name="3", mode="Tram", directions=["Wilder Mann", "Coschütz"])
        assert len(ln.directions) == 2


class TestRouteChange:
    def test_construction(self) -> None:
        t1 = datetime(2025, 1, 1, tzinfo=timezone.utc)
        t2 = datetime(2025, 1, 2, tzinfo=timezone.utc)
        rc = RouteChange(
            id="511595",
            title="Construction",
            description="<p>Details</p>",
            type="Scheduled",
            validity_periods=[ValidityPeriod(begin=t1, end=t2)],
            lines=["428296"],
        )
        assert rc.validity_periods[0].begin == t1
