from __future__ import annotations

from enum import Enum


class SortKey(str, Enum):
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    DURATION_ASC = "duration_asc"
    DURATION_DESC = "duration_desc"
    DEPARTURE_ASC = "departure_asc"
    DEPARTURE_DESC = "departure_desc"
    ARRIVAL_ASC = "arrival_asc"
    ARRIVAL_DESC = "arrival_desc"

    def label(self) -> str:
        return {
            "price_asc": "Price ↑",
            "price_desc": "Price ↓",
            "duration_asc": "Duration ↑",
            "duration_desc": "Duration ↓",
            "departure_asc": "Departs ↑",
            "departure_desc": "Departs ↓",
            "arrival_asc": "Arrives ↑",
            "arrival_desc": "Arrives ↓",
        }[self.value]

    def toggled(self) -> "SortKey":
        """Return the reversed version of this sort key."""
        opposites = {
            SortKey.PRICE_ASC: SortKey.PRICE_DESC,
            SortKey.PRICE_DESC: SortKey.PRICE_ASC,
            SortKey.DURATION_ASC: SortKey.DURATION_DESC,
            SortKey.DURATION_DESC: SortKey.DURATION_ASC,
            SortKey.DEPARTURE_ASC: SortKey.DEPARTURE_DESC,
            SortKey.DEPARTURE_DESC: SortKey.DEPARTURE_ASC,
            SortKey.ARRIVAL_ASC: SortKey.ARRIVAL_DESC,
            SortKey.ARRIVAL_DESC: SortKey.ARRIVAL_ASC,
        }
        return opposites[self]


def sort_flights(flights: list, key: SortKey) -> list:
    """Return a new sorted list of flights. Does not mutate input."""
    extractors = {
        SortKey.PRICE_ASC: (lambda f: f.price, False),
        SortKey.PRICE_DESC: (lambda f: f.price, True),
        SortKey.DURATION_ASC: (lambda f: f.total_duration.total_seconds(), False),
        SortKey.DURATION_DESC: (lambda f: f.total_duration.total_seconds(), True),
        SortKey.DEPARTURE_ASC: (lambda f: f.departure_time, False),
        SortKey.DEPARTURE_DESC: (lambda f: f.departure_time, True),
        SortKey.ARRIVAL_ASC: (lambda f: f.arrival_time, False),
        SortKey.ARRIVAL_DESC: (lambda f: f.arrival_time, True),
    }
    extractor, reverse = extractors[key]
    return sorted(flights, key=extractor, reverse=reverse)
