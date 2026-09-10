from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class DefaultsConfig:
    passengers: int = 1
    cabin_class: str = "economy"
    max_results: int = 50
    anywhere_concurrency: int = 10


@dataclass
class CacheConfig:
    ttl_seconds: int = 300
    directory: str = "~/.flight_cache"

    @property
    def resolved_directory(self) -> Path:
        return Path(self.directory).expanduser()


@dataclass
class NamedFilter:
    stops: int | None = None
    max_price: float | None = None
    min_price: float | None = None
    departure_time_start: str | None = None
    departure_time_end: str | None = None


@dataclass
class AppConfig:
    defaults: DefaultsConfig = field(default_factory=DefaultsConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    filters: dict[str, NamedFilter] = field(default_factory=dict)
    major_airports: list[str] = field(default_factory=list)

    def get_filter(self, name: str) -> NamedFilter | None:
        return self.filters.get(name)


def _parse_filter(raw: dict[str, Any]) -> NamedFilter:
    return NamedFilter(
        stops=raw.get("stops"),
        max_price=raw.get("max_price"),
        min_price=raw.get("min_price"),
        departure_time_start=raw.get("departure_time_start"),
        departure_time_end=raw.get("departure_time_end"),
    )


def load_config(path: str | Path | None = None) -> AppConfig:
    """Load config from YAML file. Falls back to defaults if file not found."""
    if path is None:
        candidates = [
            Path.cwd() / "config.yaml",
            Path.home() / ".config" / "flight-search" / "config.yaml",
        ]
        for candidate in candidates:
            if candidate.exists():
                path = candidate
                break

    if path is None or not Path(path).exists():
        return AppConfig()

    with open(path) as f:
        raw = yaml.safe_load(f) or {}

    defaults_raw = raw.get("defaults", {})
    defaults = DefaultsConfig(
        passengers=defaults_raw.get("passengers", 1),
        cabin_class=defaults_raw.get("cabin_class", "economy"),
        max_results=defaults_raw.get("max_results", 50),
        anywhere_concurrency=defaults_raw.get("anywhere_concurrency", 10),
    )

    cache_raw = raw.get("cache", {})
    cache = CacheConfig(
        ttl_seconds=cache_raw.get("ttl_seconds", 300),
        directory=cache_raw.get("directory", "~/.flight_cache"),
    )

    filters_raw = raw.get("filters", {})
    filters = {name: _parse_filter(fraw) for name, fraw in filters_raw.items()}

    airports_raw = raw.get("airports", {}).get("major", [])

    return AppConfig(
        defaults=defaults,
        cache=cache,
        filters=filters,
        major_airports=airports_raw,
    )
