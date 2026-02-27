# Frontend Documentation

The frontend is built with **Vanilla HTML, CSS, and JavaScript**. It avoids heavy frameworks in favor of native DOM manipulation and the Fetch API.

## 📂 File Structure

*   `public/index.html`: The main dashboard. Handles search, filtering, and displaying the grid of shows.
*   `public/auth.html`: A dual-purpose Login/Register page.
*   `public/profile.html`: The user's personal dashboard (My Shows, Friends).

## 🖥️ Main Dashboard Flow (`index.html`)

The main page operates as a single-page application (SPA) regarding data fetching, though it is served as a static HTML file.

```mermaid
graph TD
    Init[Page Load] --> FetchConfig[Fetch Venues & Date Range]
    Init --> CheckAuth[Check Auth (/api/auth/me)]
    FetchConfig --> BuildUI[Build Venue Selector & Date Slider]
    BuildUI --> LoadShows[Load Shows (Default: All or First Venue)]
    
    UserAction{User Interaction}
    UserAction -- Search Input --> Debounce --> LoadShows
    UserAction -- Click Venue --> ToggleSet --> LoadShows
    UserAction -- Adjust Date --> UpdateRange --> LoadShows
    
    LoadShows --> FetchScrape[GET /api/scrape?...]
    FetchScrape --> Render[Render Grid of Cards]
```

### Key Components

1.  **Venue Selector:** A dynamic list of "pill" buttons generated from the `/api/venues` response. It manages a `Set()` of selected venues.
2.  **Date Slider:** A dual-handle range slider. It maps the min/max dates from the DB to a linear range input.
3.  **Show Grid:** A CSS Grid layout.
    *   **Skeleton Loading:** While fetching, it renders simplified "shimmer" cards.
    *   **Show Card:** Displays Artist, Date, Doors, Ticket Link, and (if logged in) Status Buttons.

## 👤 Profile Flow (`profile.html`)

The profile page is protected (redirects to `/auth.html` if not logged in).

1.  **Data Loading:** It currently re-fetches **all** shows via `/api/scrape` and performs client-side filtering to find shows where `userStatus` is 'interested' or 'going'.
    *   *Note: This is an optimization candidate for future backend updates (e.g., a dedicated `/api/user/my-shows` endpoint).*
2.  **Friend Activity:** Fetches distinct data from `/api/friends/activity` to show a feed of what friends are attending.

## 🎨 Styling

*   **Variables:** CSS Custom Properties (`--bg`, `--accent`, etc.) are used for theming.
*   **Dark Mode:** The default theme is a high-contrast dark mode.
*   **Responsiveness:** The grid uses `repeat(auto-fill, minmax(240px, 1fr))` to automatically adjust column counts for mobile vs desktop.
