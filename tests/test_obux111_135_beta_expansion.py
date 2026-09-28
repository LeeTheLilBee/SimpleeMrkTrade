"""OBUX111–135 active-source integration tests, not proof of authenticated hosted owner acceptance."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def read(path): return (ROOT/path).read_text(encoding="utf-8")
CONTRACT=read("web/static/ob/ob_beta_intelligence_contract.js")
EXPERIENCE=read("web/static/ob/ob_beta_experience.js")
RESEARCH=read("web/static/ob/ob_beta_research.js")
NOTICES=read("web/static/ob/ob_notifications_settings.js")
CSS=read("web/static/ob/ob_beta_expansion.css")
ROOMS=("dashboard","review_center","trade_center","owner_console","market_map",
       "symbol_page","owner_dashboard")


def test_each_room_has_shared_source_projection_and_no_seventh_room_route():
    for room in ROOMS:
        html=read(f"web/templates/{room}.html")
        assert "ob_beta_expansion.css" in html,room
        for script in ("ob_beta_intelligence_contract.js","ob_beta_research.js",
                       "ob_beta_experience.js"):
            assert script in html, (room,script)
        assert html.index("ob_beta_intelligence_contract.js") < html.index("ob_beta_research.js")
        assert html.index("ob_beta_research.js") < html.index("ob_beta_experience.js")
        assert html.index("ob_session_state.js") < html.index("ob_beta_research.js")
    for room in ("dashboard","review_center","trade_center","owner_console"):
        assert 'id="obBetaFeatureMount"' in read(f"web/templates/{room}.html")


def test_no_hardcoded_demo_market_alerts_remain_in_shared_notification_drawer():
    for value in ("Manual Live candidate ready", "MU CALL", "sector-crowding",
                  "Semiconductors are bright", "review-receipt"):
        assert value not in NOTICES
    assert "refreshNotifications()" in NOTICES
    assert "OBBetaExperience" in NOTICES
    assert "sessionStorage" in NOTICES
    assert "Safety hold" in NOTICES


def test_living_intelligence_defaults_to_source_truth_and_safety_hold():
    for item in ("display_eligible === true","current_eligible === true",
                 'status === "fresh"', "sourceRef(source)",
                 "reviewRows(", 'r.loaded === true', "qualified:supported",
                 "synthetic_market_fallback:false", "broker_api:false",
                 "capital_movement:false", "manual_live_grant:false",
                 "durable_archive:false"):
        assert item in CONTRACT
    for prohibited in ("window.fetch(", "fetch(", "placeOrder(", "submitOrder(",
                       "buying_power", "autoExecute("):
        assert prohibited not in CONTRACT
    assert 'dismissible:false' in CONTRACT
    assert "source-only" in EXPERIENCE or "source-bound" in EXPERIENCE


def test_session_only_research_is_explicit_and_can_be_cleared():
    for fragment in ("sessionStorage", "sessionId", "ob:session-cleared",
                     "schema:1", "is_official:false", "is_broker_receipt:false",
                     "is_backtest:false", "MAXIMUM", "createObjectURL",
                     "URL.revokeObjectURL", "data-obx-delete", "data-obx-compare"):
        if fragment == "MAXIMUM":
            assert "Maximum 15" in RESEARCH
        else:
            assert fragment in RESEARCH
    assert "localStorage.setItem(KEY" not in RESEARCH
    assert "broker.submit(" not in RESEARCH
    assert "fetch(" not in RESEARCH
    assert "OB-RESEARCH-SHELF-EXPORT-V1" in RESEARCH


def test_accessibility_and_privacy_guardrails_are_not_decorative():
    for item in ('role="dialog"', 'aria-modal="true"', "Escape",
                 "focus()", "data-obx-close", "data-obx-pref",
                 "prefers-reduced-motion", "forced-colors"):
        assert item in (EXPERIENCE+RESEARCH+CSS)
    assert "ob-entry-pending" in EXPERIENCE
    assert "ob:arrival-complete" in EXPERIENCE
    assert "data-obx-focus-toggle" in EXPERIENCE
    assert "quiet_cannot_suppress_safety:true" in EXPERIENCE
    assert "window.OBBetaExperience" not in EXPERIENCE or "global.OBBetaExperience" in EXPERIENCE
