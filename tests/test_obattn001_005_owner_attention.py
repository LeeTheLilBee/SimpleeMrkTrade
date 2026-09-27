from dataclasses import replace
from hashlib import sha256

import pytest

from test_obguard001_005_distinct_source_adverse_review import (
    chain, signals, guard_entry, issue, decision,
)
from web.ob_adverse_guard_review import build_guard_review
from web.ob_soulaana_explanations import build_soulaana_explanation
from web.ob_owner_attention import (
    SCHEMA_VERSION, PRIORITY_ORDER, build_owner_attention,
    verify_owner_attention, attention_reference, attention_contract,
)


def make_queue(*, alert=None, with_intent=False, tmp_path=None, guard=None, evidence=None):
    rec, args = chain(alert=alert, with_intent=with_intent, tmp_path=tmp_path)
    explanation = build_soulaana_explanation(
        rec, **args, guard=guard, guard_evidence=evidence,
    )
    q = build_owner_attention(
        explanation, rec, **args, guard=guard, guard_evidence=evidence,
    )
    return rec, args, explanation, q


def test_obattn001_missing_source_becomes_hold_not_false_green():
    rec, args, explanation, q = make_queue()
    assert q.authority == SCHEMA_VERSION
    assert q.source_recommendation_state == "EVIDENCE_PENDING"
    assert q.top_priority == "P2_EVIDENCE_HOLD"
    assert len(q.items) == 1
    assert "OWNER_FIT_SOURCE_NOT_PROVIDED" in q.items[0].reason_codes
    assert q.owner_action_is_manual_review_only is True
    assert not q.live_notification_dispatched and not q.broker_submission
    assert verify_owner_attention(q, explanation, rec, **args)


def test_obattn002_canonical_block_is_first_and_never_dismissed():
    rec, args, explanation, q = make_queue(alert=signals(overreach=True))
    assert rec.state == "BLOCKED"
    assert q.top_priority == "P0_CANONICAL_BLOCK"
    assert q.items[0].priority == "P0_CANONICAL_BLOCK"
    assert "DANGER:OVERREACH" in q.items[0].reason_codes
    assert all(not x.dismisses_safety_block and not x.actionable_execution for x in q.items)
    assert not q.safety_override and not q.trading_mode_change
    bad = replace(q, top_priority="P3_OWNER_REVIEW")
    assert not verify_owner_attention(bad, explanation, rec, **args)


def test_obattn003_review_ready_is_not_order_permission(tmp_path):
    rec, args, explanation, q = make_queue(with_intent=True, tmp_path=tmp_path)
    assert rec.state == "OWNER_REVIEW_READY"
    assert q.top_priority == "P3_OWNER_REVIEW"
    assert q.items[0].task_code == "OWNER_MAY_INSPECT_REVIEW_PACKET"
    assert not q.external_broker_events_verified
    assert not q.broker_submission and not q.capital_movement
    assert not q.live_notification_dispatched


