from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from vault.recovery_commit_owner_decision_tower_handoff_delivery_authorization_decision_recording_preparation_layer_service import (
    CURRENT_RECOMMENDATION,
    DecisionRecordingPreparationError,
    PREPARATION_STATE,
    RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingPreparationService,
    SAFETY_STATE_FIELDS,
)


def _service(
    tmp_path: Path,
) -> RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingPreparationService:
    return (
        RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingPreparationService(
            tmp_path / "gp701_710.sqlite3"
        )
    )


def _prepare(
    service,
    **overrides,
):
    request = {
        "idempotency_key": "gp701-710-case-001",
        "recovery_case_id": "recovery-case-001",
        "owner_decision_record_id": (
            "owner-decision-record-001"
        ),
        "recording_gate_id": (
            "vault-gp691-700-gate-001"
        ),
        "recording_gate_hash": (
            "a" * 64
        ),
        "recording_gate_state": (
            "AUTHORIZATION_DECISION_RECORDING_GATE_"
            "SEALED_CLOSED"
        ),
        "tower_authority_id": (
            "tower-authority-001"
        ),
        "tower_delivery_target_id": (
            "tower-delivery-target-001"
        ),
        "target_environment": (
            "STAGING"
        ),
        "safe_metadata": {
            "prior_pack_range": "GP691-GP700",
            "reference_mode": (
                "HASH_AND_IDENTIFIER_ONLY"
            ),
            "redaction_profile": (
                "tower-safe"
            ),
        },
    }

    request.update(
        overrides
    )

    return service.prepare_decision_recording(
        **request
    )


