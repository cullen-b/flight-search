"""Main Textual application."""
from __future__ import annotations

from textual.app import App, ComposeResult
from textual.message import Message

from flight_cli.cli.screens.results import ResultsScreen
from flight_cli.cli.screens.search import SearchScreen
from flight_cli.config import AppConfig
from flight_cli.core import FlightSearchEngine
from flight_cli.models import SearchParams


class FlightSearchApp(App):
    """Root application — manages the search engine and screen stack."""

    TITLE = "Flight Search"
    SUB_TITLE = "Fast. Interactive. Yours."

    CSS = """
    App {
        background: #0d1117;
        color: #e6edf3;
    }

    Screen {
        background: #0d1117;
    }
    """

    def __init__(self, config: AppConfig, **kwargs) -> None:
        super().__init__(**kwargs)
        self._config = config
        self._engine = FlightSearchEngine(config)

    def on_mount(self) -> None:
        self.push_screen(SearchScreen(is_mock=self._engine.using_mock, engine=self._engine))

    async def on_unmount(self) -> None:
        await self._engine.close()

    def open_results(self, params: SearchParams) -> None:
        """Called by SearchScreen to push the results screen."""
        self.push_screen(
            ResultsScreen(
                params=params,
                engine=self._engine,
                is_mock=self._engine.using_mock,
            )
        )
