# Network Uptime Monitor API

A REST API built with Django and Django REST Framework for tracking websites and servers. Users register, add the sites they want to watch, and the API stores the history of checks so uptime and response times can be reviewed. The project is under active development.

## Features (implemented)

- **User registration and JWT authentication** using `djangorestframework-simplejwt`, with short-lived access tokens and refresh token rotation.
- **Custom user model** (`AbstractUser`) so the account model can be extended later.
- **Monitor management**: authenticated users can create, list, update, and delete their own monitors, each with a name, URL, check interval, and active flag.
- **Per-user data isolation**: every query is scoped to the logged-in user, so one user can never read or modify another user's monitors or results.
- **Validation**
  - Password strength checked with Django's built-in validators.
  - Emails must be unique, compared case-insensitively.
  - A user cannot add the same URL twice, but different users can monitor the same URL. This is enforced both in the serializer (clean 400 error) and by a database constraint.
  - Check interval limited to a sensible range (1 to 1440 minutes).
- **Check history endpoint**: a read-only, paginated list of a monitor's check results, newest first.

## Tech stack

- Python, Django 5
- Django REST Framework
- djangorestframework-simplejwt
- SQLite (development database)

## Data model

| Model | Purpose |
|---|---|
| `User` | Custom user model extending `AbstractUser` |
| `Monitor` | A site or server being watched. Belongs to one user. |
| `CheckResult` | One row per check: status code, response time, up/down result, error message, timestamp. Read-only through the API. |
| `Alert` | Records a state change (site went down or recovered) so users are not notified on every failed check. |

Relationships: one user has many monitors, and one monitor has many check results and alerts.

## Design decisions

- **Owner is set by the server, never by the client.** The `owner` field is read-only and filled from the authenticated user, which prevents creating monitors under someone else's account.
- **404 instead of 403 for other users' resources.** Because the viewset's queryset only contains the current user's monitors, requesting someone else's monitor returns 404, which does not reveal whether it exists.
- **Composite index on `CheckResult`** (`monitor`, `-checked_at`). This table grows quickly, and the index keeps "recent results for one monitor" queries fast.
- **Passwords are hashed** through `create_user`, and the password field is write-only so it never appears in responses.
- **Pagination on the history endpoint**, since a monitor checked every few minutes produces thousands of rows.

## Getting started

```bash
git clone <your-repo-url>
cd <repo-folder>

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install django djangorestframework djangorestframework-simplejwt

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API is then available at `http://127.0.0.1:8000/api/`.

## API endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/register/` | Create an account | No |
| POST | `/api/token/` | Obtain access and refresh tokens | No |
| POST | `/api/token/refresh/` | Get a new access token | No |
| GET, POST | `/api/monitors/` | List your monitors or create one | Yes |
| GET, PUT, PATCH, DELETE | `/api/monitors/<id>/` | Retrieve, update, or delete one monitor | Yes |
| GET | `/api/monitors/<id>/results/` | Paginated check history, newest first | Yes |

Authenticated requests need an `Authorization: Bearer <access_token>` header. Access tokens expire after 15 minutes.

## Roadmap

- [ ] Check logic: request each monitored URL with a timeout, measure response time, and record failures (timeouts, DNS and SSL errors)
- [ ] Management command to run checks for all active monitors
- [ ] Scheduled checks (cron or Celery Beat)
- [ ] Stats endpoint: uptime percentage and average response time over a time window
- [ ] Alert creation on state changes
- [ ] Automated tests with `APITestCase`
- [ ] Rate limiting and a capped page size
- [ ] Interactive API docs with `drf-spectacular`
- [ ] Deployment
- [ ] React dashboard with response-time charts

## Project structure

```
network_monitor/    Django project (settings, root URLs)
api/                App: models, serializers, views, URLs
```
