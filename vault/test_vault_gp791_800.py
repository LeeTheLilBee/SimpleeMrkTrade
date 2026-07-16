from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from vault.recovery_commit_owner_decision_tower_handoff_delivery_authorization_decision_recording_authority_gate_service import (
    CURRENT_RECOMMENDATION,
    DecisionRecordingAuthorityGateError,
    GATE_STATE,
    RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingAuthorityGateService,
    SAFETY_STATE_FIELDS,
)


def _service(
    tmp_path: Path,
) -> RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingAuthorityGateService:
    return (
        RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingAuthorityGateService(
            tmp_path / "gp791_800.sqlite3"
        )
    )


def _seal(service, **overrides):
    request = {
        "idempotency_key": "gp791-800-case-001",
        "recovery_case_id": "recovery-case-001",
        "owner_decision_record_id": "owner-decision-record-001",
        "recording_preparation_id": (
            "vault-gp781-790-preparation-001"
        ),
        "recording_preparation_hash": "a" * 64,
        "recording_preparation_state": (
            "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_"
            "RECORDING_PREPARATION_SEALED_NOT_AUTHORIZED"
        ),
        "tower_authority_id": "tower-authority-001",
        "tower_delivery_target_id": "tower-delivery-target-001",
        "target_environment": "STAGING",
        "safe_metadata": {
            "prior_pack_range": "GP781-GP790",
            "reference_mode": "HASH_AND_IDENTIFIER_ONLY",
            "redaction_profile": "tower-safe",
        },
    }

    request.update(overrides)

    return service.seal_recording_authority_gate(
        **request
    )


def test_gp791_800_seals_recording_authority_gate(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    assert receipt.recommendation == CURRENT_RECOMMENDATION
    assert receipt.gate_state == GATE_STATE

    assert receipt.gate_sealed is True
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

    payload = service.get_gate(
        receipt.gate_id
    )["payload"]

    expected = {
        "gp791_gate_shell": "GP791",
        "gp792_preparation_lineage_gate": "GP792",
        "gp793_recording_authority_request_gate": "GP793",
        "gp794_decision_reference_gate": "GP794",
        "gp795_evidence_binding_gate": "GP795",
        "gp796_tower_owner_session_gate": "GP796",
        "gp797_second_authority_gate": "GP797",
        "gp798_recording_consumption_gate": "GP798",
        "gp799_recording_authority_blocker_matrix": "GP799",
        "gp800_checkpoint": "GP800",
    }

    for key, pack in expected.items():
        assert payload[key]["pack"] == pack


def test_gp791_800_request_remains_unsent(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    request = service.get_gate(
        receipt.gate_id
    )["payload"]["gp793_recording_authority_request_gate"]

    assert request["destination"] == "TOWER"
    assert request["recording_authority"] == "TOWER"

    assert request["request_prepared"] is True
    assert request["request_sent"] is False
    assert request["request_delivered"] is False
    assert request["request_accepted"] is False
    assert request["recording_authority_granted"] is False


def test_gp791_800_all_subgates_remain_blocked(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    payload = service.get_gate(
        receipt.gate_id
    )["payload"]

    for key in (
        "gp794_decision_reference_gate",
        "gp795_evidence_binding_gate",
        "gp796_tower_owner_session_gate",
        "gp797_second_authority_gate",
        "gp798_recording_consumption_gate",
    ):
        assert payload[key]["recording_authority_blocked"] is True


def test_gp791_800_blocker_matrix_remains_false(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    matrix = service.get_gate(
        receipt.gate_id
    )["payload"]["gp799_recording_authority_blocker_matrix"]

    assert matrix["preparation_reference_present"] is True
    assert matrix["preparation_hash_present"] is True
    assert matrix["recording_authority_request_prepared"] is True

    false_fields = (
        "decision_value_reference_present",
        "decision_reason_reference_present",
        "evidence_package_reference_present",
        "evidence_package_hash_present",
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
        "owner_session_creation_authorized",
        "tower_owner_session_creation_authorized",
        "session_creation_may_proceed",
        "owner_decision_recording_gate_may_open",
    )

    for field in false_fields:
        assert matrix[field] is False


def test_gp791_800_safety_state_all_false(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    state = service.get_gate(
        receipt.gate_id
    )["payload"]["gp800_checkpoint"]["safety_state"]

    assert set(state) == set(SAFETY_STATE_FIELDS)
    assert all(
        value is False
        for value in state.values()
    )


def test_gp791_800_idempotent_replay(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    first = _seal(service)
    second = _seal(service)

    assert first.gate_id == second.gate_id
    assert first.gate_hash == second.gate_hash

    assert first.idempotent_replay is False
    assert second.idempotent_replay is True

    assert len(
        service.list_events(first.gate_id)
    ) == 1


def test_gp791_800_changed_replay_rejected(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    _seal(service)

    with pytest.raises(
        DecisionRecordingAuthorityGateError,
        match="different immutable",
    ):
        _seal(
            service,
            target_environment="PRODUCTION",
        )


def test_gp791_800_requires_sealed_preparation(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        DecisionRecordingAuthorityGateError,
        match="RECORDING_PREPARATION_SEALED",
    ):
        _seal(
            service,
            recording_preparation_state=(
                "RECORDING_AUTHORITY_GRANTED"
            ),
        )


@pytest.mark.parametrize(
    "operation",
    [
        "SEND_RECORDING_AUTHORITY_REQUEST",
        "GRANT_RECORDING_AUTHORITY",
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
def test_gp791_800_rejects_prohibited_operations(
    tmp_path: Path,
    operation: str,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        DecisionRecordingAuthorityGateError,
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
def test_gp791_800_rejects_sensitive_metadata(
    tmp_path: Path,
    safe_metadata,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        DecisionRecordingAuthorityGateError,
        match="prohibited",
    ):
        _seal(
            service,
            safe_metadata=safe_metadata,
        )


def test_gp791_800_verification_passes(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    result = service.verify_gate(
        receipt.gate_id
    )

    assert result["verified"] is True
    assert result["gate_hash_valid"] is True
    assert result["event_chain_valid"] is True
    assert result["tower_destination_only"] is True
    assert result["recording_preparation_lineage_valid"] is True

    assert result["gate_sealed"] is True

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


def test_gp791_800_records_immutable(
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
                UPDATE vault_gp791_800_recording_authority_gates
                SET gate_state = 'AUTHORITY_GRANTED'
                WHERE gate_id = ?
                """,
                (receipt.gate_id,),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp791_800_records_append_only(
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
                DELETE FROM vault_gp791_800_recording_authority_gates
                WHERE gate_id = ?
                """,
                (receipt.gate_id,),
            )

        connection.rollback()

    finally:
        connection.close()
