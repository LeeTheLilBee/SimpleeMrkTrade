from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = (
    ROOT / "web/static/ob/ob_owner_dashboard.js"
).read_text(encoding="utf-8")
CONTRACT = (
    ROOT / "web/static/ob/ob_owner_dashboard_contract.js"
).read_text(encoding="utf-8")


def test_obux024_owner_attention_is_prioritized_not_proof_wall():
    assert "OWNER ATTENTION" in JS
    assert "What actually deserves Solice." in JS
    assert "No giant queue. No proof wall." in JS
    assert "ownerAttention" in CONTRACT
    assert 'priority: "high"' in CONTRACT
    assert 'priority: "medium"' in CONTRACT


def test_obux024_readiness_trust_beta_and_lessons_are_translated():
    assert "MANUAL LIVE READINESS" in JS
    assert "SYSTEM TRUST" in JS
    assert "PRIVATE BETA" in JS
    assert "WHAT I'M LEARNING" in JS
    assert "SINCE YOU WERE HERE" in JS
    assert "WHAT CAN WAIT" in JS


def test_obux024_raw_evidence_is_progressively_disclosed():
    assert "<details" in JS
    assert "Show me why" in JS
    assert "source_state" in JS
    assert "interpretation_state" in JS
    assert "boundaries" in JS


def test_obux024_unverified_history_and_patterns_fail_closed():
    assert "No verified owner-change history yet" in CONTRACT
    assert "Cross-mission performance patterns are not verified yet" in CONTRACT
    assert "may_claim_change_history" in CONTRACT
    assert "may_claim_cross_mission_performance_patterns" in CONTRACT
