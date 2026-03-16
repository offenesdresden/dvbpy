from __future__ import annotations

import pytest

from dvb import Client
from dvb.exceptions import APIError, ConnectionError

from .conftest import mock_get


class TestFind:
    def test_parses_stops(self, mocked_responses: object, client: Client) -> None:
        mock_get(mocked_responses, "tr/pointfinder", fixture="pointfinder.json")  # type: ignore[arg-type]
        results = client.find("Helmholtz")
        assert isinstance(results, list)
        assert len(results) == 3

        stop = results[0]
        assert stop.id == "33000742"
        assert stop.name == "Helmholtzstraße"
        assert stop.city == ""
        assert stop.coords is not None
        assert abs(stop.coords.lat - 51.0) < 0.1

    def test_stop_with_city(self, mocked_responses: object, client: Client) -> None:
        mock_get(mocked_responses, "tr/pointfinder", fixture="pointfinder.json")  # type: ignore[arg-type]
        results = client.find("Helmholtz")
        assert isinstance(results, list)
        assert results[1].city == "Chemnitz"
        assert results[1].name == "Helmholtzstr"

    def test_stop_without_coords(self, mocked_responses: object, client: Client) -> None:
        mock_get(mocked_responses, "tr/pointfinder", fixture="pointfinder.json")  # type: ignore[arg-type]
        results = client.find("Helmholtz")
        assert isinstance(results, list)
        assert results[2].coords is None
        assert results[2].city == "Bonn"

    def test_raw_returns_dict(self, mocked_responses: object, client: Client) -> None:
        mock_get(mocked_responses, "tr/pointfinder", fixture="pointfinder.json")  # type: ignore[arg-type]
        result = client.find("Helmholtz", raw=True)
        assert isinstance(result, dict)
        assert "Points" in result

    def test_empty_results(self, mocked_responses: object, client: Client) -> None:
        mock_get(  # type: ignore[arg-type]
            mocked_responses,
            "tr/pointfinder",
            body={"PointStatus": "List", "Status": {"Code": "Ok"}, "Points": []},
        )
        results = client.find("nonexistent")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_api_error(self, mocked_responses: object, client: Client) -> None:
        mock_get(  # type: ignore[arg-type]
            mocked_responses,
            "tr/pointfinder",
            body={"Status": {"Code": "InvalidRequest"}},
        )
        with pytest.raises(APIError, match="InvalidRequest"):
            client.find("test")

    def test_connection_error(self, mocked_responses: object, client: Client) -> None:
        import responses as responses_lib

        mocked_responses.add(  # type: ignore[attr-defined]
            responses_lib.GET,
            "https://webapi.vvo-online.de/tr/pointfinder",
            body=ConnectionError("timeout"),
        )
        with pytest.raises(ConnectionError):
            client.find("test")
