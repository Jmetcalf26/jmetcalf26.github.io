# System Architecture

## Overview

The application follows a **Monolithic** architecture with a clear separation between the Node.js web server, the Python scraping subsystem, and the PostgreSQL database.

```mermaid
graph TD
    User[User Browser] <-->|HTTP/JSON| Server[Node.js Express Server]
    Server <-->|SQL| DB[(PostgreSQL)]
    Server -- Spawns Process --> Python[Python Scraper Subsystem]
    Python -- HTTP Requests --> Venues[External Venue Websites]
    Python -- JSON Stdout --> Server
```

## 🗄️ Database Schema

The application uses **PostgreSQL** for persistence. The schema is initialized automatically in `server.js` on startup.

```mermaid
erDiagram
    USERS ||--o{ USER_SHOWS : tracks
    USERS ||--o{ USER_ARTISTS : favorites
    USERS ||--o{ FRIENDSHIPS : requests
    SHOWS ||--o{ USER_SHOWS : "is tracked by"

    USERS {
        int id PK
        string username
        string password_hash
        string email
        timestamp created_at
    }

    SHOWS {
        int id PK
        string venue_name
        string artist
        string opener
        date show_date
        string ticket_link
        boolean is_sold_out
        timestamp last_scraped_at
    }

    USER_SHOWS {
        int user_id FK
        int show_id FK
        enum status "interested | going"
    }

    FRIENDSHIPS {
        int user_id1 FK
        int user_id2 FK
        enum status "pending | accepted"
    }
```

## 🕷️ Scraping Pipeline

The scraping system is a hybrid Node.js/Python implementation.

1.  **Trigger:** The `server.js` triggers a scrape operation on startup and then every **6 hours**.
2.  **Execution:** Node.js spawns a child process executing `scraping/scrape_json.py`.
3.  **Collection:** The Python script imports venue-specific classes (e.g., `NineThirty.py`, `DC9.py`), fetches their HTML, and parses the show data.
4.  **Output:** The Python script outputs a single JSON object to `stdout`.
5.  **Ingestion:** Node.js captures the `stdout`, parses the JSON, and performs an **UPSERT** (Insert or Update) into the `shows` table based on a composite unique key (`venue_name`, `artist`, `day`, `month`).

```mermaid
sequenceDiagram
    participant Scheduler as Node.js Scheduler
    participant Scraper as Python Script (scrape_json.py)
    participant Venue as Venue Class (e.g., DC9.py)
    participant Web as Venue Website
    participant DB as PostgreSQL

    Scheduler->>Scraper: Spawn Process (--venues ALL)
    loop For each venue
        Scraper->>Venue: Instantiate & getData()
        Venue->>Web: HTTP GET
        Web-->>Venue: HTML Response
        Venue->>Venue: Parse HTML
        Venue-->>Scraper: Return List of Dicts
    end
    Scraper-->>Scheduler: Print JSON to Stdout
    Scheduler->>DB: UPSERT shows (On Conflict Update)
```
