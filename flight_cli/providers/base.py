from __future__ import annotations

from abc import ABC, abstractmethod

from flight_cli.models import Flight, SearchParams


class FlightProvider(ABC):
    """Abstract base class for flight data providers."""

    @abstractmethod
    async def search(self, params: SearchParams) -> list[Flight]:
        """Search for flights matching the given parameters.

        Raises:
            ProviderError: if the API call fails.
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """Release any held resources (HTTP clients, etc.)."""
        ...


class ProviderError(Exception):
    """Raised when a provider API call fails."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
