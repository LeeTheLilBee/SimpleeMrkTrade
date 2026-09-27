from dataclasses import replace
from hashlib import sha256

import pytest

from test_obattn001_005_owner_attention import make_queue
from test_obguard001_005_distinct_source_adverse_review import signals
from web.ob_recovery_review import (
    SCHEMA_VERSION, build_recovery_observation, build_recovery_review,
    verify_recovery_review, recovery_reference, recovery_contract,
)

AS_OF = "2026-09-24T14:30:00+00:00"


def bundle(*, alert=None, with_intent=False, tmp_path=None):
    recommendation, args, explanation, attention = make_queue(
        alert=alert, with_intent=with_intent, tmp_path=tmp_path,
    )
    return dict(
        attention=attention, explanation=explanation,
        recommendation=recommendation, **args,
        monitored_components=("MARKET_SOURCE",), as_of_utc=AS_OF,
    )


def observation(state, revision, at, *, component="MARKET_SOURCE", account="trust",
                expires="2026-09-24T16:00:00+00:00", received=None,
                source="owner-source-feed"):
    return build_recovery_observation(
        account_key=account, component=component,
        source_ref=source, source_revision=revision,
        source_payload_hash=sha256((component + revision + state).encode()).hexdigest(),
        observed_at_utc=at, received_at_utc=received or at,
        expires_at_utc=expires, source_state=state,
    )


def test_obres001_missing_source_stays_reconciliation_required():
    args = bundle()
    result = build_recovery_review(**args)
    assert result.authority == SCHEMA_VERSION
    assert result.state == "SOURCE_RECONCILIATION_REQUIRED"
    assert result.components[0].source_state == "MISSING"
    assert result.components[0].requires_canonical_revalidation
    assert not result.owner_or_provider_authorization_granted
    assert verify_recovery_review(result, **args)


def test_obres002_outage_and_conflict_hold_no_provider_failover():
    args = bundle()
    fail = observation("OUTAGE", "r1", "2026-09-24T14:01:00+00:00")
    for value in (fail, observation("CONFLICT", "r1", "2026-09-24T14:01:00+00:00")):
        output = build_recovery_review(**args, observations=(value,))
        assert output.state == "OUTAGE_OR_CONFLICT_HOLD"
        assert output.components[0].source_state == value.source_state
        assert not output.automatic_failover and not output.automatic_restart
        assert not output.kill_switch_cleared
    assert args["attention"].source_recommendation_state == "EVIDENCE_PENDING"


def test_obres002_stale_unknown_and_expired_not_misread_as_current():
    args = bundle()
    stale = observation("STALE", "r1", "2026-09-24T14:01:00+00:00")
    unknown = observation("UNKNOWN", "r2", "2026-09-24T14:02:00+00:00")
    for obs, expected in ((stale, "STALE"), (unknown, "UNKNOWN")):
        result = build_recovery_review(**args, observations=(obs,))
        assert result.state == "SOURCE_RECONCILIATION_REQUIRED"
        assert result.components[0].source_state == expected
        assert not result.components[0].two_distinct_restoration_claims
    expired = observation(
        "RESTORED_ASSERTED", "r3", "2026-09-24T14:01:00+00:00",
        expires="2026-09-24T14:10:00+00:00",
    )
    outcome = build_recovery_review(**args, observations=(expired,))
    assert outcome.components[0].source_state == "EXPIRED"
    assert "STALE_OR_EXPIRED_EVIDENCE_CANNOT_BE_CURRENT" in outcome.reason_codes


def test_obres003_repeated_restored_source_requires_fresh_canonical_revalidation():
    args = bundle()
    outage = observation("OUTAGE", "r1", "2026-09-24T14:01:00+00:00")
    restored1 = observation("RESTORED_ASSERTED", "r2", "2026-09-24T14:02:00+00:00")
    restored2 = observation("RESTORED_ASSERTED", "r3", "2026-09-24T14:03:00+00:00")
    result = build_recovery_review(**args, observations=(outage, restored1, restored2))
    assert result.state == "FRESH_CANONICAL_REVALIDATION_REQUIRED"
    assert result.components[0].two_distinct_restoration_claims is True
    assert result.components[0].external_authenticity_verified is False
    assert result.source_recovery_authenticates_institution is False
    assert result.inherited_canonical_block_cleared is False
    assert "CANONICAL_EVIDENCE_HOLD_REQUIRES_NEW_UPSTREAM_REVIEW" in result.reason_codes
    assert verify_recovery_review(result, **args, observations=(outage, restored1, restored2))


def test_obres003_one_restoration_or_new_wallclock_same_payload_cannot_advance():
    args = bundle()
    restored1 = observation("RESTORED_ASSERTED", "r1", "2026-09-24T14:01:00+00:00")
    result = build_recovery_review(**args, observations=(restored1,))
    assert result.state == "SOURCE_RECONCILIATION_REQUIRED"
    assert not result.components[0].two_distinct_restoration_claims
    replay = replace(
        restored1, source_revision="r2", observed_at_utc="2026-09-24T14:02:00+00:00",
    )
    with pytest.raises(ValueError, match="integrity mismatch"):
        build_recovery_review(**args, observations=(restored1, replay))
    # A genuinely rebuilt receipt with exactly the old payload hash remains a replay.
    other = build_recovery_observation(
        account_key="trust", component="MARKET_SOURCE", source_ref="owner-source-feed",
        source_revision="r2", source_payload_hash=restored1.source_payload_hash,
        observed_at_utc="2026-09-24T14:02:00+00:00",
        received_at_utc="2026-09-24T14:02:00+00:00",
        expires_at_utc="2026-09-24T16:00:00+00:00",
        source_state="RESTORED_ASSERTED",
    )
    with pytest.raises(ValueError, match="source revision/payload replay"):
        build_recovery_review(**args, observations=(restored1, other))


