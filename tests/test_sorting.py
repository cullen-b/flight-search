"""Tests for flight sorting logic."""
from __future__ import annotations

import pytest

from flight_cli.sorting import SortKey, sort_flights
from tests.conftest import make_flight


def test_sort_price_asc(sample_flights):
    result = sort_flights(sample_flights, SortKey.PRICE_ASC)
    prices = [f.price for f in result]
    assert prices == sorted(prices)


def test_sort_price_desc(sample_flights):
    result = sort_flights(sample_flights, SortKey.PRICE_DESC)
    prices = [f.price for f in result]
    assert prices == sorted(prices, reverse=True)


def test_sort_duration_asc(sample_flights):
    result = sort_flights(sample_flights, SortKey.DURATION_ASC)
    durations = [f.total_duration.total_seconds() for f in result]
    assert durations == sorted(durations)


def test_sort_duration_desc(sample_flights):
    result = sort_flights(sample_flights, SortKey.DURATION_DESC)
    durations = [f.total_duration.total_seconds() for f in result]
    assert durations == sorted(durations, reverse=True)


def test_sort_departure_asc(sample_flights):
    result = sort_flights(sample_flights, SortKey.DEPARTURE_ASC)
    times = [f.departure_time for f in result]
    assert times == sorted(times)


def test_sort_departure_desc(sample_flights):
    result = sort_flights(sample_flights, SortKey.DEPARTURE_DESC)
    times = [f.departure_time for f in result]
    assert times == sorted(times, reverse=True)


def test_sort_arrival_asc(sample_flights):
    result = sort_flights(sample_flights, SortKey.ARRIVAL_ASC)
    times = [f.arrival_time for f in result]
    assert times == sorted(times)


def test_sort_does_not_mutate(sample_flights):
    original_order = [f.id for f in sample_flights]
    sort_flights(sample_flights, SortKey.PRICE_ASC)
    assert [f.id for f in sample_flights] == original_order


def test_sort_key_toggle():
    assert SortKey.PRICE_ASC.toggled() == SortKey.PRICE_DESC
    assert SortKey.PRICE_DESC.toggled() == SortKey.PRICE_ASC
    assert SortKey.DURATION_ASC.toggled() == SortKey.DURATION_DESC


def test_sort_empty_list():
    assert sort_flights([], SortKey.PRICE_ASC) == []
