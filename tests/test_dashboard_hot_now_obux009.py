from pathlib import Path


JS = Path(
    "web/static/ob/ob_dashboard.js"
)


def test_obux009_static_market_fallback_can_never_be_actionable():

    text = JS.read_text(
        encoding="utf-8"
    )

    assert (
        'source === "static_market_fallback"'
        in text
    )

    assert (
        "return false;"
        in text
    )

    assert (
        "static_market_fallback_actionable: false"
        in text
    )


def test_obux009_old_fake_open_position_symbol_fallback_removed():

    text = JS.read_text(
        encoding="utf-8"
    )

    assert (
        '["MU", "AMD", "INTC"].includes'
        not in text
    )

    assert (
        "static_market_fallback_confirmed_position: false"
        in text
    )


def test_obux009_hot_now_explains_not_automatically_money():

    text = JS.read_text(
        encoding="utf-8"
    )

    assert (
        "Worth your eyes — not automatically your money"
        in text
    )

    assert (
        "WHAT'S MISSING"
        in text
    )
