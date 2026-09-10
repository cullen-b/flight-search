"""Shared fixtures."""
from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest

from flight_cli.models import CabinClass, Flight, SearchParams, Segment


def _make_segment(
    origin: str = "JFK",
    dest: str = "LAX",
    dep: datetime | None = None,
    arr: datetime | None = None,
    carrier: str = "AA",
    number: str = "AA100",
) -> Segment:
    dep = dep or datetime(2024, 6, 15, 8, 0)
    arr = arr or datetime(2024, 6, 15, 11, 30)
    return Segment(
        departure_airport=origin,
        arrival_airport=dest,
        departure_time=dep,
        arrival_time=arr,
        carrier_code=carrier,
        flight_number=number,
    )


def make_flight(
    price: float = 200.0,
    origin: str = "JFK",
    dest: str = "LAX",
    airline: str = "AA",
    stops: int = 0,
    dep_hour: int = 8,
    duration_hours: float = 5.5,
    flight_id: str | None = None,
) -> Flight:
    dep = datetime(2024, 6, 15, dep_hour, 0)
    arr = dep + timedelta(hours=duration_hours)

    if stops == 0:
        segments = [_make_segment(origin, dest, dep, arr, airline, f"{airline}100")]
    else:
        mid_dep = dep + timedelta(hours=duration_hours / 2)
        mid_arr = mid_dep + timedelta(hours=1)
        final_arr = mid_arr + timedelta(hours=duration_hours / 2)
        hub = "ORD"
        segments = [
            _make_segment(origin, hub, dep, mid_dep, airline, f"{airline}100"),
            _make_segment(hub, dest, mid_arr, final_arr, airline, f"{airline}101"),
        ]

    return Flight(
        id=flight_id or f"F-{airline}-{price}",
        segments=segments,
        price=price,
        currency="USD",
        provider="test",
    )


@pytest.fixture
def sample_flights() -> list[Flight]:
    return [
        make_flight(price=350.0, airline="DL", stops=0, dep_hour=7, duration_hours=5.0, flight_id="f1"),
        make_flight(price=189.0, airline="NK", stops=2, dep_hour=6, duration_hours=10.0, flight_id="f2"),
        make_flight(price=210.0, airline="AA", stops=0, dep_hour=9, duration_hours=5.5, flight_id="f3"),
        make_flight(price=145.0, airline="F9", stops=1, dep_hour=14, duration_hours=8.0, flight_id="f4"),
        make_flight(price=520.0, airline="BA", stops=0, dep_hour=6, duration_hours=5.0, flight_id="f5"),
        make_flight(price=99.0,  airline="NK", stops=2, dep_hour=5, duration_hours=12.0, flight_id="f6"),
    ]


@pytest.fixture
def search_params() -> SearchParams:
    return SearchParams(
        origin="JFK",
        destination="LAX",
        date=date(2024, 6, 15),
        passengers=1,
        cabin_class=CabinClass.ECONOMY,
    )
