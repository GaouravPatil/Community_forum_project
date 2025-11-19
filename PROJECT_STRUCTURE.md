Project structure (Community_forum_project)

Top-level files
- `manage.py` : Django management entrypoint.
- `db.sqlite3` : SQLite database (dev).
- `requirements.txt` : Python dependencies.
- `Dockerfile` : project container image (dev/prod hints).
- `README.md` : existing project readme.
- `PROJECT_STRUCTURE.md` : (this file) project layout and quick commands.
- `.gitignore` : ignores pyc, db, media, IDE files, etc.

Top-level folders
- `config/` : Django project configuration and ASGI/WGI files.
  - `settings.py` : main settings (ALLOWED_HOSTS, CHANNEL_LAYERS, LOGIN_URL, MEDIA_ROOT).
  - `asgi.py` / `wsgi.py` : server entrypoints.
  - `urls.py` : root URL config.

- `chat/` : Django app for forum + chat + call features.
  - `models.py` : `Thread`, `Reply`, `Notification`, `VideoCall`, `UserProfile`, etc.
  - `views.py` : HTTP endpoints (login/register/profile/notifications/call lifecycle).
  - `consumers.py` : Django Channels consumers (chat, per-user groups, video signaling).
  - `routing.py`, `urls.py` : app routing for websockets and http endpoints.
  - `forms.py` : Thread / profile forms.
  - `migrations/` : DB migrations.

- `templates/` : project templates (moved to top-level during rebase):
  - `base.html` : site layout, header, incoming call modal, header toast, login modal JS.
  - `login.html`, `register.html`, `profile.html`, `notifications.html`, `video_call.html`, etc.
  - Note: many templates were previously under `chat/templates` and were relocated to top-level `templates/`.

- `static/` : static assets (CSS/JS/images) — used by templates.
- `media/` : user-uploaded files (avatars).
- `tests/` : unit/smoke tests (including `smoke_test.py` used to exercise call flows).

Key places to look for features you mentioned
- Login page: `templates/login.html` and the login view in `chat/views.py` (`user_login` or `login_view` depending on naming).
- Profile handling: `chat/views.py` -> `profile()` and `templates/profile.html`.
- Notifications: `chat/views.py` -> `notifications()` and `templates/notifications.html`.
- Call lifecycle endpoints: `chat/urls.py` -> `call/initiate`, `accept`, `reject`, `end`, and `call_page` view.
- WebSockets and signaling: `chat/consumers.py` and `chat/routing.py`. The JS side is in `templates/base.html` and `templates/video_call.html`.

Quick commands
- Apply migrations:
```
python3 manage.py migrate
```

- Run development server (local):
```
python3 manage.py runserver 127.0.0.1:8000
```

- Run the smoke script (server must be running or executed via manage.py shell):
```
python3 manage.py shell < tests/smoke_test.py
```

- Run Django test suite:
```
python3 manage.py test
```

Notes & recommendations
- Templates live at `templates/` (global) — you can move app-specific templates back under `chat/templates/` if you want clearer app boundaries.
- For WebSocket production use, configure `CHANNEL_LAYERS` to Redis and run an ASGI server (e.g., Daphne or Uvicorn behind Nginx).
- For reliable cross-network WebRTC, set up a TURN server (coturn) and configure it in `video_call.html` or central config.
- Consider removing tracked `__pycache__` and compiled files (done), and keep `.gitignore` up to date.

If you'd like I can:
- Commit & push this file for you.
- Reorganize templates back into `chat/templates/` to restore app structure.
- Add a short `README.md` section with the login/profile/call quickstart.

Tell me which next step you want and I'll do it.