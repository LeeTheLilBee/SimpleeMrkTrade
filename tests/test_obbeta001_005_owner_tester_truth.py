"""OBBETA001–005: public-facing beta copy must not turn source evidence into live permission."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BETA = (ROOT / "web/static/ob/ob_beta_readiness.js").read_text(encoding="utf-8")
DASH = (ROOT / "web/templates/dashboard.html").read_text(encoding="utf-8")
OWNER = (ROOT / "web/templates/owner_dashboard.html").read_text(encoding="utf-8")
NAMESPACE = (ROOT / "web/ob_manual_live_namespace_cross_check.py").read_text(encoding="utf-8")


def test_obbeta001_tester_mode_is_survey_and_paper_only():
    assert 'mode: "Survey / Paper · owner rehearsal only"' in BETA
    assert "Tester beta is Survey/Paper only" in BETA
    assert "Tester beta is Survey/Paper only, without Manual Live" in BETA
    assert 'mode: "Paper / Manual Live Level 1"' not in BETA


def test_obbeta002_manual_live_rehearsal_is_owner_only_and_not_broker_permission():
    assert 'label: "Owner Rehearsal SOP"' in BETA
    assert "Only the owner walks through the Manual Live L1 practice checklist" in BETA
    assert "No real order follows from a beta checklist" in BETA
    assert "No beta session authorizes an owner or tester to place a real broker order" in BETA
    assert "Tester manually enters the trade at broker" not in BETA
    assert "Approve for manual placement" not in BETA
    assert "Tester confirms filled, submitted" not in BETA


def test_obbeta003_source_namespace_does_not_silently_clear_tower_or_broker():
    assert "A signed OB account namespace is not owner clearance" in BETA
    assert "Real Manual Live remains HOLD" in BETA or "real Manual Live remains HOLD" in BETA
    assert 'source_claim_authenticated_to_ob": False' in NAMESPACE
    assert '"trusted_tower_owner_handoff_verified=False"' in NAMESPACE
    assert '"live_manual_mode_unlocked=False"' in NAMESPACE
    assert '"direct_buybox_access=False"' in NAMESPACE


def test_obbeta004_practice_receipts_cannot_claim_real_broker_fills():
    assert "simulated/rehearsal labels, not authenticated submitted or filled" in BETA
    assert "source-classified, separate from real provider-authenticated outcomes" in BETA
    assert "never as independently reconciled broker fills" in BETA


def test_obbeta005_preserve_normal_vs_owner_room_boundary():
    assert 'data-ob-dashboard-role="normal"' in DASH
    assert 'data-ob-owner-capital-lanes="true"' in OWNER
    assert "Live Auto Locked" in DASH and "Live Auto Locked" in OWNER
    assert "Tester beta is Survey/Paper only" in BETA
