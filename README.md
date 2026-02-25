# DC Shows

A minimal Node.js web server that sits in front of the Python venue scrapers and
presents upcoming DC area concert listings in a clean browser UI.

---

## How it works

```
Browser  ←→  server.js (Express)  ←→  scraping/scrape_json.py  ←→  Venue classes
```

1. **`server.js`** serves the single-page frontend and exposes two JSON API routes.
2. When the user clicks a venue, the browser calls `GET /api/scrape?venue=VenueName`.
3. **`server.js`** spawns `scraping/scrape_json.py` as a child process with the venue name.
4. **`scrape_json.py`** imports the matching venue class, calls `getData()` → `parse()`,
   then serialises `venue.shows` to JSON on stdout.
5. The server parses that JSON, caches it for 5 minutes, and returns it to the browser.
6. The frontend renders each show as a card.

The original `scrape.py` is untouched — `scrape_json.py` is a thin wrapper that reuses
the same venue classes and adds JSON output + argument parsing.

---

## Files added

| File | Purpose |
|---|---|
| `server.js` | Express server — API routes, child-process spawning, in-memory cache |
| `scraping/scrape_json.py` | Python wrapper — accepts `--venues` args, outputs one JSON line |
| `public/index.html` | Single-page frontend — venue selector, show cards, skeleton loader |
| `package.json` | npm manifest — only dependency is Express |

---

## Setup

### Prerequisites

- **Node.js** v18 or newer
- **Python 3** (3.8+)

### Create the Python virtual environment

```bash
python3 -m venv .venv
.venv/bin/pip install requests beautifulsoup4
```

`server.js` automatically invokes `.venv/bin/python3` so nothing needs to be
installed into the system Python.

### Install Node dependencies

```bash
npm install
```

---

## Running the server

```bash
node server.js
# or
npm start
```

Open **http://localhost:3000** in your browser.

To run on a different port:

```bash
PORT=8080 node server.js
```

For auto-restart on file changes during development (Node 18+):

```bash
npm run dev
```

---

## Using the UI

- Click a venue pill to load its upcoming shows.
- Results are **cached for 5 minutes** — re-clicking a venue within that window
  returns the cached data instantly and notes "Showing cached results."
- After the TTL expires the scraper runs again on next click.

---

## Adding a new venue

1. Write the venue class in `scraping/MyVenue.py` following the existing `Venue` subclass pattern.
2. Add it to `VENUE_MAP` in **`scraping/scrape_json.py`**.
3. Add its class name to `VENUE_NAMES` in **`server.js`**.
4. Add a display name to `VENUE_DISPLAY` in **`public/index.html`**.

---

## Notes

- The Python scrapers print cooldown and debug messages to stderr; these are
  logged server-side only and never reach the browser.
- Songbyrd's `link` field is a ticket price (integer) rather than a URL — the
  frontend detects this and renders it as `$N` instead of a link.
- DC9's `opener` field is a `string[]` rather than a plain string — the
  frontend joins the array with commas automatically.
- Scrape cooldown files live in `scraping/cooldowns/` and are respected even when called
  from the Node server (the Python side handles all rate limiting).
