/**
 * server.js — DC Shows web server with PostgreSQL persistence
 */

'use strict';

const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const { Pool } = require('pg');

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const PORT = process.env.PORT || 3000;
const PYTHON = path.join(__dirname, '.venvs/CONCERT', 'bin', 'python3');

// Database configuration from environment
const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT,
});

const VENUE_NAMES = [
  'NineThirty',
  'Atlantis',
  'DC9',
  'Songbyrd',
  'BlackCat',
  'ThePocket',
  'PieShop',
  'UnionStage',
  'JamminJava',
  'CapitalTurnaround',
  'TheHoward',
  'MiracleTheatre',
  'NatsPark',
  'PearlStreet',
];

// Interval for background scraping (e.g., every 6 hours)
const SCRAPE_INTERVAL_MS = 6 * 60 * 60 * 1000;

// ---------------------------------------------------------------------------
// Database Initialization
// ---------------------------------------------------------------------------

async function initDb() {
  const createTableQuery = `
    CREATE TABLE IF NOT EXISTS shows (
        id SERIAL PRIMARY KEY,
        venue_name TEXT NOT NULL,
        artist TEXT NOT NULL,
        opener TEXT,
        day_of_week VARCHAR(10),
        day INTEGER,
        month VARCHAR(10),
        doors_time VARCHAR(20),
        ticket_link TEXT,
        is_sold_out BOOLEAN DEFAULT FALSE,
        last_scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        show_date DATE,
        CONSTRAINT unique_show UNIQUE (venue_name, artist, day, month)
    );
    CREATE INDEX IF NOT EXISTS idx_venue_name ON shows(venue_name);
    CREATE INDEX IF NOT EXISTS idx_artist ON shows(artist);
    CREATE INDEX IF NOT EXISTS idx_show_date ON shows(show_date);
  `;
  try {
    await pool.query(createTableQuery);
    console.log('Database initialized successfully.');
  } catch (err) {
    console.error('Error initializing database:', err);
  }
}

// ---------------------------------------------------------------------------
// Data Ingestion
// ---------------------------------------------------------------------------

async function saveShowsToDb(venueName, shows) {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    for (const show of shows) {
      const isSoldOut = !show.link || show.link === 'N/A' || show.link === 'SOLD OUT';
      const ticketLink = isSoldOut ? null : String(show.link);
      
      let opener = show.opener;
      if (Array.isArray(opener)) {
        opener = opener.join(', ');
      }

      // Calculate show_date
      let showDate = null;
      if (show.day && show.month) {
        const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        let monthIdx = monthNames.indexOf(show.month);
        if (monthIdx === -1) {
          // Try full name if abbreviated fails
          const fullMonths = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
          monthIdx = fullMonths.indexOf(show.month);
        }
        
        if (monthIdx !== -1) {
          const now = new Date();
          const currentYear = now.getFullYear();
          const currentMonth = now.getMonth();
          
          let year = currentYear;
          // If the show month is earlier than the current month, it's likely next year
          if (monthIdx < currentMonth - 2) { 
            year = currentYear + 1;
          }
          
          showDate = new Date(year, monthIdx, parseInt(show.day));
        }
      }

      const query = `
        INSERT INTO shows (venue_name, artist, opener, day_of_week, day, month, doors_time, ticket_link, is_sold_out, last_scraped_at, show_date)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, CURRENT_TIMESTAMP, $10)
        ON CONFLICT (venue_name, artist, day, month) 
        DO UPDATE SET 
            opener = EXCLUDED.opener,
            day_of_week = EXCLUDED.day_of_week,
            doors_time = EXCLUDED.doors_time,
            ticket_link = EXCLUDED.ticket_link,
            is_sold_out = EXCLUDED.is_sold_out,
            last_scraped_at = CURRENT_TIMESTAMP,
            show_date = EXCLUDED.show_date;
      `;
      const values = [
        venueName,
        show.artist,
        opener || null,
        show.dayOfWeek || null,
        parseInt(show.day) || null,
        show.month || null,
        show.doors || null,
        ticketLink,
        isSoldOut,
        showDate
      ];
      await client.query(query, values);
    }
    await client.query('COMMIT');
  } catch (err) {
    await client.query('ROLLBACK');
    console.error(`Error saving shows for ${venueName}:`, err);
  } finally {
    client.release();
  }
}

// ---------------------------------------------------------------------------
// Scraping Logic
// ---------------------------------------------------------------------------

