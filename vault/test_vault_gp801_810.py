from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from vault.recovery_commit_owner_decision_tower_handoff_delivery_authorization_decision_recording_authority_preparation_layer_service import (
    CURRENT_RECOMMENDATION,
    PREPARATION_STATE,
    RecordingAuthorityPreparationError,
    RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingAuthorityPreparationLayerService,
    SAFETY_STATE_FIELDS,
)


def _service(
    tmp_path: Path,
) -> RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingAuthorityPreparationLayerService:
    return (
        RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingAuthorityPreparationLayerService(
            tmp_path / "gp801_810.sqlite3"
        )
    )


def _seal(service, **overrides):
    request = {
        "idempotency_key": "gp801-810-case-001",
        "recovery_case_id": "recovery-case-001",
        "owner_decision_record_id": "owner-decision-record-001",
        "recording_authority_gate_id": (
            "vault-gp791-800-recording-authority-gate-001"
        ),
        "recording_authority_gate_hash": "a" * 64,
        "recording_authority_gate_state": (
            "AUTHORIZATION_DECISION_RECORDING_"
            "AUTHORITY_GATE_SEALED_AUTHORITY_NOT_GRANTED"
        ),
        "tower_authority_id": "tower-authority-001",
        "tower_delivery_target_id": "tower-delivery-target-001",
        "target_environment": "STAGING",
        "safe_metadata": {
            "prior_pack_range": "GP791-GP800",
            "reference_mode": "HASH_AND_IDENTIFIER_ONLY",
            "redaction_profile": "tower-safe",
        },
    }

    request.update(overrides)

    return service.seal_recording_authority_preparation(
        **request
    )


