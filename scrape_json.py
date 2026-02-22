#!/usr/bin/env python3
"""
scrape_json.py — JSON output wrapper for venue scrapers.

Runs one or more venue scrapers and emits a single JSON object to stdout.
Used by server.js to get structured show data.

Usage:
    python3 scrape_json.py --venues NineThirty Atlantis DC9

Output (stdout, last line):
    {"NineThirty": [...shows...], "Atlantis": [...shows...]}

Each show dict has these possible keys (all optional except artist):
    dayOfWeek  string  e.g. "Fri"
    day        string  e.g. "21"
    month      string  e.g. "Feb" or "02" (numeric for Songbyrd)
    doors      string  e.g. "8PM" or "8:00 PM"
    artist     string  headlining act
    opener     string or list  supporting acts (DC9 returns a list)
    link       string or number  ticket URL, "N/A", or ticket price (Songbyrd)
"""

import sys
import json
import argparse

# --- Redirect stdout → stderr during imports and scraping ---
# Venue classes (and Venue.py itself) use print() for debug/cooldown logs.
# We capture those on stderr so they don't corrupt the JSON output line.
_real_stdout = sys.stdout
sys.stdout = sys.stderr

# Import all venue classes.
# Add new venue files here and register them in VENUE_MAP below.
from NineThirty import NineThirty
from Atlantis import Atlantis
from DC9 import DC9
from Songbyrd import Songbyrd
from BlackCat import BlackCat
from ThePocket import ThePocket
from PieShop import PieShop
from UnionStage import UnionStage
from JamminJava import JamminJava
from CapitalTurnaround import CapitalTurnaround
from TheHoward import TheHoward
from MiracleTheatre import MiracleTheatre
from NatsPark import NatsPark
from PearlStreet import PearlStreet

# Map CLI/API name strings to venue classes.
# Keys here must match the names used in server.js VENUE_NAMES.
VENUE_MAP = {
    'NineThirty':       NineThirty,
    'Atlantis':         Atlantis,
    'DC9':              DC9,
    'Songbyrd':         Songbyrd,
    'BlackCat':         BlackCat,
    'ThePocket':        ThePocket,
    'PieShop':          PieShop,
    'UnionStage':       UnionStage,
    'JamminJava':       JamminJava,
    'CapitalTurnaround': CapitalTurnaround,
    'TheHoward':        TheHoward,
    'MiracleTheatre':   MiracleTheatre,
    'NatsPark':         NatsPark,
    'PearlStreet':      PearlStreet,
}


def scrape_venues(venue_names):
    """
    Instantiate and run each requested venue scraper.
    Returns a dict: { venueName: [show, ...] }
    On per-venue failure, logs the error to stderr and returns an empty list.
    """
    results = {}
    for name in venue_names:
        if name not in VENUE_MAP:
            print(f"Unknown venue: {name}", file=sys.stderr)
            continue
        try:
            venue = VENUE_MAP[name]()     # instantiate venue class
            raw = venue.getData()         # fetch (respects cooldown)
            venue.parse(raw)              # populate venue.shows
            results[name] = venue.shows
        except Exception as e:
            print(f"Error scraping {name}: {e}", file=sys.stderr)
            results[name] = []
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Scrape venue data and output a JSON object to stdout.'
    )
    parser.add_argument(
        '--venues', nargs='+',
        default=['NineThirty', 'Atlantis', 'TheHoward'],
        help='One or more venue class names to scrape.'
    )
    args = parser.parse_args()

    data = scrape_venues(args.venues)

    # Restore real stdout and emit JSON as the final (only) line.
    # server.js reads this line directly.
    sys.stdout = _real_stdout
    print(json.dumps(data))
