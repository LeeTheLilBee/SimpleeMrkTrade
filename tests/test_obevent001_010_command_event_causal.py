
from __future__ import annotations

from copy import deepcopy

import pytest

from web.ob_authority_registry import (
    ACTIVE_AUTHORITY_RECORDS,
    PENDING_AUTHORITY_SLOTS,
    build_canonical_authority_registry,
    resolve_authority_reference,
)

from web.ob_command_event_authority import (
    COMMAND_SCHEMA_VERSION,
    EVENT_SCHEMA_VERSION,
    INVALIDATION_SCHEMA_VERSION,
    build_accepted_event,
    build_command,
    build_invalidation_plan,
    causal_chain,
    command_event_contract,
    get_command,
    get_event,
    list_events,
    mark_command_rejected,
    record_accepted_event,
    record_command_request,
    replay_event_ledger,
)

from web.ob_effective_policy import (
    effective_policy_contract,
    explicit_owner_restriction_layer,
)


def command(
    *,
    target="OB_OWNER_OPERATING_PROFILE_V1",
    key="cmd-1",
    payload=None,
    correlation_id=None,
    causation_event_id=None,
):

    return build_command(
        command_type="OWNER_REQUEST",
        target_authority=target,
        actor_type="OWNER",
        actor_id="owner-solice",
        account_key="trust",
        payload=payload or {
            "requested_change":
                "test",
        },
        idempotency_key=key,
        correlation_id=correlation_id,
        causation_event_id=causation_event_id,
    )


def accepted_event(
    cmd,
    *,
    before="state-v1",
    after="state-v2",
    event_type="OWNER_PROFILE_CHANGED",
    aggregate_type="OWNER_PROFILE",
    aggregate_id="trust-profile",
):

    return build_accepted_event(
        cmd,
        source_authority=
            cmd["target_authority"],
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        before_state_ref=before,
        after_state_ref=after,
        payload={
            "accepted":
                True,
        },
    )


def test_contract_request_is_not_truth():

    contract = command_event_contract()

    assert contract["schema_version"] == "OB_COMMAND_EVENT_CAUSAL_V1"
    assert contract["command_schema_version"] == COMMAND_SCHEMA_VERSION
    assert contract["event_schema_version"] == EVENT_SCHEMA_VERSION
    assert contract["invalidation_schema_version"] == INVALIDATION_SCHEMA_VERSION

    assert contract["request_equals_truth"] is False
    assert contract["command_requests_change"] is True
    assert contract["domain_authority_validates_and_mutates"] is True
    assert contract["event_records_accepted_change"] is True
    assert contract["rejected_command_emits_domain_event"] is False

    assert contract["execution_authority"] is False
    assert contract["broker_submission"] is False
    assert contract["capital_movement"] is False
    assert contract["automatic_contract_selection"] is False
    assert contract["automatic_execution"] is False
    assert contract["live_auto_locked"] is True


def test_command_is_request_only():

    cmd = command()

    assert cmd["status"] == "REQUESTED"
    assert cmd["request_is_truth"] is False
    assert cmd["domain_mutation_performed_here"] is False
    assert cmd["command_id"]
    assert cmd["command_fingerprint"]


def test_unknown_authority_fails_closed():

    with pytest.raises(
        ValueError,
        match="not an active canonical authority",
    ):
        build_command(
            command_type="BAD",
            target_authority="NOT_REAL",
            actor_id="owner-solice",
            payload={},
            idempotency_key="bad-target",
        )


def test_current_phase_blocks_execution_request():

    with pytest.raises(
        ValueError,
        match="forbids",
    ):
        command(
            key="bad-exec",
            payload={
                "submit_order":
                    True,
            },
        )


def test_command_recording_is_idempotent(tmp_path):

    db = tmp_path / "event.sqlite3"

    cmd = command(
        key="idempotent"
    )

    first = record_command_request(
        cmd,
        path=db,
    )

    second = record_command_request(
        deepcopy(cmd),
        path=db,
    )

    assert first["created"] is True
    assert second["created"] is False
    assert second["idempotent"] is True

    stored = get_command(
        cmd["command_id"],
        path=db,
    )

    assert stored["status"] == "REQUESTED"


def test_rejection_emits_no_domain_event(tmp_path):

    db = tmp_path / "reject.sqlite3"

    cmd = command(
        key="reject"
    )

    record_command_request(
        cmd,
        path=db,
    )

    result = mark_command_rejected(
        cmd["command_id"],
        authority_id=
            cmd["target_authority"],
        reason="domain_rejected",
        path=db,
    )

    assert result["command"]["status"] == "REJECTED"
    assert list_events(path=db) == []


