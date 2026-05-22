# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
pip install -r requirements.txt
python app.py          # starts on http://localhost:5001 in debug mode
```

## Running tests

```bash
pytest                 # run all tests
pytest tests/test_foo.py::test_name   # run a single test
```

## Architecture

**Stack:** Flask (Python) + Jinja2 templates + vanilla JS. No frontend framework, no build step.

**Entry point:** `app.py` — defines all routes and renders templates directly. No blueprints or application factory yet.

**Database:** `database/db.py` is a stub. `get_db()`, `init_db()`, and `seed_db()` are not yet implemented; the app currently has no live data.

**Templates** extend `templates/base.html`, which provides the navbar, footer (with Terms/Privacy links), and font imports (DM Serif Display + DM Sans via Google Fonts).

**CSS split:**
- `static/css/style.css` — global styles, shared across all pages
- `static/css/landing.css` — landing-page-only overrides, loaded via `{% block head %}` in `landing.html`

**JS:** `static/js/main.js` is near-empty. Page-specific JS (e.g. the YouTube modal on the landing page) lives in `{% block scripts %}` inside the relevant template.

## Route status

| Route | Status |
|---|---|
| `GET /` | Done — landing page |
| `GET /register` | Done — form rendered |
| `GET /login` | Done — form rendered |
| `GET /terms` | Done |
| `GET /privacy` | Done |
| `GET /logout` | Placeholder (Step 3) |
| `GET /profile` | Placeholder (Step 4) |
| `GET /expenses/add` | Placeholder (Step 7) |
| `GET/POST /expenses/<id>/edit` | Placeholder (Step 8) |
| `GET /expenses/<id>/delete` | Placeholder (Step 9) |

## Conventions

- Currency is Indian Rupees (₹).
- No JS libraries — vanilla JS only.
- Legal/policy pages (`terms.html`, `privacy.html`) reuse the `.terms-page` / `.terms-inner` / `.terms-section` CSS classes defined in `style.css`.
- The hero dashboard mock card uses `.dash-*` classes; the old `.mock-*` classes in `style.css` are legacy and no longer referenced in templates.
