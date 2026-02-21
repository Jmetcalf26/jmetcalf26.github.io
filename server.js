/**
 * server.js — DC Shows web server
 *
 * Serves the frontend (public/index.html) and exposes two API routes:
 *
 *   GET /api/venues          → list of available venue class names
 *   GET /api/scrape?venue=X  → scrape venue X and return its shows as JSON
 *
 * Scraping is delegated to scrape_json.py via a child process so that the
 * existing Python scrapers run unchanged. Results are cached in memory for
 * CACHE_TTL_MS to avoid hammering venue sites on every page interaction.
 */

'use strict';

const express  = require('express');
const { spawn } = require('child_process');
const path     = require('path');

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const PORT = process.env.PORT || 3000;

// Path to the Python interpreter inside the project's virtual environment.
// Using the venv interpreter ensures beautifulsoup4 / requests are available
// without touching the system Python.  Adjust if your venv lives elsewhere.
const PYTHON = path.join(__dirname, '.venv', 'bin', 'python3');

// How long to hold a scrape result in memory before expiring (ms).
// Keep this >= the per-venue Python cooldown (currently 10 s) so we never
// spawn overlapping scrapes for the same venue.
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

// All supported venue class names.  Must match keys in scrape_json.py VENUE_MAP.
// The order here controls the order the buttons appear in the UI.
const VENUE_NAMES = [
  'NineThirty',
  'Atlantis',
  'DC9',
  'Songbyrd',
  'PieShop',
  'UnionStage',
  'JamminJava',
  'CapitalTurnaround',
  'TheHoward',
  'MiracleTheatre',
  'NatsPark',
  'PearlStreet',
];

// ---------------------------------------------------------------------------
// In-memory cache
// ---------------------------------------------------------------------------

/**
 * Cache entry shape:
 *   { data: Show[], timestamp: number }
 *
 * Keyed by venue name string.
 */
const cache = {};

/** Return true if a cache entry exists and is still within TTL. */
function isCacheValid(venue) {
  const entry = cache[venue];
  return entry && (Date.now() - entry.timestamp < CACHE_TTL_MS);
}

// ---------------------------------------------------------------------------
// App setup
// ---------------------------------------------------------------------------

const app = express();

// Serve everything in /public as static files (index.html, etc.)
app.use(express.static(path.join(__dirname, 'public')));

// ---------------------------------------------------------------------------
// Routes
// ---------------------------------------------------------------------------

/**
 * GET /api/venues
 * Returns the ordered list of available venue names.
 * The frontend uses this to build the venue-selector buttons.
 */
app.get('/api/venues', (req, res) => {
  res.json(VENUE_NAMES);
});

/**
 * GET /api/scrape?venue=VenueName
 *
 * Scrapes one venue and returns:
 *   { venue: string, shows: Show[], cached: boolean }
 *
 * If a fresh cache entry exists it is returned immediately (cached: true).
 * Otherwise scrape_json.py is spawned as a child process.  The Python script
 * emits one JSON line to stdout; all other output (debug prints, cooldown
 * logs) goes to stderr and is logged here but ignored by the client.
 */
app.get('/api/scrape', (req, res) => {
  const venue = req.query.venue;

  // Validate that the requested venue is in our allow-list.
  if (!venue || !VENUE_NAMES.includes(venue)) {
    return res.status(400).json({ error: 'Invalid or missing venue name.' });
  }

  // Return cached result if still fresh.
  if (isCacheValid(venue)) {
    console.log(`[cache hit] ${venue}`);
    return res.json({ venue, shows: cache[venue].data, cached: true });
  }

  console.log(`[scraping] ${venue}`);

  // Spawn the Python scraper as a child process.
  // cwd is set to __dirname so relative paths inside the Python scripts
  // (cooldowns/, pages/) resolve correctly.
  const python = spawn(
    PYTHON,
    [path.join(__dirname, 'scrape_json.py'), '--venues', venue],
    { cwd: __dirname }
  );

  let stdout = '';
  let stderr = '';

  // Buffer all output; we process it once the process exits.
  python.stdout.on('data', chunk => { stdout += chunk.toString(); });
  python.stderr.on('data', chunk => { stderr += chunk.toString(); });

  python.on('close', code => {
    // Log any debug/error output from the Python side.
    if (stderr.trim()) {
      console.error(`[${venue} stderr]\n${stderr.trim()}`);
    }

    if (code !== 0) {
      console.error(`[${venue}] scrape_json.py exited with code ${code}`);
      return res.status(500).json({ error: 'Scraper process failed.', details: stderr });
    }

    // Parse the JSON object from the last non-empty line of stdout.
    // (Earlier lines may contain stray print() output from venue classes.)
    const lines = stdout.trim().split('\n').filter(l => l.trim());
    const jsonLine = lines[lines.length - 1];

    let result;
    try {
      result = JSON.parse(jsonLine);
    } catch (e) {
      console.error(`[${venue}] failed to parse JSON:`, e.message, '\nstdout was:', stdout);
      return res.status(500).json({ error: 'Failed to parse scraper output.' });
    }

    const shows = result[venue] ?? [];

    // Store in cache.
    cache[venue] = { data: shows, timestamp: Date.now() };

    console.log(`[${venue}] got ${shows.length} shows`);
    res.json({ venue, shows, cached: false });
  });

  // Handle spawn-level errors (e.g. python3 not found).
  python.on('error', err => {
    console.error(`[${venue}] failed to spawn python3:`, err);
    res.status(500).json({ error: 'Could not start scraper.', details: err.message });
  });
});

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------

app.listen(PORT, () => {
  console.log(`DC Shows running at http://localhost:${PORT}`);
});
