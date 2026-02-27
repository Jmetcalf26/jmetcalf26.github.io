# DC Shows Documentation

Welcome to the documentation for the **DC Shows** repository. This project is a full-stack web application designed to aggregate and display concert listings from various venues in the Washington, D.C. area.

## 📚 Documentation Map

*   **[Architecture & Overview](./ARCHITECTURE.md)**: High-level system design, database schema, and the scraping pipeline.
*   **[Frontend Documentation](./FRONTEND.md)**: User interface structure, event handling, and client-side logic.
*   **[API Reference](./API.md)**: Detailed breakdown of backend endpoints and their usage.
*   **[Authentication](./AUTHENTICATION.md)**: How user accounts, sessions, and security are handled.

## 🚀 Quick Start

### Prerequisites
*   Node.js (v18+)
*   Python 3 (with `requests`, `beautifulsoup4` etc. as needed by scrapers)
*   PostgreSQL

### Installation

1.  **Install Node dependencies:**
    ```bash
    npm install
    ```
2.  **Setup Environment:**
    Ensure you have a `.env` file or environment variables set for:
    *   `DB_USER`, `DB_HOST`, `DB_NAME`, `DB_PASSWORD`, `DB_PORT`
    *   `JWT_SECRET`
3.  **Run the Server:**
    ```bash
    npm start
    ```
    The server will initialize the database tables and start the background scraper.

## 💡 Core Features

*   **Aggregated Listings:** unified view of shows from 10+ DC venues.
*   **Search & Filter:** Filter by venue, date range, or search by artist name.
*   **User Accounts:** Register and login to track shows.
*   **Social Features:** Mark shows as "Interested" or "Going" and see friend activity.
