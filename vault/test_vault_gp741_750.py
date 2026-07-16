from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from vault.recovery_commit_owner_decision_tower_handoff_delivery_authorization_decision_recording_owner_session_creation_authorization_preparation_layer_service import (
    CURRENT_RECOMMENDATION,
    OwnerSessionCreationAuthorizationPreparationError,
    PREPARATION_STATE,
    RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationPreparationLayerService,
    SAFETY_STATE_FIELDS,
)


def _service(
    tmp_path: Path,
) -> RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationPreparationLayerService:
    return (
        RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationPreparationLayerService(
            tmp_path / "gp741_750.sqlite3"
        )
    )


def _seal(service, **overrides):
    request = {
        "idempotency_key": "gp741-750-case-001",
        "recovery_case_id": "recovery-case-001",
        "owner_decision_record_id": "owner-decision-record-001",
        "creation_authorization_gate_id": (
            "vault-gp731-740-gate-001"
        ),
        "creation_authorization_gate_hash": "a" * 64,
        "creation_authorization_gate_state": (
            "OWNER_SESSION_CREATION_AUTHORIZATION_GATE_"
            "SEALED_AUTHORIZATION_NOT_GRANTED"
        ),
        "tower_authority_id": "tower-authority-001",
        "tower_delivery_target_id": "tower-delivery-target-001",
        "target_environment": "STAGING",
        "safe_metadata": {
            "prior_pack_range": "GP731-GP740",
            "reference_mode": "HASH_AND_IDENTIFIER_ONLY",
            "redaction_profile": "tower-safe",
        },
    }

    request.update(overrides)

    return service.seal_authorization_preparation(
        **request
    )


