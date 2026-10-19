# Secure User Authentication — AVIP 2026 Task 1

Flask + SQLite full-stack registration and login application with hashed passwords, signed sessions, CSRF-protected forms, validation and protected dashboard/profile API.

## Run locally
```bash
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000/register to create a test account.

## API and pages
| Method | Route | Purpose |
|---|---|---|
| GET/POST | `/register` | Registration page and form |
| GET/POST | `/login` | Login page and form |
| GET | `/dashboard` | Authenticated dashboard |
| GET | `/api/profile` | Authenticated JSON profile |
| POST | `/logout` | Log out (CSRF token required) |
| GET | `/health` | Health check |

Example authenticated request: first log in via the browser, then visit `/api/profile` using the same session. Example response: `{"message":"Authenticated successfully","username":"demo"}`. Unauthenticated API requests return HTTP 401.

## Deploy
On Render, create a Python Web Service connected to this repository. Build: `pip install -r requirements.txt`. Start: `gunicorn app:app`. Set `SECRET_KEY` to a securely generated random value and `COOKIE_SECURE=true`. SQLite stored on ephemeral disks may reset between deployments/restarts; use persistent database storage for long-term production use. Do not use real passwords in a demo.

## Internship deliverables
Public repository, API list, authenticated request example, and screenshot or demo.
