from __future__ import annotations

import json
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

import diskcache

from flight_cli.models import Flight


class FlightCache:
    """Two-tier cache: in-memory LRU + disk persistence."""

    def __init__(self, directory: Path, ttl_seconds: int = 300) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        self._disk = diskcache.Cache(str(directory))
        self._ttl = ttl_seconds
        self._memory: dict[str, tuple[float, list[Flight]]] = {}

    def get(self, key: str) -> list[Flight] | None:
        # Check in-memory cache first
        if key in self._memory:
            ts, flights = self._memory[key]
            if time.time() - ts < self._ttl:
                return flights
            del self._memory[key]

        # Check disk cache
        raw = self._disk.get(key)
        if raw is not None:
            ts, data = raw
            if time.time() - ts < self._ttl:
                flights = [Flight.model_validate(f) for f in data]
                self._memory[key] = (ts, flights)
                return flights
            else:
                del self._disk[key]

        return None

    def set(self, key: str, flights: list[Flight]) -> None:
        ts = time.time()
        data = [f.model_dump(mode="json") for f in flights]
        self._memory[key] = (ts, flights)
        self._disk.set(key, (ts, data), expire=self._ttl * 2)

    def invalidate(self, key: str) -> None:
        self._memory.pop(key, None)
        self._disk.delete(key)

    def clear(self) -> None:
        self._memory.clear()
        self._disk.clear()

    def close(self) -> None:
        self._disk.close()
