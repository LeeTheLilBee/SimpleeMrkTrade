from copy import deepcopy

import pytest

from tower.hosted_candidate_release_gate import (
    build_hosted_candidate_release_packet,
)

from tower.hosted_owner_release_review import (
    APPROVE_RELEASE,
    GENESIS_RECEIPT_HASH,
    HOLD_RELEASE,
    REJECT_RELEASE,
    SAFETY_FALSE_FIELDS,
    build_owner_release_review,
    read_owner_release_decision_receipts,
    record_owner_release_decision,
    validate_owner_release_context,
    verify_owner_release_decision_receipt,
)


def owner():

    return {
        "owner_id": "simplee_owner",
        "owner_session_reference": (
            "owner-session-verified-001"
        ),
        "owner_role": "owner",
        "owner_verified": True,
        "session_active": True,
        "session_fresh": True,
        "step_up_verified": True,
    }


def packet(
    *,
    revision="abc123",
    passing=True,
):

    parity = {
        "status": (
            "tower_hosted_candidate_parity_pass"
            if passing
            else "tower_hosted_candidate_parity_fail"
        ),
        "parity_pass": passing,
        "expected_revision": revision,
        "actual_revision": (
            revision
            if passing
            else "wrong456"
        ),
        "entrypoint": (
            "web.managed_staging:app"
        ),
        "critical_route_count": 11,
        "checks": {
            "expected_revision_valid": True,
            "health_http_200": True,
            "manifest_http_200": True,
            "exact_candidate_revision_match": passing,
            "all_critical_routes_present": True,
        },
        "failures": (
            []
            if passing
            else [
                "candidate revision mismatch",
            ]
        ),
        "deployment_authorized": False,
        "production_promotion_authorized": False,
        "broker_submission_authorized": False,
        "capital_movement_authorized": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
        "staging_ready_changed": False,
    }

    return (
        build_hosted_candidate_release_packet(
            parity
        )[
            "packet"
        ]
    )


def decide(
    tmp_path,
    candidate=None,
    **overrides,
):

    arguments = {
        "owner_context": owner(),
        "decision": APPROVE_RELEASE,
        "reason": (
            "Exact candidate reviewed; "
            "owner approves decision only."
        ),
        "ledger_path": (
            tmp_path
            / "release-receipts.jsonl"
        ),
    }

    arguments.update(
        overrides
    )

    return (
        record_owner_release_decision(
            candidate
            or packet(),
            **arguments,
        )
    )


def test_twr096_valid_owner_can_review_sealed_packet():

    review = (
        build_owner_release_review(
            packet(),
            owner_context=owner(),
        )
    )

    assert review[
        "review_allowed"
    ] is True

    assert review[
        "approval_allowed"
    ] is True

    assert review[
        "allowed_decisions"
    ] == [
        APPROVE_RELEASE,
        HOLD_RELEASE,
        REJECT_RELEASE,
    ]

    assert review[
        "expected_revision"
    ] == "abc123"


@pytest.mark.parametrize(
    "field",
    (
        "owner_verified",
        "session_active",
        "session_fresh",
        "step_up_verified",
    ),
)
def test_twr097_owner_session_gates_fail_closed(
    field,
):

    context = owner()

    context[
        field
    ] = False

    result = (
        build_owner_release_review(
            packet(),
            owner_context=context,
        )
    )

    assert result[
        "review_allowed"
    ] is False

    assert (
        field
        + "_required"
        in result[
            "errors"
        ]
    )


def test_twr097_nonowner_is_denied():

    context = owner()

    context[
        "owner_role"
    ] = "beta_tester"

    result = (
        validate_owner_release_context(
            context
        )
    )

    assert result[
        "valid"
    ] is False

    assert (
        "owner_role_required"
        in result[
            "errors"
        ]
    )


def test_twr097_tampered_packet_is_denied():

    candidate = packet()

    candidate[
        "actual_revision"
    ] = "tampered"

    result = (
        build_owner_release_review(
            candidate,
            owner_context=owner(),
        )
    )

    assert result[
        "review_allowed"
    ] is False

    assert (
        "packet_integrity_hash_mismatch"
        in result[
            "errors"
        ]
    )


def test_twr098_hold_candidate_cannot_be_approved(
    tmp_path,
):

    candidate = packet(
        passing=False
    )

    review = (
        build_owner_release_review(
            candidate,
            owner_context=owner(),
        )
    )

    assert review[
        "approval_allowed"
    ] is False

    assert (
        APPROVE_RELEASE
        not in review[
            "allowed_decisions"
        ]
    )

    result = decide(
        tmp_path,
        candidate,
    )

    assert result[
        "recorded"
    ] is False

    assert result[
        "status"
    ] == (
        "tower_owner_release_approval_blocked"
    )


@pytest.mark.parametrize(
    "decision",
    (
        HOLD_RELEASE,
        REJECT_RELEASE,
    ),
)
def test_twr098_hold_and_reject_create_receipts(
    tmp_path,
    decision,
):

    result = decide(
        tmp_path,
        packet(
            passing=False
        ),
        decision=decision,
        reason=(
            "Hosted candidate requires additional review."
        ),
    )

    assert result[
        "recorded"
    ] is True

    assert result[
        "receipt"
    ][
        "decision"
    ] == decision

    verification = (
        verify_owner_release_decision_receipt(
            result[
                "receipt"
            ]
        )
    )

    assert verification[
        "valid"
    ] is True


def test_twr098_empty_reason_is_rejected(
    tmp_path,
):

    result = decide(
        tmp_path,
        reason=" ",
    )

    assert result[
        "recorded"
    ] is False

    assert result[
        "status"
    ] == (
        "tower_owner_release_reason_invalid"
    )


