from dataclasses import replace
from hashlib import sha256

import pytest

from test_obguard001_005_distinct_source_adverse_review import (
    chain, signals, guard_entry, issue, decision,
)
from web.ob_adverse_guard_review import build_guard_review
from web.ob_soulaana_explanations import (
    SCHEMA_VERSION, build_soulaana_explanation, verify_soulaana_explanation,
    soulaana_explanation_reference, soulaana_contract,
)


def test_obsoul001_source_pending_explained_without_invented_permission():
    rec, args = chain()
    result = build_soulaana_explanation(rec, **args)
    assert result.authority == SCHEMA_VERSION
    assert result.source_state == "EVIDENCE_PENDING"
    assert result.cards[0].source_code == rec.state
    assert any(c.source_code == "OWNER_FIT_SOURCE_NOT_PROVIDED" for c in result.cards)
    assert all(c.observed_fact_only for c in result.cards)
    assert result.source_is_historical_simulation is True
    assert result.source_claims_broker_authenticated is False
    assert verify_soulaana_explanation(result, rec, **args)


def test_obsoul002_complete_canonical_review_explanation_does_not_authorize_order(tmp_path):
    rec, args = chain(with_intent=True, tmp_path=tmp_path)
    result = build_soulaana_explanation(rec, **args)
    assert result.source_state == "OWNER_REVIEW_READY"
    assert result.selected_candidate_id == rec.selected_candidate_id
    assert any(c.kind == "OWNER_SELECTED_CANDIDATE" for c in result.cards)
    assert any("not a live quote or order" in c.text for c in result.cards)
    assert not result.trade_intent_created and not result.broker_submission
    assert not result.safety_decision_overridden and not result.capital_movement
    ref = soulaana_explanation_reference(result, rec, **args)
    assert ref["amounts_exposed"] is False
    assert ref["tower_authorization_required"] is True


def test_obsoul003_blocked_safety_cannot_be_explained_as_ready():
    rec, args = chain(alert=signals(overreach=True))
    result = build_soulaana_explanation(rec, **args)
    assert rec.state == "BLOCKED" and result.source_state == "BLOCKED"
    assert any(c.source_code == "DANGER:OVERREACH" for c in result.cards)
    assert "owner review" in result.cards[0].text
    forged = replace(result, source_state="OWNER_REVIEW_READY")
    assert not verify_soulaana_explanation(forged, rec, **args)
    with pytest.raises(ValueError, match="verified source lineage"):
        soulaana_explanation_reference(forged, rec, **args)


def test_obsoul004_optional_guard_requires_full_lineage_and_same_recommendation(tmp_path):
    rec, args = chain(with_intent=True, tmp_path=tmp_path)
    first = issue("NEGATIVE_DIVE")
    second = issue("NEGATIVE_DIVE", issue_id="ISSUE-SECOND", source_ref="issue-r2",
                   source_revision="r2",
                   source_payload_hash=sha256(b"distinct verified-as-payload-only").hexdigest())
    owner1 = decision("DEFER")
    owner2 = decision("REQUEST_MORE_EVIDENCE", decision_id="OWNER-R2",
                      recorded_at_utc="2026-09-24T15:05:00+00:00")
    evidence = (
        guard_entry(rec, args, owner=owner1, issues=(first,)),
        guard_entry(rec, args, owner=owner2, issues=(second,)),
    )
    guard = build_guard_review(evidence)
    result = build_soulaana_explanation(
        rec, **args, guard=guard, guard_evidence=evidence,
    )
    assert result.guard_id == guard.guard_id
    cards = [c for c in result.cards if c.kind == "SOURCE_GUARD_PATTERN"]
    assert len(cards) == 1
    assert "not independently authenticated market incidents" in cards[0].text
    assert verify_soulaana_explanation(
        result, rec, **args, guard=guard, guard_evidence=evidence,
    )
    with pytest.raises(ValueError, match="both receipt"):
        build_soulaana_explanation(rec, **args, guard=guard)
    with pytest.raises(ValueError, match="guard context"):
        build_soulaana_explanation(
            rec, **args, guard=replace(guard, integrity_hash="0"*64),
            guard_evidence=evidence,
        )


def test_obsoul005_tampered_source_and_outcome_escalation_fail_closed():
    rec, args = chain()
    result = build_soulaana_explanation(rec, **args)
    tampered = replace(rec, integrity_hash="0"*64)
    with pytest.raises(ValueError, match="OBREC/OBSAFE"):
        build_soulaana_explanation(tampered, **args)
    assert not verify_soulaana_explanation(
        replace(result, broker_submission=True), rec, **args,
    )
    assert not verify_soulaana_explanation(
        replace(result, cards=()), rec, **args,
    )
    c = soulaana_contract()
    assert c["canonical_state_not_overridden"] is True
    assert c["unknown_reason_codes_preserved_not_invented"] is True
    assert c["no_new_market_or_financial_truth"] is True
    assert c["direct_buybox_access"] is False
    for flag in ("numeric_return_prediction", "execution_authority",
                 "capital_movement", "broker_submission",
                 "manual_live_unlock", "hybrid_unlock", "automated_unlock"):
        assert c[flag] is False
