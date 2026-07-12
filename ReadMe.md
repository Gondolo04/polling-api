# Polling Application API

*Progettazione e Produzione Multimediale — Back-end (2026) — Andrea Panico*

---

## Project type

**REST API** — Polling API

---

## Framework

- Python 3.13
- Django 6.x
- Django REST Framework
- djangorestframework-simplejwt (JWT authentication)
- django-cors-headers

---

## Description

A REST API for a polling platform. Authenticated users can create polls with multiple choices, vote on open polls, and manage their own content. Moderators and admins can manage any poll regardless of ownership. Admins have the additional ability to ban and unban user accounts. Anonymous users can browse polls and view results without logging in.

---

## Features by role

### Anonymous (not logged in)
- Browse the full list of polls
- View a single poll and its choices
- View results for any poll (including closed ones)

### Authenticated user (role: `user`)
- All anonymous features
- Register a new account
- Log in and receive a JWT access token
- Create a new poll with at least 2 choices
- Edit or delete own polls
- Close own polls
- Cast one vote per poll (open polls only)

### Moderator (role: `moderator`)
- All authenticated user features
- Edit, delete, or close any poll regardless of ownership

### Admin (role: `admin`)
- All moderator features
- View the full list of users with their roles and statuses
- Ban any non-admin user (sets `is_active=False`, immediately invalidates existing tokens)
- Unban previously banned users

### Django superuser (`superuser_demo`)
- Access to the Django `/admin/` panel for direct database inspection

---

## Deployment

**Live API:** https://polling-api-npt4.onrender.com

**Test client:** https://gondolo04.github.io/polling-api/

> **Note:** the API is hosted on Render's free tier, which spins down after 15 minutes of inactivity. The first request after a period of inactivity may take 30–60 seconds to respond. Subsequent requests are fast.

---

## Local installation (optional)

### 1. Clone the repository
```bash
git clone https://github.com/gondolo04/polling-api.git
cd polling-api
```

### 2. Create and activate a virtual environment

With conda:
```bash
conda create -n polling-api python=3.13
conda activate polling-api
```

Or with venv:
```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply migrations
```bash
python manage.py migrate
```

### 5. Populate the database with demo data
```bash
python popola_db.py
```

This creates all demo accounts, 5 sample polls with choices, and 12 pre-existing votes spread across polls. The script clears all existing data first, so it can safely be run multiple times to reset the database to a clean demo state.

### 6. Start the development server
```bash
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000`.

---

## SQLite database

The repository includes `db.sqlite3`, pre-populated with demo accounts, polls, choices, and votes. The application can be explored immediately without running `popola_db.py`, though the script can be used to reset the database to a clean demo state at any time.

---

## Demo accounts

| Username | Password | Role | Notes |
| :--- | :--- | :--- | :--- |
| `superuser_demo` | `superuser12345` | Django superuser | `/admin/` panel access only |
| `admin_demo` | `admin12345` | Admin | Can ban/unban users via API |
| `mod_demo` | `mod12345` | Moderator | Can manage any poll |
| `user_demo` | `user12345` | User | Standard account |
| `alice_demo` | `alice12345` | User | Additional standard account |

---

## Endpoint documentation

### Authentication and registration

| Method | URL | Auth | Role | Request body | Response | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| POST | `/api/auth/register/` | No | — | `{"username": "...", "email": "...", "password": "..."}` | User object | Register a new account (role defaults to `user`) |
| POST | `/api/auth/token/` | No | — | `{"username": "...", "password": "..."}` | `{"access": "...", "refresh": "..."}` | Log in and receive JWT tokens |
| POST | `/api/auth/token/refresh/` | No | — | `{"refresh": "..."}` | `{"access": "..."}` | Obtain a new access token using the refresh token |

### Polls

| Method | URL | Auth | Role | Request body | Response | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| GET | `/api/polls/` | No | Anonymous | — | List of polls | List all polls ordered by newest first |
| GET | `/api/polls/{id}/` | No | Anonymous | — | Poll object with choices | Retrieve a single poll |
| POST | `/api/polls/` | Yes | User | `{"title": "...", "description": "...", "choices": ["...", "..."]}` | Created poll | Create a new poll (minimum 2 choices required) |
| PATCH | `/api/polls/{id}/` | Yes | Owner / Mod / Admin | `{"title": "...", "description": "..."}` | Updated poll | Update a poll |
| DELETE | `/api/polls/{id}/` | Yes | Owner / Mod / Admin | — | 204 No Content | Delete a poll |
| POST | `/api/polls/{id}/vote/` | Yes | User | `{"choice_id": 1}` | `{"detail": "Vote recorded."}` | Cast a vote (one per user per poll, open polls only) |
| GET | `/api/polls/{id}/results/` | No | Anonymous | — | Poll title + choice vote counts | View vote results |
| PATCH | `/api/polls/{id}/close/` | Yes | Owner / Mod / Admin | — | `{"detail": "Poll closed."}` | Close a poll to prevent further voting |

### User management (admin only)

| Method | URL | Auth | Role | Request body | Response | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| GET | `/api/auth/users/` | Yes | Admin | — | List of users with id, username, role, is_active | List all users |
| PATCH | `/api/auth/users/{id}/ban/` | Yes | Admin | — | `{"detail": "username has been banned."}` | Ban a user — immediately invalidates their tokens |
| PATCH | `/api/auth/users/{id}/unban/` | Yes | Admin | — | `{"detail": "username has been unbanned."}` | Restore access to a banned user |

### Response examples

**Poll list** `GET /api/polls/`
```json
[
  {
    "id": 1,
    "title": "Favorite season?",
    "description": "Which season do you prefer?",
    "created_by": "user_demo",
    "created_at": "2026-06-19T12:00:00Z",
    "is_open": true,
    "choices": [
      {"id": 1, "text": "Spring", "vote_count": 2},
      {"id": 2, "text": "Summer", "vote_count": 1},
      {"id": 3, "text": "Autumn", "vote_count": 1},
      {"id": 4, "text": "Winter", "vote_count": 0}
    ]
  }
]
```

**Validation error — too few choices** `POST /api/polls/`
```json
{
  "choices": ["A poll needs at least 2 choices."]
}
```

**Validation error — poll closed** `POST /api/polls/3/vote/`
```json
{
  "choice_id": ["This poll is closed."]
}
```

**Permission denied** `DELETE /api/polls/1/` (as non-owner, non-moderator)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

## Testing workflow — HTML client

A standalone HTML test client is available at:

**https://gondolo04.github.io/polling-api/**

Open it in any browser — no installation or local server required. The client is pre-configured to point at the live deployed API at `https://polling-api-npt4.onrender.com`. To test against a local instance instead, update the "API base" field at the top of the page to `http://127.0.0.1:8000`.

