# Spec: Date Filter for Profile Page

## Overview
Step 6 adds a date range filter to the profile page so users can narrow the
summary stats, transaction list, and category breakdown to a specific month or
custom date window. Without filtering, every section always shows all-time
data, which becomes unwieldy as expenses accumulate. This step adds a filter
bar above the stats row — driven by GET query parameters — so the page is
self-contained, bookmarkable, and requires no JavaScript to function. The
default view (no filter applied) continues to show all-time data.

## Depends on
- Step 1: Database setup (`expenses` table with a `date` TEXT column)
- Step 2: Registration (users exist in the database)
- Step 3: Login / Logout (`session["user_id"]` is set on login)
- Step 4: Profile page UI (template with stats row, transaction list, category breakdown)
- Step 5: Backend profile route (live query helpers in `database/queries.py`)

## Routes
- `GET /profile` — extended to accept optional query parameters `date_from`
  and `date_to` (both `YYYY-MM-DD`). When absent the page shows all-time data.
  Access: logged-in only.

No new routes.

## Database changes
No database changes. The `expenses.date` column (`TEXT`, `YYYY-MM-DD`) is
already sufficient for `BETWEEN` filtering.

## Templates
- **Modify:** `templates/profile.html`
  - Add a filter bar between the page header and the stats row containing:
    - A "From" date input (`<input type="date" name="date_from">`)
    - A "To" date input (`<input type="date" name="date_to">`)
    - An "Apply" submit button
    - A "Clear" link that resets to `/profile` (no query params)
  - Pre-populate the date inputs with the current filter values so the user
    sees what is active after submitting.
  - When a filter is active, show a visible indicator (e.g. a label "Filtered:
    {date_from} → {date_to}") so it is clear the view is not all-time.

## Files to change
- `app.py` — read `date_from` and `date_to` from `request.args`; validate and
  sanitise them; pass them to each query helper.
- `database/queries.py` — add an optional `date_from` / `date_to` parameter
  to `get_summary_stats`, `get_recent_transactions`, and
  `get_category_breakdown`. When both are provided, add a
  `AND date BETWEEN ? AND ?` clause; when absent the queries are unchanged.
- `templates/profile.html` — add the filter bar and active-filter indicator
  (see Templates section above).
- `static/css/profile.css` — add styles for `.filter-bar`, `.filter-form`,
  `.filter-active-label`, and the Apply / Clear controls.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- Parameterised queries only — never string-format values into SQL
- Passwords hashed with werkzeug (no changes to auth in this step)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- No inline styles
- Date validation in `app.py`: parse with `datetime.strptime(value, "%Y-%m-%d")`
  inside a `try/except`; silently discard any value that does not parse. Do
  not raise HTTP errors — fall back to unfiltered data instead.
- If `date_from` is after `date_to`, treat both as absent (show all-time data).
- The filter form must use `method="get"` and `action="/profile"` so that the
  date range is reflected in the URL.
- Pass `date_from` and `date_to` back to the template as strings (empty string
  when absent) so the inputs can be pre-populated via `value="{{ date_from }}"`.
- The "Clear" link must be a plain `<a href="/profile">` — not a button — so
  it works without JavaScript.
- All amounts still display the ₹ symbol.

## Definition of done
- [ ] Visiting `/profile` with no query params shows all-time stats (same as
  before this step).
- [ ] Submitting the filter form with `date_from=2026-05-01` and
  `date_to=2026-05-15` updates the URL to
  `/profile?date_from=2026-05-01&date_to=2026-05-15` and shows only expenses
  in that range.
- [ ] Summary stats (total spent, transaction count, top category) reflect only
  the filtered expenses.
- [ ] The transaction list shows only expenses within the date range, ordered
  newest-first.
- [ ] The category breakdown shows only categories that have at least one
  expense in the date range.
- [ ] The date inputs are pre-populated with the active filter values after
  the form is submitted.
- [ ] A visible "Filtered" indicator appears when a date range is active.
- [ ] Clicking "Clear" navigates to `/profile` and shows all-time data again.
- [ ] Submitting the form with an invalid date (e.g. `date_from=not-a-date`)
  falls back to all-time data without raising an error.
- [ ] Submitting with `date_from` after `date_to` falls back to all-time data.
- [ ] A user with no expenses in the selected range sees empty states — not
  errors.
