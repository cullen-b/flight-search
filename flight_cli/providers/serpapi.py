"""SerpAPI Google Flights provider.

SerpAPI proxies Google Flights and returns structured JSON.
Free tier: 250 searches/month  — sign up at https://serpapi.com/

Environment variable:
    SERPAPI_KEY   your API key
"""
from __future__ import annotations

import os
from datetime import datetime

import httpx

from flight_cli.models import Flight, SearchParams, Segment
from flight_cli.providers.base import FlightProvider, ProviderError

_BASE = "https://serpapi.com/search"
_CABIN_MAP = {
    "economy": 1,
    "premium_economy": 2,
    "business": 3,
    "first": 4,
}


class SerpApiProvider(FlightProvider):
    """Google Flights via SerpAPI."""

    def __init__(self, api_key: str | None = None) -> None:
        self._key = api_key or os.getenv("SERPAPI_KEY", "")
        self._http = httpx.AsyncClient(
            timeout=httpx.Timeout(20.0, connect=5.0),
        )

    async def search(self, params: SearchParams) -> list[Flight]:
        if not self._key:
            raise ProviderError(
                "SerpAPI key not configured. Set SERPAPI_KEY in .env"
            )

        query = {
            "engine": "google_flights",
            "departure_id": params.origin,
            "arrival_id": params.destination,
            "outbound_date": params.date.isoformat(),
            "type": "2",  # one-way
            "travel_class": _CABIN_MAP.get(params.cabin_class.value, 1),
            "adults": params.passengers,
            "currency": "USD",
            "hl": "en",
            "api_key": self._key,
        }

        resp = await self._http.get(_BASE, params=query)
        if resp.status_code != 200:
            raise ProviderError(
                f"SerpAPI error {resp.status_code}: {resp.text}", resp.status_code
            )
        body = resp.json()

        if "error" in body:
            raise ProviderError(f"SerpAPI: {body['error']}")

        flights: list[Flight] = []
        for section in ("best_flights", "other_flights"):
            for item in body.get(section, []):
                try:
                    flights.append(self._parse_item(item))
                except (KeyError, ValueError, IndexError):
                    continue

        return flights

    async def close(self) -> None:
        await self._http.aclose()

    # ── Parsing ───────────────────────────────────────────────────────────────

    def _parse_item(self, item: dict) -> Flight:
        raw_segs = item["flights"]
        segments: list[Segment] = []

        for i, seg in enumerate(raw_segs):
            dep_airport = seg["departure_airport"]["id"]
            arr_airport = seg["arrival_airport"]["id"]
            dep_time_str = seg["departure_airport"]["time"]   # "2024-06-15 08:10"
            arr_time_str = seg["arrival_airport"]["time"]

            dep_time = datetime.strptime(dep_time_str, "%Y-%m-%d %H:%M")
            arr_time = datetime.strptime(arr_time_str, "%Y-%m-%d %H:%M")

            # SerpAPI uses full airline name; extract carrier from flight_number
            flight_number = seg.get("flight_number", f"?{i}")
            # flight_number looks like "AF 6" → carrier "AF", num "6"
            parts = flight_number.split()
            carrier = parts[0] if parts else "??"

            segments.append(
                Segment(
                    departure_airport=dep_airport,
                    arrival_airport=arr_airport,
                    departure_time=dep_time,
                    arrival_time=arr_time,
                    carrier_code=carrier,
                    flight_number=flight_number.replace(" ", ""),
                )
            )

        # Build a stable ID from departure + first segment + price
        first = raw_segs[0]
        price = float(item.get("price", 0))
        flight_id = (
            f"SERP-{first['flight_number'].replace(' ', '')}"
            f"-{first['departure_airport']['time'][:10]}-{price}"
        )

        return Flight(
            id=flight_id,
            segments=segments,
            price=price,
            currency="USD",
            seats_available=None,
            provider="serpapi",
        )
