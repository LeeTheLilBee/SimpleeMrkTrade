from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CSS = (
    ROOT
    / "web/static/ob/ob_atmosphere.css"
).read_text(
    encoding="utf-8"
)


def test_obux026_has_one_shared_css_only_sky_engine():
    assert "OBUX026_SHARED_OBSERVATORY_ATMOSPHERE_ENGINE" in CSS
    assert ".ob-sky {" in CSS
    assert ".ob-sky::before" in CSS
    assert ".ob-sky::after" in CSS
    assert ".ob-sky__weather" in CSS
    assert ".ob-sky__horizon" in CSS
    assert ".ob-sky__grid" in CSS


def test_obux026_retires_uniform_old_room_canvas_without_touching_components():
    assert 'body[data-ob-room] #ob-app' in CSS
    assert "background: transparent !important;" in CSS
    assert 'body[data-ob-room] #ob-app::before' in CSS
    assert 'body[data-ob-room] #ob-app::after' in CSS


def test_obux026_uses_no_external_background_assets():
    assert "url(" not in CSS


def test_obux026_respects_reduced_motion():
    assert "@media (prefers-reduced-motion: reduce)" in CSS
    assert "animation:" in CSS
    assert "none" in CSS
