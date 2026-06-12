# Spec: Add Expense

## Overview
This feature lets a logged-in user record a new expense via a form at `GET/POST /expenses/add`. The form collects the required fields (amount, category, date, description), validates them server-side, inserts the row into the `expenses` table, and redirects to the profile page on success. This is the first route where users actively produce data, making it a core milestone in the Spendly roadmap.

## Depends on
- Step 05 — backend profile route (session auth pattern, `get_db`)
- Step 03 — login/logout (session must contain `user_id`)
- Step 01 — database setup (`expenses` table exists)

## Routes
- `GET /expenses/add` — render the add-expense form — logged-in only
- `POST /expenses/add` — validate and insert the expense, redirect to `/profile` — logged-in only

## Database changes
No new tables or columns. The `expenses` table already has all required fields:
- `user_id` (INTEGER, FK → users.id)
- `amount` (REAL)
- `category` (TEXT)
- `date` (TEXT, YYYY-MM-DD)
- `description` (TEXT, nullable)

## Templates
- **Create:** `templates/add_expense.html` — form with fields: amount, category, date, description; shows inline error messages; extends `base.html`
- **Modify:** `templates/profile.html` — add an "Add Expense" button/link pointing to `/expenses/add`

## Files to change
- `app.py` — replace the placeholder `add_expense` route with a full GET/POST implementation

## Files to create
- `templates/add_expense.html` — the add-expense form template

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` via `get_db()` only
- Parameterised queries only — never string-interpolate user input into SQL
- Passwords hashed with werkzeug (not relevant here, but keep the pattern)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Redirect unauthenticated users to `/login`
- `amount` must be a positive number (> 0); reject non-numeric input
- `category` must be one of the fixed list: Food, Transport, Bills, Health, Entertainment, Shopping, Other
- `date` must be a valid YYYY-MM-DD date; default the field to today's date
- `description` is optional (max 200 chars if provided)
- On validation failure, re-render the form with the error message and previously entered values (sticky form)
- On success, redirect to `url_for("profile")` with a flash or query-param confirmation (keep it simple — no flash framework required; a `?added=1` param is fine)

## Definition of done
- [ ] Visiting `/expenses/add` while logged out redirects to `/login`
- [ ] Visiting `/expenses/add` while logged in renders a form with amount, category (dropdown), date, and description fields
- [ ] The date field is pre-filled with today's date
- [ ] Submitting the form with a valid expense inserts a row in `expenses` and redirects to `/profile`
- [ ] The new expense appears in the Recent Transactions list on `/profile`
- [ ] Submitting with a blank amount shows an error and does not insert a row
- [ ] Submitting with a non-numeric amount (e.g. "abc") shows an error
- [ ] Submitting with amount ≤ 0 shows an error
- [ ] Submitting with an invalid date shows an error
- [ ] Previously entered values are retained in the form after a validation error
- [ ] The profile page has a visible "Add Expense" link/button pointing to `/expenses/add`
