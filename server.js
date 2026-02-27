/**
 * server.js — DC Shows web server with PostgreSQL persistence
 */

'use strict';

const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const { Pool } = require('pg');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const cookieParser = require('cookie-parser');
const morgan = require('morgan');
const rfs = require('rotating-file-stream');
const fs = require('fs');
const rateLimit = require('express-rate-limit');
const crypto = require('crypto');

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const PORT = process.env.PORT || 3000;
const PYTHON = path.join(__dirname, '.venvs/CONCERT', 'bin', 'python3');
const JWT_SECRET = process.env.JWT_SECRET;

// Ensure log directory exists
const logDirectory = path.join(__dirname, 'logs');
fs.existsSync(logDirectory) || fs.mkdirSync(logDirectory);

// Create a rotating write stream
const accessLogStream = rfs.createStream('access.log', {
  interval: '1d', // rotate daily
  path: logDirectory
});

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

    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT UNIQUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS user_shows (
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        show_id INTEGER REFERENCES shows(id) ON DELETE CASCADE,
        status TEXT CHECK (status IN ('interested', 'going')),
        PRIMARY KEY (user_id, show_id)
    );

    CREATE TABLE IF NOT EXISTS user_artists (
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        artist_name TEXT NOT NULL,
        PRIMARY KEY (user_id, artist_name)
    );

    CREATE TABLE IF NOT EXISTS friendships (
        user_id1 INTEGER REFERENCES users(id) ON DELETE CASCADE,
        user_id2 INTEGER REFERENCES users(id) ON DELETE CASCADE,
        status TEXT CHECK (status IN ('pending', 'accepted')),
        PRIMARY KEY (user_id1, user_id2),
        CHECK (user_id1 < user_id2)
    );
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
      [path.join(__dirname, 'scraping', 'scrape_json.py'), '--venues', venue],
      { cwd: path.join(__dirname, 'scraping') }
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
app.use(express.json());
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

// Rate Limiter for Authentication
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10, // Limit each IP to 10 requests per windowMs
  message: { error: 'Too many authentication attempts, please try again in 15 minutes.' },
  standardHeaders: true,
  legacyHeaders: false,
});

// Middleware to verify CSRF token (Double Submit Cookie)
function checkCsrf(req, res, next) {
  if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) return next();
  
  // Exempt login and register from CSRF check as they are entry points
  if (req.path === '/api/auth/login' || req.path === '/api/auth/register') {
    return next();
  }

  const cookieToken = req.cookies.csrfToken;
  const headerToken = req.headers['x-csrf-token'];
  if (!cookieToken || cookieToken !== headerToken) {
    return res.status(403).json({ error: 'CSRF validation failed' });
  }
  next();
}

// Function to set CSRF cookie
function setCsrfCookie(res) {
  const token = crypto.randomBytes(32).toString('hex');
  res.cookie('csrfToken', token, { 
    httpOnly: false, // Must be readable by frontend JS
    secure: process.env.NODE_ENV === 'production', 
    sameSite: 'lax' 
  });
  return token;
}

// Apply CSRF protection to state-changing routes
app.use('/api', checkCsrf);

// --- Public Data Routes ---

app.get('/api/venues', (req, res) => {
  setCsrfCookie(res);
  res.json(VENUE_NAMES);
});

app.get('/api/date-range', async (req, res) => {
  try {
    setCsrfCookie(res);
    const result = await pool.query('SELECT MIN(show_date) as min, MAX(show_date) as max FROM shows WHERE show_date >= CURRENT_DATE');
    res.json(result.rows[0]);
  } catch (err) {
    console.error('Date range error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Setup log for all GET requests to a logfile rotated by the day
app.use(morgan('combined', {
  stream: accessLogStream,
  skip: (req, res) => req.method !== 'GET'
}));

// Middleware to authenticate JWT
function authenticateToken(req, res, next) {
  const token = req.cookies.token;
  if (!token) return res.status(401).json({ error: 'Unauthorized' });

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: 'Forbidden' });
    req.user = user;
    next();
  });
}

// --- Auth Routes ---

app.post('/api/auth/register', authLimiter, async (req, res) => {
  const { username, password, email } = req.body;
  if (!username || !password) return res.status(400).json({ error: 'Username and password required' });

  try {
    const passwordHash = await bcrypt.hash(password, 10);
    const result = await pool.query(
      'INSERT INTO users (username, password_hash, email) VALUES ($1, $2, $3) RETURNING id, username',
      [username, passwordHash, email]
    );
    setCsrfCookie(res);
    res.status(201).json(result.rows[0]);
  } catch (err) {
    if (err.code === '23505') return res.status(400).json({ error: 'Username or email already exists' });
    console.error(err);
    res.status(500).json({ error: 'Registration failed' });
  }
});

app.post('/api/auth/login', authLimiter, async (req, res) => {
  const { username, password } = req.body;
  try {
    const result = await pool.query('SELECT * FROM users WHERE username = $1', [username]);
    const user = result.rows[0];
    if (!user || !(await bcrypt.compare(password, user.password_hash))) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = jwt.sign({ id: user.id, username: user.username }, JWT_SECRET, { expiresIn: '1h' });
    res.cookie('token', token, { 
      httpOnly: true, 
      maxAge: 3600000, 
      secure: process.env.NODE_ENV === 'production', 
      sameSite: 'lax' 
    });
    setCsrfCookie(res);
    res.json({ id: user.id, username: user.username });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Login failed' });
  }
});

