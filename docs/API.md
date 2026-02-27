# API Reference

The backend is built with **Express.js**. All API routes are prefixed with `/api`.

## 🔍 Public / Data Endpoints

### `GET /api/scrape`
Despite the name, this is the primary **search/read** endpoint. It queries the database for cached show data. It does *not* trigger a live scrape.

*   **Query Parameters:**
    *   `venue` (optional): Comma-separated list of venue names (e.g., `DC9,TheHoward`).
    *   `search` (optional): Search string for artist or opener names.
    *   `startDate` (optional): Filter shows after this date (ISO format `YYYY-MM-DD`).
    *   `endDate` (optional): Filter shows before this date.
*   **Response:**
    ```json
    {
      "shows": [
        {
          "id": 123,
          "artist": "Band Name",
          "venue": "DC9",
          "day": 21,
          "month": "Feb",
          "link": "http://ticket.url",
          "isSoldOut": false,
          "userStatus": "interested" // Only if logged in
        }
      ],
      "cached": true
    }
    ```

### `GET /api/venues`
Returns a list of all supported venue identifiers.
*   **Response:** `["NineThirty", "Atlantis", "DC9", ...]`

### `GET /api/date-range`
Returns the minimum and maximum show dates currently in the database. Used to initialize the frontend date slider.
*   **Response:** `{"min": "2023-10-01", "max": "2024-12-31"}`

---

## 🔐 Authentication Endpoints

### `POST /api/auth/register`
Creates a new user account.
*   **Body:** `{"username": "user", "password": "pw", "email": "me@test.com"}`
*   **Response:** `201 Created` or `400 Error`.

### `POST /api/auth/login`
Authenticates a user and sets an **HttpOnly** cookie named `token`.
*   **Body:** `{"username": "user", "password": "pw"}`
*   **Response:** User info.

### `POST /api/auth/logout`
Clears the auth cookie.

### `GET /api/auth/me`
Checks the current session.
*   **Response:** `{"id": 1, "username": "user"}` or `null`.

---

## 👤 User & Social Endpoints

### `POST /api/user/shows/:showId`
Updates the authenticated user's status for a specific show.
*   **Headers:** `Cookie: token=...`
*   **Body:** `{"status": "interested"}` or `{"status": "going"}` or `{"status": null}` (to remove).

### `GET /api/friends/activity`
Returns a list of recent actions taken by accepted friends.
*   **Response:**
    ```json
    [
      {
        "username": "friend_user",
        "artist": "The Band",
        "venue_name": "DC9",
        "status": "going"
      }
    ]
    ```

### `POST /api/friends/request/:friendId`
Sends a friend request to another user.
