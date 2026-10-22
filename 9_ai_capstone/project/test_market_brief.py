"""Verify It — offline smoke tests for the Morning Market Brief.

Every test here runs with no API key, no SMTP config, and no network:
the pure-Python parts of the brief (the math and the rendering) are exactly
the parts a test CAN pin down, because no model is involved.

Run (terminal in ai_capstone/, venv activated):
    pytest project/test_market_brief.py
"""

from market_brief import (
    compute_pct_change,
    get_dry_run_prices,
    render_brief_markdown,
)


def test_pct_change_basic():
    # +1% and -50%, computed by Python — never by the AI.
    assert compute_pct_change(101.0, 100.0) == 1.0
    assert compute_pct_change(50.0, 100.0) == -50.0


def test_pct_change_zero_prev_is_safe():
    # A zero previous close must not divide by zero.
    assert compute_pct_change(100.0, 0.0) == 0.0


def test_dry_run_prices_cover_every_ticker():
    # Known tickers get their canned data; unknown ones still get a row —
    # the mock never leaves a hole in the brief.
    prices = get_dry_run_prices(["AAPL", "ZZZZ"])
    assert set(prices) == {"AAPL", "ZZZZ"}
    for data in prices.values():
        assert {"last", "prev", "pct"} <= set(data)


def test_markdown_brief_has_table_and_narrative():
    prices = get_dry_run_prices(["AAPL", "NVDA"])
    brief = render_brief_markdown(prices, "A test narrative.", "A news line.")
    assert brief.startswith("# Morning Market Brief")
    assert "| AAPL |" in brief and "| NVDA |" in brief
    assert "## Narrative" in brief and "A test narrative." in brief
    assert "## In the News" in brief and "A news line." in brief


def test_markdown_brief_ships_without_news_line():
    # The grounded call may fail; the brief must still render, minus that section.
    prices = get_dry_run_prices(["AAPL"])
    brief = render_brief_markdown(prices, "A test narrative.", None)
    assert "## In the News" not in brief
    assert "## Narrative" in brief