app.post('/api/auth/logout', (req, res) => {
  res.clearCookie('token');
  res.clearCookie('csrfToken');
  res.json({ message: 'Logged out' });
});

app.get('/api/auth/me', (req, res) => {
  const token = req.cookies.token;
  if (!token) return res.json(null);
  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.json(null);
    setCsrfCookie(res);
    res.json(user);
  });
});

// --- Account / Social Routes ---

// Update show status (interested/going)
app.post('/api/user/shows/:showId', authenticateToken, async (req, res) => {
  const { status } = req.body; // 'interested', 'going', or null to remove
  const { showId } = req.params;
  const userId = req.user.id;

  try {
    if (!status) {
      await pool.query('DELETE FROM user_shows WHERE user_id = $1 AND show_id = $2', [userId, showId]);
    } else {
      await pool.query(
        'INSERT INTO user_shows (user_id, show_id, status) VALUES ($1, $2, $3) ON CONFLICT (user_id, show_id) DO UPDATE SET status = EXCLUDED.status',
        [userId, showId, status]
      );
    }
    res.json({ success: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to update show status' });
  }
});

// Add favorite artist
app.post('/api/user/artists', authenticateToken, async (req, res) => {
  const { artistName } = req.body;
  const userId = req.user.id;
  try {
    await pool.query('INSERT INTO user_artists (user_id, artist_name) VALUES ($1, $2) ON CONFLICT DO NOTHING', [userId, artistName]);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: 'Failed to add artist' });
  }
});

// Friend requests / management
app.post('/api/friends/request/:friendId', authenticateToken, async (req, res) => {
  const userId = req.user.id;
  const friendId = parseInt(req.params.friendId);
  const [id1, id2] = [userId, friendId].sort((a, b) => a - b);
  
  try {
    await pool.query(
      'INSERT INTO friendships (user_id1, user_id2, status) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING',
      [id1, id2, 'pending']
    );
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: 'Failed to send friend request' });
  }
});

// Get friend activity
app.get('/api/friends/activity', authenticateToken, async (req, res) => {
  const userId = req.user.id;
  try {
    const result = await pool.query(`
      SELECT u.username, s.artist, s.venue_name, s.show_date, us.status
      FROM friendships f
      JOIN users u ON (f.user_id1 = u.id OR f.user_id2 = u.id) AND u.id != $1
      JOIN user_shows us ON us.user_id = u.id
      JOIN shows s ON us.show_id = s.id
      WHERE (f.user_id1 = $1 OR f.user_id2 = $1) AND f.status = 'accepted'
      AND s.show_date >= CURRENT_DATE
      ORDER BY s.show_date ASC
    `, [userId]);
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to fetch friend activity' });
  }
});

app.get('/api/scrape', async (req, res) => {
  const venueParam = req.query.venue;
  const searchQuery = req.query.search;
  const startDate = req.query.startDate;
  const endDate = req.query.endDate;

  // Check if user is logged in
  let userId = null;
  const token = req.cookies.token;
  if (token) {
    try {
      const decoded = jwt.verify(token, JWT_SECRET);
      userId = decoded.id;
    } catch (e) {}
  }

  let venuesToQuery = [];
  if (venueParam) {
    venuesToQuery = Array.isArray(venueParam) ? venueParam : venueParam.split(',');
    venuesToQuery = venuesToQuery.filter(v => VENUE_NAMES.includes(v));
  } else if (!searchQuery && !startDate && !endDate) {
    return res.status(400).json({ error: 'Missing venue, search, or date query.' });
  }

  try {
    let query = `
      SELECT s.id, s.artist, s.opener, s.day_of_week as "dayOfWeek", s.day, s.month, 
             s.doors_time as doors, s.ticket_link as link, s.is_sold_out as "isSoldOut", 
             s.venue_name as venue, us.status as "userStatus"
      FROM shows s
      LEFT JOIN user_shows us ON s.id = us.show_id AND us.user_id = $1
      WHERE (s.show_date >= CURRENT_DATE OR s.show_date IS NULL)
    `;
    const params = [userId];

    if (venuesToQuery.length > 0) {
      const placeholders = venuesToQuery.map((_, i) => `$${params.length + i + 1}`).join(',');
      query += ` AND s.venue_name IN (${placeholders})`;
      params.push(...venuesToQuery);
    }

    if (searchQuery) {
      query += ` AND (s.artist ILIKE $${params.length + 1} OR s.opener ILIKE $${params.length + 1})`;
      params.push(`%${searchQuery}%`);
    }

    if (startDate) {
      query += ` AND s.show_date >= $${params.length + 1}`;
      params.push(startDate);
    }

    if (endDate) {
      query += ` AND s.show_date <= $${params.length + 1}`;
      params.push(endDate);
    }

    query += ' ORDER BY s.show_date ASC, s.last_scraped_at DESC';

    const result = await pool.query(query, params);

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
