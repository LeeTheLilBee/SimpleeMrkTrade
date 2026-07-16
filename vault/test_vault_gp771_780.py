from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from vault.recovery_commit_owner_decision_tower_handoff_delivery_authorization_decision_recording_owner_session_creation_authorization_decision_recording_gate_service import (
    CURRENT_RECOMMENDATION,
    GATE_STATE,
    OwnerSessionCreationAuthorizationDecisionRecordingGateError,
    RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionRecordingGateService,
    SAFETY_STATE_FIELDS,
)


def _service(
    tmp_path: Path,
) -> RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionRecordingGateService:
    return (
        RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionRecordingGateService(
            tmp_path / "gp771_780.sqlite3"
        )
    )


def _seal(service, **overrides):
    request = {
        "idempotency_key": "gp771-780-case-001",
        "recovery_case_id": "recovery-case-001",
        "owner_decision_record_id": "owner-decision-record-001",
        "decision_preparation_id": (
            "vault-gp761-770-preparation-001"
        ),
        "decision_preparation_hash": "a" * 64,
        "decision_preparation_state": (
            "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_"
            "PREPARATION_SEALED_DECISION_NOT_RECORDED"
        ),
        "tower_authority_id": "tower-authority-001",
        "tower_delivery_target_id": "tower-delivery-target-001",
        "target_environment": "STAGING",
        "safe_metadata": {
            "prior_pack_range": "GP761-GP770",
            "reference_mode": "HASH_AND_IDENTIFIER_ONLY",
            "redaction_profile": "tower-safe",
        },
    }

    request.update(overrides)

    return service.seal_decision_recording_gate(
        **request
    )


