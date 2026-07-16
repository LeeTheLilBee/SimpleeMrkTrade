from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from vault.recovery_commit_owner_decision_tower_handoff_delivery_authorization_decision_recording_authority_authorization_gate_service import (
    CURRENT_RECOMMENDATION,
    GATE_STATE,
    RecordingAuthorityAuthorizationGateError,
    RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingAuthorityAuthorizationGateService,
    SAFETY_STATE_FIELDS,
)


def _service(
    tmp_path: Path,
) -> RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingAuthorityAuthorizationGateService:
    return (
        RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingAuthorityAuthorizationGateService(
            tmp_path / "gp811_820.sqlite3"
        )
    )


def _seal(service, **overrides):
    request = {
        "idempotency_key": "gp811-820-case-001",
        "recovery_case_id": "recovery-case-001",
        "owner_decision_record_id": "owner-decision-record-001",
        "authorization_preparation_id": (
            "vault-gp801-810-preparation-001"
        ),
        "authorization_preparation_hash": "a" * 64,
        "authorization_preparation_state": (
            "AUTHORIZATION_DECISION_RECORDING_AUTHORITY_"
            "PREPARATION_SEALED_AUTHORITY_NOT_GRANTED"
        ),
        "tower_authority_id": "tower-authority-001",
        "tower_delivery_target_id": "tower-delivery-target-001",
        "target_environment": "STAGING",
        "safe_metadata": {
            "prior_pack_range": "GP801-GP810",
            "reference_mode": "HASH_AND_IDENTIFIER_ONLY",
            "redaction_profile": "tower-safe",
        },
    }

    request.update(overrides)

    return service.seal_authorization_gate(
        **request
    )


