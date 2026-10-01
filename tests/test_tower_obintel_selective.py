"""OBINTEL source-only Tower seam: optional evidence, no fabricated hosted data."""
from pathlib import Path

from flask import Flask
from jinja2 import select_autoescape
import pytest

from engine.market_intake.research_bridge import project_research
from tower.ob_route_guard import match_ob_guard_policy

ROOT = Path(__file__).resolve().parents[1]
ROOMS = {
    "market_map": "market_map.html",
    "symbol_page": "symbol_page.html",
    "trade_center": "trade_center.html",
    "review_center": "review_center.html",
}


def test_current_hosted_rooms_keep_optional_source_partial_out_of_room_shells():
    partial = (ROOT / "web/templates/ob_research_context_partial.html").read_text()
    assert 'schema' in partial and 'OB_RESEARCH_HANDOFF_V1' in partial
    assert "may_authorize_order" in partial
    for room, name in ROOMS.items():
        html = (ROOT / "web/templates" / name).read_text()
        assert "ob_research_context.css" not in html
        assert "ob_research_context is defined" not in html
        assert "include 'ob_research_context_partial.html'" not in html
    symbol = (ROOT / "web/templates/symbol_page.html").read_text()
    assert "/static/ob/ob_symbol_research.js?v=publicoptions005" in symbol
    nav = (ROOT / "web/static/ob/ob_nav_shell.js").read_text()
    assert 'navLink(path, "/ob/trade-center", "Trade Center"' in nav
    assert 'navLink(path, "/ob/review-center", "Review Center"' in nav
    assert 'navLink(path, "/ob/data-desk", "Market Data Desk"' in nav
    assert 'TOWER_RETURN_PATH = "/tower/return/observatory"' in nav


@pytest.mark.parametrize("room", list(ROOMS))
def test_no_live_research_is_invented_without_trusted_server_envelope(room):
    app = Flask(__name__, template_folder=str(ROOT / "web/templates"))
    app.jinja_env.autoescape = select_autoescape(["html"])
    with app.app_context():
        template = app.jinja_env.get_template("ob_research_context_partial.html")
        assert "ob-research-context" not in template.render()
        for value in (
            {"schema": "OB_RESEARCH_HANDOFF_V1", "room": room,
             "context_only": False, "may_authorize_order": False,
             "may_authorize_candidate": False},
            {"schema": "OB_RESEARCH_HANDOFF_V1", "room": room,
             "context_only": True, "may_authorize_order": True,
             "may_authorize_candidate": False},
            {"schema": "OB_RESEARCH_HANDOFF_V1", "room": room,
             "context_only": True, "may_authorize_order": False,
             "may_authorize_candidate": True},
        ):
            assert "ob-research-context" not in template.render(ob_research_context=value)


def test_no_auto_registration_of_source_research_or_unmapped_corridors():
    hosted = (ROOT / "web/hosted_tower.py").read_text()
    assert "register_protected_ob_market_data_desk(app)" in hosted
    # Optional OBINTEL modules are importable source but must not register an
    # endpoint, inject demo evidence, connect a real provider, or grant an order.
    assert "research_context_adapter" not in hosted
    assert "symbol_research_snapshot" not in hosted
    for path in ("/ob/research/approve", "/ob/research/feed", "/ob/symbol/research/write"):
        assert match_ob_guard_policy(path)["match_type"] == "unmapped_default_deny"
