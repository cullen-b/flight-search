"""Tests for ANYWHERE search logic."""
from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, patch

import pytest

from flight_cli.core.anywhere import search_anywhere
from flight_cli.models import CabinClass, SearchParams
from tests.conftest import make_flight


def _make_params(origin="JFK", destination="ANYWHERE") -> SearchParams:
    return SearchParams(
        origin=origin,
        destination=destination,
        date=date(2024, 6, 15),
        passengers=1,
        cabin_class=CabinClass.ECONOMY,
    )


@pytest.mark.asyncio
async def test_anywhere_destination_fans_out():
    """Should query multiple airports as destinations."""
    provider = AsyncMock()
    provider.search = AsyncMock(return_value=[])

    params = _make_params(origin="JFK", destination="ANYWHERE")
    major = ["LAX", "ORD", "LHR"]

    await search_anywhere(provider, params, major, concurrency=3)

    called_dests = {call.args[0].destination for call in provider.search.call_args_list}
    assert called_dests == set(major)


@pytest.mark.asyncio
async def test_anywhere_origin_fans_out():
    """Should query multiple airports as origins."""
    provider = AsyncMock()
    provider.search = AsyncMock(return_value=[])

    params = _make_params(origin="ANYWHERE", destination="JFK")
    major = ["LAX", "ORD", "LHR"]

    await search_anywhere(provider, params, major, concurrency=3)

    called_origins = {call.args[0].origin for call in provider.search.call_args_list}
    assert called_origins == set(major)


@pytest.mark.asyncio
async def test_anywhere_excludes_matching_airport():
    """origin/destination should not appear as its own counterpart."""
    provider = AsyncMock()
    provider.search = AsyncMock(return_value=[])

    params = _make_params(origin="JFK", destination="ANYWHERE")
    major = ["JFK", "LAX", "ORD"]  # JFK is in the list but should be excluded

    await search_anywhere(provider, params, major, concurrency=3)

    called_dests = {call.args[0].destination for call in provider.search.call_args_list}
    assert "JFK" not in called_dests


@pytest.mark.asyncio
async def test_anywhere_deduplicates_results():
    """Flights with same ID from multiple calls should appear only once."""
    shared_flight = make_flight(price=200.0, flight_id="shared-1")

    provider = AsyncMock()
    provider.search = AsyncMock(return_value=[shared_flight])

    params = _make_params(origin="JFK", destination="ANYWHERE")
    major = ["LAX", "ORD"]

    results = await search_anywhere(provider, params, major, concurrency=2)

    ids = [f.id for f in results]
    assert len(ids) == len(set(ids)), "Duplicate flight IDs in results"


@pytest.mark.asyncio
async def test_anywhere_both_raises():
    provider = AsyncMock()
    params = _make_params(origin="ANYWHERE", destination="ANYWHERE")

    with pytest.raises(ValueError, match="ANYWHERE"):
        await search_anywhere(provider, params, ["LAX"], concurrency=1)


@pytest.mark.asyncio
async def test_anywhere_handles_provider_errors_gracefully():
    """Should still return results even if some sub-queries fail."""

    call_count = 0

    async def flaky_search(p):
        nonlocal call_count
        call_count += 1
        if call_count % 2 == 0:
            raise RuntimeError("API error")
        return [make_flight(price=float(call_count * 100), flight_id=f"f-{call_count}")]

    provider = AsyncMock()
    provider.search = AsyncMock(side_effect=flaky_search)

    params = _make_params(origin="JFK", destination="ANYWHERE")
    major = ["LAX", "ORD", "LHR", "FRA"]

    results = await search_anywhere(provider, params, major, concurrency=4)
    # Some results despite errors
    assert len(results) > 0


@pytest.mark.asyncio
async def test_anywhere_mock_provider():
    """Integration-style test using MockProvider."""
    from flight_cli.providers.mock import MockProvider

    provider = MockProvider()
    params = _make_params(origin="JFK", destination="ANYWHERE")
    major = ["LAX", "ORD", "LHR"]

    results = await search_anywhere(provider, params, major, concurrency=3)
    assert isinstance(results, list)
    assert all(hasattr(f, "price") for f in results)
    await provider.close()
