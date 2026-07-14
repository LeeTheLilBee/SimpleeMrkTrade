from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from vault.recovery_commit_owner_decision_tower_handoff_delivery_authorization_decision_recording_owner_session_requirement_gate_service import (
    CURRENT_RECOMMENDATION,
    GATE_STATE,
    OwnerSessionRequirementGateError,
    RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionRequirementGateService,
    SAFETY_STATE_FIELDS,
)


def _service(
    tmp_path: Path,
) -> RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionRequirementGateService:
    return (
        RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionRequirementGateService(
            tmp_path / "gp711_720.sqlite3"
        )
    )


def _seal(
    service,
    **overrides,
):
    request = {
        "idempotency_key": "gp711-720-case-001",
        "recovery_case_id": "recovery-case-001",
        "owner_decision_record_id": (
            "owner-decision-record-001"
        ),
        "recording_preparation_id": (
            "vault-gp701-710-preparation-001"
        ),
        "recording_preparation_hash": (
            "a" * 64
        ),
        "recording_preparation_state": (
            "AUTHORIZATION_DECISION_RECORDING_"
            "PREPARED_GATE_REMAINS_CLOSED"
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
            "prior_pack_range": "GP701-GP710",
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

    return service.seal_owner_session_requirement_gate(
        **request
    )


def test_gp711_720_seals_owner_session_requirement_gate(
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
    assert receipt.owner_session_required is True

    assert (
        receipt.owner_session_created
        is False
    )

    assert (
        receipt.owner_session_started
        is False
    )

    assert (
        receipt.tower_owner_session_created
        is False
    )

    assert (
        receipt.tower_owner_session_started
        is False
    )

    assert (
        receipt.recording_gate_open
        is False
    )

    assert (
        receipt.owner_decision_recorded
        is False
    )

    assert receipt.immutable is True
    assert receipt.append_only is True
    assert receipt.idempotent_replay is False

    record = service.get_gate(
        receipt.gate_id
    )

    payload = record[
        "gate_payload"
    ]

    assert (
        payload[
            "gp711_gate_shell"
        ]["pack"]
        == "GP711"
    )

    assert (
        payload[
            "gp712_preparation_lineage_gate"
        ]["pack"]
        == "GP712"
    )

    assert (
        payload[
            "gp713_owner_session_contract_board"
        ]["pack"]
        == "GP713"
    )

    assert (
        payload[
            "gp714_tower_session_authority_board"
        ]["pack"]
        == "GP714"
    )

    assert (
        payload[
            "gp715_session_binding_requirement_board"
        ]["pack"]
        == "GP715"
    )

    assert (
        payload[
            "gp716_session_expiry_requirement_board"
        ]["pack"]
        == "GP716"
    )

    assert (
        payload[
            "gp717_replay_protection_requirement_board"
        ]["pack"]
        == "GP717"
    )

    assert (
        payload[
            "gp718_session_prerequisite_matrix"
        ]["pack"]
        == "GP718"
    )

    assert (
        payload[
            "gp719_session_blocker_board"
        ]["pack"]
        == "GP719"
    )

    assert (
        payload[
            "gp720_checkpoint"
        ]["pack"]
        == "GP720"
    )


def test_gp711_720_session_contract_remains_absent(
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

    contract = record[
        "owner_session_contract_board"
    ]

    assert (
        contract["session_required"]
        is True
    )

    assert (
        contract["session_created"]
        is False
    )

    assert (
        contract["session_started"]
        is False
    )

    assert (
        contract["session_issued"]
        is False
    )

    assert (
        contract["session_activated"]
        is False
    )

    assert (
        contract["session_reference"]
        is None
    )


def test_gp711_720_vault_and_teller_cannot_create_owner_session(
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

    board = record[
        "tower_session_authority_board"
    ]

    assert (
        board["tower_is_session_authority"]
        is True
    )

    assert (
        board["vault_may_create_owner_session"]
        is False
    )

    assert (
        board["vault_may_start_owner_session"]
        is False
    )

    assert (
        board["teller_may_create_owner_session"]
        is False
    )

    assert (
        board["teller_may_start_owner_session"]
        is False
    )

    assert (
        board["direct_user_vault_session_allowed"]
        is False
    )


def test_gp711_720_session_prerequisites_remain_unsatisfied(
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
        "session_prerequisite_matrix"
    ]

    assert (
        matrix["owner_session_created"]
        is False
    )

    assert (
        matrix["owner_session_started"]
        is False
    )

    assert (
        matrix["tower_owner_session_created"]
        is False
    )

    assert (
        matrix["tower_owner_session_started"]
        is False
    )

    assert (
        matrix["session_binding_receipt_present"]
        is False
    )

    assert (
        matrix["session_expiry_verified"]
        is False
    )

    assert (
        matrix["session_replay_protection_verified"]
        is False
    )

    assert (
        matrix["owner_authenticated"]
        is False
    )

    assert (
        matrix["owner_stepped_up"]
        is False
    )

    assert (
        matrix["all_owner_session_prerequisites_satisfied"]
        is False
    )

    assert (
        matrix["recording_gate_may_open"]
        is False
    )


def test_gp711_720_safety_state_is_all_false(
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
        "session_blocker_board"
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


def test_gp711_720_exact_idempotent_replay(
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


def test_gp711_720_rejects_changed_idempotent_inputs(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    _seal(
        service
    )

    with pytest.raises(
        OwnerSessionRequirementGateError,
        match="different immutable",
    ):
        _seal(
            service,
            target_environment="PRODUCTION",
        )


def test_gp711_720_requires_closed_recording_preparation_lineage(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        OwnerSessionRequirementGateError,
        match="AUTHORIZATION_DECISION_RECORDING",
    ):
        _seal(
            service,
            recording_preparation_state=(
                "OWNER_SESSION_STARTED"
            ),
        )


@pytest.mark.parametrize(
    "operation",
    [
        "CREATE_OWNER_SESSION",
        "START_OWNER_SESSION",
        "CREATE_TOWER_OWNER_SESSION",
        "START_TOWER_OWNER_SESSION",
        "ISSUE_OWNER_SESSION",
        "ACTIVATE_OWNER_SESSION",
        "AUTHENTICATE_OWNER",
        "STEP_UP_OWNER",
        "OPEN_OWNER_DECISION_RECORDING_GATE",
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
def test_gp711_720_rejects_prohibited_operations(
    tmp_path: Path,
    operation: str,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        OwnerSessionRequirementGateError,
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
            "session_token": "do-not-store"
        },
        {
            "session_cookie": "do-not-store"
        },
        {
            "session_secret": "do-not-store"
        },
        {
            "session_id": "do-not-store"
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
def test_gp711_720_rejects_raw_secret_or_session_metadata(
    tmp_path: Path,
    safe_metadata,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        OwnerSessionRequirementGateError,
        match="prohibited",
    ):
        _seal(
            service,
            safe_metadata=safe_metadata,
        )


def test_gp711_720_verification_passes(
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
        result["recording_preparation_closed_lineage"]
        is True
    )

    assert result["gate_sealed"] is True
    assert result["owner_session_required"] is True

    assert (
        result["owner_session_created"]
        is False
    )

    assert (
        result["owner_session_started"]
        is False
    )

    assert (
        result["owner_session_issued"]
        is False
    )

    assert (
        result["owner_session_activated"]
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
        result["session_binding_receipt_present"]
        is False
    )

    assert (
        result["session_expiry_verified"]
        is False
    )

    assert (
        result["session_replay_protection_verified"]
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
        result["recording_gate_open"]
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
        result["destructive_action_occurred"]
        is False
    )

    assert (
        result["unsafe_completed_actions"]
        == []
    )


def test_gp711_720_gate_records_are_immutable(
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
                    vault_gp711_720_owner_session_requirement_gates
                SET gate_state = 'SESSION_ACTIVE'
                WHERE gate_id = ?
                """,
                (
                    receipt.gate_id,
                ),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp711_720_gate_records_are_append_only(
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
                    vault_gp711_720_owner_session_requirement_gates
                WHERE gate_id = ?
                """,
                (
                    receipt.gate_id,
                ),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp711_720_events_are_immutable_and_append_only(
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
                    vault_gp711_720_owner_session_requirement_gate_events
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
                    vault_gp711_720_owner_session_requirement_gate_events
                WHERE event_id = ?
                """,
                (
                    event["event_id"],
                ),
            )

        connection.rollback()

    finally:
        connection.close()
