from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import responses

FIXTURES = Path(__file__).parent / "fixtures"
BASE_URL = "https://webapi.vvo-online.de"


def load_fixture(name: str) -> dict[str, Any]:
    """Load a JSON fixture file."""
    return json.loads((FIXTURES / name).read_text())  # type: ignore[no-any-return]


@pytest.fixture()
def mocked_responses() -> responses.RequestsMock:
    """Activate responses mocking for the duration of a test."""
    with responses.RequestsMock() as rsps:
        yield rsps


def mock_get(
    rsps: responses.RequestsMock,
    endpoint: str,
    fixture: str | None = None,
    body: dict[str, Any] | None = None,
    status: int = 200,
) -> None:
    """Register a mocked GET response."""
    rsps.add(
        responses.GET,
        f"{BASE_URL}/{endpoint}",
        json=body or load_fixture(fixture) if fixture else body,
        status=status,
    )


def mock_post(
    rsps: responses.RequestsMock,
    endpoint: str,
    fixture: str | None = None,
    body: dict[str, Any] | None = None,
    status: int = 200,
) -> None:
    """Register a mocked POST response."""
    rsps.add(
        responses.POST,
        f"{BASE_URL}/{endpoint}",
        json=body or load_fixture(fixture) if fixture else body,
        status=status,
    )


def mock_find_helmholtzstrasse(rsps: responses.RequestsMock) -> None:
    """Mock the pointfinder endpoint to resolve 'Helmholtzstraße'."""
    mock_get(rsps, "tr/pointfinder", fixture="pointfinder.json")
