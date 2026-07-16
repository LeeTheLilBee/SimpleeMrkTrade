from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from vault.recovery_commit_owner_decision_tower_handoff_delivery_authorization_decision_recording_owner_session_creation_authorization_decision_recording_preparation_layer_service import (
    CURRENT_RECOMMENDATION,
    DecisionRecordingPreparationError,
    PREPARATION_STATE,
    RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionRecordingPreparationLayerService,
    SAFETY_STATE_FIELDS,
)


def _service(
    tmp_path: Path,
) -> RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionRecordingPreparationLayerService:
    return (
        RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionRecordingPreparationLayerService(
            tmp_path / "gp781_790.sqlite3"
        )
    )


def _seal(service, **overrides):
    request = {
        "idempotency_key": "gp781-790-case-001",
        "recovery_case_id": "recovery-case-001",
        "owner_decision_record_id": "owner-decision-record-001",
        "prior_recording_gate_id": "vault-gp771-780-gate-001",
        "prior_recording_gate_hash": "a" * 64,
        "prior_recording_gate_state": (
            "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_"
            "RECORDING_GATE_SEALED_RECORDING_NOT_AUTHORIZED"
        ),
        "tower_authority_id": "tower-authority-001",
        "tower_delivery_target_id": "tower-delivery-target-001",
        "target_environment": "STAGING",
        "safe_metadata": {
            "prior_pack_range": "GP771-GP780",
            "reference_mode": "HASH_AND_IDENTIFIER_ONLY",
            "redaction_profile": "tower-safe",
        },
    }

    request.update(overrides)

    return service.seal_recording_preparation(
        **request
    )