---

### Workflow 1 — Anonymous access

On page load, the poll list fetches automatically with no login required. All 5 demo polls are visible. Click **View results** on any poll to see vote counts and proportional bars without logging in.

---

### Workflow 2 — Register and log in

1. In the **Register** panel, fill in a new username, email, and password (minimum 8 characters), then click **Create account**. A green confirmation appears and the fields clear automatically.
2. In the **Log in** panel, enter the same credentials and click **Log in**. The session bar at the top updates to show the logged-in username.

---

### Workflow 3 — Create a poll and vote

1. Fill in the **Create poll** panel with a title, optional description, and at least 2 choices. Click **Create poll**. The new poll appears at the top of the list and the form resets automatically.
2. Scroll to **Best Italian city to visit?** (0 votes by default). Click any choice pill to cast a vote. An alert confirms "Vote recorded."
3. Click **View results** on the same poll to see the updated count.
4. Try voting again on the same poll — the alert returns "You already voted on this poll." (400 error).

---

### Workflow 4 — Test a closed poll

1. Scroll to **Preferred work style?** — it shows a red `(closed)` tag.
2. Click any of its choices. The alert returns "This poll is closed." (400 error from server-side validation).

---

### Workflow 5 — Close a poll (owner permission)

1. Still logged in as the user who created a poll, click **Close poll** on that poll.
2. After confirmation the poll refreshes with a `(closed)` tag.
3. Log out and log in as a different standard user. Attempt to close a poll you did not create — the alert returns a 403 permission denied error.

---

### Workflow 6 — Moderator managing any poll

1. Log out, then log in as `mod_demo / mod12345`.
2. Click **Close poll** on **Favorite season?** (created by `user_demo`, not `mod_demo`).
3. The poll closes successfully — moderator permission is enforced correctly.

---

### Workflow 7 — Admin banning a user

1. Log out, then log in as `admin_demo / admin12345`.
2. Scroll to the **User management** panel at the bottom and click **Load users**.
3. A table appears showing all users, their roles, and active/banned status.
4. Click **Ban** next to `user_demo`. A confirmation message appears and the table refreshes — `user_demo` now shows as banned.
5. Log out, then attempt to log in as `user_demo / user12345`. The login returns "No active account found with the given credentials." — banned users cannot authenticate.
6. Log back in as `admin_demo`, reload users, and click **Unban** next to `user_demo` to restore access.
7. Note that admin accounts show "protected" in the Action column and cannot be banned.

---

## Technical notes

### Authentication

All protected endpoints require a JWT access token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

Tokens are obtained via `POST /api/auth/token/` and stored in memory by the HTML client for the duration of the browser session. Banning a user immediately invalidates their existing tokens — `JWTAuthentication` re-checks `is_active` on every request, not only at login.

### Permissions

| Check | Enforced in |
| :--- | :--- |
| Anonymous read access | `IsAuthenticatedOrReadOnly` (global default) |
| Write access requires login | `has_permission` in `IsOwnerOrPrivilegedOrReadOnly` |
| Owner / moderator / admin object actions | `has_object_permission` in `IsOwnerOrPrivilegedOrReadOnly` |
| Admin-only user management | `IsAdminRole` permission class |

### Validation

- Poll creation requires at least 2 choices — enforced in `PollCreateSerializer.validate_choices`
- Voting on a closed poll returns a 400 error — enforced in `VoteSerializer.validate_choice_id`
- One vote per user per poll — enforced by `unique_together = ("poll", "user")` on the `Vote` model
- Password minimum length of 8 characters — enforced in `RegisterSerializer`
- Admins cannot ban other admins — enforced in `BanUserView`

### Project structure

```
polling-api/
├── accounts/
│   ├── models.py         — custom User model with role field
│   ├── serializers.py    — RegisterSerializer, UserListSerializer
│   ├── permissions.py    — IsAdminRole
│   ├── views.py          — RegisterView, UserListView, BanUserView, UnbanUserView
│   ├── admin.py          — CustomUserAdmin with role dropdown
│   └── urls.py
├── polls/
│   ├── models.py         — Poll, Choice, Vote
│   ├── serializers.py    — PollSerializer, PollCreateSerializer, VoteSerializer, ChoiceSerializer
│   ├── permissions.py    — IsOwnerOrPrivilegedOrReadOnly
│   ├── views.py          — PollViewSet
│   └── urls.py
├── config/
│   ├── settings.py
│   └── urls.py
├── client/
│   └── poll_api_client.html
├── db.sqlite3
├── popola_db.py
├── manage.py
├── requirements.txt
└── README.md
```

---
