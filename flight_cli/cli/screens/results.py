"""Results screen: full-width flight table with a compact top filter bar."""
from __future__ import annotations

import time
from typing import TYPE_CHECKING

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.message import Message
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Input,
    Label,
    LoadingIndicator,
    Static,
)

from flight_cli.filters import FilterState, apply_filters
from flight_cli.models import Flight, SearchParams
from flight_cli.sorting import SortKey, sort_flights
from flight_cli.utils.airlines import get_airline_name
from flight_cli.utils.airports import get_airport

if TYPE_CHECKING:
    pass


# ── Filter bar ────────────────────────────────────────────────────────────────

_STOP_OPTS: list[tuple[str, str, int | None]] = [
    ("Any", "any", None),
    ("Nonstop", "nonstop", 0),
    ("1 stop", "one", 1),
    ("2+ stops", "twoplus", 2),
]


class FilterBar(Vertical):
    """Compact horizontal filter bar rendered above the flight table."""

    class Changed(Message):
        def __init__(self, state: FilterState) -> None:
            self.state = state
            super().__init__()

    DEFAULT_CSS = """
    FilterBar {
        height: auto;
        width: 100%;
        background: $panel;
        border-bottom: solid $primary-darken-1;
        padding: 0 1;
    }

    .filter-row {
        height: 3;
        align: left middle;
    }

    .filter-sep {
        width: 1;
        height: 3;
        content-align: center middle;
        color: $primary-darken-1;
    }

    .filter-label {
        color: $text-muted;
        height: 3;
        content-align: left middle;
        padding: 0 1 0 0;
    }

    .stop-btn {
        min-width: 10;
        height: 3;
        border: blank;
        background: $surface;
        color: $text-muted;
        margin-right: 1;
    }

    .stop-btn:hover {
        background: $primary-darken-2;
        color: $foreground;
    }

    .stop-btn.active {
        background: $accent;
        color: $background;
        text-style: bold;
    }

    #price-input {
        width: 9;
        height: 3;
        border: solid $primary-darken-2;
    }

    #reset-btn {
        min-width: 9;
        height: 3;
        background: $surface;
        color: $text-muted;
        border: solid $primary-darken-2;
        margin-left: 2;
    }

    #reset-btn:hover {
        background: $error-darken-1;
        color: $foreground;
    }

    #airlines-row {
        height: 3;
        align: left middle;
        overflow-x: auto;
    }

    .airline-btn {
        width: auto;
        min-width: 6;
        height: 3;
        border: blank;
        background: $primary-darken-1;
        color: $foreground;
        margin-right: 1;
        margin-bottom: 0;
    }

    .airline-btn:hover {
        background: $primary;
    }

    .airline-btn.dimmed {
        background: $surface;
        color: $text-muted;
        text-style: strike;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._max_stops: int | None = None
        self._disabled_airlines: set[str] = set()
        self._all_airlines: list[str] = []
        self._max_price: float | None = None

    def compose(self) -> ComposeResult:
        with Horizontal(classes="filter-row"):
            yield Static("Stops:", classes="filter-label")
            for label, slug, value in _STOP_OPTS:
                classes = "stop-btn active" if value is None else "stop-btn"
                yield Button(label, id=f"stop-{slug}", classes=classes)
            yield Static("  $max:", classes="filter-label")
            yield Input(placeholder="∞", id="price-input", max_length=7)
            yield Button("↺ Reset", id="reset-btn")

        with Horizontal(id="airlines-row"):
            yield Static("Airlines:", classes="filter-label")
            # Airline buttons are added dynamically via update_airlines()

    # ── public API ────────────────────────────────────────────────────────────

    def update_airlines(self, airlines: list[str]) -> None:
        """Rebuild the airline toggle buttons from a fresh list."""
        row = self.query_one("#airlines-row", Horizontal)
        # Remove existing airline buttons (keep the label)
        for btn in row.query(".airline-btn"):
            btn.remove()
        self._all_airlines = sorted(airlines)
        for code in self._all_airlines:
            name = get_airline_name(code, max_len=14)
            is_dimmed = code in self._disabled_airlines
            btn = Button(name, id=f"airline-{code}",
                         classes="airline-btn dimmed" if is_dimmed else "airline-btn")
            row.mount(btn)

    def get_state(self) -> FilterState:
        try:
            price_val = float(self.query_one("#price-input", Input).value)
            max_price = price_val if price_val > 0 else None
        except (ValueError, TypeError):
            max_price = None

        if self._disabled_airlines and self._all_airlines:
            active = set(self._all_airlines) - self._disabled_airlines
        else:
            active = set()  # empty = all

        return FilterState(
            max_stops=self._max_stops,
            airlines=active,
            max_price=max_price,
        )

    # ── event handlers ────────────────────────────────────────────────────────

    @on(Button.Pressed)
    def _on_button(self, event: Button.Pressed) -> None:
        btn_id = str(event.button.id or "")

        if btn_id.startswith("stop-"):
            slug = btn_id[5:]
            self._max_stops = next(
                (v for _, s, v in _STOP_OPTS if s == slug), None
            )
            for _, s, _ in _STOP_OPTS:
                b = self.query_one(f"#stop-{s}", Button)
                if s == slug:
                    b.add_class("active")
                else:
                    b.remove_class("active")
            self.post_message(self.Changed(self.get_state()))

        elif btn_id.startswith("airline-"):
            code = btn_id[len("airline-"):]
            btn = event.button
            if code in self._disabled_airlines:
                self._disabled_airlines.discard(code)
                btn.remove_class("dimmed")
            else:
                self._disabled_airlines.add(code)
                btn.add_class("dimmed")
            self.post_message(self.Changed(self.get_state()))

        elif btn_id == "reset-btn":
            self._reset()

        event.stop()

    @on(Input.Changed, "#price-input")
    def _on_price_changed(self, _: Input.Changed) -> None:
        self.post_message(self.Changed(self.get_state()))

    def _reset(self) -> None:
        self._max_stops = None
        self._disabled_airlines.clear()
        self._max_price = None
        self.query_one("#price-input", Input).value = ""
        for _, slug, val in _STOP_OPTS:
            b = self.query_one(f"#stop-{slug}", Button)
            if val is None:
                b.add_class("active")
            else:
                b.remove_class("active")
        for code in self._all_airlines:
            try:
                self.query_one(f"#airline-{code}", Button).remove_class("dimmed")
            except Exception:
                pass
        self.post_message(self.Changed(FilterState()))


# ── Results screen ────────────────────────────────────────────────────────────


class ResultsScreen(Screen):
    """Full-width results table with a compact filter bar at the top."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
        Binding("p", "sort_price", "Price", show=True),
        Binding("d", "sort_duration", "Duration", show=True),
        Binding("t", "sort_departs", "Dep time", show=True),
        Binding("a", "sort_arrives", "Arr time", show=True),
        Binding("r", "do_refresh", "Refresh", show=True),
        Binding("ctrl+q", "quit", "Quit", show=True),
        # vim navigation (show=False so they don't crowd the footer)
        Binding("j", "vim_down", "", show=False),
        Binding("k", "vim_up", "", show=False),
        Binding("G", "vim_end", "", show=False),
        Binding("g", "vim_g_press", "", show=False),
        Binding("ctrl+d", "vim_half_down", "", show=False),
        Binding("ctrl+u", "vim_half_up", "", show=False),
    ]

    CSS = """
    ResultsScreen {
        layout: vertical;
    }

    #header-bar {
        height: 3;
        background: $panel;
        border-bottom: solid $primary;
        padding: 0 2;
        align: left middle;
    }

    #route-label {
        text-style: bold;
        color: $accent;
    }

    #count-label {
        color: $text-muted;
        margin-left: 2;
    }

    #sort-label {
        color: $success;
        margin-left: 2;
    }

    #mock-badge {
        color: $warning;
        margin-left: 2;
    }

    #results-area {
        height: 1fr;
        width: 100%;
    }

    #loading-container {
        align: center middle;
        height: 100%;
        width: 100%;
    }

    DataTable {
        height: 1fr;
        width: 100%;
    }

    DataTable > .datatable--header {
        text-style: bold;
        color: $accent;
        background: $panel;
    }

    DataTable > .datatable--cursor {
        background: $accent;
        color: $background;
    }

    DataTable > .datatable--hover {
        background: $primary-darken-2;
    }

    #empty-msg {
        text-align: center;
        color: $text-muted;
        margin-top: 4;
        width: 100%;
    }
    """

    def __init__(self, params: SearchParams, engine, is_mock: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self._params = params
        self._engine = engine
        self._is_mock = is_mock
        self._all_flights: list[Flight] = []
        self._filtered: list[Flight] = []
        self._filter_state = FilterState()
        self._sort_key = SortKey.PRICE_ASC
        self._last_g_time: float = 0.0

    def compose(self) -> ComposeResult:
        with Horizontal(id="header-bar"):
            yield Static(self._route_label(), id="route-label")
            yield Static("", id="count-label")
            yield Static(f"  Sort: {self._sort_key.label()}", id="sort-label")
            if self._is_mock:
                yield Static("  [DEMO]", id="mock-badge")

        yield FilterBar(id="filter-bar")

        with Vertical(id="results-area"):
            with Container(id="loading-container"):
                yield LoadingIndicator()
                yield Static("Searching for flights…", id="loading-msg")

        yield Footer()

    def on_mount(self) -> None:
        self._fetch_flights()

    # ── Data loading ──────────────────────────────────────────────────────────

    @work(exclusive=True)
    async def _fetch_flights(self) -> None:
        try:
            flights = await self._engine.search(self._params)
        except Exception as exc:
            self._teardown_loading()
            self.query_one("#results-area", Vertical).mount(
                Static(f"Error: {exc}", id="empty-msg")
            )
            return
        self._all_flights = flights
        self._apply_and_render()

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _apply_and_render(self) -> None:
        self._filtered = sort_flights(
            apply_filters(self._all_flights, self._filter_state),
            self._sort_key,
        )
        self._show_results(self._filtered)
        self._update_header()
        self._update_airline_buttons()

    def _teardown_loading(self) -> None:
        area = self.query_one("#results-area", Vertical)
        for w in area.query("#loading-container"):
            w.remove()

    def _airport_label(self, iata: str, expanded: bool) -> str:
        """Return 'City (CODE)' if expanded, else just 'CODE'."""
        if not expanded:
            return iata
        airport = get_airport(iata)
        city = airport.city if airport else iata
        return f"{city} ({iata})"

    def _show_results(self, flights: list[Flight]) -> None:
        area = self.query_one("#results-area", Vertical)
        self._teardown_loading()

        # Remove empty-msg if present
        for w in area.query("#empty-msg"):
            w.remove()

        if not flights:
            # Remove table if present then show message
            for w in area.query(DataTable):
                w.remove()
            area.mount(Static(
                "No flights match your filters. Try adjusting the criteria.",
                id="empty-msg",
            ))
            return

        # In ANYWHERE/region mode, expand whichever side is variable to city names
        from flight_cli.utils.airports import REGIONS
        expand_origin = self._params.origin in REGIONS or self._params.origin == "ANYWHERE"
        expand_dest = self._params.destination in REGIONS or self._params.destination == "ANYWHERE"
        from_width = 16 if expand_origin else 5
        to_width = 16 if expand_dest else 5

        # Reuse existing table to avoid async-removal DuplicateIds crash
        existing = list(area.query(DataTable))
        if existing:
            table = existing[0]
            table.clear(columns=False)
        else:
            table = DataTable(id="flight-table", cursor_type="row", zebra_stripes=True)
            area.mount(table)
            table.add_column("Airline", key="airline", width=20)
            table.add_column("Flight", key="flight", width=8)
            table.add_column("From", key="from", width=from_width)
            table.add_column("Departs", key="departs", width=7)
            table.add_column("To", key="to", width=to_width)
            table.add_column("Arrives", key="arrives", width=7)
            table.add_column("Duration", key="duration", width=9)
            table.add_column("Stops", key="stops", width=10)
            table.add_column("Price", key="price", width=9)

        for f in flights:
            table.add_row(
                get_airline_name(f.airline, max_len=19),
                f.segments[0].flight_number,
                self._airport_label(f.departure_airport, expand_origin),
                f.departure_time.strftime("%H:%M"),
                self._airport_label(f.arrival_airport, expand_dest),
                f.arrival_time.strftime("%H:%M"),
                f.duration_str(),
                f.stops_label(),
                f"${f.price:,.0f}",
                key=f.id,
            )
        table.focus()

    def _update_header(self) -> None:
        total = len(self._all_flights)
        shown = len(self._filtered)
        txt = f"  {shown} of {total}" if shown < total else f"  {total} flight{'s' if total != 1 else ''}"
        self.query_one("#count-label", Static).update(txt)
        self.query_one("#sort-label", Static).update(f"  Sort: {self._sort_key.label()}")

    def _update_airline_buttons(self) -> None:
        airlines = sorted({f.airline for f in self._all_flights})
        self.query_one("#filter-bar", FilterBar).update_airlines(airlines)

    def _route_label(self) -> str:
        p = self._params
        return (
            f"  ✈  {p.origin} → {p.destination}   "
            f"{p.date.strftime('%b %-d, %Y')}   "
            f"{p.passengers} pax   "
            f"{p.cabin_class.value.replace('_', ' ').title()}"
        )

    # ── Filter events ─────────────────────────────────────────────────────────

    def on_filter_bar_changed(self, event: FilterBar.Changed) -> None:
        self._filter_state = event.state
        self._apply_and_render()

    # ── Sort actions ──────────────────────────────────────────────────────────

    def _toggle_sort(self, asc: SortKey, desc: SortKey) -> None:
        self._sort_key = desc if self._sort_key == asc else asc
        self._apply_and_render()

    def action_sort_price(self) -> None:
        self._toggle_sort(SortKey.PRICE_ASC, SortKey.PRICE_DESC)

    def action_sort_duration(self) -> None:
        self._toggle_sort(SortKey.DURATION_ASC, SortKey.DURATION_DESC)

    def action_sort_departs(self) -> None:
        self._toggle_sort(SortKey.DEPARTURE_ASC, SortKey.DEPARTURE_DESC)

    def action_sort_arrives(self) -> None:
        self._toggle_sort(SortKey.ARRIVAL_ASC, SortKey.ARRIVAL_DESC)

    # ── Vim navigation ────────────────────────────────────────────────────────

    def _get_table(self) -> DataTable | None:
        try:
            return self.query_one(DataTable)
        except Exception:
            return None

    def _nav(self, delta: int) -> None:
        """Move the DataTable cursor by delta rows."""
        table = self._get_table()
        if table is None:
            return
        table.focus()
        new_row = max(0, min(table.row_count - 1, table.cursor_row + delta))
        table.move_cursor(row=new_row)

    def action_vim_down(self) -> None:
        self._nav(+1)

    def action_vim_up(self) -> None:
        self._nav(-1)

    def action_vim_end(self) -> None:
        table = self._get_table()
        if table:
            table.focus()
            table.move_cursor(row=max(0, table.row_count - 1))

    def action_vim_g_press(self) -> None:
        """Single g → go to top; gg (two presses <500ms) also goes to top."""
        now = time.monotonic()
        if now - self._last_g_time < 0.5:
            # double-g
            self._last_g_time = 0.0
        else:
            self._last_g_time = now
        # Either way, go to top (single g is fine for our purposes)
        table = self._get_table()
        if table:
            table.focus()
            table.move_cursor(row=0)

    def action_vim_half_down(self) -> None:
        table = self._get_table()
        if table:
            self._nav(max(1, table.row_count // 2))

    def action_vim_half_up(self) -> None:
        table = self._get_table()
        if table:
            self._nav(-max(1, table.row_count // 2))

    # ── Other actions ─────────────────────────────────────────────────────────

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_do_refresh(self) -> None:
        self._engine._cache.invalidate(self._params.cache_key)
        self._all_flights = []
        area = self.query_one("#results-area", Vertical)
        for w in area.query(DataTable):
            w.remove()
        for w in area.query("#empty-msg"):
            w.remove()
        loading = Container(id="loading-container")
        area.mount(loading)
        loading.mount(LoadingIndicator())
        loading.mount(Static("Refreshing…", id="loading-msg"))
        self._fetch_flights()
