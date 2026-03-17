from __future__ import annotations

from dvb import Client

from .conftest import mock_get


class TestAddress:
    def test_returns_stop(self, mocked_responses: object, client: Client) -> None:
        mock_get(  # type: ignore[arg-type]
            mocked_responses,
            "tr/pointfinder",
            body={
                "PointStatus": "List",
                "Status": {"Code": "Ok"},
                "Points": ["33000742|||Helmholtzstraße|5655904|4621157|42||"],
            },
        )
        result = client.address(51.03, 13.73)
        assert result is not None
        assert not isinstance(result, dict)
        assert result.name == "Helmholtzstraße"
        assert result.id == "33000742"

    def test_returns_none_when_empty(self, mocked_responses: object, client: Client) -> None:
        mock_get(  # type: ignore[arg-type]
            mocked_responses,
            "tr/pointfinder",
            body={"PointStatus": "List", "Status": {"Code": "Ok"}, "Points": []},
        )
        result = client.address(0.0, 0.0)
        assert result is None

    def test_raw_returns_dict(self, mocked_responses: object, client: Client) -> None:
        mock_get(  # type: ignore[arg-type]
            mocked_responses,
            "tr/pointfinder",
            body={
                "PointStatus": "List",
                "Status": {"Code": "Ok"},
                "Points": ["33000742|||Helmholtzstraße|5655904|4621157|42||"],
            },
        )
        result = client.address(51.03, 13.73, raw=True)
        assert isinstance(result, dict)
        assert "Points" in result
