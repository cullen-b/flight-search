from __future__ import annotations

from datetime import date, datetime, timedelta
from enum import Enum

from pydantic import BaseModel, computed_field, field_validator


class CabinClass(str, Enum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"

    def to_amadeus(self) -> str:
        return {
            "economy": "ECONOMY",
            "premium_economy": "PREMIUM_ECONOMY",
            "business": "BUSINESS",
            "first": "FIRST",
        }[self.value]


class Segment(BaseModel):
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    carrier_code: str
    flight_number: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def duration(self) -> timedelta:
        return self.arrival_time - self.departure_time


class Flight(BaseModel):
    id: str
    segments: list[Segment]
    price: float
    currency: str = "USD"
    seats_available: int | None = None
    provider: str = "unknown"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def airline(self) -> str:
        return self.segments[0].carrier_code

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stops(self) -> int:
        return len(self.segments) - 1

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_duration(self) -> timedelta:
        return self.segments[-1].arrival_time - self.segments[0].departure_time

    @computed_field  # type: ignore[prop-decorator]
    @property
    def departure_airport(self) -> str:
        return self.segments[0].departure_airport

    @computed_field  # type: ignore[prop-decorator]
    @property
    def arrival_airport(self) -> str:
        return self.segments[-1].arrival_airport

    @computed_field  # type: ignore[prop-decorator]
    @property
    def departure_time(self) -> datetime:
        return self.segments[0].departure_time

    @computed_field  # type: ignore[prop-decorator]
    @property
    def arrival_time(self) -> datetime:
        return self.segments[-1].arrival_time

    def duration_str(self) -> str:
        total = int(self.total_duration.total_seconds())
        h, m = divmod(total // 60, 60)
        return f"{h}h {m:02d}m"

    def stops_label(self) -> str:
        if self.stops == 0:
            return "Nonstop"
        elif self.stops == 1:
            return "1 stop"
        return f"{self.stops} stops"


class SearchParams(BaseModel):
    origin: str
    destination: str
    date: date
    passengers: int = 1
    cabin_class: CabinClass = CabinClass.ECONOMY
    max_results: int = 50

    @field_validator("origin", "destination", mode="before")
    @classmethod
    def normalize_airport(cls, v: str) -> str:
        from flight_cli.utils.airports import REGIONS
        v = v.strip().upper()
        if v == "ANYWHERE" or v in REGIONS:
            return v
        if len(v) != 3 or not v.isalpha():
            raise ValueError(
                f"'{v}' is not a valid IATA code (3 letters), region name, or 'ANYWHERE'"
            )
        return v

    @property
    def has_anywhere(self) -> bool:
        return self.origin == "ANYWHERE" or self.destination == "ANYWHERE"

    @property
    def has_region(self) -> bool:
        from flight_cli.utils.airports import REGIONS
        return self.origin in REGIONS or self.destination in REGIONS

    @property
    def cache_key(self) -> str:
        return (
            f"{self.origin}:{self.destination}:{self.date}:"
            f"{self.passengers}:{self.cabin_class.value}"
        )
