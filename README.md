# ✈ flight-search

Fast, interactive CLI flight search — like Google Flights in your terminal.

```
  ✈  JFK → LAX   Jun 15, 2024   1 pax   Economy              Sort: Price ↑

 ─── Filters ─── │  Airline  Flight   From  Departs  To    Arrives   Duration  Stops    Price
                 │─────────────────────────────────────────────────────────────────────────────
 Stops           │  NK       NK2341   JFK   05:30    LAX   10:45     10h 15m   2 stops   $99
  ○ Any          │▶ F9       F9881    JFK   14:00    LAX   19:15     8h 00m    1 stop    $145
  ● Max 1 stop   │  AA       AA100    JFK   08:00    LAX   11:30     5h 30m    Nonstop   $210
  ○ Nonstop      │  DL       DL421    JFK   07:00    LAX   10:00     5h 00m    Nonstop   $350
                 │  BA       BA178    JFK   06:00    LAX   10:00     5h 00m    Nonstop   $520
 Airlines        │
  ☑ AA           │
  ☑ DL           │
  ☑ F9           │
  ☑ NK           │
  ☑ BA           │

  ↑↓ Navigate   p Price   d Duration   t Dep Time   a Arr Time   f Filters   ESC Back   ^Q Quit
```

## Quick Start

```bash
git clone <repo>
cd flight-search
uv sync

# Run in demo mode (no API key needed)
uv run flights --mock

# Or just launch — uses demo data if no .env present
uv run flights
```

## API Setup (for real flight data)

Copy `.env.example` to `.env` and fill in **one** of the following:

### Option A — Amadeus (recommended)
Free test environment, ~2,000 requests/month, no credit card required.

1. Sign up at [developers.amadeus.com](https://developers.amadeus.com/register) (~5 min, self-service)
2. Create an app → copy **Client ID** and **Client Secret**
3. Add to `.env`:
   ```
   AMADEUS_CLIENT_ID=...
   AMADEUS_CLIENT_SECRET=...
   ```

> **Note:** The Amadeus test environment covers routes involving US, Spain, UK, Germany, and India airports. Use `--mock` for other routes while developing.

### Option B — SerpAPI (Google Flights data)
Real Google Flights results, 250 free searches/month.

1. Sign up at [serpapi.com](https://serpapi.com/users/sign_up)
2. Copy your API key from the dashboard
3. Add to `.env`:
   ```
   SERPAPI_KEY=...
   ```

## Usage

```bash
uv run flights                     # launch interactive TUI
uv run flights --mock              # demo mode (offline, no API key)
uv run flights -f nonstop_only     # pre-apply a named filter from config.yaml
uv run flights -c my-config.yaml   # use a custom config file
uv run flights --debug             # verbose logging
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate flight list |
| `p` | Sort by price (toggle ↑/↓) |
| `d` | Sort by duration |
| `t` | Sort by departure time |
| `a` | Sort by arrival time |
| `f` | Focus filter panel |
| `r` | Refresh (bypass cache) |
| `ESC` | Back to search form |
| `Ctrl+Q` | Quit |

## Search

- **Airports**: standard IATA codes (`JFK`, `LHR`, `SYD`)
- **ANYWHERE**: type `ANYWHERE` as origin or destination to search all major airports
  - `JFK → ANYWHERE`: find all destinations from New York
  - `ANYWHERE → LHR`: find all routes into London Heathrow

## Configuration

Edit `config.yaml` to define named filters, defaults, and the major-airports list used for ANYWHERE searches.

```yaml
defaults:
  passengers: 1
  cabin_class: economy
  max_results: 50
  anywhere_concurrency: 10   # parallel API calls for ANYWHERE

filters:
  cheap:
    max_price: 200
  nonstop_only:
    stops: 0
  business_trip:
    departure_time_start: "06:00"
    departure_time_end: "10:00"
    stops: 0
```

Apply a named filter at launch:
```bash
uv run flights -f cheap
uv run flights -f nonstop_only
```

## Architecture

```
flight_cli/
├── cli/screens/      # Textual TUI screens (search form, results table)
├── core/             # Search engine + ANYWHERE fan-out logic
├── providers/        # API integrations (Amadeus, SerpAPI, Mock)
├── models/           # Pydantic data models (Flight, Segment, SearchParams)
├── filters/          # FilterState + apply_filters()
├── sorting/          # SortKey enum + sort_flights()
├── config/           # YAML config loader
├── cache/            # Two-tier cache (in-memory LRU + diskcache)
└── utils/            # Airport database (~150 airports) + fuzzy search
```

### Provider Auto-detection

```
AMADEUS_CLIENT_ID + AMADEUS_CLIENT_SECRET  →  Amadeus (priority)
SERPAPI_KEY                                →  SerpAPI / Google Flights
(neither set)                              →  Mock (demo data, always works)
```

### ANYWHERE Logic

ANYWHERE searches fan out in parallel across all configured major airports via `asyncio.gather` with a semaphore. A search like `JFK → ANYWHERE` fires ~80 concurrent API requests, deduplicates by flight ID, and returns all results sorted by price.

## Tests

```bash
uv run pytest tests/ -v
```

28 tests covering filters, sorting, ANYWHERE fan-out/deduplication/error-handling.

## API Tradeoffs

| Provider | Data | Free Tier | Notes |
|----------|------|-----------|-------|
| Amadeus | GDS (real bookable fares) | ~2K req/mo | Best option; test routes limited to select markets |
| SerpAPI | Google Flights scrape | 250/mo | Real display prices; no booking path |
| Mock | Deterministic fake data | Unlimited | Great for development and demos |
