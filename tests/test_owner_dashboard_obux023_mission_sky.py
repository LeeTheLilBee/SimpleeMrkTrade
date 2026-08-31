from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

CONTRACT = (
    ROOT / "web/static/ob/ob_owner_dashboard_contract.js"
).read_text(
    encoding="utf-8",
    errors="replace",
)

SURFACE = (
    ROOT / "web/static/ob/ob_owner_dashboard.js"
).read_text(
    encoding="utf-8",
    errors="replace",
)

CSS = (
    ROOT / "web/static/ob/ob_owner_dashboard.css"
).read_text(
    encoding="utf-8",
    errors="replace",
)


def compact(value):
    return re.sub(
        r"\s+",
        "",
        value,
    )


def test_obux023_six_owner_capital_lanes_are_defined():
    source = compact(
        CONTRACT
    )

    for marker in [
        'lane_id:"trust"',
        'lane_id:"personal"',
        'lane_id:"simplee_world"',
        'lane_id:"atm"',
        'lane_id:"apartment"',
        'lane_id:"proof_demo"',
    ]:
        assert marker in source


def test_obux023_capital_lanes_are_real_owner_surface():
    for marker in [
        "CAPITAL LANES",
        "CURRENT CAPITAL LANE",
        "One lane at a time.",
        "data-capital-lane-open",
        "Capital truth unavailable",
        "No verified alert",
        "Enter this lane",
    ]:
        assert marker in SURFACE


def test_obux023_capital_lane_layout_is_focused_not_table_wall():
    for marker in [
        ".ob-capital-lanes-section",
        ".ob-capital-focus",
        ".ob-capital-lane-nodes",
        ".ob-capital-lane-node",
        ".ob-capital-lane-star",
        ".ob-capital-drawer",
    ]:
        assert marker in CSS

    assert (
        "display: grid"
        in CSS
    )

    assert (
        "radial-gradient"
        in CSS
    )
