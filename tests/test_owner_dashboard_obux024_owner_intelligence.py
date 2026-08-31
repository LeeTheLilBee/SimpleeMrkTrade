from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

JS = (
    ROOT / "web/static/ob/ob_owner_dashboard.js"
).read_text(
    encoding="utf-8",
    errors="replace",
)

CONTRACT = (
    ROOT / "web/static/ob/ob_owner_dashboard_contract.js"
).read_text(
    encoding="utf-8",
    errors="replace",
)

SOULAANA = (
    ROOT / "web/static/ob/ob_owner_dashboard_soulaana.js"
).read_text(
    encoding="utf-8",
    errors="replace",
)


def test_obux024_owner_attention_is_prioritized_not_proof_wall():
    for marker in [
        "WHAT NEEDS YOU",
        "Only the top three.",
        "No giant queue.",
        "More owner intelligence",
    ]:
        assert marker in JS

    assert "ownerAttention" in CONTRACT

    assert (
        ".slice(\n              0,\n              3"
        in JS
    )


def test_obux024_today_edge_is_the_primary_owner_research_layer():
    for marker in [
        "TODAY’S EDGE",
        "NOW",
        "WATCH",
        "NOT YET",
        "Open analysis",
        "OPTIONS FIRST · RESEARCH ONLY",
    ]:
        assert marker in JS


def test_obux024_readiness_trust_beta_are_progressively_disclosed():
    for marker in [
        "MANUAL LIVE READINESS",
        "SYSTEM TRUST",
        "PRIVATE BETA",
        "More owner intelligence",
    ]:
        assert marker in JS


def test_obux024_owner_learning_and_change_claims_fail_closed():
    for marker in [
        "No verified owner-change history yet",
        "No verified cross-lane pattern yet",
        "may_claim_change_history",
        "may_claim_cross_lane_performance_patterns",
    ]:
        assert marker in CONTRACT

    assert "what_changed" in SOULAANA
    assert "what_im_learning" in SOULAANA


def test_obux024_raw_evidence_is_progressively_disclosed():
    assert "<details" in JS
    assert "Show me why" in JS
    assert "source_state" in JS
    assert "interpretation_state" in JS
    assert "boundaries" in JS
