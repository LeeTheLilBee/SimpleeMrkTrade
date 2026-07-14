from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from vault.recovery_commit_owner_decision_tower_handoff_delivery_authorization_decision_recording_gate_service import (
    CURRENT_RECOMMENDATION,
    DecisionRecordingGateError,
    GATE_STATE,
    RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingGateService,
    SAFETY_STATE_FIELDS,
)


def _service(
    tmp_path: Path,
) -> RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingGateService:
    return (
        RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingGateService(
            tmp_path / "gp691_700.sqlite3"
        )
    )


def _seal(
    service,
    **overrides,
):
    request = {
        "idempotency_key": "gp691-700-case-001",
        "recovery_case_id": "recovery-case-001",
        "owner_decision_record_id": (
            "owner-decision-record-001"
        ),
        "decision_preparation_id": (
            "vault-gp681-690-preparation-001"
        ),
        "decision_preparation_hash": (
            "a" * 64
        ),
        "decision_preparation_state": (
            "AUTHORIZATION_DECISION_PREPARED_NOT_RECORDED"
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
            "prior_pack_range": "GP681-GP690",
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

    return service.seal_decision_recording_gate(
        **request
    )


def test_gp691_700_seals_closed_recording_gate(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

    assert (
        receipt.recommendation
        == CURRENT_RECOMMENDATION
    )

    assert (
        receipt.gate_state
        == GATE_STATE
    )

    assert receipt.gate_sealed is True
    assert receipt.gate_open is False

    assert (
        receipt.owner_decision_selected
        is False
    )

    assert (
        receipt.owner_decision_recorded
        is False
    )

    assert (
        receipt.authorization_granted
        is False
    )

    assert (
        receipt.authorization_token_issued
        is False
    )

    assert receipt.immutable is True
    assert receipt.append_only is True

    assert (
        receipt.idempotent_replay
        is False
    )

    record = service.get_gate(
        receipt.gate_id
    )

    payload = record[
        "gate_payload"
    ]

    assert (
        payload[
            "gp691_recording_gate_shell"
        ]["pack"]
        == "GP691"
    )

    assert (
        payload[
            "gp692_preparation_lineage_gate"
        ]["pack"]
        == "GP692"
    )

    assert (
        payload[
            "gp693_owner_identity_requirement_gate"
        ]["pack"]
        == "GP693"
    )

    assert (
        payload[
            "gp694_owner_step_up_requirement_gate"
        ]["pack"]
        == "GP694"
    )

    assert (
        payload[
            "gp695_dual_receipt_requirement_gate"
        ]["pack"]
        == "GP695"
    )

    assert (
        payload[
            "gp696_second_authority_requirement_gate"
        ]["pack"]
        == "GP696"
    )

    assert (
        payload[
            "gp697_recording_prerequisite_matrix"
        ]["pack"]
        == "GP697"
    )

    assert (
        payload[
            "gp698_recording_blocker_board"
        ]["pack"]
        == "GP698"
    )

    assert (
        payload[
            "gp699_recording_receipt_draft"
        ]["pack"]
        == "GP699"
    )

    assert (
        payload[
            "gp700_checkpoint"
        ]["pack"]
        == "GP700"
    )


def test_gp691_700_recording_gate_remains_closed(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

    record = service.get_gate(
        receipt.gate_id
    )

    shell = record[
        "recording_gate_shell"
    ]

    matrix = record[
        "recording_prerequisite_matrix"
    ]

    assert (
        shell["gate_sealed"]
        is True
    )

    assert (
        shell["gate_open"]
        is False
    )

    assert (
        shell["owner_decision_recorded"]
        is False
    )

    assert (
        matrix[
            "all_recording_prerequisites_satisfied"
        ]
        is False
    )

    assert (
        matrix[
            "decision_recording_gate_open"
        ]
        is False
    )


def test_gp691_700_recording_requirements_are_not_satisfied(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

    record = service.get_gate(
        receipt.gate_id
    )

    matrix = record[
        "recording_prerequisite_matrix"
    ]

    assert (
        matrix["owner_authenticated"]
        is False
    )

    assert (
        matrix["owner_stepped_up"]
        is False
    )

    assert (
        matrix[
            "owner_admin_approval_granted"
        ]
        is False
    )

    assert (
        matrix["dual_receipt_satisfied"]
        is False
    )

    assert (
        matrix[
            "second_authority_review_granted"
        ]
        is False
    )

    assert (
        matrix["owner_decision_selected"]
        is False
    )

    assert (
        matrix["owner_decision_recorded"]
        is False
    )


def test_gp691_700_safety_state_is_all_false(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

    record = service.get_gate(
        receipt.gate_id
    )

    safety_state = record[
        "recording_blocker_board"
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


def test_gp691_700_exact_idempotent_replay(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    first = _seal(
        service
    )

    second = _seal(
        service
    )

    assert (
        first.gate_id
        == second.gate_id
    )

    assert (
        first.gate_hash
        == second.gate_hash
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
        first.gate_id
    )

    assert len(events) == 1


def test_gp691_700_rejects_changed_idempotent_inputs(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    _seal(
        service
    )

    with pytest.raises(
        DecisionRecordingGateError,
        match="different immutable",
    ):
        _seal(
            service,
            target_environment="PRODUCTION",
        )


def test_gp691_700_requires_prepared_not_recorded_lineage(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        DecisionRecordingGateError,
        match="AUTHORIZATION_DECISION_PREPARED_NOT_RECORDED",
    ):
        _seal(
            service,
            decision_preparation_state=(
                "OWNER_DECISION_RECORDED"
            ),
        )


@pytest.mark.parametrize(
    "operation",
    [
        "SELECT_OWNER_DECISION",
        "INVENT_OWNER_DECISION",
        "RECORD_OWNER_DECISION",
        "OPEN_OWNER_DECISION_RECORDING_GATE",
        "AUTHENTICATE_OWNER",
        "STEP_UP_OWNER",
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
def test_gp691_700_rejects_prohibited_operations(
    tmp_path: Path,
    operation: str,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        DecisionRecordingGateError,
        match="prohibited operation",
    ):
        _seal(
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
def test_gp691_700_rejects_raw_or_secret_metadata(
    tmp_path: Path,
    safe_metadata,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        DecisionRecordingGateError,
        match="prohibited",
    ):
        _seal(
            service,
            safe_metadata=safe_metadata,
        )


def test_gp691_700_verification_passes(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

    result = service.verify_gate(
        receipt.gate_id
    )

    assert result["verified"] is True
    assert result["gate_hash_valid"] is True
    assert result["event_chain_valid"] is True
    assert result["tower_destination_only"] is True

    assert (
        result[
            "decision_preparation_not_recorded_lineage"
        ]
        is True
    )

    assert result["gate_sealed"] is True
    assert result["gate_open"] is False

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
        result["owner_authenticated"]
        is False
    )

    assert (
        result["owner_stepped_up"]
        is False
    )

    assert (
        result[
            "owner_admin_approval_granted"
        ]
        is False
    )

    assert (
        result["dual_receipt_satisfied"]
        is False
    )

    assert (
        result[
            "second_authority_review_granted"
        ]
        is False
    )

    assert (
        result["go_decision_granted"]
        is False
    )

    assert (
        result[
            "recovery_authorization_granted"
        ]
        is False
    )

    assert (
        result["authorization_token_issued"]
        is False
    )

    assert (
        result["handoff_delivered"]
        is False
    )

    assert (
        result[
            "tower_delivery_session_started"
        ]
        is False
    )

    assert (
        result["scope_freeze_activated"]
        is False
    )

    assert (
        result["commit_window_activated"]
        is False
    )

    assert (
        result["execution_window_activated"]
        is False
    )

    assert (
        result["commit_point_opened"]
        is False
    )

    assert (
        result["recovery_commit_command_issued"]
        is False
    )

    assert (
        result["recovery_commit_executed"]
        is False
    )

    assert (
        result["restore_occurred"]
        is False
    )

    assert (
        result["production_mount_occurred"]
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


def test_gp691_700_gate_records_are_immutable(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
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
                    vault_gp691_700_authorization_decision_recording_gates
                SET gate_state = 'OPEN'
                WHERE gate_id = ?
                """,
                (
                    receipt.gate_id,
                ),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp691_700_gate_records_are_append_only(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
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
                    vault_gp691_700_authorization_decision_recording_gates
                WHERE gate_id = ?
                """,
                (
                    receipt.gate_id,
                ),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp691_700_events_are_immutable_and_append_only(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

    event = service.list_events(
        receipt.gate_id
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
                    vault_gp691_700_authorization_decision_recording_gate_events
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
                    vault_gp691_700_authorization_decision_recording_gate_events
                WHERE event_id = ?
                """,
                (
                    event["event_id"],
                ),
            )

        connection.rollback()

    finally:
        connection.close()
