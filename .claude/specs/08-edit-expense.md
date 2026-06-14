# Spec: Edit Expense

## Overview
This feature lets a logged-in user edit an existing expense via a pre-filled form at `GET/POST /expenses/<id>/edit`. The route loads the expense by ID, verifies it belongs to the current user, renders the form with existing values, validates the submission, updates the row in the `expenses` table, and redirects to the profile page on success. It mirrors the Add Expense flow but operates on an existing record instead of inserting a new one.

## Depends on
- Step 07 — Add Expense (same form fields, same validation rules, same CATEGORIES list)
- Step 05 — backend profile route (session auth pattern, `get_db`)
- Step 03 — login/logout (session must contain `user_id`)
- Step 01 — database setup (`expenses` table exists)

## Routes
- `GET /expenses/<id>/edit` — render the edit form pre-filled with the expense's current values — logged-in only
- `POST /expenses/<id>/edit` — validate and update the expense, redirect to `/profile` — logged-in only

## Database changes
No new tables or columns. The existing `expenses` table has all required fields.

## Templates
- **Create:** `templates/edit_expense.html` — pre-filled form with fields: amount, category, date, description; shows inline error messages; extends `base.html`
- **Modify:** `templates/profile.html` — add an "Edit" link on each row in the Recent Transactions list, pointing to `/expenses/<id>/edit`

## Files to change
- `app.py` — replace the placeholder `edit_expense` route with a full GET/POST implementation; add `methods=["GET", "POST"]` to the route decorator
- `templates/profile.html` — add Edit links to each transaction row

## Files to create
- `templates/edit_expense.html` — the edit-expense form template

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` via `get_db()` only
- Parameterised queries only — never string-interpolate user input into SQL
- Passwords hashed with werkzeug (not relevant here, but keep the pattern)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Redirect unauthenticated users to `/login`
- After loading the expense by ID, verify `expense["user_id"] == session["user_id"]`; if not (or if the expense doesn't exist), return a 404 with `abort(404)`
- Reuse the same `CATEGORIES` list defined in `app.py`
- `amount` must be a positive number (> 0); reject non-numeric input
- `category` must be one of the fixed CATEGORIES list
- `date` must be a valid YYYY-MM-DD date
- `description` is optional (max 200 chars if provided)
- On validation failure, re-render the edit form with the error message and submitted values (sticky form)
- On success, redirect to `url_for("profile")` with `?edited=1` query param

## Definition of done
- [ ] Visiting `/expenses/1/edit` while logged out redirects to `/login`
- [ ] Visiting `/expenses/999/edit` (non-existent ID) returns a 404
- [ ] Visiting `/expenses/<id>/edit` for an expense belonging to another user returns a 404
- [ ] Visiting `/expenses/<id>/edit` while logged in renders a form pre-filled with the expense's current amount, category, date, and description
- [ ] The category dropdown shows the correct current category as selected
- [ ] Submitting valid changes updates the expense row in the database and redirects to `/profile`
- [ ] The updated values appear in the Recent Transactions list on `/profile` after editing
- [ ] Submitting with a blank amount shows an error and does not update the row
- [ ] Submitting with a non-numeric amount shows an error
- [ ] Submitting with amount ≤ 0 shows an error
- [ ] Submitting with an invalid date shows an error
- [ ] Previously submitted values are retained in the form after a validation error
- [ ] Each transaction row on `/profile` has a visible "Edit" link pointing to the correct `/expenses/<id>/edit` URL
