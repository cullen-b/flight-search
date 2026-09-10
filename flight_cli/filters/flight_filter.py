from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time


@dataclass
class FilterState:
    """Encapsulates all active filter criteria."""

    # stops: None = any, 0 = nonstop, 1 = max 1 stop, 2 = max 2 stops
    max_stops: int | None = None

    # Airline codes to include (empty set = all airlines)
    airlines: set[str] = field(default_factory=set)

    min_price: float | None = None
    max_price: float | None = None

    # Departure time window
    dep_time_start: time | None = None
    dep_time_end: time | None = None

    @property
    def is_default(self) -> bool:
        return (
            self.max_stops is None
            and not self.airlines
            and self.min_price is None
            and self.max_price is None
            and self.dep_time_start is None
            and self.dep_time_end is None
        )

    def summary(self) -> str:
        parts = []
        if self.max_stops is not None:
            parts.append(f"≤{self.max_stops} stop{'s' if self.max_stops != 1 else ''}"
                         if self.max_stops > 0 else "nonstop")
        if self.airlines:
            parts.append(f"airlines: {', '.join(sorted(self.airlines))}")
        if self.max_price is not None:
            parts.append(f"≤${self.max_price:.0f}")
        if self.dep_time_start or self.dep_time_end:
            s = self.dep_time_start.strftime("%H:%M") if self.dep_time_start else "00:00"
            e = self.dep_time_end.strftime("%H:%M") if self.dep_time_end else "23:59"
            parts.append(f"dep {s}–{e}")
        return " · ".join(parts) if parts else "no filters"


def apply_filters(flights: list, state: FilterState) -> list:
    """Return flights matching the given FilterState.

    Args:
        flights: list of Flight objects.
        state: active filter criteria.
    Returns:
        Filtered list (does not mutate the input).
    """
    if state.is_default:
        return flights

    result = []
    for f in flights:
        if state.max_stops is not None and f.stops > state.max_stops:
            continue
        if state.airlines and f.airline not in state.airlines:
            continue
        if state.min_price is not None and f.price < state.min_price:
            continue
        if state.max_price is not None and f.price > state.max_price:
            continue
        if state.dep_time_start is not None:
            dep = f.departure_time.time()
            if dep < state.dep_time_start:
                continue
        if state.dep_time_end is not None:
            dep = f.departure_time.time()
            if dep > state.dep_time_end:
                continue
        result.append(f)
    return result
