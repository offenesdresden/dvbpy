from __future__ import annotations

from dvb import Client
from dvb.models import Route

from .conftest import mock_get, mock_post


class TestRoute:
    def test_parses_routes(self, mocked_responses: object, client: Client) -> None:
        mock_post(mocked_responses, "tr/trips", fixture="trips.json")  # type: ignore[arg-type]
        results = client.route("33000028", "33000016")
        assert isinstance(results, list)
        assert len(results) == 1

        r = results[0]
        assert isinstance(r, Route)
        assert r.duration == 11
        assert r.interchanges == 0
        assert r.price == "2,30"
        assert r.fare_zones == "TZ 10 (Dresden)"
        assert r.cancelled is False
        assert r.session_id == "367417461:efa4"

    def test_parses_legs(self, mocked_responses: object, client: Client) -> None:
        mock_post(mocked_responses, "tr/trips", fixture="trips.json")  # type: ignore[arg-type]
        results = client.route("33000028", "33000016")
        assert isinstance(results, list)

        leg = results[0].legs[0]
        assert leg.duration == 11
        assert leg.line == "3"
        assert leg.mode == "Tram"
        assert leg.direction == "Btf Trachenberge"
        assert leg.cancelled is False
        assert leg.changeover_endangered is False

    def test_parses_regular_stops(self, mocked_responses: object, client: Client) -> None:
        mock_post(mocked_responses, "tr/trips", fixture="trips.json")  # type: ignore[arg-type]
        results = client.route("33000028", "33000016")
        assert isinstance(results, list)

        stops = results[0].legs[0].stops
        assert len(stops) == 2
        assert stops[0].name == "Hauptbahnhof"
        assert stops[0].city == "Dresden"
        assert stops[0].id == "33000028"
        assert stops[0].platform is not None
        assert stops[0].platform.type == "Railtrack"
        assert stops[0].coords is not None
        assert stops[0].arrival is not None
        assert stops[0].departure is not None

    def test_parses_path(self, mocked_responses: object, client: Client) -> None:
        mock_post(mocked_responses, "tr/trips", fixture="trips.json")  # type: ignore[arg-type]
        results = client.route("33000028", "33000016")
        assert isinstance(results, list)

        path = results[0].legs[0].path
        assert path is not None
        assert len(path) == 2
        assert abs(path[0].lat - 51.0) < 0.1

    def test_resolves_stop_names(self, mocked_responses: object, client: Client) -> None:
        mock_get(mocked_responses, "tr/pointfinder", fixture="pointfinder.json")  # type: ignore[arg-type]
        mock_get(mocked_responses, "tr/pointfinder", fixture="pointfinder.json")  # type: ignore[arg-type]
        mock_post(mocked_responses, "tr/trips", fixture="trips.json")  # type: ignore[arg-type]
        results = client.route("Helmholtzstraße", "Postplatz")
        assert isinstance(results, list)
        assert len(results) == 1

    def test_raw_returns_dict(self, mocked_responses: object, client: Client) -> None:
        mock_post(mocked_responses, "tr/trips", fixture="trips.json")  # type: ignore[arg-type]
        result = client.route("33000028", "33000016", raw=True)
        assert isinstance(result, dict)
        assert "Routes" in result
