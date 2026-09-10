"""Mock provider for testing and demo use when no API credentials are present."""
from __future__ import annotations

import hashlib
import random
from datetime import date, datetime, timedelta

from flight_cli.models import CabinClass, Flight, SearchParams, Segment
from flight_cli.providers.base import FlightProvider

_AIRLINES = [
    ("AA", "American Airlines"),
    ("DL", "Delta Air Lines"),
    ("UA", "United Airlines"),
    ("WN", "Southwest Airlines"),
    ("B6", "JetBlue Airways"),
    ("AS", "Alaska Airlines"),
    ("NK", "Spirit Airlines"),
    ("F9", "Frontier Airlines"),
    ("BA", "British Airways"),
    ("LH", "Lufthansa"),
    ("AF", "Air France"),
    ("KL", "KLM"),
    ("EK", "Emirates"),
    ("QR", "Qatar Airways"),
    ("SQ", "Singapore Airlines"),
    ("CX", "Cathay Pacific"),
]

_PRICE_BASE = {
    CabinClass.ECONOMY: 180.0,
    CabinClass.PREMIUM_ECONOMY: 450.0,
    CabinClass.BUSINESS: 1800.0,
    CabinClass.FIRST: 5000.0,
}


class MockProvider(FlightProvider):
    """Generates deterministic-ish fake flights for a given route."""

    async def search(self, params: SearchParams) -> list[Flight]:
        # Use a seeded RNG so same query → same results
        seed = int(
            hashlib.md5(params.cache_key.encode()).hexdigest()[:8], 16
        )
        rng = random.Random(seed)

        base_price = _PRICE_BASE[params.cabin_class]
        flights: list[Flight] = []

        n = min(rng.randint(8, 25), params.max_results)
        for i in range(n):
            airline_code, _airline_name = rng.choice(_AIRLINES)
            flight_num = rng.randint(100, 9999)

            dep_hour = rng.randint(5, 22)
            dep_minute = rng.choice([0, 15, 30, 45])
            dep_time = datetime(
                params.date.year,
                params.date.month,
                params.date.day,
                dep_hour,
                dep_minute,
            )

            # Nonstop or 1-stop
            stops = rng.choices([0, 1, 2], weights=[60, 30, 10])[0]
            segments = _make_segments(
                rng, params.origin, params.destination, dep_time, stops,
                airline_code, flight_num
            )

            # Price variance: ±40%
            price = round(base_price * rng.uniform(0.6, 1.4), 2)
            # Nonstop slight premium
            if stops == 0:
                price *= rng.uniform(0.9, 1.15)
            price = round(price, 2)

            flights.append(
                Flight(
                    id=f"MOCK-{i:04d}-{seed}",
                    segments=segments,
                    price=price,
                    currency="USD",
                    seats_available=rng.randint(1, 9),
                    provider="mock",
                )
            )

        return sorted(flights, key=lambda f: f.price)

    async def close(self) -> None:
        pass


# ── helpers ──────────────────────────────────────────────────────────────────

_HUBS = ["ORD", "ATL", "DFW", "DEN", "PHX", "IAH", "CLT", "MSP", "JFK", "LAX"]


def _make_segments(
    rng: random.Random,
    origin: str,
    destination: str,
    dep_time: datetime,
    stops: int,
    carrier: str,
    base_num: int,
) -> list[Segment]:
    if stops == 0:
        duration_min = rng.randint(60, 720)
        arr_time = dep_time + timedelta(minutes=duration_min)
        return [
            Segment(
                departure_airport=origin,
                arrival_airport=destination,
                departure_time=dep_time,
                arrival_time=arr_time,
                carrier_code=carrier,
                flight_number=f"{carrier}{base_num}",
            )
        ]

    # Pick a layover hub
    hub = rng.choice([h for h in _HUBS if h not in (origin, destination)] or _HUBS)
    seg1_min = rng.randint(45, 300)
    layover_min = rng.randint(45, 180)
    seg2_min = rng.randint(45, 300)

    mid_arr = dep_time + timedelta(minutes=seg1_min)
    mid_dep = mid_arr + timedelta(minutes=layover_min)
    final_arr = mid_dep + timedelta(minutes=seg2_min)

    segs = [
        Segment(
            departure_airport=origin,
            arrival_airport=hub,
            departure_time=dep_time,
            arrival_time=mid_arr,
            carrier_code=carrier,
            flight_number=f"{carrier}{base_num}",
        ),
        Segment(
            departure_airport=hub,
            arrival_airport=destination,
            departure_time=mid_dep,
            arrival_time=final_arr,
            carrier_code=carrier,
            flight_number=f"{carrier}{base_num + 1}",
        ),
    ]

    if stops == 2:
        # Add a third segment
        hub2 = rng.choice([h for h in _HUBS if h not in (origin, destination, hub)] or _HUBS)
        seg3_dep = final_arr + timedelta(minutes=rng.randint(45, 120))
        seg3_arr = seg3_dep + timedelta(minutes=rng.randint(45, 200))
        segs.append(
            Segment(
                departure_airport=destination,
                arrival_airport=hub2,
                departure_time=final_arr,
                arrival_time=seg3_dep,
                carrier_code=carrier,
                flight_number=f"{carrier}{base_num + 2}",
            )
        )
        segs[-2] = segs[-2].model_copy(
            update={"arrival_airport": hub2, "arrival_time": final_arr}
        )

    return segs
