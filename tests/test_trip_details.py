from __future__ import annotations

from datetime import datetime, timezone

import dvb
from dvb.models import RegularStop

from .conftest import mock_post


class TestTripDetails:
    def test_parses_stops(self, mocked_responses: object) -> None:
        mock_post(mocked_responses, "dm/trip", fixture="trip_details.json")  # type: ignore[arg-type]
        results = dvb.trip_details(
            trip_id="71313709",
            time=datetime(2017, 12, 6, 13, 24, 41, tzinfo=timezone.utc),
            stop_id="33000077",
        )
        assert isinstance(results, list)
        assert len(results) == 3

        stop = results[0]
        assert isinstance(stop, RegularStop)
        assert stop.id == "33000076"
        assert stop.name == "Laibacher Straße"
        assert stop.city == "Dresden"
        assert stop.platform is not None
        assert stop.platform.name == "2"

    def test_stop_with_coords(self, mocked_responses: object) -> None:
        mock_post(mocked_responses, "dm/trip", fixture="trip_details.json")  # type: ignore[arg-type]
        results = dvb.trip_details(
            trip_id="71313709",
            time=datetime(2017, 12, 6, 13, 24, 41, tzinfo=timezone.utc),
            stop_id="33000077",
        )
        assert isinstance(results, list)
        stop = results[0]
        assert stop.coords is not None
        assert abs(stop.coords.lat - 51.0) < 0.1

    def test_stop_without_coords(self, mocked_responses: object) -> None:
        mock_post(mocked_responses, "dm/trip", fixture="trip_details.json")  # type: ignore[arg-type]
        results = dvb.trip_details(
            trip_id="71313709",
            time=datetime(2017, 12, 6, 13, 24, 41, tzinfo=timezone.utc),
            stop_id="33000077",
        )
        assert isinstance(results, list)
        # Second stop has no Latitude/Longitude in fixture
        stop = results[1]
        assert stop.coords is None

    def test_time_parsing(self, mocked_responses: object) -> None:
        mock_post(mocked_responses, "dm/trip", fixture="trip_details.json")  # type: ignore[arg-type]
        results = dvb.trip_details(
            trip_id="71313709",
            time=datetime(2017, 12, 6, 13, 24, 41, tzinfo=timezone.utc),
            stop_id="33000077",
        )
        assert isinstance(results, list)
        stop = results[0]
        assert stop.arrival is not None
        assert stop.arrival.year == 2017
        assert stop.arrival_real_time is not None

    def test_stop_without_realtime(self, mocked_responses: object) -> None:
        mock_post(mocked_responses, "dm/trip", fixture="trip_details.json")  # type: ignore[arg-type]
        results = dvb.trip_details(
            trip_id="71313709",
            time=datetime(2017, 12, 6, 13, 24, 41, tzinfo=timezone.utc),
            stop_id="33000077",
        )
        assert isinstance(results, list)
        # Third stop has no RealTime
        stop = results[2]
        assert stop.arrival_real_time is None

    def test_occupancy(self, mocked_responses: object) -> None:
        mock_post(mocked_responses, "dm/trip", fixture="trip_details.json")  # type: ignore[arg-type]
        results = dvb.trip_details(
            trip_id="71313709",
            time=datetime(2017, 12, 6, 13, 24, 41, tzinfo=timezone.utc),
            stop_id="33000077",
        )
        assert isinstance(results, list)
        assert results[0].occupancy == "Unknown"
        assert results[1].occupancy == "ManySeats"

    def test_raw_returns_dict(self, mocked_responses: object) -> None:
        mock_post(mocked_responses, "dm/trip", fixture="trip_details.json")  # type: ignore[arg-type]
        result = dvb.trip_details(
            trip_id="71313709",
            time=datetime(2017, 12, 6, 13, 24, 41, tzinfo=timezone.utc),
            stop_id="33000077",
            raw=True,
        )
        assert isinstance(result, dict)
        assert "Stops" in result