def test_gp801_810_seals_preparation(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    assert receipt.recommendation == CURRENT_RECOMMENDATION
    assert receipt.preparation_state == PREPARATION_STATE

    assert receipt.preparation_sealed is True
    assert receipt.authorization_request_prepared is True

    assert receipt.recording_authority_granted is False
    assert receipt.recording_authority_authorized is False
    assert receipt.decision_recording_authorized is False
    assert receipt.authorization_decision_recorded is False

    assert receipt.owner_session_created is False
    assert receipt.owner_authenticated is False
    assert receipt.owner_stepped_up is False

    assert receipt.immutable is True
    assert receipt.append_only is True
    assert receipt.idempotent_replay is False

    payload = service.get_preparation(
        receipt.preparation_id
    )["payload"]

    expected = {
        "gp801_preparation_shell": "GP801",
        "gp802_gate_lineage_intake": "GP802",
        "gp803_authorization_request_envelope": "GP803",
        "gp804_scope_requirement_board": "GP804",
        "gp805_evidence_requirement_board": "GP805",
        "gp806_tower_owner_session_board": "GP806",
        "gp807_second_authority_board": "GP807",
        "gp808_replay_protection_board": "GP808",
        "gp809_authorization_prerequisite_board": "GP809",
        "gp810_checkpoint": "GP810",
    }

    for key, pack in expected.items():
        assert payload[key]["pack"] == pack


def test_gp801_810_request_remains_unsent(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    envelope = service.get_preparation(
        receipt.preparation_id
    )["payload"]["gp803_authorization_request_envelope"]

    assert envelope["destination"] == "TOWER"
    assert envelope["authorization_authority"] == "TOWER"

    assert envelope["request_prepared"] is True
    assert envelope["request_sent"] is False
    assert envelope["request_delivered"] is False
    assert envelope["request_accepted"] is False
    assert envelope["recording_authority_granted"] is False


def test_gp801_810_requirements_remain_unsatisfied(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    payload = service.get_preparation(
        receipt.preparation_id
    )["payload"]

    scope = payload["gp804_scope_requirement_board"]
    evidence = payload["gp805_evidence_requirement_board"]
    session = payload["gp806_tower_owner_session_board"]
    second_authority = payload["gp807_second_authority_board"]
    replay = payload["gp808_replay_protection_board"]

    assert scope["scope_reference_present"] is False
    assert scope["scope_hash_present"] is False
    assert scope["scope_bindings_verified"] is False

    assert evidence["decision_value_reference_present"] is False
    assert evidence["decision_reason_reference_present"] is False
    assert evidence["evidence_package_reference_present"] is False
    assert evidence["all_evidence_requirements_satisfied"] is False

    assert session["tower_owner_session_present"] is False
    assert session["owner_authenticated"] is False
    assert session["owner_stepped_up"] is False
    assert session["session_bindings_verified"] is False

    assert second_authority["owner_admin_approval_granted"] is False
    assert second_authority["second_authority_review_granted"] is False
    assert second_authority["dual_receipt_satisfied"] is False

    assert replay["authorization_nonce_reference_present"] is False
    assert replay["authorization_consumption_receipt_present"] is False
    assert replay["replay_protection_verified"] is False


def test_gp801_810_prerequisite_board_remains_false(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    board = service.get_preparation(
        receipt.preparation_id
    )["payload"]["gp809_authorization_prerequisite_board"]

    assert board["gate_reference_present"] is True
    assert board["gate_hash_present"] is True
    assert board["authorization_request_prepared"] is True

    false_fields = (
        "scope_reference_present",
        "scope_hash_present",
        "scope_bindings_verified",
        "decision_value_reference_present",
        "decision_reason_reference_present",
        "evidence_package_reference_present",
        "evidence_package_hash_present",
        "all_evidence_requirements_satisfied",
        "tower_owner_session_present",
        "owner_authenticated",
        "owner_stepped_up",
        "session_bindings_verified",
        "owner_admin_approval_granted",
        "second_authority_review_granted",
        "dual_receipt_satisfied",
        "authorization_nonce_reference_present",
        "authorization_consumption_receipt_present",
        "replay_protection_verified",
        "all_authorization_prerequisites_satisfied",
        "recording_authority_authorized",
        "recording_authority_granted",
        "decision_recording_authorized",
        "authorization_decision_may_be_recorded",
        "authorization_decision_recorded",
        "owner_session_creation_authorized",
        "session_creation_may_proceed",
    )

    for field in false_fields:
        assert board[field] is False


def test_gp801_810_safety_state_all_false(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    state = service.get_preparation(
        receipt.preparation_id
    )["payload"]["gp810_checkpoint"]["safety_state"]

    assert set(state) == set(SAFETY_STATE_FIELDS)

    assert all(
        value is False
        for value in state.values()
    )


def test_gp801_810_idempotent_replay(
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


def test_gp801_810_changed_replay_rejected(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    _seal(service)

    with pytest.raises(
        RecordingAuthorityPreparationError,
        match="different immutable",
    ):
        _seal(
            service,
            target_environment="PRODUCTION",
        )


def test_gp801_810_requires_sealed_prior_gate(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        RecordingAuthorityPreparationError,
        match="AUTHORITY_GATE_SEALED",
    ):
        _seal(
            service,
            recording_authority_gate_state=(
                "RECORDING_AUTHORITY_GRANTED"
            ),
        )


@pytest.mark.parametrize(
    "operation",
    [
        "SEND_RECORDING_AUTHORITY_AUTHORIZATION_REQUEST",
        "GRANT_RECORDING_AUTHORITY",
        "AUTHORIZE_RECORDING_AUTHORITY",
        "AUTHORIZE_DECISION_RECORDING",
        "OPEN_RECORDING_AUTHORITY_AUTHORIZATION_GATE",
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
def test_gp801_810_rejects_prohibited_operations(
    tmp_path: Path,
    operation: str,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        RecordingAuthorityPreparationError,
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
def test_gp801_810_rejects_sensitive_metadata(
    tmp_path: Path,
    safe_metadata,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        RecordingAuthorityPreparationError,
        match="prohibited",
    ):
        _seal(
            service,
            safe_metadata=safe_metadata,
        )


def test_gp801_810_verification_passes(
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
    assert result["recording_authority_gate_lineage_valid"] is True

    assert result["preparation_sealed"] is True

    assert result["authorization_request_prepared"] is True
    assert result["authorization_request_sent"] is False
    assert result["authorization_request_delivered"] is False
    assert result["authorization_request_accepted"] is False

    assert result["recording_authority_authorized"] is False
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


def test_gp801_810_records_immutable(
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
                UPDATE vault_gp801_810_recording_authority_preparations
                SET preparation_state = 'AUTHORITY_GRANTED'
                WHERE preparation_id = ?
                """,
                (receipt.preparation_id,),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp801_810_records_append_only(
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
                DELETE FROM vault_gp801_810_recording_authority_preparations
                WHERE preparation_id = ?
                """,
                (receipt.preparation_id,),
            )

        connection.rollback()

    finally:
        connection.close()
