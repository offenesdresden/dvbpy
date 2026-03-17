from __future__ import annotations

from dvb import Client
from dvb.models import Departure

from .conftest import mock_get, mock_post


class TestMonitor:
    def test_parses_departures(self, mocked_responses: object, client: Client) -> None:
        mock_post(mocked_responses, "dm", fixture="departure_monitor.json")  # type: ignore[arg-type]
        results = client.monitor("33000742")
        assert isinstance(results, list)
        assert len(results) == 2

        dep = results[0]
        assert isinstance(dep, Departure)
        assert dep.line == "3"
        assert dep.direction == "Wilder Mann"
        assert dep.state == "Delayed"
        assert dep.mode == "Tram"
        assert dep.occupancy == "ManySeats"
        assert dep.platform is not None
        assert dep.platform.name == "1"
        assert dep.platform.type == "Platform"

    def test_scheduled_time_parsed(self, mocked_responses: object, client: Client) -> None:
        mock_post(mocked_responses, "dm", fixture="departure_monitor.json")  # type: ignore[arg-type]
        results = client.monitor("33000742")
        assert isinstance(results, list)
        dep = results[0]
        assert dep.scheduled.year == 2017
        assert dep.real_time is not None

    def test_departure_without_realtime(self, mocked_responses: object, client: Client) -> None:
        mock_post(mocked_responses, "dm", fixture="departure_monitor.json")  # type: ignore[arg-type]
        results = client.monitor("33000742")
        assert isinstance(results, list)
        dep = results[1]
        assert dep.line == "8"
        assert dep.real_time is None

    def test_resolves_stop_name(self, mocked_responses: object, client: Client) -> None:
        mock_get(mocked_responses, "tr/pointfinder", fixture="pointfinder.json")  # type: ignore[arg-type]
        mock_post(mocked_responses, "dm", fixture="departure_monitor.json")  # type: ignore[arg-type]
        results = client.monitor("Helmholtzstraße")
        assert isinstance(results, list)
        assert len(results) == 2

    def test_raw_returns_dict(self, mocked_responses: object, client: Client) -> None:
        mock_post(mocked_responses, "dm", fixture="departure_monitor.json")  # type: ignore[arg-type]
        result = client.monitor("33000742", raw=True)
        assert isinstance(result, dict)
        assert "Departures" in result

    def test_empty_departures(self, mocked_responses: object, client: Client) -> None:
        mock_post(  # type: ignore[arg-type]
            mocked_responses,
            "dm",
            body={
                "Name": "Test",
                "Status": {"Code": "Ok"},
                "Place": "Dresden",
                "Departures": [],
            },
        )
        results = client.monitor("33000742")
        assert isinstance(results, list)
        assert len(results) == 0
