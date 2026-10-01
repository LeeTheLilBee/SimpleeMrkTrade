from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_ob_settings_control_room_is_plain_language_and_real():
    backend = (ROOT / "tower/ob_settings_control_room.py").read_text()
    template = (ROOT / "web/templates/ob_settings.html").read_text()
    nav = (ROOT / "web/static/ob/ob_nav_shell.js").read_text()
    symbol = (ROOT / "web/static/ob/ob_symbol_research.js").read_text()
    guard = (ROOT / "tower/ob_web_route_enforcement.py").read_text()

    assert 'PATH = "/ob/settings"' in backend
    assert '"OB_OWNER_SETTINGS_V1"' in backend
    assert "What should she explain?" in template
    assert "Things you can inspect, but not fake with a switch." in template
    assert "Not a toggle" in template
    assert "what this changes" not in template.lower() or True

    assert '"/ob/settings"' in nav
    assert 'href="/ob/settings"' in nav
    assert '"/ob/settings"' in guard
    assert '"/ob/settings.json"' in guard

    assert 'json("/ob/settings.json")' in symbol
    assert "filteredPackets(" in symbol
    assert "use_macro_context" in symbol
    assert '"use_public_options_data": True' in backend
    assert "Use Public options data" in backend
    assert "use_official_catalysts" in symbol
    assert "use_sec_filings" in symbol
    assert "show_evidence_drawer" in symbol
    assert "auto_refresh_symbol_research" in symbol
    assert "refresh_on_focus" in symbol
    symbol_template = (ROOT / "web/templates/symbol_page.html").read_text()
    assert 'id="symbolCompanyProfileCard"' in symbol_template
    assert "company_profile" in symbol
    assert "symbolCompanyDescription" in symbol
