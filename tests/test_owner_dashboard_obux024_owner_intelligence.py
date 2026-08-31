from pathlib import Path
import re


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


def compact(value):
    return re.sub(
        r"\s+",
        "",
        value,
    )


def test_obux024_owner_attention_is_prioritized_not_proof_wall():
    assert "WHAT NEEDS YOU" in JS

    assert "Only the top three." in JS

    assert "No giant queue." in JS

    assert (
        "Lower-priority owner intelligence stays collapsed."
        in JS
    )

    assert "ownerAttention" in CONTRACT

    source = compact(
        CONTRACT
    )

    assert 'priority:"high"' in source

    assert 'priority:"medium"' in source


def test_obux024_readiness_trust_beta_and_lessons_are_progressively_translated():
    for marker in [
        "MANUAL LIVE READINESS",
        "SYSTEM TRUST",
        "PRIVATE BETA",
        "WHAT I'M LEARNING",
        "SINCE YOU WERE HERE",
        "More owner intelligence",
    ]:
        assert marker in JS


def test_obux024_raw_evidence_is_progressively_disclosed():
    assert "<details" in JS

    assert "Show me why" in JS

    assert "source_state" in JS

    assert "interpretation_state" in JS

    assert "boundaries" in JS


def test_obux024_unverified_history_and_patterns_fail_closed():
    assert (
        "No verified owner-change history yet"
        in CONTRACT
    )

    assert (
        "No verified cross-lane pattern yet"
        in CONTRACT
    )

    assert (
        "may_claim_change_history"
        in CONTRACT
    )

    assert (
        "may_claim_cross_lane_performance_patterns"
        in CONTRACT
    )
