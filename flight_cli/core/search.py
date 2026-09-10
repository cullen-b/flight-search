"""Central search orchestrator.

Ties together provider, cache, and ANYWHERE logic.
"""
from __future__ import annotations

import logging
import os

from flight_cli.cache import FlightCache
from flight_cli.config import AppConfig
from flight_cli.core.anywhere import search_anywhere, search_region
from flight_cli.models import Flight, SearchParams
from flight_cli.providers.amadeus import AmadeusProvider
from flight_cli.providers.base import FlightProvider, ProviderError
from flight_cli.providers.mock import MockProvider
from flight_cli.providers.serpapi import SerpApiProvider

log = logging.getLogger(__name__)


class FlightSearchEngine:
    """High-level search entry point used by the CLI."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._cache = FlightCache(
            directory=config.cache.resolved_directory,
            ttl_seconds=config.cache.ttl_seconds,
        )
        self._provider = self._build_provider()

    def _build_provider(self) -> FlightProvider:
        # Priority: Amadeus → SerpAPI → Mock
        client_id = os.getenv("AMADEUS_CLIENT_ID", "")
        client_secret = os.getenv("AMADEUS_CLIENT_SECRET", "")
        if client_id and client_secret:
            log.info("Using Amadeus provider")
            return AmadeusProvider(client_id=client_id, client_secret=client_secret)

        serpapi_key = os.getenv("SERPAPI_KEY", "")
        if serpapi_key:
            log.info("Using SerpAPI provider (Google Flights)")
            return SerpApiProvider(api_key=serpapi_key)

        log.info("No API credentials found — using mock provider (demo data)")
        return MockProvider()

    @property
    def using_mock(self) -> bool:
        return isinstance(self._provider, MockProvider)

    async def search(self, params: SearchParams) -> list[Flight]:
        """Search for flights, using cache when possible."""
        cache_key = params.cache_key

        cached = self._cache.get(cache_key)
        if cached is not None:
            log.debug("Cache hit: %s", cache_key)
            return cached

        log.debug("Cache miss: %s — fetching from provider", cache_key)

        if params.has_anywhere:
            flights = await search_anywhere(
                self._provider,
                params,
                major_airports=self._config.major_airports,
                concurrency=self._config.defaults.anywhere_concurrency,
            )
        elif params.has_region:
            flights = await search_region(
                self._provider,
                params,
                concurrency=self._config.defaults.anywhere_concurrency,
            )
        else:
            flights = await self._provider.search(params)

        self._cache.set(cache_key, flights)
        return flights

    async def close(self) -> None:
        await self._provider.close()
        self._cache.close()