function scrapeVenue(venue) {
  return new Promise((resolve, reject) => {
    console.log(`[scraping] ${venue}`);
    const python = spawn(
      PYTHON,
      [path.join(__dirname, 'scrape_json.py'), '--venues', venue],
      { cwd: __dirname }
    );

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', chunk => { stdout += chunk.toString(); });
    python.stderr.on('data', chunk => { stderr += chunk.toString(); });

    python.on('close', async (code) => {
      if (stderr.trim()) {
        console.error(`[${venue} stderr]\n${stderr.trim()}`);
      }

      if (code !== 0) {
        return reject(new Error(`Scraper exited with code ${code}`));
      }

      const lines = stdout.trim().split('\n').filter(l => l.trim());
      const jsonLine = lines[lines.length - 1];

      try {
        const result = JSON.parse(jsonLine);
        const shows = result[venue] ?? [];
        await saveShowsToDb(venue, shows);
        console.log(`[${venue}] saved ${shows.length} shows to DB`);
        resolve(shows);
      } catch (e) {
        reject(new Error(`Failed to parse JSON: ${e.message}`));
      }
    });

    python.on('error', reject);
  });
}

async function runBackgroundScrapers() {
  console.log('Starting background scrape of all venues...');
  for (const venue of VENUE_NAMES) {
    try {
      await scrapeVenue(venue);
    } catch (err) {
      console.error(`Background scrape failed for ${venue}:`, err.message);
    }
  }
  console.log('Background scrape complete.');
}

// ---------------------------------------------------------------------------
// App setup
// ---------------------------------------------------------------------------

const app = express();
app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/venues', (req, res) => {
  res.json(VENUE_NAMES);
});

app.get('/api/date-range', async (req, res) => {
  try {
    const result = await pool.query('SELECT MIN(show_date) as min, MAX(show_date) as max FROM shows WHERE show_date >= CURRENT_DATE');
    res.json(result.rows[0]);
  } catch (err) {
    console.error('Date range error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/scrape', async (req, res) => {
  const venueParam = req.query.venue;
  const searchQuery = req.query.search;
  const startDate = req.query.startDate;
  const endDate = req.query.endDate;

  let venuesToQuery = [];
  if (venueParam) {
    // Handle both comma-separated and multiple query parameters
    venuesToQuery = Array.isArray(venueParam) ? venueParam : venueParam.split(',');
    venuesToQuery = venuesToQuery.filter(v => VENUE_NAMES.includes(v));
  } else if (!searchQuery && !startDate && !endDate) {
    return res.status(400).json({ error: 'Missing venue, search, or date query.' });
  }

  try {
    let query = 'SELECT artist, opener, day_of_week as "dayOfWeek", day, month, doors_time as doors, ticket_link as link, is_sold_out as "isSoldOut", venue_name as venue FROM shows WHERE (show_date >= CURRENT_DATE OR show_date IS NULL)';
    const params = [];

    if (venuesToQuery.length > 0) {
      const placeholders = venuesToQuery.map((_, i) => `$${params.length + i + 1}`).join(',');
      query += ` AND venue_name IN (${placeholders})`;
      params.push(...venuesToQuery);
    }

    if (searchQuery) {
      query += ` AND (artist ILIKE $${params.length + 1} OR opener ILIKE $${params.length + 1})`;
      params.push(`%${searchQuery}%`);
    }

    if (startDate) {
      query += ` AND show_date >= $${params.length + 1}`;
      params.push(startDate);
    }

    if (endDate) {
      query += ` AND show_date <= $${params.length + 1}`;
      params.push(endDate);
    }

    query += ' ORDER BY show_date ASC, last_scraped_at DESC';

    const result = await pool.query(query, params);

    // If a venue was specifically requested but has no data, we could trigger a scrape
    // but for multi-venue/search, we'll just return what we have in the DB.
    
    // Map DB rows back to the format the frontend expects
    const shows = result.rows.map(row => ({
      ...row,
      link: row.isSoldOut ? 'SOLD OUT' : row.link
    }));
    
    return res.json({ shows, cached: true });
  } catch (err) {
    console.error('Route error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------

async function start() {
  await initDb();
  
  // Start background scraper
  setInterval(runBackgroundScrapers, SCRAPE_INTERVAL_MS);
  
  // Initial run (don't wait for it)
  runBackgroundScrapers().catch(console.error);

  app.listen(PORT, () => {
    console.log(`DC Shows running at http://localhost:${PORT}`);
  });
}

start();
