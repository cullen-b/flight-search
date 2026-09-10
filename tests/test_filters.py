"""Tests for flight filtering logic."""
from __future__ import annotations

import pytest

from flight_cli.filters import FilterState, apply_filters
from tests.conftest import make_flight


def test_filter_nonstop_only(sample_flights):
    state = FilterState(max_stops=0)
    result = apply_filters(sample_flights, state)
    assert all(f.stops == 0 for f in result)
    assert len(result) == 3


def test_filter_max_one_stop(sample_flights):
    state = FilterState(max_stops=1)
    result = apply_filters(sample_flights, state)
    assert all(f.stops <= 1 for f in result)


def test_filter_by_airline(sample_flights):
    state = FilterState(airlines={"NK", "DL"})
    result = apply_filters(sample_flights, state)
    assert all(f.airline in {"NK", "DL"} for f in result)
    assert len(result) == 3  # DL×1, NK×2


def test_filter_max_price(sample_flights):
    state = FilterState(max_price=210.0)
    result = apply_filters(sample_flights, state)
    assert all(f.price <= 210.0 for f in result)


def test_filter_min_price(sample_flights):
    state = FilterState(min_price=200.0)
    result = apply_filters(sample_flights, state)
    assert all(f.price >= 200.0 for f in result)


def test_filter_price_range(sample_flights):
    state = FilterState(min_price=150.0, max_price=400.0)
    result = apply_filters(sample_flights, state)
    assert all(150.0 <= f.price <= 400.0 for f in result)


def test_filter_departure_time(sample_flights):
    from datetime import time
    state = FilterState(dep_time_start=time(7, 0), dep_time_end=time(12, 0))
    result = apply_filters(sample_flights, state)
    for f in result:
        dep = f.departure_time.time()
        assert time(7, 0) <= dep <= time(12, 0)


def test_no_filters_returns_all(sample_flights):
    state = FilterState()
    assert state.is_default
    result = apply_filters(sample_flights, state)
    assert len(result) == len(sample_flights)


def test_combined_filters(sample_flights):
    state = FilterState(max_stops=0, max_price=400.0)
    result = apply_filters(sample_flights, state)
    assert all(f.stops == 0 and f.price <= 400.0 for f in result)


def test_empty_flight_list():
    state = FilterState(max_stops=0)
    assert apply_filters([], state) == []


def test_filter_state_summary():
    state = FilterState(max_stops=0, max_price=300.0)
    summary = state.summary()
    assert "nonstop" in summary
    assert "$300" in summary
