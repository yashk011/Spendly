from datetime import datetime
from database.db import get_db


def get_user_by_id(user_id):
    """Return basic profile info for a user, or None if not found."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if row is None:
            return None
        member_since = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S").strftime("%B %Y")
        return {
            "name": row["name"],
            "email": row["email"],
            "member_since": member_since,
        }
    finally:
        conn.close()


def _date_clause(date_from, date_to):
    """Return (sql_fragment, extra_params) for an optional date BETWEEN filter."""
    if date_from and date_to:
        return " AND date BETWEEN ? AND ?", [date_from, date_to]
    return "", []


def get_summary_stats(user_id, date_from=None, date_to=None):
    """Return total spent, transaction count, and top spending category."""
    conn = get_db()
    try:
        clause, dparams = _date_clause(date_from, date_to)

        row = conn.execute(
            "SELECT SUM(amount), COUNT(*) FROM expenses WHERE user_id = ?" + clause,
            [user_id] + dparams,
        ).fetchone()

        total_raw = row[0]
        count = row[1]

        total_spent = "₹{:,.2f}".format(total_raw if total_raw is not None else 0)
        transaction_count = count if count is not None else 0

        top_row = conn.execute(
            "SELECT category FROM expenses WHERE user_id = ?" + clause +
            " GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            [user_id] + dparams,
        ).fetchone()
        top_category = top_row[0] if top_row is not None else "—"

        return {
            "total_spent": total_spent,
            "transaction_count": transaction_count,
            "top_category": top_category,
        }
    finally:
        conn.close()


def get_recent_transactions(user_id, limit=10, date_from=None, date_to=None):
    """Return the most recent expenses for a user, formatted for display."""
    conn = get_db()
    try:
        clause, dparams = _date_clause(date_from, date_to)

        rows = conn.execute(
            "SELECT id, amount, category, date, description "
            "FROM expenses WHERE user_id = ?" + clause +
            " ORDER BY date DESC, id DESC LIMIT ?",
            [user_id] + dparams + [limit],
        ).fetchall()

        result = []
        for r in rows:
            formatted_date = datetime.strptime(r["date"], "%Y-%m-%d").strftime("%d %b %Y")
            result.append({
                "id": r["id"],
                "date": formatted_date,
                "category": r["category"],
                "amount": "₹{:,.2f}".format(r["amount"]),
                "description": r["description"] if r["description"] is not None else "",
            })
        return result
    finally:
        conn.close()


def get_category_breakdown(user_id, date_from=None, date_to=None):
    """Return per-category totals and integer percentages that sum exactly to 100."""
    conn = get_db()
    try:
        clause, dparams = _date_clause(date_from, date_to)

        rows = conn.execute(
            "SELECT category, COUNT(*) as cnt, SUM(amount) as total "
            "FROM expenses WHERE user_id = ?" + clause +
            " GROUP BY category ORDER BY total DESC",
            [user_id] + dparams,
        ).fetchall()

        if not rows:
            return []

        grand_total = sum(r["total"] for r in rows)

        # Compute raw (float) percentages and floor them to integers.
        items = []
        for r in rows:
            raw_pct = (r["total"] / grand_total) * 100
            items.append({
                "name": r["category"],
                "count": r["cnt"],
                "amount": "₹{:,.2f}".format(r["total"]),
                "_raw_pct": raw_pct,
                "pct": int(raw_pct),
                "_total": r["total"],
            })

        # Distribute the rounding remainder to the largest category.
        remainder = 100 - sum(item["pct"] for item in items)
        if remainder > 0:
            # Find the item with the largest total (already first due to ORDER BY DESC,
            # but be explicit to be safe).
            largest = max(items, key=lambda x: x["_total"])
            largest["pct"] += remainder

        # Strip internal keys before returning.
        return [
            {"name": item["name"], "count": item["count"], "amount": item["amount"], "pct": item["pct"]}
            for item in items
        ]
    finally:
        conn.close()


def get_expense_by_id(expense_id, user_id):
    """Return a single expense row for editing, or None if not found / not owned by user."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id, amount, category, date, description FROM expenses "
            "WHERE id = ? AND user_id = ?",
            (expense_id, user_id),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
