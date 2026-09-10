"""Amadeus for Developers API provider.

Free test environment: https://developers.amadeus.com/
Docs: https://developers.amadeus.com/self-service/category/flights
"""
from __future__ import annotations

import asyncio
import os
import time
from datetime import datetime, timezone

import httpx

from flight_cli.models import CabinClass, Flight, SearchParams, Segment
from flight_cli.providers.base import FlightProvider, ProviderError


_TEST_BASE = "https://test.api.amadeus.com"
_PROD_BASE = "https://api.amadeus.com"


class AmadeusProvider(FlightProvider):
    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        environment: str = "test",
    ) -> None:
        self._client_id = client_id or os.getenv("AMADEUS_CLIENT_ID", "")
        self._client_secret = client_secret or os.getenv("AMADEUS_CLIENT_SECRET", "")
        env = environment or os.getenv("AMADEUS_ENV", "test")
        self._base_url = _PROD_BASE if env == "production" else _TEST_BASE

        self._http = httpx.AsyncClient(
            timeout=httpx.Timeout(15.0, connect=5.0),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )
        self._access_token: str | None = None
        self._token_expires_at: float = 0.0
        self._token_lock = asyncio.Lock()

    # ── Auth ──────────────────────────────────────────────────────────────────

    async def _ensure_token(self) -> str:
        async with self._token_lock:
            if self._access_token and time.time() < self._token_expires_at - 30:
                return self._access_token

            resp = await self._http.post(
                f"{self._base_url}/v1/security/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if resp.status_code != 200:
                raise ProviderError(
                    f"Amadeus auth failed: {resp.text}", resp.status_code
                )
            body = resp.json()
            self._access_token = body["access_token"]
            self._token_expires_at = time.time() + body["expires_in"]
            return self._access_token  # type: ignore[return-value]

    async def _get(self, path: str, params: dict) -> dict:
        token = await self._ensure_token()
        resp = await self._http.get(
            f"{self._base_url}{path}",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
        )
        if resp.status_code == 200:
            return resp.json()
        body = resp.text
        raise ProviderError(f"Amadeus API error {resp.status_code}: {body}", resp.status_code)

    # ── Public API ────────────────────────────────────────────────────────────

    async def search(self, params: SearchParams) -> list[Flight]:
        if not self._client_id or not self._client_secret:
            raise ProviderError(
                "Amadeus credentials not configured. "
                "Set AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET in .env"
            )

        raw = await self._get(
            "/v2/shopping/flight-offers",
            {
                "originLocationCode": params.origin,
                "destinationLocationCode": params.destination,
                "departureDate": params.date.isoformat(),
                "adults": params.passengers,
                "travelClass": params.cabin_class.to_amadeus(),
                "nonStop": "false",
                "max": min(params.max_results, 250),
                "currencyCode": "USD",
            },
        )
        return self._parse_offers(raw.get("data", []))

    async def close(self) -> None:
        await self._http.aclose()

    # ── Parsing ───────────────────────────────────────────────────────────────

    def _parse_offers(self, offers: list[dict]) -> list[Flight]:
        flights: list[Flight] = []
        for offer in offers:
            try:
                flight = self._parse_offer(offer)
                flights.append(flight)
            except (KeyError, ValueError, IndexError):
                # Skip malformed offers
                continue
        return flights

    def _parse_offer(self, offer: dict) -> Flight:
        # Amadeus v2 has one itinerary for one-way
        itinerary = offer["itineraries"][0]
        segments = [self._parse_segment(s) for s in itinerary["segments"]]

        price_info = offer["price"]
        price = float(price_info.get("grandTotal") or price_info.get("total", 0))
        currency = price_info.get("currency", "USD")

        seats = offer.get("numberOfBookableSeats")

        return Flight(
            id=offer["id"],
            segments=segments,
            price=price,
            currency=currency,
            seats_available=seats,
            provider="amadeus",
        )

    def _parse_segment(self, seg: dict) -> Segment:
        dep = seg["departure"]
        arr = seg["arrival"]

        dep_time = datetime.fromisoformat(dep["at"])
        arr_time = datetime.fromisoformat(arr["at"])

        carrier = seg.get("carrierCode", seg.get("operating", {}).get("carrierCode", "??"))
        flight_num = seg.get("number", "")

        return Segment(
            departure_airport=dep["iataCode"],
            arrival_airport=arr["iataCode"],
            departure_time=dep_time,
            arrival_time=arr_time,
            carrier_code=carrier,
            flight_number=f"{carrier}{flight_num}",
        )
