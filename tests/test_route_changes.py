from __future__ import annotations

from dvb import Client
from dvb.models import RouteChange

from .conftest import mock_post


class TestRouteChanges:
    def test_parses_changes(self, mocked_responses: object, client: Client) -> None:
        mock_post(mocked_responses, "rc", fixture="route_changes.json")  # type: ignore[arg-type]
        results = client.route_changes()
        assert isinstance(results, list)
        assert len(results) == 2

        change = results[0]
        assert isinstance(change, RouteChange)
        assert change.id == "511595"
        assert "Mengsstraße" in change.title
        assert change.type == "Scheduled"
        assert "<p>" in change.description
        assert change.lines == ["428296"]

    def test_validity_periods(self, mocked_responses: object, client: Client) -> None:
        mock_post(mocked_responses, "rc", fixture="route_changes.json")  # type: ignore[arg-type]
        results = client.route_changes()
        assert isinstance(results, list)

        change = results[0]
        assert len(change.validity_periods) == 1
        vp = change.validity_periods[0]
        assert vp.begin.year == 2017
        assert vp.end.year == 2017

    def test_multiple_line_ids(self, mocked_responses: object, client: Client) -> None:
        mock_post(mocked_responses, "rc", fixture="route_changes.json")  # type: ignore[arg-type]
        results = client.route_changes()
        assert isinstance(results, list)
        assert results[1].lines == ["428300", "428301"]

    def test_raw_returns_dict(self, mocked_responses: object, client: Client) -> None:
        mock_post(mocked_responses, "rc", fixture="route_changes.json")  # type: ignore[arg-type]
        result = client.route_changes(raw=True)
        assert isinstance(result, dict)
        assert "Changes" in result
