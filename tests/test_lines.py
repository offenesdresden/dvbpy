from __future__ import annotations

import dvb
from dvb.models import Line

from .conftest import mock_get, mock_post


class TestLines:
    def test_parses_lines(self, mocked_responses: object) -> None:
        mock_post(mocked_responses, "stt/lines", fixture="lines.json")  # type: ignore[arg-type]
        results = dvb.lines("33000742")
        assert isinstance(results, list)
        assert len(results) == 2

        line = results[0]
        assert isinstance(line, Line)
        assert line.name == "3"
        assert line.mode == "Tram"
        assert len(line.directions) == 2
        assert "Dresden Wilder Mann" in line.directions
        assert "Dresden Coschütz" in line.directions

    def test_second_line(self, mocked_responses: object) -> None:
        mock_post(mocked_responses, "stt/lines", fixture="lines.json")  # type: ignore[arg-type]
        results = dvb.lines("33000742")
        assert isinstance(results, list)
        line = results[1]
        assert line.name == "66"
        assert line.mode == "CityBus"
        assert len(line.directions) == 1

    def test_resolves_stop_name(self, mocked_responses: object) -> None:
        mock_get(mocked_responses, "tr/pointfinder", fixture="pointfinder.json")  # type: ignore[arg-type]
        mock_post(mocked_responses, "stt/lines", fixture="lines.json")  # type: ignore[arg-type]
        results = dvb.lines("Helmholtzstraße")
        assert isinstance(results, list)
        assert len(results) == 2

    def test_raw_returns_dict(self, mocked_responses: object) -> None:
        mock_post(mocked_responses, "stt/lines", fixture="lines.json")  # type: ignore[arg-type]
        result = dvb.lines("33000742", raw=True)
        assert isinstance(result, dict)
        assert "Lines" in result
