"""Search form screen with airport autocomplete and step-by-step date picker."""
from __future__ import annotations

import calendar
from datetime import date

from rich.markup import escape
from rich.text import Text
from textual import events, on
from textual.app import ComposeResult
from textual.widget import Widget
from textual.binding import Binding
from textual.containers import Center, Horizontal, Middle, Vertical
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Footer, Input, Label, ListItem, ListView, Static

from flight_cli.models import SearchParams
from flight_cli.utils.airports import REGIONS, fuzzy_search_airport, fuzzy_search_region


_MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

_STAGE_HINTS = [
    "j/k · type year · Enter →",
    "← Backspace · j/k · type month · Enter →",
    "← Backspace · j/k · type day · Enter to confirm",
]


# ── DatePicker ────────────────────────────────────────────────────────────────


class DatePicker(Widget):
    """Step-by-step date input: Year → Month → Day.

    Navigation:
        j / ↓    decrement active field
        k / ↑    increment active field
        0-9      type digits into the active field
        Enter    confirm and advance to next field (or emit Submitted)
        Escape   reset to year stage
    """

    can_focus = True

    class Submitted(Message):
        def __init__(self, value: date) -> None:
            self.value = value
            super().__init__()

    DEFAULT_CSS = """
    DatePicker {
        height: 5;
        width: 100%;
        background: $panel;
        border: solid $primary-darken-2;
        padding: 0 1;
        color: $foreground;
    }
    DatePicker:focus {
        border: solid $accent;
    }
    """

    def __init__(self, initial: date | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        d = initial or date.today()
        self._year = d.year
        self._month = d.month
        self._day = 15
        self._stage = 0          # 0=year, 1=month, 2=day
        self._buf = ""

    # ── value ─────────────────────────────────────────────────────────────────

    @property
    def value(self) -> date:
        """Current date value (always valid — clamps to calendar)."""
        max_day = calendar.monthrange(self._year, self._month)[1]
        return date(self._year, self._month, min(self._day, max_day))

    # ── render ────────────────────────────────────────────────────────────────

    def render(self) -> Text:
        t = Text()

        # ── date segments ──
        if self._stage == 0 and self._buf:
            y_str = self._buf + "▌"
        else:
            y_str = str(self._year)
        t.append(f" {y_str} ", style="bold dark_orange underline" if self._stage == 0 else "white")

        t.append("  —  ", style="dim")

        if self._stage >= 1:
            if self._stage == 1 and self._buf:
                m_str = self._buf + "▌"
            else:
                m_str = f"{_MONTH_NAMES[self._month - 1]} {self._month:02d}"
            t.append(f" {m_str} ", style="bold dark_orange underline" if self._stage == 1 else "white")
        else:
            t.append(" ── ", style="dim")

        t.append("  —  ", style="dim")

        if self._stage >= 2:
            max_day = calendar.monthrange(self._year, self._month)[1]
            day = min(self._day, max_day)
            d_str = (self._buf + "▌") if self._buf else f"{day:02d}"
            t.append(f" {d_str} ", style="bold dark_orange underline")
        else:
            t.append(" ── ", style="dim")

        # ── hint on next line ──
        t.append("\n")
        t.append(_STAGE_HINTS[self._stage], style="dim")

        return t

    # ── keyboard ──────────────────────────────────────────────────────────────

    def on_key(self, event: events.Key) -> None:
        key = event.key

        if key in ("j", "down"):
            self._step(-1)
            self._buf = ""
            self._refresh()
            event.stop()

        elif key in ("k", "up"):
            self._step(+1)
            self._buf = ""
            self._refresh()
            event.stop()

        elif key.isdigit():
            self._buf += key
            self._refresh()
            self._maybe_auto_advance()
            event.stop()

        elif key == "backspace":
            if self._buf:
                self._buf = self._buf[:-1]
            elif self._stage > 0:
                self._stage -= 1
                self._buf = ""
            self._refresh()
            event.stop()

        elif key in ("left", "h"):
            if self._stage > 0:
                self._buf = ""
                self._stage -= 1
                self._refresh()
            event.stop()

        elif key in ("right", "l"):
            if self._stage < 2:
                if self._buf:
                    self._commit_buf()
                self._stage += 1
                self._buf = ""
                self._refresh()
            event.stop()

        elif key == "enter":
            if self._buf:
                self._commit_buf()
            if self._stage < 2:
                self._stage += 1
                self._buf = ""
                self._refresh()
            else:
                self.post_message(self.Submitted(self.value))
            event.stop()

        elif key == "escape":
            self._stage = 0
            self._buf = ""
            self._refresh()
            event.stop()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _refresh(self) -> None:
        max_day = calendar.monthrange(self._year, self._month)[1]
        self._day = min(self._day, max_day)
        self.refresh()

    def _step(self, delta: int) -> None:
        if self._stage == 0:
            self._year = max(date.today().year, min(2099, self._year + delta))
        elif self._stage == 1:
            self._month = (self._month - 1 + delta) % 12 + 1
        else:
            max_day = calendar.monthrange(self._year, self._month)[1]
            self._day = (self._day - 1 + delta) % max_day + 1

    def _commit_buf(self) -> bool:
        """Commit the digit buffer. Returns True if the value was valid and applied."""
        try:
            val = int(self._buf)
        except ValueError:
            self._buf = ""
            return False
        committed = False
        if self._stage == 0 and date.today().year <= val <= 2099:
            self._year = val
            committed = True
        elif self._stage == 1 and 1 <= val <= 12:
            self._month = val
            committed = True
        elif self._stage == 2:
            max_day = calendar.monthrange(self._year, self._month)[1]
            if 1 <= val <= max_day:
                self._day = val
                committed = True
        self._buf = ""
        self._refresh()
        return committed

    def _maybe_auto_advance(self) -> None:
        """Auto-advance to next field when enough digits are typed — only on valid input."""
        max_len = [4, 2, 2][self._stage]
        if len(self._buf) >= max_len:
            committed = self._commit_buf()
            if committed and self._stage < 2:
                self._stage += 1
                self._buf = ""
                self._refresh()


# ── Airport autocomplete widget ───────────────────────────────────────────────


class AirportInput(Vertical):
    """Airport input with live fuzzy-search suggestions."""

    class Selected(Message):
        def __init__(self, input_id: str, iata: str) -> None:
            self.input_id = input_id
            self.iata = iata
            super().__init__()

    DEFAULT_CSS = """
    AirportInput { height: auto; width: 100%; }

    AirportInput Input { width: 100%; margin-bottom: 0; }

    AirportInput ListView {
        display: none;
        height: auto;
        max-height: 6;
        border: solid $primary-darken-1;
        background: $panel;
        margin-top: 0;
        padding: 0;
    }

    AirportInput ListView.visible { display: block; }

    AirportInput ListItem {
        padding: 0 1;
        background: $panel;
    }

    AirportInput ListItem:hover,
    AirportInput ListItem.-highlighted {
        background: $primary-darken-1;
    }
    """

    def __init__(self, field_id: str, placeholder: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._field_id = field_id
        self._placeholder = placeholder
        # Each entry is either an IATA code ("ORD") or a region key ("EUROPE")
        self._suggestion_values: list[str] = []

    def compose(self) -> ComposeResult:
        yield Input(placeholder=self._placeholder, id=self._field_id)
        yield ListView(id=f"{self._field_id}-suggestions")

    @on(Input.Changed)
    def _on_changed(self, event: Input.Changed) -> None:
        query = event.value.strip()
        lv = self.query_one(f"#{self._field_id}-suggestions", ListView)

        # Suppress suggestions when input is already a resolved value
        upper = query.upper()
        if (
            len(query) < 2
            or upper == "ANYWHERE"
            or upper in REGIONS
            or (len(query) == 3 and query.isalpha())
        ):
            lv.remove_class("visible")
            lv.clear()
            self._suggestion_values = []
            return

        # Build combined airport + region suggestions
        airport_results = fuzzy_search_airport(query, limit=5)
        region_results = fuzzy_search_region(query)  # [(key, display_label), ...]

        items: list[tuple[str, str]] = []  # (value_to_store, display_label)
        for a in airport_results:
            items.append((a.iata, f"{a.iata}  {a.city}, {a.country}  —  {a.name}"))
        for key, label in region_results:
            items.append((key, f"◎  {label}"))

        if not items:
            lv.remove_class("visible")
            lv.clear()
            self._suggestion_values = []
            return

        self._suggestion_values = [v for v, _ in items]
        lv.clear()
        for _, display in items:
            lv.append(ListItem(Static(display)))
        lv.add_class("visible")

    @on(Input.Submitted)
    def _on_submitted(self, _: Input.Submitted) -> None:
        self._dismiss()

    @on(ListView.Selected)
    def _on_suggestion_selected(self, event: ListView.Selected) -> None:
        # Look up by index in our stored values list
        try:
            idx = list(event.list_view._nodes).index(event.item)
            value = self._suggestion_values[idx]
        except (ValueError, IndexError):
            # Fallback: parse first word from label
            try:
                label_widget = event.item.query_one(Static)
                raw = str(label_widget.renderable).lstrip("◎ ").split()[0]
                value = raw
            except Exception:
                value = ""

        if value:
            # Display regions in title case, IATA codes as-is
            display = value.title() if value in REGIONS else value
            inp = self.query_one(f"#{self._field_id}", Input)
            inp.value = display
            inp.cursor_position = len(display)
        self._dismiss()
        self.post_message(self.Selected(self._field_id, value))

    def _dismiss(self) -> None:
        lv = self.query_one(f"#{self._field_id}-suggestions", ListView)
        lv.remove_class("visible")
        lv.clear()

    def current_value(self) -> str:
        return self.query_one(f"#{self._field_id}", Input).value

    def focus_input(self) -> None:
        self.query_one(f"#{self._field_id}", Input).focus()


# ── Search screen ─────────────────────────────────────────────────────────────


class SearchScreen(Screen):
    BINDINGS = [Binding("ctrl+q", "quit", "Quit", show=True)]

    CSS = """
    SearchScreen {
        align: center middle;
        background: $surface;
    }

    #form-container {
        width: 68;
        height: auto;
        background: $panel;
        border: solid $primary;
        padding: 2 3;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        width: 100%;
    }

    #subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
        width: 100%;
    }

    .field-label {
        color: $text-muted;
        margin-top: 1;
    }

    Input { width: 100%; margin-bottom: 0; }

    #search-btn {
        width: 100%;
        margin-top: 2;
        background: $accent;
        color: $background;
        text-style: bold;
    }

    #search-btn:hover { background: $accent-lighten-1; }

    #error-msg {
        color: $error;
        text-align: center;
        margin-top: 1;
        display: none;
        width: 100%;
    }

    #error-msg.visible { display: block; }

    #mock-notice {
        text-align: center;
        color: $warning;
        margin-top: 1;
        width: 100%;
    }
    """

    def __init__(self, is_mock: bool = False, engine=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._is_mock = is_mock
        self._engine = engine

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                with Vertical(id="form-container"):
                    yield Static("✈  Flight Search", id="title")
                    yield Static("City · IATA code · Region (Europe, Asia…) · ANYWHERE", id="subtitle")

                    yield Label("From", classes="field-label")
                    yield AirportInput(
                        field_id="origin",
                        placeholder="e.g. Chicago · JFK · Europe · ANYWHERE",
                        id="origin-widget",
                    )

                    yield Label("To", classes="field-label")
                    yield AirportInput(
                        field_id="destination",
                        placeholder="e.g. London · LAX · Asia · ANYWHERE",
                        id="destination-widget",
                    )

                    yield Label("Date  (j/k to adjust, Enter to confirm each part)", classes="field-label")
                    yield DatePicker(id="date-picker")

                    yield Button("Search Flights  ▶", id="search-btn", variant="primary")
                    yield Static("", id="error-msg")

                    if self._is_mock:
                        yield Static(
                            "⚠  No API credentials — showing demo data. "
                            "Set SERPAPI_KEY in .env for real flights.",
                            id="mock-notice",
                        )

        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#origin-widget", AirportInput).focus_input()

    # ── Navigation flow ───────────────────────────────────────────────────────

    @on(AirportInput.Selected)
    def _airport_selected(self, event: AirportInput.Selected) -> None:
        if event.input_id == "origin":
            self.query_one("#destination-widget", AirportInput).focus_input()
        elif event.input_id == "destination":
            self.query_one("#date-picker", DatePicker).focus()

    @on(Input.Submitted, "#origin")
    @on(Input.Submitted, "#destination")
    def _advance_airport(self, event: Input.Submitted) -> None:
        if event.input.id == "origin":
            self.query_one("#destination-widget", AirportInput).focus_input()
        elif event.input.id == "destination":
            self.query_one("#date-picker", DatePicker).focus()

    @on(DatePicker.Submitted)
    def _date_confirmed(self, _: DatePicker.Submitted) -> None:
        self._do_search()

    @on(Button.Pressed, "#search-btn")
    def _on_search_pressed(self) -> None:
        self._do_search()

    # ── Search ────────────────────────────────────────────────────────────────

    def _do_search(self) -> None:
        origin = self.query_one("#origin-widget", AirportInput).current_value().strip().upper()
        destination = self.query_one("#destination-widget", AirportInput).current_value().strip().upper()
        search_date = self.query_one("#date-picker", DatePicker).value

        try:
            params = SearchParams(
                origin=origin,
                destination=destination,
                date=search_date,
            )
        except Exception as exc:
            self._show_error(_clean_validation_error(exc))
            return

        self._hide_error()
        self.app.open_results(params)  # type: ignore[attr-defined]

    def _show_error(self, msg: str) -> None:
        err = self.query_one("#error-msg", Static)
        err.update(Text.assemble(("⚠  ", "bold red"), msg))
        err.add_class("visible")

    def _hide_error(self) -> None:
        self.query_one("#error-msg", Static).remove_class("visible")


# ── helpers ───────────────────────────────────────────────────────────────────


def _clean_validation_error(exc: Exception) -> str:
    import re
    raw = str(exc)
    for line in raw.splitlines():
        line = line.strip()
        if "Value error," in line:
            msg = re.sub(r"\s*\[type=\w+.*", "", line.replace("Value error,", "").strip())
            return escape(msg)
        if "value is not a valid" in line.lower():
            return escape(re.sub(r"\s*\[type=\w+.*", "", line.strip()))
    for line in raw.splitlines():
        if line.strip():
            return escape(re.sub(r"\s*\[type=\w+.*", "", line.strip())[:120])
    return escape(raw[:120])
