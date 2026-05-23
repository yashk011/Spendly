# Spec: Login and Logout Flow

## Overview
Implement the POST handler for `/login` and a working `/logout` route so users can
authenticate into Spendly and end their session. Login validates the submitted email
and password against the `users` table, stores the authenticated user's `id` and `name`
in `session`, and redirects to `/` (or a future dashboard). Logout clears the session
and redirects to `/login`. Both routes depend on `app.secret_key` already added in
Step 02. The login form UI already exists in `login.html`.

## Depends on
- Step 01: Database setup — `users` table and `get_db()` must exist.
- Step 02: Registration — `app.secret_key` set, Flask session infrastructure in place.

## Routes
- `POST /login` — validate credentials, write session, redirect to `/` — public
- `GET /logout` — clear session, redirect to `/login` — public (no login guard needed here)

## Database changes
No database changes.

## Templates
- **Modify:** `templates/login.html`
  - Preserve `email` field value on failed login via `value="{{ email }}"`.
- **Modify:** `templates/base.html`
  - Navbar: show **"Sign out"** link (pointing to `/logout`) when `session.user_id` is set,
    replacing the current "Sign in" / "Get started" links.

## Files to change
- `app.py` — add `POST` method to `/login` route; replace placeholder `/logout` with
  a real implementation; import `check_password_hash` from `werkzeug.security`;
  import `session` from Flask.
- `templates/login.html` — add `value="{{ email }}"` to the email input.
- `templates/base.html` — conditional navbar links based on session state.

## Files to create
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — use `sqlite3` via `get_db()` only.
- Parameterised queries only — never interpolate values into SQL strings.
- Verify passwords with `werkzeug.security.check_password_hash` — never compare plain text.
- Use CSS variables — never hardcode hex values in any template or stylesheet.
- All templates extend `base.html`.
- Login validation order (stop at first failure):
  1. Both fields non-empty.
  2. Email exists in `users` table — if not, show generic error (do not reveal whether
     the email is registered or the password is wrong — use "Invalid email or password.").
  3. `check_password_hash(row["password_hash"], password)` — same generic error on mismatch.
- On success: store `session["user_id"] = row["id"]` and `session["user_name"] = row["name"]`,
  then `redirect(url_for("landing"))`.
- On failure: re-render `login.html` with `error` and `email` (never preserve password).
- Logout: call `session.clear()` then `redirect(url_for("login"))`.
- Do NOT implement a login-required guard (`@login_required`) in this step — that is
  a separate cross-cutting concern for a later step.

## Definition of done
- [ ] Submitting valid credentials stores `user_id` and `user_name` in the session and
      redirects to `/`.
- [ ] Submitting an unrecognised email shows "Invalid email or password." without a 500 error.
- [ ] Submitting the correct email but wrong password shows the same generic error.
- [ ] Submitting with either field empty shows a validation error.
- [ ] After login the navbar shows "Sign out" instead of "Sign in" / "Get started".
- [ ] Visiting `/logout` clears the session and redirects to `/login`.
- [ ] After logout the navbar reverts to showing "Sign in" / "Get started".
- [ ] The app starts without errors after all changes.
