from __future__ import annotations

import dvb
from dvb.models import Pin

from .conftest import mock_post


class TestPins:
    def test_parses_pins(self, mocked_responses: object) -> None:
        mock_post(mocked_responses, "map/pins", fixture="pins.json")  # type: ignore[arg-type]
        results = dvb.pins(51.0, 13.7, 51.1, 13.8)
        assert isinstance(results, list)
        assert len(results) == 3

    def test_stop_pin(self, mocked_responses: object) -> None:
        mock_post(mocked_responses, "map/pins", fixture="pins.json")  # type: ignore[arg-type]
        results = dvb.pins(51.0, 13.7, 51.1, 13.8)
        assert isinstance(results, list)

        pin = results[0]
        assert isinstance(pin, Pin)
        assert pin.id == "33000028"
        assert pin.name == "Hauptbahnhof"
        assert pin.city == "Dresden"
        assert pin.type == "Stop"
        assert pin.coords is not None

    def test_platform_pin(self, mocked_responses: object) -> None:
        mock_post(mocked_responses, "map/pins", fixture="pins.json")  # type: ignore[arg-type]
        results = dvb.pins(51.0, 13.7, 51.1, 13.8)
        assert isinstance(results, list)
        assert results[1].type == "Platform"
        assert results[1].id == "pf:1234"

    def test_park_and_ride_pin(self, mocked_responses: object) -> None:
        mock_post(mocked_responses, "map/pins", fixture="pins.json")  # type: ignore[arg-type]
        results = dvb.pins(51.0, 13.7, 51.1, 13.8)
        assert isinstance(results, list)
        assert results[2].type == "ParkAndRide"

    def test_raw_returns_dict(self, mocked_responses: object) -> None:
        mock_post(mocked_responses, "map/pins", fixture="pins.json")  # type: ignore[arg-type]
        result = dvb.pins(51.0, 13.7, 51.1, 13.8, raw=True)
        assert isinstance(result, dict)
        assert "Pins" in result

    def test_empty_pins(self, mocked_responses: object) -> None:
        mock_post(  # type: ignore[arg-type]
            mocked_responses,
            "map/pins",
            body={"Pins": [], "Status": {"Code": "Ok"}},
        )
        results = dvb.pins(51.0, 13.7, 51.1, 13.8)
        assert isinstance(results, list)
        assert len(results) == 0