def test_obattn004_repeated_distinct_source_guard_is_prioritized_without_actuator(tmp_path):
    rec, args = chain(with_intent=True, tmp_path=tmp_path)
    i1 = issue("NEGATIVE_DIVE")
    i2 = issue(
        "NEGATIVE_DIVE", issue_id="OWNER-ISSUE-SECOND",
        source_ref="owner-source-r2", source_revision="r2",
        source_payload_hash=sha256(b"source-distinct-r2").hexdigest(),
    )
    d1 = decision("DEFER")
    d2 = decision(
        "REQUEST_MORE_EVIDENCE", decision_id="OWNER-DECISION-SECOND",
        recorded_at_utc="2026-09-24T15:05:00+00:00",
    )
    evidence = (
        guard_entry(rec, args, owner=d1, issues=(i1,)),
        guard_entry(rec, args, owner=d2, issues=(i2,)),
    )
    guard = build_guard_review(evidence)
    explanation = build_soulaana_explanation(
        rec, **args, guard=guard, guard_evidence=evidence,
    )
    q = build_owner_attention(
        explanation, rec, **args, guard=guard, guard_evidence=evidence,
    )
    assert q.top_priority == "P1_REPEATED_SOURCE_GUARD"
    assert tuple(item.priority for item in q.items) == (
        "P1_REPEATED_SOURCE_GUARD", "P3_OWNER_REVIEW",
    )
    assert q.items[0].reason_codes == ("NEGATIVE_DIVE",)
    assert "not authenticated market events" in q.items[0].text
    assert not q.live_notification_dispatched
    assert not q.broker_submission and not q.source_truth_mutated
    assert verify_owner_attention(
        q, explanation, rec, **args, guard=guard, guard_evidence=evidence,
    )
    tampered_guard = replace(guard, integrity_hash="0"*64)
    with pytest.raises(ValueError, match="OBSOUL"):
        build_owner_attention(
            explanation, rec, **args, guard=tampered_guard, guard_evidence=evidence,
        )
    with pytest.raises(ValueError, match="OBSOUL"):
        build_owner_attention(explanation, rec, **args)
    return q


def test_obattn004_source_block_remains_above_source_guard(tmp_path):
    rec, args = chain(with_intent=True, tmp_path=tmp_path, alert=signals(overreach=True))
    i1 = issue("NEGATIVE_DIVE")
    i2 = issue(
        "NEGATIVE_DIVE", issue_id="OWNER-ISSUE-SECOND",
        source_ref="owner-source-r2", source_revision="r2",
        source_payload_hash=sha256(b"source-distinct-r2").hexdigest(),
    )
    evidence = (
        guard_entry(rec, args, owner=decision("DEFER"), issues=(i1,)),
        guard_entry(rec, args, owner=decision(
            "REQUEST_MORE_EVIDENCE", decision_id="OWNER-DECISION-SECOND",
            recorded_at_utc="2026-09-24T15:05:00+00:00",
        ), issues=(i2,)),
    )
    guard = build_guard_review(evidence)
    exp = build_soulaana_explanation(rec, **args, guard=guard, guard_evidence=evidence)
    queue = build_owner_attention(exp, rec, **args, guard=guard, guard_evidence=evidence)
    assert queue.top_priority == "P0_CANONICAL_BLOCK"
    assert tuple(item.priority for item in queue.items) == (
        "P0_CANONICAL_BLOCK", "P1_REPEATED_SOURCE_GUARD",
    )


def test_obattn005_lineage_proof_redaction_and_nonactuation():
    rec, args, explanation, q = make_queue()
    assert q == build_owner_attention(explanation, rec, **args)
    ref = attention_reference(q, explanation, rec, **args)
    assert ref["amounts_exposed"] is False
    assert ref["tower_authorization_required"] is True
    assert "cash" not in str(ref).lower()
    assert "equity" not in str(ref).lower()
    assert not verify_owner_attention(
        replace(q, live_notification_dispatched=True), explanation, rec, **args,
    )
    assert not verify_owner_attention(
        replace(q, items=(replace(q.items[0], actionable_execution=True),)),
        explanation, rec, **args,
    )
    with pytest.raises(ValueError, match="fully verified source"):
        attention_reference(replace(q, integrity_hash="0"*64), explanation, rec, **args)
    c = attention_contract()
    assert tuple(PRIORITY_ORDER) == (
        "P0_CANONICAL_BLOCK", "P1_REPEATED_SOURCE_GUARD",
        "P2_EVIDENCE_HOLD", "P3_OWNER_REVIEW",
    )
    assert c["canonical_state_never_overridden"]
    assert c["repeated_guard_requires_distinct_source_payloads"]
    assert c["direct_buybox_access"] is False
    for flag in (
        "live_notification_dispatch", "acknowledgement_or_dismissal_mutates_safety",
        "order_authority", "broker_submission", "capital_movement",
        "trading_mode_change", "manual_live_unlock",
        "hybrid_unlock", "automated_unlock",
    ):
        assert c[flag] is False
