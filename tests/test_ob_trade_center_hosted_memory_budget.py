from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / "web/templates/trade_center.html").read_text(encoding="utf-8")
SCRIPT = (ROOT / "web/static/ob/ob_trade_center.js").read_text(encoding="utf-8")


def _scripts():
    return re.findall(r'<script[^>]+src="([^"]+)"', TEMPLATE)


def test_trade_center_hosted_script_budget_is_bounded():
    scripts = _scripts()
    assert len(scripts) <= 8
    assert any("ob_engine_feed_adapter.js" in item for item in scripts)
    assert any("ob_trade_center_modes.js" in item for item in scripts)
    assert any("ob_trade_center.js" in item for item in scripts)
    assert any("ob_nav_shell.js" in item for item in scripts)
    assert "/static/ob/ob_session_state.js" in scripts
    assert "/static/ob/ob_global_session_shell.js" in scripts


def test_trade_center_does_not_boot_historical_proof_or_rehearsal_runtime():
    assert "obtc-proof-compatibility" not in TEMPLATE
    assert "tradeCenterMount" not in TEMPLATE
    for forbidden in (
        "ob_private_beta_",
        "ob_owner_rehearsal_",
        "ob_rehearsal_",
        "ob_practice_",
        "ob_owner_practice_",
        "ob_manual_live_",
        "ob_beta_readiness",
        "ob_engine_feed_expansion",
        "ob_engine_feed_diagnostics",
        "ob_engine_trust_labels",
        "ob_engine_room_mapping",
        "ob_owner_source_audit",
    ):
        assert forbidden not in TEMPLATE


def test_trade_center_uses_one_canonical_market_feed_and_reacts_to_updates():
    assert "ob_engine_feed_adapter.js" in TEMPLATE
    assert SCRIPT.count("obEngineFeedAdapterUpdated") == 1
    assert 'window.addEventListener(\n      "obEngineFeedAdapterUpdated",\n      syncCanonicalProjection' in SCRIPT
    assert "function syncCanonicalProjection()" in SCRIPT
    assert "state.positions =" in SCRIPT
    assert "state.candidates =" in SCRIPT
    assert "contractsForSymbol(" in SCRIPT


def test_trade_center_template_has_no_legacy_json_fetch_storm_sources():
    # The canonical room must not directly reference the retired proof endpoints.
    for endpoint_fragment in (
        "private-beta-",
        "manual-live-",
        "owner-rehearsal",
        "practice-review",
        "engine-feed-expanded",
        "engine-room-mapping",
        "owner-source-audit",
    ):
        assert endpoint_fragment not in TEMPLATE
