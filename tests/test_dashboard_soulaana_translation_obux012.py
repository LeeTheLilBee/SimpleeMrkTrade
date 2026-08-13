from pathlib import Path


JS = Path(
    "web/static/ob/ob_dashboard.js"
)


def test_obux012_soulaana_translates_account_attention_and_next_move():

    text = JS.read_text(
        encoding="utf-8"
    )

    assert (
        "YOUR ACCOUNT"
        in text
    )

    assert (
        "WHAT NEEDS YOU"
        in text
    )

    assert (
        "WHAT CHANGED"
        in text
    )

    assert (
        "WHAT CAN WAIT"
        in text
    )

    assert (
        "NEXT BEST MOVE"
        in text
    )


def test_obux012_no_action_language_still_exists():

    text = JS.read_text(
        encoding="utf-8"
    )

    assert (
        "Nothing needs you right now."
        in text
    )

    assert (
        "You can stay informed without turning information into activity."
        in text
    )
