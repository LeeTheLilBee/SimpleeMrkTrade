# Historical OBUX006–020 checks inspect the exact archived V16 design.
# Active Dashboard uses separate modern product and security assertions.
from pathlib import Path


JS = Path(
    "docs/historical/obux_v16_dashboard.js"
)


def test_obux008_dashboard_has_session_snapshot_change_interpreter():

    text = JS.read_text(
        encoding="utf-8"
    )

    assert (
        "sessionStorage"
        in text
    )

    assert (
        "SINCE YOU WERE HERE"
        in text
    )

    assert (
        "Here’s what changed since you were here."
        in text
    )

    assert (
        "Nothing material changed since your last Dashboard visit."
        in text
    )
