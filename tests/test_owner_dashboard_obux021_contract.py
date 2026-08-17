from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (
    ROOT / "web/static/ob/ob_owner_dashboard_contract.js"
).read_text(encoding="utf-8")


def test_obux021_uses_guarded_existing_owner_intelligence_endpoints():
    assert "/ob/account-experience.json" in CONTRACT
    assert "/ob/engine-feed-trust-labels.json" in CONTRACT
    assert "/ob/manual-live-operator-confidence-readiness-checkpoint.json" in CONTRACT
    assert "/ob/private-beta-launch-control.json" in CONTRACT
    assert "sourceLooksVerified" in CONTRACT
    assert "credentials: \"same-origin\"" in CONTRACT


def test_obux021_does_not_turn_policy_text_into_fake_capital_truth():
    assert "actual_capital_known: false" in CONTRACT
    assert "capital_progress_known: false" in CONTRACT
    assert "verified_snapshot: false" in CONTRACT
    assert "Policy text is not a balance" in CONTRACT
    assert "OB_OWNER_MISSION_SNAPSHOT" in CONTRACT


def test_obux021_execution_boundaries_remain_fail_closed():
    assert "broker_api_enabled: false" in CONTRACT
    assert "broker_order_submission_enabled: false" in CONTRACT
    assert "real_capital_movement_enabled: false" in CONTRACT
    assert "auto_execution_enabled: false" in CONTRACT
    assert "live_auto_locked: true" in CONTRACT
    assert "gp066_advanced: false" in CONTRACT


def test_obux021_does_not_resurrect_legacy_fake_position_logic():
    assert '["MU", "AMD", "INTC"]' not in CONTRACT
    assert "sample_signals" not in CONTRACT
    assert "static_market_fallback_actionable" not in CONTRACT