def test_gp811_820_seals_authorization_gate(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    assert receipt.recommendation == CURRENT_RECOMMENDATION
    assert receipt.gate_state == GATE_STATE

    assert receipt.gate_sealed is True
    assert receipt.authorization_granted is False
    assert receipt.recording_authority_authorized is False
    assert receipt.recording_authority_granted is False
    assert receipt.decision_recording_authorized is False
    assert receipt.authorization_decision_recorded is False

    assert receipt.owner_session_created is False
    assert receipt.owner_authenticated is False
    assert receipt.owner_stepped_up is False

    assert receipt.immutable is True
    assert receipt.append_only is True
    assert receipt.idempotent_replay is False

    payload = service.get_gate(
        receipt.gate_id
    )["payload"]

    expected = {
        "gp811_gate_shell": "GP811",
        "gp812_preparation_lineage_gate": "GP812",
        "gp813_authorization_request_gate": "GP813",
        "gp814_scope_binding_gate": "GP814",
        "gp815_evidence_binding_gate": "GP815",
        "gp816_owner_session_gate": "GP816",
        "gp817_second_authority_gate": "GP817",
        "gp818_replay_protection_gate": "GP818",
        "gp819_authorization_blocker_matrix": "GP819",
        "gp820_checkpoint": "GP820",
    }

    for key, pack in expected.items():
        assert payload[key]["pack"] == pack


def test_gp811_820_request_remains_unsent(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    request = service.get_gate(
        receipt.gate_id
    )["payload"]["gp813_authorization_request_gate"]

    assert request["destination"] == "TOWER"
    assert request["authorization_authority"] == "TOWER"

    assert request["request_prepared"] is True
    assert request["request_sent"] is False
    assert request["request_delivered"] is False
    assert request["request_accepted"] is False
    assert request["authorization_granted"] is False


@pytest.mark.parametrize(
    "gate_name",
    [
        "gp814_scope_binding_gate",
        "gp815_evidence_binding_gate",
        "gp816_owner_session_gate",
        "gp817_second_authority_gate",
        "gp818_replay_protection_gate",
    ],
)
def test_gp811_820_subgates_remain_blocked(
    tmp_path: Path,
    gate_name: str,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    gate = service.get_gate(
        receipt.gate_id
    )["payload"][gate_name]

    assert gate["authorization_blocked"] is True


def test_gp811_820_blocker_matrix_remains_false(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    board = service.get_gate(
        receipt.gate_id
    )["payload"]["gp819_authorization_blocker_matrix"]

    assert board["preparation_reference_present"] is True
    assert board["preparation_hash_present"] is True
    assert board["authorization_request_prepared"] is True

    false_fields = (
        "scope_reference_present",
        "scope_hash_present",
        "scope_bindings_verified",
        "decision_value_reference_present",
        "decision_reason_reference_present",
        "evidence_package_reference_present",
        "evidence_package_hash_present",
        "authentication_evidence_present",
        "step_up_evidence_present",
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
        "recording_authority_authorization_granted",
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


def test_gp811_820_safety_state_all_false(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    state = service.get_gate(
        receipt.gate_id
    )["payload"]["gp820_checkpoint"]["safety_state"]

    assert set(state) == set(SAFETY_STATE_FIELDS)
    assert all(value is False for value in state.values())


def test_gp811_820_idempotent_replay(
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


def test_gp811_820_changed_replay_rejected(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    _seal(service)

    with pytest.raises(
        RecordingAuthorityAuthorizationGateError,
        match="different immutable",
    ):
        _seal(
            service,
            target_environment="PRODUCTION",
        )


def test_gp811_820_requires_sealed_preparation(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        RecordingAuthorityAuthorizationGateError,
        match="PREPARATION_SEALED",
    ):
        _seal(
            service,
            authorization_preparation_state=(
                "RECORDING_AUTHORITY_AUTHORIZATION_GRANTED"
            ),
        )


@pytest.mark.parametrize(
    "operation",
    [
        "SEND_RECORDING_AUTHORITY_AUTHORIZATION_REQUEST",
        "GRANT_RECORDING_AUTHORITY_AUTHORIZATION",
        "GRANT_RECORDING_AUTHORITY",
        "AUTHORIZE_RECORDING_AUTHORITY",
        "AUTHORIZE_DECISION_RECORDING",
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
        "DELIVER_HANDOFF",
        "EXECUTE_RECOVERY_COMMIT",
        "RESTORE_DATA",
        "WRITE_PRODUCTION_STORAGE",
        "CONNECT_EXTERNAL_PROVIDER",
        "DELETE_DATA",
        "DESTROY_DATA",
    ],
)
def test_gp811_820_rejects_prohibited_operations(
    tmp_path: Path,
    operation: str,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        RecordingAuthorityAuthorizationGateError,
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
def test_gp811_820_rejects_sensitive_metadata(
    tmp_path: Path,
    safe_metadata,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        RecordingAuthorityAuthorizationGateError,
        match="prohibited",
    ):
        _seal(
            service,
            safe_metadata=safe_metadata,
        )


def test_gp811_820_verification_passes(
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
    assert result["authorization_preparation_lineage_valid"] is True

    assert result["gate_sealed"] is True
    assert result["authorization_request_prepared"] is True
    assert result["authorization_request_sent"] is False

    assert result["recording_authority_authorization_granted"] is False
    assert result["recording_authority_authorized"] is False
    assert result["recording_authority_granted"] is False
    assert result["decision_recording_authorized"] is False
    assert result["authorization_decision_recorded"] is False

    assert result["owner_session_creation_authorized"] is False
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


def test_gp811_820_records_immutable(
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
                    vault_gp811_820_recording_authority_authorization_gates
                SET gate_state = 'AUTHORIZATION_GRANTED'
                WHERE gate_id = ?
                """,
                (receipt.gate_id,),
            )

        connection.rollback()
    finally:
        connection.close()


def test_gp811_820_records_append_only(
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
                    vault_gp811_820_recording_authority_authorization_gates
                WHERE gate_id = ?
                """,
                (receipt.gate_id,),
            )

        connection.rollback()
    finally:
        connection.close()
