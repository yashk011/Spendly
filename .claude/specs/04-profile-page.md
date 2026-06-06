# Spec: Profile Page

## Overview
Implement the `GET /profile` route so logged-in users can view their account details
and a summary of their spending. The page displays the user's name, email, and member-since
date pulled from the `users` table, plus an expense summary (total amount spent, total
number of expenses, and a per-category breakdown) aggregated from the `expenses` table.
Unauthenticated visitors are redirected to `/login`. The navbar is updated to include a
"Profile" link for logged-in users so the page is reachable without typing the URL.

## Depends on
- Step 01: Database setup — `users` and `expenses` tables and `get_db()` must exist.
- Step 02: Registration — user rows must be creatable.
- Step 03: Login / Logout — `session["user_id"]` and `session["user_name"]` must be set
  on login; the logged-in navbar state in `base.html` must already be in place.

## Routes
- `GET /profile` — render profile page with user info and expense summary — logged-in only
  (redirect to `/login` if `session.get("user_id")` is falsy)

## Database changes
No database changes. All required data exists in `users` (id, name, email, created_at)
and `expenses` (user_id, amount, category).

## Templates
- **Create:** `templates/profile.html`
  - Extends `base.html`.
  - Two sections:
    1. **Account info card** — displays name, email, member since (formatted date).
    2. **Spending summary card** — displays total amount spent (₹), total number of
       expenses, and a per-category breakdown list (category name + total ₹ + count).
  - Shows a friendly empty state ("No expenses recorded yet.") when the user has no
    expenses.
- **Modify:** `templates/base.html`
  - In the logged-in navbar block, add a "Profile" link (`url_for('profile')`) before
    the existing "Sign out" link.

## Files to change
- `app.py` — replace the placeholder string return in `/profile` with a real
  implementation: login guard, DB queries for user row and expense aggregates, pass data
  to `profile.html`.
- `templates/base.html` — add "Profile" nav link for authenticated users.

## Files to create
- `templates/profile.html` — profile page template.
- `static/css/profile.css` — profile-specific styles, loaded via `{% block head %}` in
  `profile.html` (mirrors the pattern used by `landing.css`).

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — use `sqlite3` via `get_db()` only.
- Parameterised queries only — never interpolate values into SQL strings.
- Passwords hashed with werkzeug — do not display or transmit `password_hash` to the
  template under any circumstances.
- Use CSS variables — never hardcode hex values in any stylesheet or template.
- All templates extend `base.html`.
- Login guard: if `not session.get("user_id")`, do `redirect(url_for("login"))` at the
  top of the route — before any DB call.
- Fetch the user row with `SELECT id, name, email, created_at FROM users WHERE id = ?`
  using `session["user_id"]`. If the row is missing (deleted account edge case), clear
  the session and redirect to `/login`.
- Fetch expense summary with a single aggregation query:
  `SELECT category, COUNT(*) as count, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC`
- Compute the grand total and grand count in Python from the returned rows — do not run
  a second query.
- Format `created_at` for display in the route (Python `datetime.strptime` + `strftime`)
  and pass the formatted string to the template — do not format in Jinja.
- Currency values must be displayed as `₹X,XXX.XX` — use Python's
  `f"₹{value:,.2f}"` formatting in the route before passing to the template, or a
  custom Jinja filter; do not rely on browser locale.
- Do not add edit/delete capabilities to this step — the profile page is read-only.

## Definition of done
- [ ] Visiting `/profile` while logged out redirects to `/login`.
- [ ] Visiting `/profile` while logged in renders the page without errors.
- [ ] The page displays the correct name, email, and member-since date for the
      logged-in user.
- [ ] The page displays the correct total amount spent and total expense count,
      matching the data in the DB.
- [ ] The per-category breakdown lists every category for that user with correct
      totals and counts.
- [ ] A user with no expenses sees the empty-state message instead of a broken table.
- [ ] The navbar shows a "Profile" link when logged in that navigates to `/profile`.
- [ ] `password_hash` is never passed to or rendered in any template.
- [ ] The app starts without errors after all changes.
- The page displays at least three summary stat values (e.g. total spent, transaction count, top category)
- The page displays a transaction history table with at least three hardcoded rows
- The page displays a category breakdown section with at least three categories


