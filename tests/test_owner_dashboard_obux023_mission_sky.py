from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (
    ROOT / "web/static/ob/ob_owner_dashboard_contract.js"
).read_text(encoding="utf-8")
SURFACE = (
    ROOT / "web/static/ob/ob_owner_dashboard.js"
).read_text(encoding="utf-8")
CSS = (
    ROOT / "web/static/ob/ob_owner_dashboard.css"
).read_text(encoding="utf-8")


def test_obux023_six_owner_missions_are_defined():
    for marker in [
        'mission_id: "trust"',
        'mission_id: "personal"',
        'mission_id: "simplee_world"',
        'mission_id: "atm"',
        'mission_id: "apartment"',
        'mission_id: "proof_demo"',
    ]:
        assert marker in CONTRACT


def test_obux023_mission_sky_is_a_real_owner_surface():
    assert "MISSION SKY" in SURFACE
    assert 'data-mission-id=' in SURFACE
    assert "Your capital has different jobs." in SURFACE
    assert "Capital progress not verified" in SURFACE
    assert "No verified attention flag" in SURFACE


def test_obux023_visual_layout_is_constellation_like_not_table_wall():
    assert ".ob-owner-mission-grid" in CSS
    assert "repeat(12, minmax(0, 1fr))" in CSS
    assert ".ob-owner-mission-orbit" in CSS
    assert ".ob-owner-mission-star" in CSS
    assert ".ob-owner-observatory" in CSS
