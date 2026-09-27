"""OBBETA006–010: operator-confidence UI cannot claim Tower/provider live authority."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (ROOT / "web/static/ob/ob_owner_dashboard_contract.js").read_text(encoding="utf-8")
OWNER_UI = (ROOT / "web/static/ob/ob_owner_dashboard.js").read_text(encoding="utf-8")
OWNER_HTML = (ROOT / "web/templates/owner_dashboard.html").read_text(encoding="utf-8")
USER_HTML = (ROOT / "web/templates/dashboard.html").read_text(encoding="utf-8")
BETA = (ROOT / "web/static/ob/ob_beta_readiness.js").read_text(encoding="utf-8")
NAMESPACE = (ROOT / "web/ob_manual_live_namespace_cross_check.py").read_text(encoding="utf-8")
READY = CONTRACT.split("const readinessSummary = () => {", 1)[1].split("const betaSummary", 1)[0]


def test_obbeta006_operator_score_is_never_labeled_as_live_clearance():
    assert '"Owner rehearsal evidence · Real Manual Live HOLD"' in READY
    assert 'scorecard.readiness_label' not in READY
    assert '"operator_practice_only_not_tower_or_provider"' in READY
    assert 'score_is_practice_only:' in READY
    assert 'source.verified === true' in READY


def test_obbeta007_external_authority_cannot_be_inferred_from_endpoint_presence():
    for flag in (
        "tower_owner_clearance_verified:",
        "authenticated_broker_source_verified:",
        "production_manual_live_permission:",
        "real_manual_live_ready:",
        "broker_order_submission_enabled:",
        "automatic_contract_selection_enabled:",
        "auto_execution_enabled:",
    ):
        assert flag in READY
        assert READY.split(flag, 1)[1].lstrip().startswith("false")
    assert "live_auto_locked:" in READY
    assert READY.split("live_auto_locked:", 1)[1].lstrip().startswith("true")


def test_obbeta008_attention_is_practice_only_not_production_authorization():
    assert "Owner rehearsal checklist needs review" in CONTRACT
    assert "operator practice checkpoint, not live authorization" in CONTRACT
    assert '"Manual Live readiness needs review"' not in CONTRACT


def test_obbeta009_owner_card_exposes_unresolved_external_gate():
    assert '"OWNER REHEARSAL · LIVE HOLD"' in OWNER_UI
    assert '"External Tower/provider gates pending"' in OWNER_UI
    assert '" practice blocker"' in OWNER_UI
    assert '"MANUAL LIVE READINESS"' not in OWNER_UI


def test_obbeta010_preserve_accepted_tower_source_and_beta_boundaries():
    assert 'data-ob-owner-dashboard-role="owner-only-active"' in OWNER_HTML
    assert 'data-ob-dashboard-role="normal"' in USER_HTML
    assert "Live Auto Locked" in OWNER_HTML and "Live Auto Locked" in USER_HTML
    assert "Tester beta is Survey/Paper only" in BETA
    assert 'source_claim_authenticated_to_ob": False' in NAMESPACE
    assert 'live_manual_mode_unlocked=False' in NAMESPACE