def test_gp771_780_seals_recording_gate(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    assert receipt.recommendation == CURRENT_RECOMMENDATION
    assert receipt.gate_state == GATE_STATE

    assert receipt.gate_sealed is True
    assert receipt.decision_recording_authorized is False
    assert receipt.authorization_decision_recorded is False
    assert receipt.authorization_granted is False

    assert receipt.owner_session_creation_authorized is False
    assert receipt.owner_session_created is False
    assert receipt.owner_session_started is False

    assert receipt.recording_gate_open is False
    assert receipt.owner_decision_recorded is False

    assert receipt.immutable is True
    assert receipt.append_only is True
    assert receipt.idempotent_replay is False

    payload = service.get_gate(
        receipt.gate_id
    )["gate_payload"]

    expected_packs = {
        "gp771_gate_shell": "GP771",
        "gp772_preparation_lineage_gate": "GP772",
        "gp773_recording_request_gate": "GP773",
        "gp774_decision_value_gate": "GP774",
        "gp775_decision_reason_gate": "GP775",
        "gp776_evidence_binding_gate": "GP776",
        "gp777_authority_gate": "GP777",
        "gp778_replay_protection_gate": "GP778",
        "gp779_recording_blocker_matrix": "GP779",
        "gp780_checkpoint": "GP780",
    }

    for key, pack in expected_packs.items():
        assert payload[key]["pack"] == pack


def test_gp771_780_request_remains_unsent(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    gate = service.get_gate(
        receipt.gate_id
    )["recording_request_gate"]

    assert gate["destination"] == "TOWER"
    assert gate["recording_authority"] == "TOWER"

    assert gate["request_prepared"] is True
    assert gate["request_sent"] is False
    assert gate["request_delivered"] is False
    assert gate["request_accepted"] is False

    assert gate["decision_recording_authorized"] is False
    assert gate["authorization_decision_recorded"] is False
    assert gate["authorization_granted"] is False


def test_gp771_780_no_decision_value_or_reason(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    record = service.get_gate(
        receipt.gate_id
    )

    value_gate = record["decision_value_gate"]
    reason_gate = record["decision_reason_gate"]

    assert value_gate["decision_value_present"] is False
    assert value_gate["decision_value_selected"] is False
    assert value_gate["decision_value_invented"] is False
    assert value_gate["default_decision_allowed"] is False
    assert value_gate["implicit_decision_allowed"] is False
    assert value_gate["decision_recording_blocked"] is True

    assert reason_gate["decision_reason_present"] is False
    assert reason_gate["decision_reason_reference_present"] is False
    assert reason_gate["freeform_raw_reason_allowed"] is False
    assert reason_gate["decision_recording_blocked"] is True


@pytest.mark.parametrize(
    "gate_name",
    [
        "decision_value_gate",
        "decision_reason_gate",
        "evidence_binding_gate",
        "authority_gate",
        "replay_protection_gate",
    ],
)
def test_gp771_780_all_recording_gates_remain_blocked(
    tmp_path: Path,
    gate_name: str,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    gate = service.get_gate(
        receipt.gate_id
    )[gate_name]

    assert gate["decision_recording_blocked"] is True


def test_gp771_780_recording_matrix_remains_false(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    matrix = service.get_gate(
        receipt.gate_id
    )["recording_blocker_matrix"]

    assert matrix["preparation_reference_present"] is True
    assert matrix["preparation_hash_present"] is True
    assert matrix["decision_recording_request_prepared"] is True

    false_fields = (
        "decision_value_present",
        "decision_value_selected",
        "decision_reason_present",
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
        "replay_protection_verified",
        "all_recording_prerequisites_satisfied",
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


def test_gp771_780_safety_state_is_all_false(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    receipt = _seal(service)

    state = service.get_gate(
        receipt.gate_id
    )["checkpoint"]["safety_state"]

    assert set(state) == set(
        SAFETY_STATE_FIELDS
    )

    assert all(
        value is False
        for value in state.values()
    )


def test_gp771_780_exact_idempotent_replay(
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


def test_gp771_780_rejects_changed_idempotent_input(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    _seal(service)

    with pytest.raises(
        OwnerSessionCreationAuthorizationDecisionRecordingGateError,
        match="different immutable",
    ):
        _seal(
            service,
            target_environment="PRODUCTION",
        )


def test_gp771_780_requires_unrecorded_preparation_lineage(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        OwnerSessionCreationAuthorizationDecisionRecordingGateError,
        match="OWNER_SESSION_CREATION_AUTHORIZATION_DECISION",
    ):
        _seal(
            service,
            decision_preparation_state=(
                "AUTHORIZATION_DECISION_RECORDED"
            ),
        )


@pytest.mark.parametrize(
    "operation",
    [
        "SEND_DECISION_RECORDING_REQUEST",
        "DELIVER_DECISION_RECORDING_REQUEST",
        "ACCEPT_DECISION_RECORDING_REQUEST",
        "AUTHORIZE_DECISION_RECORDING",
        "RECORD_AUTHORIZATION_DECISION",
        "RECORD_OWNER_SESSION_CREATION_AUTHORIZATION_DECISION",
        "GRANT_OWNER_SESSION_CREATION_AUTHORIZATION",
        "GRANT_TOWER_OWNER_SESSION_CREATION_AUTHORIZATION",
        "AUTHORIZE_OWNER_SESSION_CREATION",
        "AUTHORIZE_TOWER_OWNER_SESSION_CREATION",
        "CREATE_OWNER_SESSION",
        "START_OWNER_SESSION",
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
def test_gp771_780_rejects_prohibited_operations(
    tmp_path: Path,
    operation: str,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        OwnerSessionCreationAuthorizationDecisionRecordingGateError,
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
        {"session_token": "do-not-store"},
        {"session_id": "do-not-store"},
        {"decision_value": "GRANT"},
        {"selected_decision": "GRANT"},
        {"owner_decision": "GRANT"},
        {"decision_reason": "invented"},
        {"credentials": {"username": "x"}},
        {"nested": {"private_key": "x"}},
        {"raw_material": {"content": "x"}},
        {"provider_secret": "x"},
    ],
)
def test_gp771_780_rejects_sensitive_or_decision_metadata(
    tmp_path: Path,
    safe_metadata,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        OwnerSessionCreationAuthorizationDecisionRecordingGateError,
        match="prohibited",
    ):
        _seal(
            service,
            safe_metadata=safe_metadata,
        )


def test_gp771_780_verification_passes(
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
    assert result["decision_preparation_lineage_valid"] is True

    assert result["gate_sealed"] is True

    assert result["decision_recording_request_prepared"] is True
    assert result["decision_recording_request_sent"] is False
    assert result["decision_recording_request_delivered"] is False
    assert result["decision_recording_request_accepted"] is False

    assert result["decision_value_present"] is False
    assert result["decision_value_selected"] is False
    assert result["decision_value_invented"] is False

    assert result["decision_reason_present"] is False
    assert result["decision_reason_reference_present"] is False

    assert result["tower_owner_session_present"] is False
    assert result["owner_authenticated"] is False
    assert result["owner_stepped_up"] is False

    assert result["owner_admin_approval_granted"] is False
    assert result["second_authority_review_granted"] is False
    assert result["dual_receipt_satisfied"] is False

    assert result["decision_recording_authorized"] is False
    assert result["authorization_decision_recorded"] is False
    assert result["authorization_granted"] is False

    assert result["owner_session_creation_authorized"] is False
    assert result["tower_owner_session_creation_authorized"] is False

    assert result["owner_session_created"] is False
    assert result["owner_session_started"] is False

    assert result["recording_gate_open"] is False
    assert result["owner_decision_recorded"] is False

    assert result["go_decision_granted"] is False
    assert result["recovery_authorization_granted"] is False
    assert result["authorization_token_issued"] is False

    assert result["recovery_commit_executed"] is False
    assert result["production_write_occurred"] is False
    assert result["provider_connection_occurred"] is False
    assert result["destructive_action_occurred"] is False

    assert result["unsafe_completed_actions"] == []


def test_gp771_780_records_are_immutable(
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
                    vault_gp771_780_owner_session_creation_authorization_decision_recording_gates
                SET gate_state = 'RECORDING_AUTHORIZED'
                WHERE gate_id = ?
                """,
                (receipt.gate_id,),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp771_780_records_are_append_only(
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
                    vault_gp771_780_owner_session_creation_authorization_decision_recording_gates
                WHERE gate_id = ?
                """,
                (receipt.gate_id,),
            )

        connection.rollback()

    finally:
        connection.close()