def test_gp701_710_prepares_recording_without_opening_gate(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _prepare(
        service
    )

    assert (
        receipt.recommendation
        == CURRENT_RECOMMENDATION
    )

    assert (
        receipt.preparation_state
        == PREPARATION_STATE
    )

    assert receipt.recording_prepared is True
    assert receipt.recording_gate_open is False
    assert receipt.owner_session_created is False
    assert receipt.owner_session_started is False
    assert receipt.owner_decision_selected is False
    assert receipt.owner_decision_recorded is False
    assert receipt.authorization_granted is False
    assert receipt.authorization_token_issued is False
    assert receipt.immutable is True
    assert receipt.append_only is True
    assert receipt.idempotent_replay is False

    record = service.get_preparation(
        receipt.preparation_id
    )

    payload = record[
        "preparation_payload"
    ]

    assert (
        payload[
            "gp701_preparation_shell"
        ]["pack"]
        == "GP701"
    )

    assert (
        payload[
            "gp702_recording_gate_lineage"
        ]["pack"]
        == "GP702"
    )

    assert (
        payload[
            "gp703_owner_session_requirement_board"
        ]["pack"]
        == "GP703"
    )

    assert (
        payload[
            "gp704_owner_identity_requirement_board"
        ]["pack"]
        == "GP704"
    )

    assert (
        payload[
            "gp705_owner_step_up_requirement_board"
        ]["pack"]
        == "GP705"
    )

    assert (
        payload[
            "gp706_dual_receipt_requirement_board"
        ]["pack"]
        == "GP706"
    )

    assert (
        payload[
            "gp707_second_authority_requirement_board"
        ]["pack"]
        == "GP707"
    )

    assert (
        payload[
            "gp708_recording_preparation_envelope"
        ]["pack"]
        == "GP708"
    )

    assert (
        payload[
            "gp709_recording_preparation_receipt_draft"
        ]["pack"]
        == "GP709"
    )

    assert (
        payload[
            "gp710_checkpoint"
        ]["pack"]
        == "GP710"
    )


def test_gp701_710_owner_session_requirement_remains_unsatisfied(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _prepare(
        service
    )

    record = service.get_preparation(
        receipt.preparation_id
    )

    board = record[
        "owner_session_requirement_board"
    ]

    assert (
        board[
            "tower_owner_session_required_for_future_recording"
        ]
        is True
    )

    assert (
        board["owner_session_created"]
        is False
    )

    assert (
        board["owner_session_started"]
        is False
    )

    assert (
        board["tower_owner_session_created"]
        is False
    )

    assert (
        board["tower_owner_session_started"]
        is False
    )

    assert (
        board["recording_blocked_without_owner_session"]
        is True
    )


def test_gp701_710_envelope_contains_no_active_owner_evidence(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _prepare(
        service
    )

    record = service.get_preparation(
        receipt.preparation_id
    )

    envelope = record[
        "recording_preparation_envelope"
    ]

    assert envelope["owner_session_reference"] is None

    assert (
        envelope["owner_authentication_reference"]
        is None
    )

    assert (
        envelope["owner_step_up_reference"]
        is None
    )

    assert (
        envelope["dual_receipt_reference"]
        is None
    )

    assert (
        envelope["second_authority_reference"]
        is None
    )

    assert (
        envelope["owner_decision_value"]
        is None
    )

    assert (
        envelope["owner_decision_recommended"]
        is False
    )

    assert (
        envelope["owner_decision_defaulted"]
        is False
    )

    assert (
        envelope["owner_decision_selected"]
        is False
    )

    assert (
        envelope["owner_decision_invented"]
        is False
    )

    assert (
        envelope["owner_decision_recorded"]
        is False
    )

    assert (
        envelope["recording_gate_open"]
        is False
    )


def test_gp701_710_safety_state_is_all_false(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _prepare(
        service
    )

    record = service.get_preparation(
        receipt.preparation_id
    )

    safety_state = record[
        "checkpoint"
    ]["safety_state"]

    assert (
        set(
            safety_state
        )
        == set(
            SAFETY_STATE_FIELDS
        )
    )

    assert all(
        value is False
        for value in safety_state.values()
    )


def test_gp701_710_exact_idempotent_replay(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    first = _prepare(
        service
    )

    second = _prepare(
        service
    )

    assert (
        first.preparation_id
        == second.preparation_id
    )

    assert (
        first.preparation_hash
        == second.preparation_hash
    )

    assert (
        first.idempotent_replay
        is False
    )

    assert (
        second.idempotent_replay
        is True
    )

    events = service.list_events(
        first.preparation_id
    )

    assert len(events) == 1


def test_gp701_710_rejects_changed_idempotent_inputs(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    _prepare(
        service
    )

    with pytest.raises(
        DecisionRecordingPreparationError,
        match="different immutable",
    ):
        _prepare(
            service,
            target_environment="PRODUCTION",
        )


def test_gp701_710_requires_closed_recording_gate_lineage(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        DecisionRecordingPreparationError,
        match="AUTHORIZATION_DECISION_RECORDING_GATE_SEALED_CLOSED",
    ):
        _prepare(
            service,
            recording_gate_state=(
                "AUTHORIZATION_DECISION_RECORDING_GATE_OPEN"
            ),
        )


@pytest.mark.parametrize(
    "operation",
    [
        "OPEN_OWNER_DECISION_RECORDING_GATE",
        "CREATE_OWNER_SESSION",
        "START_OWNER_SESSION",
        "CREATE_TOWER_OWNER_SESSION",
        "START_TOWER_OWNER_SESSION",
        "AUTHENTICATE_OWNER",
        "STEP_UP_OWNER",
        "RECOMMEND_OWNER_DECISION",
        "DEFAULT_OWNER_DECISION",
        "SELECT_OWNER_DECISION",
        "INVENT_OWNER_DECISION",
        "RECORD_OWNER_DECISION",
        "GRANT_OWNER_APPROVAL",
        "GRANT_ADMIN_APPROVAL",
        "SATISFY_DUAL_RECEIPT",
        "GRANT_SECOND_AUTHORITY_REVIEW",
        "GRANT_GO_DECISION",
        "ISSUE_RECOVERY_AUTHORIZATION",
        "GRANT_RECOVERY_AUTHORIZATION",
        "ISSUE_AUTHORIZATION_TOKEN",
        "MINT_AUTHORIZATION_TOKEN",
        "DELIVER_HANDOFF",
        "SEND_HANDOFF",
        "ACCEPT_HANDOFF",
        "CREATE_TOWER_DELIVERY_SESSION",
        "START_TOWER_DELIVERY_SESSION",
        "ACTIVATE_SCOPE_FREEZE",
        "ACTIVATE_COMMIT_WINDOW",
        "ACTIVATE_EXECUTION_WINDOW",
        "OPEN_COMMIT_POINT",
        "ISSUE_RECOVERY_COMMIT_COMMAND",
        "EXECUTE_RECOVERY_COMMIT",
        "RESTORE_DATA",
        "MOUNT_PRODUCTION_STORAGE",
        "WRITE_PRODUCTION_STORAGE",
        "CONNECT_EXTERNAL_PROVIDER",
        "EXPOSE_RAW_MATERIAL",
        "DELETE_DATA",
        "DESTROY_DATA",
    ],
)
def test_gp701_710_rejects_prohibited_operations(
    tmp_path: Path,
    operation: str,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        DecisionRecordingPreparationError,
        match="prohibited operation",
    ):
        _prepare(
            service,
            idempotency_key=(
                "prohibited-"
                + operation.lower()
            ),
            requested_operations=[
                operation
            ],
        )


@pytest.mark.parametrize(
    "safe_metadata",
    [
        {
            "raw_path": "/tmp/raw"
        },
        {
            "raw_url": "https://example.test/raw"
        },
        {
            "token": "do-not-store"
        },
        {
            "authorization_token": "do-not-store"
        },
        {
            "session_token": "do-not-store"
        },
        {
            "session_cookie": "do-not-store"
        },
        {
            "credentials": {
                "username": "x"
            }
        },
        {
            "nested": {
                "private_key": "x"
            }
        },
        {
            "raw_material": {
                "content": "x"
            }
        },
        {
            "provider_secret": "x"
        },
    ],
)
def test_gp701_710_rejects_raw_secret_or_session_metadata(
    tmp_path: Path,
    safe_metadata,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        DecisionRecordingPreparationError,
        match="prohibited",
    ):
        _prepare(
            service,
            safe_metadata=safe_metadata,
        )


def test_gp701_710_verification_passes(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _prepare(
        service
    )

    result = service.verify_preparation(
        receipt.preparation_id
    )

    assert result["verified"] is True
    assert result["preparation_hash_valid"] is True
    assert result["event_chain_valid"] is True
    assert result["tower_destination_only"] is True

    assert (
        result["recording_gate_closed_lineage"]
        is True
    )

    assert (
        result["recording_prepared"]
        is True
    )

    assert (
        result["recording_gate_open"]
        is False
    )

    assert (
        result["owner_session_created"]
        is False
    )

    assert (
        result["owner_session_started"]
        is False
    )

    assert (
        result["tower_owner_session_created"]
        is False
    )

    assert (
        result["tower_owner_session_started"]
        is False
    )

    assert (
        result["owner_authenticated"]
        is False
    )

    assert (
        result["owner_stepped_up"]
        is False
    )

    assert (
        result["owner_admin_approval_granted"]
        is False
    )

    assert (
        result["dual_receipt_satisfied"]
        is False
    )

    assert (
        result["second_authority_review_granted"]
        is False
    )

    assert (
        result["owner_decision_recommended"]
        is False
    )

    assert (
        result["owner_decision_defaulted"]
        is False
    )

    assert (
        result["owner_decision_selected"]
        is False
    )

    assert (
        result["owner_decision_invented"]
        is False
    )

    assert (
        result["owner_decision_recorded"]
        is False
    )

    assert (
        result["go_decision_granted"]
        is False
    )

    assert (
        result["recovery_authorization_granted"]
        is False
    )

    assert (
        result["authorization_token_issued"]
        is False
    )

    assert (
        result["recovery_commit_command_issued"]
        is False
    )

    assert (
        result["production_write_occurred"]
        is False
    )

    assert (
        result["provider_connection_occurred"]
        is False
    )

    assert (
        result["raw_material_exposed"]
        is False
    )

    assert (
        result["destructive_action_occurred"]
        is False
    )

    assert (
        result["unsafe_completed_actions"]
        == []
    )


def test_gp701_710_preparation_records_are_immutable(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _prepare(
        service
    )

    connection = sqlite3.connect(
        str(
            service.database_path
        )
    )

    try:
        with pytest.raises(
            sqlite3.IntegrityError,
            match="immutable",
        ):
            connection.execute(
                """
                UPDATE
                    vault_gp701_710_authorization_decision_recording_preparations
                SET preparation_state = 'RECORDING_GATE_OPEN'
                WHERE preparation_id = ?
                """,
                (
                    receipt.preparation_id,
                ),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp701_710_preparation_records_are_append_only(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _prepare(
        service
    )

    connection = sqlite3.connect(
        str(
            service.database_path
        )
    )

    try:
        with pytest.raises(
            sqlite3.IntegrityError,
            match="append-only",
        ):
            connection.execute(
                """
                DELETE FROM
                    vault_gp701_710_authorization_decision_recording_preparations
                WHERE preparation_id = ?
                """,
                (
                    receipt.preparation_id,
                ),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp701_710_events_are_immutable_and_append_only(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _prepare(
        service
    )

    event = service.list_events(
        receipt.preparation_id
    )[0]

    connection = sqlite3.connect(
        str(
            service.database_path
        )
    )

    try:
        with pytest.raises(
            sqlite3.IntegrityError,
            match="immutable",
        ):
            connection.execute(
                """
                UPDATE
                    vault_gp701_710_authorization_decision_recording_preparation_events
                SET event_type = 'MUTATED'
                WHERE event_id = ?
                """,
                (
                    event["event_id"],
                ),
            )

        connection.rollback()

        with pytest.raises(
            sqlite3.IntegrityError,
            match="append-only",
        ):
            connection.execute(
                """
                DELETE FROM
                    vault_gp701_710_authorization_decision_recording_preparation_events
                WHERE event_id = ?
                """,
                (
                    event["event_id"],
                ),
            )

        connection.rollback()

    finally:
        connection.close()