def test_rejected_outcome_cannot_be_rewritten(tmp_path):

    db = tmp_path / "reject-rewrite.sqlite3"

    cmd = command(
        key="reject-rewrite"
    )

    record_command_request(
        cmd,
        path=db,
    )

    mark_command_rejected(
        cmd["command_id"],
        authority_id=
            cmd["target_authority"],
        reason="reason-one",
        path=db,
    )

    same = mark_command_rejected(
        cmd["command_id"],
        authority_id=
            cmd["target_authority"],
        reason="reason-one",
        path=db,
    )

    assert same["idempotent"] is True

    with pytest.raises(
        ValueError,
        match="silently rewritten",
    ):
        mark_command_rejected(
            cmd["command_id"],
            authority_id=
                cmd["target_authority"],
            reason="reason-two",
            path=db,
        )


def test_accepted_event_requires_real_state_change():

    cmd = command(
        key="same-state"
    )

    with pytest.raises(
        ValueError,
        match="actual accepted state change",
    ):
        accepted_event(
            cmd,
            before="same",
            after="same",
        )


def test_event_source_must_own_command():

    cmd = command(
        key="wrong-owner"
    )

    with pytest.raises(
        ValueError,
        match="source authority",
    ):
        build_accepted_event(
            cmd,
            source_authority="OB_EFFECTIVE_POLICY_V1",
            event_type="WRONG",
            aggregate_type="TEST",
            aggregate_id="test",
            before_state_ref="a",
            after_state_ref="b",
            payload={},
        )


def test_accepted_event_recording_is_idempotent(tmp_path):

    db = tmp_path / "accepted.sqlite3"

    cmd = command(
        key="accepted"
    )

    record_command_request(
        cmd,
        path=db,
    )

    event = accepted_event(
        cmd
    )

    first = record_accepted_event(
        event,
        path=db,
    )

    second = record_accepted_event(
        deepcopy(event),
        path=db,
    )

    assert first["created"] is True
    assert second["created"] is False
    assert second["idempotent"] is True

    assert (
        get_command(
            cmd["command_id"],
            path=db,
        )["status"]
        ==
        "ACCEPTED"
    )

    assert (
        get_event(
            event["event_id"],
            path=db,
        )["event_fingerprint"]
        ==
        event["event_fingerprint"]
    )


def test_rejected_command_cannot_emit_accepted_event(tmp_path):

    db = tmp_path / "rejected-no-event.sqlite3"

    cmd = command(
        key="rejected-no-event"
    )

    record_command_request(
        cmd,
        path=db,
    )

    mark_command_rejected(
        cmd["command_id"],
        authority_id=
            cmd["target_authority"],
        reason="no",
        path=db,
    )

    with pytest.raises(
        ValueError,
        match="Rejected command",
    ):
        record_accepted_event(
            accepted_event(cmd),
            path=db,
        )


def test_owner_profile_change_invalidates_structural_dependents_only():

    cmd = command(
        key="profile-change"
    )

    event = accepted_event(
        cmd
    )

    plan = build_invalidation_plan(
        event
    )

    assert set(
        plan["direct_dependents"]
    ) == {
        "OB_ACCOUNT_IDENTITY_TRUTH_V1",
        "OB_EFFECTIVE_POLICY_V1",
        "OB_OWNER_FIT_ELIGIBILITY_V1",
        "OB_PROOF_DEMO_ACCOUNT_V1",
    }

    assert (
        "OB_PROOF_SANITIZED_SCOREBOARD_V1"
        in
        plan["transitive_dependents"]
    )

    assert (
        "existing_canonical_engine_feed"
        not in
        plan["transitive_dependents"]
    )

    assert (
        "OB_OPTIONS_RESEARCH_V1"
        not in
        plan["transitive_dependents"]
    )

    assert plan["whole_system_invalidated"] is False
    assert plan["domain_state_mutated"] is False
    assert plan["durable_domain_state_deleted"] is False


def test_market_change_does_not_invalidate_owner_profile():

    cmd = command(
        target="existing_canonical_engine_feed",
        key="market",
    )

    event = accepted_event(
        cmd,
        event_type="CANDIDATE_TRUTH_CHANGED",
        aggregate_type="MARKET_CANDIDATE",
        aggregate_id="AMD",
    )

    plan = build_invalidation_plan(
        event
    )

    assert (
        "OB_OWNER_OPERATING_PROFILE_V1"
        not in
        plan["transitive_dependents"]
    )

    assert (
        "OB_EFFECTIVE_POLICY_V1"
        not in
        plan["transitive_dependents"]
    )

    assert (
        "OB_OPTIONS_RESEARCH_V1"
        in
        plan["transitive_dependents"]
    )

    assert (
        "OB_TRADE_INTENT_V1"
        in
        plan["transitive_dependents"]
    )