def test_gp781_790_seals_recording_preparation(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    assert receipt.recommendation == CURRENT_RECOMMENDATION
    assert receipt.preparation_state == PREPARATION_STATE

    assert receipt.preparation_sealed is True
    assert receipt.recording_authority_request_prepared is True
    assert receipt.recording_authority_granted is False
    assert receipt.decision_recording_authorized is False
    assert receipt.authorization_decision_recorded is False
    assert receipt.authorization_granted is False

    assert receipt.owner_session_created is False
    assert receipt.owner_session_started is False
    assert receipt.owner_authenticated is False
    assert receipt.owner_stepped_up is False

    assert receipt.immutable is True
    assert receipt.append_only is True
    assert receipt.idempotent_replay is False

    payload = service.get_preparation(
        receipt.preparation_id
    )["payload"]

    expected = {
        "gp781_preparation_shell": "GP781",
        "gp782_prior_gate_lineage": "GP782",
        "gp783_recording_authority_request": "GP783",
        "gp784_decision_value_reference_board": "GP784",
        "gp785_decision_reason_reference_board": "GP785",
        "gp786_evidence_package_board": "GP786",
        "gp787_tower_owner_session_board": "GP787",
        "gp788_recording_consumption_board": "GP788",
        "gp789_recording_authority_prerequisites": "GP789",
        "gp790_checkpoint": "GP790",
    }

    for key, pack in expected.items():
        assert payload[key]["pack"] == pack


def test_gp781_790_authority_request_unsent(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    request = service.get_preparation(
        receipt.preparation_id
    )["payload"]["gp783_recording_authority_request"]

    assert request["destination"] == "TOWER"
    assert request["recording_authority"] == "TOWER"

    assert request["request_prepared"] is True
    assert request["request_sent"] is False
    assert request["request_delivered"] is False
    assert request["request_accepted"] is False
    assert request["recording_authority_granted"] is False


def test_gp781_790_references_remain_absent(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    payload = service.get_preparation(
        receipt.preparation_id
    )["payload"]

    value_board = payload[
        "gp784_decision_value_reference_board"
    ]
    reason_board = payload[
        "gp785_decision_reason_reference_board"
    ]
    evidence_board = payload[
        "gp786_evidence_package_board"
    ]

    assert value_board["decision_value_reference_present"] is False
    assert value_board["decision_value_present"] is False
    assert value_board["decision_value_selected"] is False
    assert value_board["decision_value_invented"] is False

    assert reason_board["decision_reason_reference_present"] is False
    assert reason_board["raw_reason_allowed"] is False

    assert evidence_board["evidence_package_reference_present"] is False
    assert evidence_board["evidence_package_hash_present"] is False
    assert evidence_board["all_evidence_bindings_verified"] is False


def test_gp781_790_prerequisites_remain_false(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    board = service.get_preparation(
        receipt.preparation_id
    )["payload"]["gp789_recording_authority_prerequisites"]

    assert board["prior_gate_reference_present"] is True
    assert board["prior_gate_hash_present"] is True
    assert board["recording_authority_request_prepared"] is True

    false_fields = (
        "decision_value_reference_present",
        "decision_reason_reference_present",
        "evidence_package_reference_present",
        "all_evidence_bindings_verified",
        "tower_owner_session_present",
        "owner_authenticated",
        "owner_stepped_up",
        "owner_admin_approval_granted",
        "second_authority_review_granted",
        "dual_receipt_satisfied",
        "decision_nonce_reference_present",
        "recording_consumption_receipt_present",
        "replay_protection_verified",
        "all_recording_authority_prerequisites_satisfied",
        "recording_authority_granted",
        "decision_recording_authorized",
        "authorization_decision_may_be_recorded",
        "authorization_decision_recorded",
        "authorization_granted",
    )

    for field in false_fields:
        assert board[field] is False


def test_gp781_790_safety_state_all_false(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    state = service.get_preparation(
        receipt.preparation_id
    )["payload"]["gp790_checkpoint"]["safety_state"]

    assert set(state) == set(SAFETY_STATE_FIELDS)
    assert all(value is False for value in state.values())


def test_gp781_790_idempotent_replay(
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


def test_gp781_790_changed_replay_rejected(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    _seal(service)

    with pytest.raises(
        DecisionRecordingPreparationError,
        match="different immutable",
    ):
        _seal(
            service,
            target_environment="PRODUCTION",
        )


def test_gp781_790_requires_sealed_prior_gate(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        DecisionRecordingPreparationError,
        match="RECORDING_GATE_SEALED",
    ):
        _seal(
            service,
            prior_recording_gate_state=(
                "RECORDING_AUTHORIZED"
            ),
        )


@pytest.mark.parametrize(
    "operation",
    [
        "SEND_RECORDING_AUTHORITY_REQUEST",
        "AUTHORIZE_DECISION_RECORDING",
        "OPEN_DECISION_RECORDING_AUTHORITY_GATE",
        "RECORD_AUTHORIZATION_DECISION",
        "GRANT_OWNER_SESSION_CREATION_AUTHORIZATION",
        "AUTHORIZE_OWNER_SESSION_CREATION",
        "CREATE_OWNER_SESSION",
        "START_OWNER_SESSION",
        "AUTHENTICATE_OWNER",
        "STEP_UP_OWNER",
        "OPEN_OWNER_DECISION_RECORDING_GATE",
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
def test_gp781_790_rejects_prohibited_operations(
    tmp_path: Path,
    operation: str,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        DecisionRecordingPreparationError,
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
        {"session_id": "do-not-store"},
        {"decision_value": "GRANT"},
        {"selected_decision": "GRANT"},
        {"owner_decision": "GRANT"},
        {"decision_reason": "invented"},
        {"credentials": {"username": "x"}},
        {"nested": {"private_key": "x"}},
        {"raw_material": {"content": "x"}},
    ],
)
def test_gp781_790_rejects_sensitive_metadata(
    tmp_path: Path,
    safe_metadata,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        DecisionRecordingPreparationError,
        match="prohibited",
    ):
        _seal(
            service,
            safe_metadata=safe_metadata,
        )


def test_gp781_790_verification_passes(
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
    assert result["prior_recording_gate_lineage_valid"] is True

    assert result["preparation_sealed"] is True
    assert result["recording_authority_request_prepared"] is True
    assert result["recording_authority_request_sent"] is False
    assert result["recording_authority_granted"] is False

    assert result["decision_recording_authorized"] is False
    assert result["authorization_decision_recorded"] is False
    assert result["authorization_granted"] is False

    assert result["owner_session_creation_authorized"] is False
    assert result["tower_owner_session_creation_authorized"] is False

    assert result["owner_session_created"] is False
    assert result["owner_session_started"] is False

    assert result["owner_authenticated"] is False
    assert result["owner_stepped_up"] is False

    assert result["owner_decision_recording_gate_open"] is False
    assert result["owner_decision_recorded"] is False

    assert result["recovery_commit_executed"] is False
    assert result["production_write_occurred"] is False
    assert result["provider_connection_occurred"] is False
    assert result["destructive_action_occurred"] is False

    assert result["unsafe_completed_actions"] == []


def test_gp781_790_records_immutable(
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
                UPDATE vault_gp781_790_recording_preparations
                SET preparation_state = 'AUTHORIZED'
                WHERE preparation_id = ?
                """,
                (receipt.preparation_id,),
            )

        connection.rollback()
    finally:
        connection.close()


def test_gp781_790_records_append_only(
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
                DELETE FROM vault_gp781_790_recording_preparations
                WHERE preparation_id = ?
                """,
                (receipt.preparation_id,),
            )

        connection.rollback()
    finally:
        connection.close()
