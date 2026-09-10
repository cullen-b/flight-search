"""Fan-out search logic for ANYWHERE and region-based searches."""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from flight_cli.models import Flight, SearchParams

if TYPE_CHECKING:
    from flight_cli.providers.base import FlightProvider

log = logging.getLogger(__name__)


async def _fanout(
    provider: "FlightProvider",
    param_list: list[SearchParams],
    label: str,
    concurrency: int,
) -> list[Flight]:
    """Run param_list searches in parallel, deduplicate by id."""
    sem = asyncio.Semaphore(concurrency)
    errors = 0

    async def fetch_one(p: SearchParams) -> list[Flight]:
        nonlocal errors
        async with sem:
            try:
                return await provider.search(p)
            except Exception as exc:
                log.debug("%s sub-query failed for %s→%s: %s", label, p.origin, p.destination, exc)
                errors += 1
                return []

    gathered = await asyncio.gather(*[fetch_one(p) for p in param_list])

    seen_ids: set[str] = set()
    results: list[Flight] = []
    for batch in gathered:
        for flight in batch:
            if flight.id not in seen_ids:
                seen_ids.add(flight.id)
                results.append(flight)

    if errors:
        log.info("%s: %d/%d sub-queries failed, %d results collected",
                 label, errors, len(param_list), len(results))
    return results


async def search_anywhere(
    provider: "FlightProvider",
    params: SearchParams,
    major_airports: list[str],
    concurrency: int = 10,
) -> list[Flight]:
    """Fan out to all major airports for an ANYWHERE search."""
    if params.origin == "ANYWHERE" and params.destination == "ANYWHERE":
        raise ValueError("Both origin and destination cannot be ANYWHERE.")

    if params.origin == "ANYWHERE":
        targets = [a for a in major_airports if a != params.destination]
        param_list = [params.model_copy(update={"origin": a}) for a in targets]
    else:
        targets = [a for a in major_airports if a != params.origin]
        param_list = [params.model_copy(update={"destination": a}) for a in targets]

    return await _fanout(provider, param_list, "ANYWHERE", concurrency)


async def search_region(
    provider: "FlightProvider",
    params: SearchParams,
    concurrency: int = 10,
) -> list[Flight]:
    """Fan out to airports within the specified region."""
    from flight_cli.utils.airports import REGIONS, get_region_airports

    if params.origin in REGIONS:
        region_airports = get_region_airports(params.origin)
        targets = [a for a in region_airports if a != params.destination]
        param_list = [params.model_copy(update={"origin": a}) for a in targets]
        label = f"REGION({params.origin})"
    elif params.destination in REGIONS:
        region_airports = get_region_airports(params.destination)
        targets = [a for a in region_airports if a != params.origin]
        param_list = [params.model_copy(update={"destination": a}) for a in targets]
        label = f"REGION({params.destination})"
    else:
        raise ValueError("No region keyword found in params.")

    return await _fanout(provider, param_list, label, concurrency)
