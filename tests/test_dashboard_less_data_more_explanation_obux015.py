from pathlib import Path


JS = Path(
    "web/static/ob/ob_dashboard.js"
)


def test_obux015_raw_financial_metrics_are_not_primary_surface():

    text = JS.read_text(
        encoding="utf-8"
    )

    assert (
        "raw_financial_metrics_primary_surface: false"
        in text
    )

    evidence_index = text.index(
        'id="obuxDashboardEvidence"'
    )

    buying_power_index = text.index(
        '"Buying power"',
        evidence_index,
    )

    account_value_index = text.index(
        '"Account value"',
        evidence_index,
    )

    open_pnl_index = text.index(
        '"Open P&L"',
        evidence_index,
    )

    assert buying_power_index > evidence_index
    assert account_value_index > evidence_index
    assert open_pnl_index > evidence_index


def test_obux015_show_me_why_remains_progressive_disclosure():

    text = JS.read_text(
        encoding="utf-8"
    )

    assert (
        "<details"
        in text
    )

    assert (
        "Show me why"
        in text
    )

    assert (
        '<details\n          id="obuxDashboardEvidence"'
        in text
    )

    assert (
        '<details\n          id="obuxDashboardEvidence"\n          open'
        not in text
    )


def test_obux015_source_truth_guards_remain():

    text = JS.read_text(
        encoding="utf-8"
    )

    assert (
        "static_market_fallback_actionable: false"
        in text
    )

    assert (
        "static_market_fallback_confirmed_position: false"
        in text
    )

    assert (
        '["MU", "AMD", "INTC"].includes'
        not in text
    )

    assert (
        "sample_signals"
        not in text
    )