def test_invalidation_is_deterministic():

    cmd = command(
        key="deterministic"
    )

    event = accepted_event(
        cmd
    )

    first = build_invalidation_plan(
        event
    )

    second = build_invalidation_plan(
        deepcopy(event)
    )

    assert (
        first["plan_fingerprint"]
        ==
        second["plan_fingerprint"]
    )

    assert (
        first["recompute_order"]
        ==
        second["recompute_order"]
    )


def test_causal_chain_is_durable(tmp_path):

    db = tmp_path / "causal.sqlite3"

    parent_cmd = command(
        key="parent"
    )

    record_command_request(
        parent_cmd,
        path=db,
    )

    parent_event = accepted_event(
        parent_cmd
    )

    record_accepted_event(
        parent_event,
        path=db,
    )

    child_cmd = command(
        target="OB_EFFECTIVE_POLICY_V1",
        key="child",
        correlation_id=
            parent_event["correlation_id"],
        causation_event_id=
            parent_event["event_id"],
    )

    record_command_request(
        child_cmd,
        path=db,
    )

    child_event = accepted_event(
        child_cmd,
        event_type="EFFECTIVE_POLICY_RECOMPUTED",
        aggregate_type="EFFECTIVE_POLICY",
        aggregate_id="trust-policy",
    )

    record_accepted_event(
        child_event,
        path=db,
    )

    chain = causal_chain(
        child_event["event_id"],
        path=db,
    )

    assert [
        item["event_id"]
        for item in chain
    ] == [
        parent_event["event_id"],
        child_event["event_id"],
    ]


def test_replay_is_audit_only(tmp_path):

    db = tmp_path / "replay.sqlite3"

    cmd = command(
        key="replay"
    )

    record_command_request(
        cmd,
        path=db,
    )

    event = accepted_event(
        cmd
    )

    record_accepted_event(
        event,
        path=db,
    )

    replay = replay_event_ledger(
        path=db,
    )

    assert replay["event_count"] == 1
    assert replay["domain_state_reapplied"] is False
    assert replay["audit_replay_only"] is True
    assert replay["replay_fingerprint"]


def test_registry_activates_obevent():

    registry = build_canonical_authority_registry()

    assert registry["validation"]["valid"] is True
    assert registry["validation"]["errors"] == []
    assert registry["validation"]["dependency_cycle_free"] is True

    assert (
        registry[
            "authority_records"
        ][
            "event_authority"
        ][
            "authority_id"
        ]
        ==
        "OB_COMMAND_EVENT_CAUSAL_V1"
    )

    assert (
        "event_authority"
        not in
        PENDING_AUTHORITY_SLOTS
    )


def test_pending_obevent_is_retired_alias():

    result = resolve_authority_reference(
        "PENDING_OBEVENT"
    )

    assert result["resolution"] == "RETIRED_ALIAS"

    assert (
        result["resolved_authority_id"]
        ==
        "OB_COMMAND_EVENT_CAUSAL_V1"
    )


def test_event_authority_not_reverse_structural_dependency():

    registry = build_canonical_authority_registry()

    for concept in (
        "trade_intent",
        "proof_demo_account",
        "effective_policy",
    ):
        record = (
            registry[
                "authority_records"
            ][concept]
        )

        assert (
            "OB_COMMAND_EVENT_CAUSAL_V1"
            not in
            record["inputs"]
        )

        assert (
            "event_authority"
            not in
            record["deferred_integrations"]
        )


def test_effective_policy_names_event_authority():

    contract = effective_policy_contract()

    assert (
        contract["event_authority"]
        ==
        "OB_COMMAND_EVENT_CAUSAL_V1"
    )

    restriction = explicit_owner_restriction_layer(
        account_key="trust",
        restriction_id="event-test",
        restrictions={
            "max_loss_per_trade_pct":
                0.5,
        },
        owner_confirmed=True,
    )

    assert (
        restriction[
            "source_ref"
        ][
            "event_authority"
        ]
        ==
        "OB_COMMAND_EVENT_CAUSAL_V1"
    )

    assert (
        restriction[
            "source_ref"
        ][
            "future_event_authority"
        ]
        ==
        "OB_COMMAND_EVENT_CAUSAL_V1"
    )

    assert (
        restriction[
            "source_ref"
        ][
            "adoption_persisted"
        ]
        is False
    )


def test_registry_event_authority_has_no_execution_capabilities():

    record = (
        ACTIVE_AUTHORITY_RECORDS[
            "event_authority"
        ]
    )

    assert record["execution_authority"] is False
    assert record["broker_submission"] is False
    assert record["capital_movement"] is False
    assert record["automatic_contract_selection"] is False
    assert record["automatic_execution"] is False
