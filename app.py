import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db, init_db, seed_db
from database.queries import get_user_by_id, get_summary_stats, get_recent_transactions, get_category_breakdown, get_expense_by_id

app = Flask(__name__)
# TODO: replace with os.environ["SECRET_KEY"] in production
app.secret_key = "dev-secret-change-me"

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("landing"))
    if request.method == "GET":
        return render_template("register.html")

    name             = request.form.get("name", "").strip()
    email            = request.form.get("email", "").strip()
    password         = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not name or not email or not password or not confirm_password:
        return render_template("register.html",
                               error="All fields are required.",
                               name=name, email=email)

    if len(password) < 8:
        return render_template("register.html",
                               error="Password must be at least 8 characters.",
                               name=name, email=email)

    if password != confirm_password:
        return render_template("register.html",
                               error="Passwords do not match.",
                               name=name, email=email)

    try:
        db = get_db()
        db.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        db.commit()
        db.close()
    except sqlite3.IntegrityError:
        return render_template("register.html",
                               error="That email is already registered.",
                               name=name, email=email)

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("landing"))
    if request.method == "GET":
        return render_template("login.html")

    email    = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        return render_template("login.html",
                               error="All fields are required.",
                               email=email)

    db   = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    db.close()

    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("login.html",
                               error="Invalid email or password.",
                               email=email)

    session["user_id"]   = user["id"]
    session["user_name"] = user["name"]
    return redirect(url_for("profile"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


def _parse_date_filters(raw_from, raw_to):
    """Return (date_from, date_to) as YYYY-MM-DD strings, or (None, None) if invalid/absent."""
    try:
        d_from = datetime.strptime(raw_from, "%Y-%m-%d").date()
        d_to   = datetime.strptime(raw_to,   "%Y-%m-%d").date()
    except ValueError:
        return None, None
    if d_from > d_to:
        return None, None
    return raw_from, raw_to


def _fmt_date(date_str):
    """Format a YYYY-MM-DD string as 'DD Mon YYYY' for display."""
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d %b %Y")


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user = get_user_by_id(session["user_id"])

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    raw_from = request.args.get("date_from", "").strip()
    raw_to   = request.args.get("date_to",   "").strip()
    date_from, date_to = _parse_date_filters(raw_from, raw_to)

    any_input   = bool(raw_from or raw_to)
    filter_active = bool(date_from and date_to)
    filter_error  = any_input and not filter_active

    stats = get_summary_stats(session["user_id"], date_from=date_from, date_to=date_to)
    recent_transactions = get_recent_transactions(session["user_id"], date_from=date_from, date_to=date_to)
    categories = get_category_breakdown(session["user_id"], date_from=date_from, date_to=date_to)

    return render_template("profile.html",
        user_name=user["name"],
        user_email=user["email"],
        member_since=user["member_since"],
        grand_total=stats["total_spent"],
        grand_count=stats["transaction_count"],
        top_category=stats["top_category"],
        recent_transactions=recent_transactions,
        has_recent=bool(recent_transactions),
        categories=categories,
        has_expenses=bool(categories),
        date_from=date_from or "",
        date_to=date_to or "",
        filter_active=filter_active,
        filter_error=filter_error,
        filter_label_from=_fmt_date(date_from) if date_from else "",
        filter_label_to=_fmt_date(date_to)   if date_to   else "",
    )


CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    today = datetime.today().strftime("%Y-%m-%d")

    if request.method == "GET":
        return render_template("add_expense.html", categories=CATEGORIES, today=today)

    amount_raw  = request.form.get("amount", "").strip()
    category    = request.form.get("category", "").strip()
    date_raw    = request.form.get("date", "").strip()
    description = request.form.get("description", "").strip()[:200]

    def fail(msg):
        return render_template("add_expense.html", categories=CATEGORIES, today=today,
                               error=msg, amount=amount_raw, category=category,
                               date=date_raw, description=description)

    if not amount_raw:
        return fail("Amount is required.")
    try:
        amount = float(amount_raw)
    except ValueError:
        return fail("Amount must be a number.")
    if amount <= 0:
        return fail("Amount must be greater than zero.")

    if category not in CATEGORIES:
        return fail("Please select a valid category.")

    if not date_raw:
        return fail("Date is required.")
    try:
        datetime.strptime(date_raw, "%Y-%m-%d")
    except ValueError:
        return fail("Date must be a valid date.")

    db = get_db()
    db.execute(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        (session["user_id"], amount, category, date_raw, description or None),
    )
    db.commit()
    db.close()

    return redirect(url_for("profile") + "?added=1")


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
def edit_expense(id):
    if not session.get("user_id"):
        return redirect(url_for("login"))

    expense = get_expense_by_id(id, session["user_id"])
    if expense is None:
        abort(404)

    if request.method == "GET":
        return render_template("edit_expense.html",
                               categories=CATEGORIES, expense=expense)

    amount_raw  = request.form.get("amount", "").strip()
    category    = request.form.get("category", "").strip()
    date_raw    = request.form.get("date", "").strip()
    description = request.form.get("description", "").strip()[:200]

    def fail(msg):
        return render_template("edit_expense.html", categories=CATEGORIES,
                               expense=expense, error=msg,
                               amount=amount_raw, category=category,
                               date=date_raw, description=description)

    if not amount_raw:
        return fail("Amount is required.")
    try:
        amount = float(amount_raw)
    except ValueError:
        return fail("Amount must be a number.")
    if amount <= 0:
        return fail("Amount must be greater than zero.")
    if category not in CATEGORIES:
        return fail("Please select a valid category.")
    if not date_raw:
        return fail("Date is required.")
    try:
        datetime.strptime(date_raw, "%Y-%m-%d")
    except ValueError:
        return fail("Date must be a valid date.")

    db = get_db()
    db.execute(
        "UPDATE expenses SET amount=?, category=?, date=?, description=? WHERE id=? AND user_id=?",
        (amount, category, date_raw, description or None, id, session["user_id"]),
    )
    db.commit()
    db.close()

    return redirect(url_for("profile") + "?edited=1")


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
