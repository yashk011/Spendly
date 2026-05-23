# Spec: Registration

## Overview
Implement the POST handler for `/register` so users can create a Spendly account.
The form UI already exists in `register.html` (renders `name`, `email`, `password` fields
and displays an `{{ error }}` variable). This step wires the form to the database: validate
input, hash the password, insert the new user, and redirect to `/login` on success.
It also adds `app.secret_key` to `app.py` so Flask sessions work in later steps.

## Depends on
- Step 01: Database setup — `users` table and `get_db()` must exist.

## Routes
- `POST /register` — validate form data, create user, redirect to login — public

## Database changes
No database changes. The `users` table (id, name, email, password_hash, created_at)
already exists from Step 01.

## Templates
- **Modify:** `templates/register.html`
  - Re-render with `value="{{ name }}"` and `value="{{ email }}"` on the inputs so the
    user does not lose their typed values after a validation error.

## Files to change
- `app.py` — add `POST` to the `/register` route, import `request` and `redirect`/`url_for`
  from Flask, import `generate_password_hash` from `werkzeug.security`, import `get_db`,
  add `app.secret_key`, implement registration logic.
- `templates/register.html` — preserve field values on error via `value` attributes.

## Files to create
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — use `sqlite3` via `get_db()` only.
- Parameterised queries only — never interpolate values into SQL strings.
- Hash passwords with `werkzeug.security.generate_password_hash`.
- Use CSS variables — never hardcode hex values in any template or stylesheet.
- All templates extend `base.html`.
- Validate in this order, stopping at the first failure:
  1. All three fields non-empty.
  2. Password is at least 8 characters.
  3. Email not already registered (catch the `sqlite3.IntegrityError` on INSERT, or
     pre-check with a SELECT — either is acceptable, but the IntegrityError approach
     is preferred to avoid a race condition).
- On any validation failure: re-render `register.html` passing `error`, `name`, and
  `email` so the user's input is preserved (do not preserve the password).
- On success: `redirect(url_for('login'))` — do not auto-login the user here (that is
  Step 03).
- Set `app.secret_key` to a hard-coded development string for now
  (e.g. `"dev-secret-change-me"`). Add a comment that this must be replaced in
  production via an environment variable.

## Definition of done
- [ ] Submitting the form with valid data inserts a new row into `users` with a hashed
      password and redirects to `/login`.
- [ ] Submitting with any empty field re-renders the registration page with an error
      message and the previously typed name and email still visible.
- [ ] Submitting a password shorter than 8 characters shows a validation error.
- [ ] Registering with an already-used email shows "Email already registered" (or
      similar) without a 500 error.
- [ ] The password is never stored in plain text — verify via SQLite browser or a
      quick `SELECT password_hash FROM users` query.
- [ ] The app starts without errors after changes to `app.py`.
- [ ] No new pip packages are required.
