"""
tests/test_date_filter.py

Tests for Step 06 — Date Filter for Profile Page.

Seed data reference (from database/db.py seed_db, user_id=1):
  2026-05-01  Bills         4500.00
  2026-05-03  Food           850.00
  2026-05-05  Transport      320.00
  2026-05-08  Health        1200.00
  2026-05-11  Entertainment  599.00
  2026-05-14  Shopping      2300.00
  2026-05-18  Food           480.00
  2026-05-21  Other          150.00

All tests use the real (seeded) spendly.db that the application initialises on
import, mirroring the pattern established in test_backend_connection.py.
Sessions are injected directly via client.session_transaction() to simulate
authenticated users without going through the login form.
"""

import pytest
import re
from app import app
from database.queries import (
    get_summary_stats,
    get_recent_transactions,
    get_category_breakdown,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SEED_USER_ID = 1  # Demo User — always present after init_db() + seed_db()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def auth_client(client):
    """Test client with a valid session for the seed demo user."""
    with client.session_transaction() as sess:
        sess["user_id"] = SEED_USER_ID
        sess["user_name"] = "Demo User"
    return client


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _html(response):
    return response.data.decode("utf-8")


# ---------------------------------------------------------------------------
# Auth-guard tests
# ---------------------------------------------------------------------------

class TestAuthGuard:
    def test_unauthenticated_no_params_redirects_to_login(self, client):
        """GET /profile without session must redirect to /login."""
        resp = client.get("/profile")
        assert resp.status_code == 302, "Expected redirect for unauthenticated request"
        assert "/login" in resp.headers["Location"]

    def test_unauthenticated_with_date_params_redirects_to_login(self, client):
        """GET /profile with date params but no session must still redirect to /login."""
        resp = client.get("/profile?date_from=2026-05-01&date_to=2026-05-15")
        assert resp.status_code == 302, "Date params must not bypass auth guard"
        assert "/login" in resp.headers["Location"]


# ---------------------------------------------------------------------------
# Default (no filter params) behaviour
# ---------------------------------------------------------------------------

class TestDefaultNoFilter:
    def test_returns_200(self, auth_client):
        """Authenticated GET /profile with no params must return 200."""
        resp = auth_client.get("/profile")
        assert resp.status_code == 200

    def test_shows_all_time_data(self, auth_client):
        """All 8 seed expenses are present in all-time view — ₹ symbol and Bills visible."""
        resp = auth_client.get("/profile")
        body = _html(resp)
        assert "₹" in body, "Currency symbol must appear in all-time view"
        assert "Bills" in body, "Top category Bills must appear in all-time view"

    def test_no_filter_indicator_when_no_params(self, auth_client):
        """When no date params are supplied, the 'Filtered' indicator must not appear."""
        resp = auth_client.get("/profile")
        body = _html(resp)
        assert "Filtered" not in body, "Filter indicator must be absent when no params are given"

    def test_date_inputs_are_empty_when_no_params(self, auth_client):
        """The date inputs must have empty values when no filter is active."""
        resp = auth_client.get("/profile")
        body = _html(resp)
        # The template uses value="{{ date_from }}" and value="{{ date_to }}"
        # When both are empty strings the rendered attributes should be value=""
        assert 'value=""' in body or "value=''" in body, (
            "Date inputs must carry empty value attributes when no filter is active"
        )


# ---------------------------------------------------------------------------
# Happy path — valid date range
# ---------------------------------------------------------------------------

class TestValidDateRange:
    # Range covers: Bills(05-01), Food(05-03), Transport(05-05), Health(05-08)
    EARLY_FROM = "2026-05-01"
    EARLY_TO   = "2026-05-10"

    def test_returns_200(self, auth_client):
        resp = auth_client.get(f"/profile?date_from={self.EARLY_FROM}&date_to={self.EARLY_TO}")
        assert resp.status_code == 200

    def test_filter_indicator_is_shown(self, auth_client):
        """A visible 'Filtered' indicator must appear when a valid date range is active."""
        resp = auth_client.get(f"/profile?date_from={self.EARLY_FROM}&date_to={self.EARLY_TO}")
        body = _html(resp)
        assert "Filtered" in body, "Filter active indicator must be visible for a valid date range"

    def test_date_inputs_are_prepopulated(self, auth_client):
        """The date inputs must be pre-populated with the submitted filter values."""
        resp = auth_client.get(f"/profile?date_from={self.EARLY_FROM}&date_to={self.EARLY_TO}")
        body = _html(resp)
        assert self.EARLY_FROM in body, "date_from value must appear in the rendered page"
        assert self.EARLY_TO in body, "date_to value must appear in the rendered page"

    def test_in_range_category_appears(self, auth_client):
        """Bills is within 2026-05-01 to 2026-05-10 and must appear in the response."""
        resp = auth_client.get(f"/profile?date_from={self.EARLY_FROM}&date_to={self.EARLY_TO}")
        body = _html(resp)
        assert "Bills" in body, "Bills (in-range) must appear in filtered view"

    def test_out_of_range_category_absent(self, auth_client):
        """Shopping (2026-05-14) is outside 2026-05-01→2026-05-10 and must not appear."""
        resp = auth_client.get(f"/profile?date_from={self.EARLY_FROM}&date_to={self.EARLY_TO}")
        body = _html(resp)
        assert "Shopping" not in body, "Shopping (out of range) must not appear in filtered view"

    def test_later_range_shows_shopping(self, auth_client):
        """Range 2026-05-14→2026-05-21 must include Shopping, Food(05-18), Other(05-21)."""
        resp = auth_client.get("/profile?date_from=2026-05-14&date_to=2026-05-21")
        body = _html(resp)
        assert "Shopping" in body, "Shopping must appear in 2026-05-14→2026-05-21 range"
        assert "Other" in body, "Other must appear in 2026-05-14→2026-05-21 range"

    def test_later_range_excludes_early_categories(self, auth_client):
        """Range 2026-05-14→2026-05-21 must NOT include Transport (2026-05-05)."""
        resp = auth_client.get("/profile?date_from=2026-05-14&date_to=2026-05-21")
        body = _html(resp)
        assert "Transport" not in body, "Transport (out of range) must not appear"

    def test_single_day_range(self, auth_client):
        """date_from == date_to is a valid single-day range (2026-05-01 has one expense)."""
        resp = auth_client.get("/profile?date_from=2026-05-01&date_to=2026-05-01")
        assert resp.status_code == 200
        body = _html(resp)
        assert "Bills" in body, "Bills on 2026-05-01 must appear in single-day range"
        assert "Filtered" in body, "Filter indicator must appear for single-day range"


# ---------------------------------------------------------------------------
# Fallback behaviour — invalid / illogical params
# ---------------------------------------------------------------------------

class TestInvalidParamsFallback:
    """Each of these cases must silently fall back to all-time data (no HTTP error,
    no 'Filtered' indicator)."""

    def _assert_fallback(self, auth_client, url):
        resp = auth_client.get(url)
        assert resp.status_code == 200, f"Expected 200, not an error page, for {url}"
        body = _html(resp)
        assert "Filtered" not in body, f"Filtered indicator must be absent on fallback for {url}"
        # All-time data includes Bills
        assert "Bills" in body, f"All-time data (Bills) must appear on fallback for {url}"

    def test_invalid_date_from_falls_back(self, auth_client):
        self._assert_fallback(auth_client, "/profile?date_from=not-a-date&date_to=2026-05-31")

    def test_invalid_date_to_falls_back(self, auth_client):
        self._assert_fallback(auth_client, "/profile?date_from=2026-05-01&date_to=not-a-date")

    def test_both_params_invalid_falls_back(self, auth_client):
        self._assert_fallback(auth_client, "/profile?date_from=abc&date_to=xyz")

    def test_date_from_after_date_to_falls_back(self, auth_client):
        """date_from > date_to must be silently treated as absent — show all-time data."""
        self._assert_fallback(auth_client, "/profile?date_from=2026-05-31&date_to=2026-05-01")

    def test_partial_date_format_falls_back(self, auth_client):
        """A partial date like '2026-05' is not YYYY-MM-DD and must fall back."""
        self._assert_fallback(auth_client, "/profile?date_from=2026-05&date_to=2026-05-31")

    def test_empty_strings_fall_back(self, auth_client):
        """Explicitly supplied empty strings must behave like absent params."""
        self._assert_fallback(auth_client, "/profile?date_from=&date_to=")

    @pytest.mark.parametrize("bad_from,bad_to", [
        ("2026/05/01", "2026-05-31"),   # wrong separator
        ("01-05-2026", "2026-05-31"),   # DD-MM-YYYY instead of YYYY-MM-DD
        ("2026-13-01", "2026-05-31"),   # month 13 does not exist
        ("2026-05-32", "2026-05-31"),   # day 32 does not exist
        ("",           "2026-05-31"),   # only one param supplied
        ("2026-05-01", ""),             # only one param supplied
    ])
    def test_parametrized_invalid_dates_fall_back(self, auth_client, bad_from, bad_to):
        url = f"/profile?date_from={bad_from}&date_to={bad_to}"
        resp = auth_client.get(url)
        assert resp.status_code == 200, f"Must not raise an error for {url}"
        body = _html(resp)
        assert "Filtered" not in body, f"Must not show filter indicator for {url}"


# ---------------------------------------------------------------------------
# Empty date range — valid dates but no expenses match
# ---------------------------------------------------------------------------

class TestEmptyDateRange:
    """A valid date range that has no matching expenses must return zeros/empty
    lists, not a server error."""

    # No seed expenses exist in 2025
    EMPTY_FROM = "2025-01-01"
    EMPTY_TO   = "2025-01-31"

    def test_returns_200_not_error(self, auth_client):
        resp = auth_client.get(f"/profile?date_from={self.EMPTY_FROM}&date_to={self.EMPTY_TO}")
        assert resp.status_code == 200, "Empty date range must still return 200"

    def test_filter_indicator_is_shown(self, auth_client):
        """Even an empty range has valid dates so the filter indicator must be visible."""
        resp = auth_client.get(f"/profile?date_from={self.EMPTY_FROM}&date_to={self.EMPTY_TO}")
        body = _html(resp)
        assert "Filtered" in body, "Filter indicator must appear even when no expenses match"

    def test_zero_total_displayed(self, auth_client):
        """Total spent must display as ₹0.00 when no expenses fall in the range."""
        resp = auth_client.get(f"/profile?date_from={self.EMPTY_FROM}&date_to={self.EMPTY_TO}")
        body = _html(resp)
        assert "₹0.00" in body, "Zero total must be shown for an empty date range"

    def test_date_inputs_prepopulated_even_when_empty(self, auth_client):
        """Date inputs must still be pre-populated with the (matching) empty-range values."""
        resp = auth_client.get(f"/profile?date_from={self.EMPTY_FROM}&date_to={self.EMPTY_TO}")
        body = _html(resp)
        assert self.EMPTY_FROM in body
        assert self.EMPTY_TO in body


# ---------------------------------------------------------------------------
# Unit tests — get_summary_stats with date filters
# ---------------------------------------------------------------------------

class TestGetSummaryStatsDateFilter:
    def test_filtered_range_count(self):
        """2026-05-01→2026-05-10 covers 4 expenses."""
        stats = get_summary_stats(SEED_USER_ID, date_from="2026-05-01", date_to="2026-05-10")
        assert stats["transaction_count"] == 4, (
            f"Expected 4 transactions in 2026-05-01→2026-05-10, got {stats['transaction_count']}"
        )

    def test_filtered_range_total(self):
        """2026-05-01→2026-05-10: 4500 + 850 + 320 + 1200 = 6870.00."""
        stats = get_summary_stats(SEED_USER_ID, date_from="2026-05-01", date_to="2026-05-10")
        assert stats["total_spent"] == "₹6,870.00", (
            f"Expected ₹6,870.00 for range 2026-05-01→2026-05-10, got {stats['total_spent']}"
        )

    def test_filtered_range_top_category(self):
        """In 2026-05-01→2026-05-10, Bills (4500) is the top category."""
        stats = get_summary_stats(SEED_USER_ID, date_from="2026-05-01", date_to="2026-05-10")
        assert stats["top_category"] == "Bills"

    def test_later_range_top_category(self):
        """In 2026-05-14→2026-05-21, Shopping (2300) is the top category."""
        stats = get_summary_stats(SEED_USER_ID, date_from="2026-05-14", date_to="2026-05-21")
        assert stats["top_category"] == "Shopping"

    def test_empty_range_zero_count(self):
        """A range with no matching expenses must return transaction_count == 0."""
        stats = get_summary_stats(SEED_USER_ID, date_from="2025-01-01", date_to="2025-01-31")
        assert stats["transaction_count"] == 0

    def test_empty_range_zero_total(self):
        """A range with no matching expenses must return total_spent == '₹0.00'."""
        stats = get_summary_stats(SEED_USER_ID, date_from="2025-01-01", date_to="2025-01-31")
        assert stats["total_spent"] == "₹0.00"

    def test_empty_range_dash_top_category(self):
        """A range with no matching expenses must return top_category == '—'."""
        stats = get_summary_stats(SEED_USER_ID, date_from="2025-01-01", date_to="2025-01-31")
        assert stats["top_category"] == "—"

    def test_no_filter_returns_all_time_count(self):
        """Calling without date args must return all 8 seed expenses."""
        stats = get_summary_stats(SEED_USER_ID)
        assert stats["transaction_count"] >= 8


# ---------------------------------------------------------------------------
# Unit tests — get_recent_transactions with date filters
# ---------------------------------------------------------------------------

class TestGetRecentTransactionsDateFilter:
    def test_filtered_range_length(self):
        """2026-05-01→2026-05-10 has exactly 4 seed expenses."""
        txns = get_recent_transactions(SEED_USER_ID, date_from="2026-05-01", date_to="2026-05-10")
        assert len(txns) == 4, f"Expected 4 transactions, got {len(txns)}"

    def test_filtered_range_newest_first(self):
        """Results must be ordered newest-first; last item in range is 2026-05-08 (Health)."""
        txns = get_recent_transactions(SEED_USER_ID, date_from="2026-05-01", date_to="2026-05-10")
        assert txns[0]["category"] == "Health", (
            "Newest transaction (2026-05-08) must be first"
        )

    def test_filtered_range_excludes_later_expenses(self):
        """Entertainment (2026-05-11) must not appear in 2026-05-01→2026-05-10."""
        txns = get_recent_transactions(SEED_USER_ID, date_from="2026-05-01", date_to="2026-05-10")
        categories = [t["category"] for t in txns]
        assert "Entertainment" not in categories

    def test_filtered_range_all_have_currency(self):
        """Every returned transaction must contain the ₹ symbol in its amount."""
        txns = get_recent_transactions(SEED_USER_ID, date_from="2026-05-01", date_to="2026-05-10")
        for t in txns:
            assert "₹" in t["amount"], f"Missing ₹ in amount: {t['amount']}"

    def test_empty_range_returns_empty_list(self):
        """A range with no matching expenses must return an empty list."""
        txns = get_recent_transactions(SEED_USER_ID, date_from="2025-01-01", date_to="2025-01-31")
        assert txns == []

    def test_no_filter_returns_all_time(self):
        """Without date args all seed transactions are returned (up to limit)."""
        txns = get_recent_transactions(SEED_USER_ID)
        assert len(txns) >= 8

    def test_single_day_filter(self):
        """date_from == date_to == 2026-05-14 must return exactly Shopping."""
        txns = get_recent_transactions(SEED_USER_ID, date_from="2026-05-14", date_to="2026-05-14")
        assert len(txns) == 1
        assert txns[0]["category"] == "Shopping"


# ---------------------------------------------------------------------------
# Unit tests — get_category_breakdown with date filters
# ---------------------------------------------------------------------------

class TestGetCategoryBreakdownDateFilter:
    def test_filtered_range_category_count(self):
        """2026-05-01→2026-05-10 covers Bills, Food, Transport, Health — 4 categories."""
        cats = get_category_breakdown(SEED_USER_ID, date_from="2026-05-01", date_to="2026-05-10")
        assert len(cats) == 4, f"Expected 4 categories, got {len(cats)}"

    def test_filtered_range_percentages_sum_to_100(self):
        """Percentages for the filtered range must sum to exactly 100."""
        cats = get_category_breakdown(SEED_USER_ID, date_from="2026-05-01", date_to="2026-05-10")
        total_pct = sum(c["pct"] for c in cats)
        assert total_pct == 100, f"Percentages must sum to 100, got {total_pct}"

    def test_filtered_range_bills_is_first(self):
        """Bills (4500) is the largest in 2026-05-01→2026-05-10 and must be first."""
        cats = get_category_breakdown(SEED_USER_ID, date_from="2026-05-01", date_to="2026-05-10")
        assert cats[0]["name"] == "Bills"

    def test_filtered_range_excludes_out_of_range_categories(self):
        """Shopping, Entertainment, Other are outside 2026-05-01→2026-05-10."""
        cats = get_category_breakdown(SEED_USER_ID, date_from="2026-05-01", date_to="2026-05-10")
        names = [c["name"] for c in cats]
        for absent in ("Shopping", "Entertainment", "Other"):
            assert absent not in names, f"{absent} must not appear in 2026-05-01→2026-05-10 breakdown"

    def test_filtered_range_amounts_contain_currency(self):
        """Each category's amount string must contain ₹."""
        cats = get_category_breakdown(SEED_USER_ID, date_from="2026-05-01", date_to="2026-05-10")
        for c in cats:
            assert "₹" in c["amount"], f"Missing ₹ in category amount: {c['amount']}"

    def test_empty_range_returns_empty_list(self):
        """A range with no matching expenses must return an empty list, not an error."""
        cats = get_category_breakdown(SEED_USER_ID, date_from="2025-01-01", date_to="2025-01-31")
        assert cats == []

    def test_no_filter_returns_all_seven_categories(self):
        """Without date args all 7 seed categories must be present."""
        cats = get_category_breakdown(SEED_USER_ID)
        assert len(cats) == 7

    def test_later_range_shopping_is_top(self):
        """In 2026-05-14→2026-05-21 Shopping (2300) must be the first category."""
        cats = get_category_breakdown(SEED_USER_ID, date_from="2026-05-14", date_to="2026-05-21")
        assert cats[0]["name"] == "Shopping"

    def test_later_range_percentages_sum_to_100(self):
        """Percentages for 2026-05-14→2026-05-21 must still sum to 100."""
        cats = get_category_breakdown(SEED_USER_ID, date_from="2026-05-14", date_to="2026-05-21")
        total_pct = sum(c["pct"] for c in cats)
        assert total_pct == 100