def test_obres004_cross_account_component_and_chronology_fail_closed():
    args = bundle()
    cross = observation(
        "OUTAGE", "r1", "2026-09-24T14:01:00+00:00", account="personal",
    )
    with pytest.raises(ValueError, match="crosses account"):
        build_recovery_review(**args, observations=(cross,))
    position = observation(
        "OUTAGE", "r1", "2026-09-24T14:01:00+00:00",
        component="POSITION_SOURCE",
    )
    with pytest.raises(ValueError, match="monitored component"):
        build_recovery_review(**args, observations=(position,))
    latest = observation("RESTORED_ASSERTED", "r2", "2026-09-24T14:02:00+00:00")
    earlier = observation("OUTAGE", "r1", "2026-09-24T14:01:00+00:00")
    with pytest.raises(ValueError, match="advance strictly"):
        build_recovery_review(**args, observations=(latest, earlier))
    with pytest.raises(ValueError, match="duplicate recovery observation"):
        build_recovery_review(**args, observations=(earlier, earlier))
    future = observation("OUTAGE", "r3", "2026-09-24T15:01:00+00:00")
    with pytest.raises(ValueError, match="future-dated"):
        build_recovery_review(**args, observations=(future,))
    with pytest.raises(ValueError, match="chronology"):
        observation("OUTAGE", "r4", "2026-09-24T14:02:00+00:00",
                    received="2026-09-24T14:01:00+00:00")


def test_obres004_monitored_component_missing_never_counts_as_restored():
    args = bundle()
    args["monitored_components"] = ("MARKET_SOURCE", "POSITION_SOURCE")
    market1 = observation("RESTORED_ASSERTED", "r1", "2026-09-24T14:01:00+00:00")
    market2 = observation("RESTORED_ASSERTED", "r2", "2026-09-24T14:02:00+00:00")
    result = build_recovery_review(**args, observations=(market1, market2))
    assert result.state == "SOURCE_RECONCILIATION_REQUIRED"
    assert tuple(x.source_state for x in result.components) == ("RESTORED_ASSERTED", "MISSING")
    assert all(x.requires_canonical_revalidation for x in result.components)


def test_obres004_canonical_block_never_cleared_by_two_restorations():
    args = bundle(alert=signals(overreach=True))
    r1 = observation("RESTORED_ASSERTED", "r1", "2026-09-24T14:01:00+00:00")
    r2 = observation("RESTORED_ASSERTED", "r2", "2026-09-24T14:02:00+00:00")
    result = build_recovery_review(**args, observations=(r1, r2))
    assert result.state == "CANONICAL_BLOCK_RETAINED"
    assert result.canonical_recommendation_state == "BLOCKED"
    assert "CANONICAL_SAFETY_BLOCK_CANNOT_BE_CLEARED_BY_SOURCE_RECOVERY" in result.reason_codes
    assert result.inherited_canonical_block_cleared is False
    assert result.execution_authority is False


def test_obres005_tampered_lineage_forbidden_grants_and_redacted_reference():
    args = bundle()
    r1 = observation("RESTORED_ASSERTED", "r1", "2026-09-24T14:01:00+00:00")
    r2 = observation("RESTORED_ASSERTED", "r2", "2026-09-24T14:02:00+00:00")
    values = (r1, r2)
    result = build_recovery_review(**args, observations=values)
    reference = recovery_reference(result, **args, observations=values)
    assert reference["amounts_exposed"] is False
    assert reference["tower_authorization_required"] is True
    assert "cash" not in str(reference).lower()
    assert not verify_recovery_review(
        replace(result, automatic_restart=True), **args, observations=values,
    )
    assert not verify_recovery_review(
        replace(result, source_recovery_authenticates_institution=True),
        **args, observations=values,
    )
    with pytest.raises(ValueError, match="verified entire source"):
        recovery_reference(replace(result, state="CLEARED"), **args, observations=values)
    bad_attention = replace(args["attention"], top_priority="P3_OWNER_REVIEW")
    with pytest.raises(ValueError, match="OBATTN"):
        build_recovery_review(**{**args, "attention": bad_attention}, observations=values)
    with pytest.raises(ValueError, match="external authenticity"):
        build_recovery_review(
            **args, observations=(replace(r1, source_claim_external_authenticity=True),),
        )


def test_obres005_contract_is_never_mode_or_capital_authority():
    c = recovery_contract()
    assert c["recompute_full_source_lineage"]
    assert c["strict_chronology_and_distinct_source_fingerprints"]
    assert c["restoration_assertion_is_not_actual_reconciliation"]
    assert c["canonical_block_or_hold_never_auto_cleared"]
    assert c["source_hash_proves_external_authenticity"] is False
    assert c["teller_owns_acquisition_readiness"]
    for field in ("automatic_provider_failover", "automatic_restart", "automatic_replay",
                  "kill_switch_clear", "release_protected_capital", "execution_authority",
                  "broker_submission", "capital_movement", "manual_live_unlock",
                  "hybrid_unlock", "automated_unlock", "direct_buybox_access"):
        assert c[field] is False