def test_gp741_750_seals_preparation(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    assert receipt.recommendation == CURRENT_RECOMMENDATION
    assert receipt.preparation_state == PREPARATION_STATE

    assert receipt.preparation_sealed is True
    assert receipt.authorization_decision_request_prepared is True
    assert receipt.authorization_granted is False

    assert receipt.owner_session_creation_authorized is False
    assert receipt.tower_owner_session_creation_authorized is False

    assert receipt.owner_session_created is False
    assert receipt.owner_session_started is False
    assert receipt.recording_gate_open is False
    assert receipt.owner_decision_recorded is False

    assert receipt.immutable is True
    assert receipt.append_only is True
    assert receipt.idempotent_replay is False

    payload = service.get_preparation(
        receipt.preparation_id
    )["preparation_payload"]

    expected_packs = {
        "gp741_preparation_shell": "GP741",
        "gp742_gate_lineage_intake": "GP742",
        "gp743_decision_request_envelope": "GP743",
        "gp744_scope_binding_evidence_board": "GP744",
        "gp745_lifetime_evidence_board": "GP745",
        "gp746_replay_evidence_board": "GP746",
        "gp747_authentication_evidence_board": "GP747",
        "gp748_step_up_evidence_board": "GP748",
        "gp749_decision_prerequisite_board": "GP749",
        "gp750_checkpoint": "GP750",
    }

    for key, pack in expected_packs.items():
        assert payload[key]["pack"] == pack


def test_gp741_750_request_prepared_but_not_sent(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    envelope = service.get_preparation(
        receipt.preparation_id
    )["decision_request_envelope"]

    assert envelope["destination"] == "TOWER"
    assert envelope["decision_authority"] == "TOWER"

    assert envelope["request_prepared"] is True
    assert envelope["request_sent"] is False
    assert envelope["request_delivered"] is False
    assert envelope["request_accepted"] is False
    assert envelope["authorization_decision_recorded"] is False
    assert envelope["authorization_granted"] is False


@pytest.mark.parametrize(
    "board_name",
    [
        "scope_binding_evidence_board",
        "lifetime_evidence_board",
        "replay_evidence_board",
        "authentication_evidence_board",
        "step_up_evidence_board",
    ],
)
def test_gp741_750_evidence_remains_absent(
    tmp_path: Path,
    board_name: str,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    board = service.get_preparation(
        receipt.preparation_id
    )[board_name]

    evidence_fields = [
        field
        for field in board
        if field.endswith("_evidence_present")
    ]

    for field in evidence_fields:
        assert board[field] is False

    reference_fields = [
        field
        for field in board
        if field.endswith("_evidence_reference")
    ]

    for field in reference_fields:
        assert board[field] is None

    assert board["authorization_decision_ready"] is False


def test_gp741_750_prerequisites_remain_unsatisfied(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    board = service.get_preparation(
        receipt.preparation_id
    )["decision_prerequisite_board"]

    assert board["prior_gate_reference_present"] is True
    assert board["prior_gate_hash_present"] is True
    assert board["authorization_decision_request_prepared"] is True

    false_fields = (
        "scope_binding_evidence_present",
        "scope_bindings_verified",
        "lifetime_evidence_present",
        "session_lifetime_verified",
        "replay_evidence_present",
        "replay_protection_verified",
        "authentication_evidence_present",
        "owner_authenticated",
        "authentication_verified",
        "step_up_evidence_present",
        "owner_stepped_up",
        "step_up_verified",
        "all_authorization_decision_prerequisites_satisfied",
        "authorization_decision_may_be_recorded",
        "owner_session_creation_authorization_granted",
        "tower_owner_session_creation_authorization_granted",
        "owner_session_creation_authorized",
        "tower_owner_session_creation_authorized",
        "session_creation_may_proceed",
        "recording_gate_may_open",
    )

    for field in false_fields:
        assert board[field] is False


def test_gp741_750_safety_state_is_all_false(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    state = service.get_preparation(
        receipt.preparation_id
    )["checkpoint"]["safety_state"]

    assert set(state) == set(SAFETY_STATE_FIELDS)
    assert all(value is False for value in state.values())


def test_gp741_750_exact_idempotent_replay(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    first = _seal(service)
    second = _seal(service)

    assert first.preparation_id == second.preparation_id
    assert first.preparation_hash == second.preparation_hash

    assert first.idempotent_replay is False
    assert second.idempotent_replay is True

    assert len(
        service.list_events(first.preparation_id)
    ) == 1


def test_gp741_750_rejects_changed_idempotent_input(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    _seal(service)

    with pytest.raises(
        OwnerSessionCreationAuthorizationPreparationError,
        match="different immutable",
    ):
        _seal(
            service,
            target_environment="PRODUCTION",
        )


def test_gp741_750_requires_sealed_not_granted_lineage(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        OwnerSessionCreationAuthorizationPreparationError,
        match="OWNER_SESSION_CREATION_AUTHORIZATION_GATE",
    ):
        _seal(
            service,
            creation_authorization_gate_state=(
                "AUTHORIZATION_GRANTED"
            ),
        )


@pytest.mark.parametrize(
    "operation",
    [
        "SEND_AUTHORIZATION_DECISION_REQUEST",
        "DELIVER_AUTHORIZATION_DECISION_REQUEST",
        "ACCEPT_AUTHORIZATION_DECISION_REQUEST",
        "AUTHORIZE_OWNER_SESSION_CREATION",
        "AUTHORIZE_TOWER_OWNER_SESSION_CREATION",
        "GRANT_OWNER_SESSION_CREATION_AUTHORIZATION",
        "GRANT_TOWER_OWNER_SESSION_CREATION_AUTHORIZATION",
        "CREATE_OWNER_SESSION",
        "START_OWNER_SESSION",
        "ISSUE_OWNER_SESSION",
        "ACTIVATE_OWNER_SESSION",
        "CREATE_TOWER_OWNER_SESSION",
        "START_TOWER_OWNER_SESSION",
        "ISSUE_TOWER_OWNER_SESSION",
        "ACTIVATE_TOWER_OWNER_SESSION",
        "AUTHENTICATE_OWNER",
        "STEP_UP_OWNER",
        "OPEN_OWNER_DECISION_RECORDING_GATE",
        "RECOMMEND_OWNER_DECISION",
        "DEFAULT_OWNER_DECISION",
        "SELECT_OWNER_DECISION",
        "INVENT_OWNER_DECISION",
        "RECORD_OWNER_DECISION",
        "GRANT_GO_DECISION",
        "ISSUE_RECOVERY_AUTHORIZATION",
        "ISSUE_AUTHORIZATION_TOKEN",
        "EXECUTE_RECOVERY_COMMIT",
        "RESTORE_DATA",
        "WRITE_PRODUCTION_STORAGE",
        "CONNECT_EXTERNAL_PROVIDER",
        "DELETE_DATA",
        "DESTROY_DATA",
    ],
)
def test_gp741_750_rejects_prohibited_operations(
    tmp_path: Path,
    operation: str,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        OwnerSessionCreationAuthorizationPreparationError,
        match="prohibited operation",
    ):
        _seal(
            service,
            idempotency_key=(
                "prohibited-" + operation.lower()
            ),
            requested_operations=[operation],
        )


@pytest.mark.parametrize(
    "safe_metadata",
    [
        {"raw_path": "/tmp/raw"},
        {"raw_url": "https://example.test/raw"},
        {"token": "do-not-store"},
        {"authorization_token": "do-not-store"},
        {"session_token": "do-not-store"},
        {"session_id": "do-not-store"},
        {"credentials": {"username": "x"}},
        {"nested": {"private_key": "x"}},
        {"raw_material": {"content": "x"}},
        {"provider_secret": "x"},
    ],
)
def test_gp741_750_rejects_sensitive_metadata(
    tmp_path: Path,
    safe_metadata,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        OwnerSessionCreationAuthorizationPreparationError,
        match="prohibited",
    ):
        _seal(
            service,
            safe_metadata=safe_metadata,
        )


def test_gp741_750_verification_passes(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    result = service.verify_preparation(
        receipt.preparation_id
    )

    assert result["verified"] is True
    assert result["preparation_hash_valid"] is True
    assert result["event_chain_valid"] is True
    assert result["tower_destination_only"] is True
    assert result["authorization_gate_lineage_valid"] is True

    assert result["preparation_sealed"] is True
    assert result["authorization_decision_request_prepared"] is True
    assert result["authorization_decision_request_sent"] is False
    assert result["authorization_decision_recorded"] is False

    assert result["authorization_granted"] is False

    assert result["owner_session_creation_authorization_granted"] is False
    assert (
        result["tower_owner_session_creation_authorization_granted"]
        is False
    )

    assert result["owner_session_creation_authorized"] is False
    assert result["tower_owner_session_creation_authorized"] is False

    assert result["owner_session_created"] is False
    assert result["owner_session_started"] is False
    assert result["owner_session_issued"] is False
    assert result["owner_session_activated"] is False

    assert result["owner_authenticated"] is False
    assert result["owner_stepped_up"] is False

    assert result["recording_gate_open"] is False
    assert result["owner_decision_recorded"] is False

    assert result["go_decision_granted"] is False
    assert result["recovery_authorization_granted"] is False
    assert result["authorization_token_issued"] is False

    assert result["recovery_commit_command_issued"] is False
    assert result["recovery_commit_executed"] is False

    assert result["production_write_occurred"] is False
    assert result["provider_connection_occurred"] is False
    assert result["destructive_action_occurred"] is False

    assert result["unsafe_completed_actions"] == []


def test_gp741_750_records_are_immutable(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    connection = sqlite3.connect(
        str(service.database_path)
    )

    try:
        with pytest.raises(
            sqlite3.IntegrityError,
            match="immutable",
        ):
            connection.execute(
                """
                UPDATE
                    vault_gp741_750_owner_session_creation_authorization_preparations
                SET preparation_state = 'AUTHORIZED'
                WHERE preparation_id = ?
                """,
                (receipt.preparation_id,),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp741_750_records_are_append_only(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    connection = sqlite3.connect(
        str(service.database_path)
    )

    try:
        with pytest.raises(
            sqlite3.IntegrityError,
            match="append-only",
        ):
            connection.execute(
                """
                DELETE FROM
                    vault_gp741_750_owner_session_creation_authorization_preparations
                WHERE preparation_id = ?
                """,
                (receipt.preparation_id,),
            )

        connection.rollback()

    finally:
        connection.close()