def test_twr098_sensitive_reason_is_rejected(
    tmp_path,
):

    result = decide(
        tmp_path,
        reason=(
            "github_token="
            "ghp_should_not_survive"
        ),
    )

    assert result[
        "recorded"
    ] is False

    assert result[
        "status"
    ] == (
        "tower_owner_release_reason_rejected"
    )


def test_twr099_approval_receipt_is_persisted_and_sealed(
    tmp_path,
):

    candidate = packet()

    result = decide(
        tmp_path,
        candidate,
    )

    receipt = result[
        "receipt"
    ]

    ledger = (
        tmp_path
        / "release-receipts.jsonl"
    )

    assert result[
        "recorded"
    ] is True

    assert ledger.exists()

    assert receipt[
        "previous_receipt_hash"
    ] == GENESIS_RECEIPT_HASH

    assert receipt[
        "owner_id"
    ] == "simplee_owner"

    assert receipt[
        "packet_integrity_hash"
    ] == candidate[
        "packet_integrity_hash"
    ]

    assert (
        verify_owner_release_decision_receipt(
            receipt
        )[
            "valid"
        ]
        is True
    )


def test_twr099_receipt_tampering_is_detected(
    tmp_path,
):

    receipt = deepcopy(
        decide(
            tmp_path
        )[
            "receipt"
        ]
    )

    receipt[
        "decision"
    ] = REJECT_RELEASE

    result = (
        verify_owner_release_decision_receipt(
            receipt
        )
    )

    assert result[
        "valid"
    ] is False

    assert (
        "receipt_integrity_hash_mismatch"
        in result[
            "errors"
        ]
    )


def test_twr099_duplicate_packet_cannot_create_second_receipt(
    tmp_path,
):

    candidate = packet()

    first = decide(
        tmp_path,
        candidate,
    )

    second = decide(
        tmp_path,
        candidate,
    )

    assert first[
        "recorded"
    ] is True

    assert second[
        "recorded"
    ] is False

    assert second[
        "duplicate"
    ] is True

    receipts = (
        read_owner_release_decision_receipts(
            owner_context=owner(),
            ledger_path=(
                tmp_path
                / "release-receipts.jsonl"
            ),
        )
    )

    assert receipts[
        "receipt_count"
    ] == 1


def test_twr099_distinct_packets_form_receipt_chain(
    tmp_path,
):

    first = decide(
        tmp_path,
        packet(
            revision="abc123"
        ),
    )[
        "receipt"
    ]

    second = decide(
        tmp_path,
        packet(
            revision="def456"
        ),
    )[
        "receipt"
    ]

    assert second[
        "previous_receipt_hash"
    ] == first[
        "receipt_integrity_hash"
    ]

    receipts = (
        read_owner_release_decision_receipts(
            owner_context=owner(),
            ledger_path=(
                tmp_path
                / "release-receipts.jsonl"
            ),
        )
    )

    assert receipts[
        "receipt_count"
    ] == 2

    assert receipts[
        "chain_valid"
    ] is True


def test_twr099_corrupted_ledger_blocks_decisions(
    tmp_path,
):

    decide(
        tmp_path
    )

    ledger = (
        tmp_path
        / "release-receipts.jsonl"
    )

    ledger.write_text(
        "not-valid-json\n",
        encoding="utf-8",
    )

    result = decide(
        tmp_path,
        packet(
            revision="def456"
        ),
    )

    assert result[
        "recorded"
    ] is False

    assert result[
        "status"
    ] == (
        "tower_owner_release_receipt_persistence_failed"
    )


def test_twr099_persistence_failure_denies_decision(
    tmp_path,
    monkeypatch,
):

    import tower.hosted_owner_release_review as review

    def broken_append(
        path,
        receipt,
    ):

        raise OSError(
            "disk unavailable"
        )

    monkeypatch.setattr(
        review,
        "_append_receipt",
        broken_append,
    )

    result = decide(
        tmp_path
    )

    assert result[
        "recorded"
    ] is False

    assert result[
        "status"
    ] == (
        "tower_owner_release_receipt_persistence_failed"
    )


def test_twr099_hosted_runtime_requires_durable_receipt_storage(
    monkeypatch,
):

    monkeypatch.setenv(
        "RENDER",
        "true",
    )

    monkeypatch.delenv(
        "TOWER_RELEASE_RECEIPT_LEDGER_PATH",
        raising=False,
    )

    monkeypatch.delenv(
        "TOWER_RELEASE_RECEIPT_STORE_DURABLE",
        raising=False,
    )

    result = (
        record_owner_release_decision(
            packet(),
            owner_context=owner(),
            decision=APPROVE_RELEASE,
            reason=(
                "Owner reviewed the exact hosted candidate."
            ),
        )
    )

    assert result[
        "recorded"
    ] is False

    assert (
        "receipt_durable_storage_not_configured"
        in result[
            "errors"
        ]
    )


def test_twr100_approval_keeps_all_execution_boundaries_closed(
    tmp_path,
):

    result = decide(
        tmp_path
    )

    receipt = result[
        "receipt"
    ]

    for field in (
        SAFETY_FALSE_FIELDS
    ):

        assert result[
            field
        ] is False

        assert receipt[
            field
        ] is False

    assert receipt[
        "separate_release_execution_gate_required"
    ] is True


def test_twr100_receipts_remain_owner_only(
    tmp_path,
):

    decide(
        tmp_path
    )

    context = owner()

    context[
        "step_up_verified"
    ] = False

    result = (
        read_owner_release_decision_receipts(
            owner_context=context,
            ledger_path=(
                tmp_path
                / "release-receipts.jsonl"
            ),
        )
    )

    assert result[
        "receipts"
    ] == []

    assert result[
        "status"
    ] == (
        "tower_owner_release_receipts_denied"
    )
