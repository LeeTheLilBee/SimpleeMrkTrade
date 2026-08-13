from pathlib import Path


JS = Path(
    "web/static/ob/ob_dashboard.js"
)


def source():
    return JS.read_text(
        encoding="utf-8"
    )


def test_obux006_soulaana_leads_real_dashboard_renderer():

    text = source()

    assert (
        "SOULAANA · RIGHT NOW"
        in text
    )

    assert (
        "WHAT THIS MEANS"
        in text
    )

    assert (
        "WHY IT MATTERS"
        in text
    )

    assert (
        "WHAT NEEDS YOU"
        in text
    )

    assert (
        "WHAT CAN WAIT"
        in text
    )


def test_obux006_no_action_is_first_class_dashboard_state():

    text = source()

    assert (
        "Nothing needs you right now."
        in text
    )

    assert (
        "no_action_needed"
        in text
    )
