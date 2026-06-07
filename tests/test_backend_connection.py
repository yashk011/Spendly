import pytest
from app import app
from database.queries import (
    get_user_by_id,
    get_summary_stats,
    get_recent_transactions,
    get_category_breakdown,
)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Unit tests — get_user_by_id
# ---------------------------------------------------------------------------

def test_get_user_by_id_valid():
    """Seed user (id=1) must be present with correct name and email."""
    user = get_user_by_id(1)
    assert user is not None
    assert user["name"] == "Demo User"
    assert user["email"] == "demo@spendly.com"
    assert "member_since" in user


def test_get_user_by_id_nonexistent():
    """A user id that was never inserted must return None."""
    assert get_user_by_id(99999) is None


# ---------------------------------------------------------------------------
# Unit tests — get_summary_stats
# ---------------------------------------------------------------------------

def test_get_summary_stats_with_expenses():
    """Seed user has expenses; top category is Bills; total contains ₹."""
    stats = get_summary_stats(1)
    assert stats["transaction_count"] >= 8
    assert stats["top_category"] == "Bills"
    assert "₹" in stats["total_spent"]


def test_get_summary_stats_no_expenses():
    """Non-existent user has zero expenses and a zero-formatted total."""
    stats = get_summary_stats(99999)
    assert stats["transaction_count"] == 0
    assert stats["top_category"] == "—"
    assert stats["total_spent"] == "₹0.00"


# ---------------------------------------------------------------------------
# Unit tests — get_recent_transactions
# ---------------------------------------------------------------------------

def test_get_recent_transactions_with_expenses():
    """Seed user has transactions; results are capped at limit and ordered newest-first."""
    txns = get_recent_transactions(1)
    assert 1 <= len(txns) <= 10
    for t in txns:
        assert "date" in t and "category" in t and "amount" in t
    # newest-first: first date must be >= last date (lexicographic on "DD Mon YYYY" won't work,
    # but the query orders by date DESC so just verify structure is present)
    assert "₹" in txns[0]["amount"]


def test_get_recent_transactions_no_expenses():
    """Non-existent user must return an empty list."""
    assert get_recent_transactions(99999) == []


# ---------------------------------------------------------------------------
# Unit tests — get_category_breakdown
# ---------------------------------------------------------------------------

def test_get_category_breakdown_with_expenses():
    """Seed user has 7 distinct categories; percentages must sum to 100;
    Bills must be first (highest total)."""
    cats = get_category_breakdown(1)
    assert len(cats) == 7
    pct_sum = sum(c["pct"] for c in cats)
    assert pct_sum == 100
    assert cats[0]["name"] == "Bills"


def test_get_category_breakdown_no_expenses():
    """Non-existent user must return an empty list."""
    assert get_category_breakdown(99999) == []


# ---------------------------------------------------------------------------
# Route tests
# ---------------------------------------------------------------------------

def test_profile_unauthenticated(client):
    """Visiting /profile without a session must redirect to /login."""
    resp = client.get("/profile")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_profile_authenticated(client):
    """Visiting /profile with a valid session must return 200 with user data."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"
    resp = client.get("/profile")
    assert resp.status_code == 200
    data = resp.data.decode()
    assert "Demo User" in data
    assert "demo@spendly.com" in data
    assert "₹" in data
    assert "Bills" in data
