from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from vault.recovery_commit_owner_decision_tower_handoff_delivery_authorization_decision_recording_owner_session_creation_authorization_decision_gate_service import (
    CURRENT_RECOMMENDATION,
    GATE_STATE,
    OwnerSessionCreationAuthorizationDecisionGateError,
    RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionGateService,
    SAFETY_STATE_FIELDS,
)


def _service(
    tmp_path: Path,
) -> RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionGateService:
    return (
        RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionGateService(
            tmp_path / "gp751_760.sqlite3"
        )
    )


def _seal(
    service,
    **overrides,
):
    request = {
        "idempotency_key": "gp751-760-case-001",
        "recovery_case_id": "recovery-case-001",
        "owner_decision_record_id": "owner-decision-record-001",
        "authorization_preparation_id": (
            "vault-gp741-750-preparation-001"
        ),
        "authorization_preparation_hash": "a" * 64,
        "authorization_preparation_state": (
            "OWNER_SESSION_CREATION_AUTHORIZATION_"
            "PREPARATION_SEALED_AUTHORIZATION_NOT_GRANTED"
        ),
        "tower_authority_id": "tower-authority-001",
        "tower_delivery_target_id": "tower-delivery-target-001",
        "target_environment": "STAGING",
        "safe_metadata": {
            "prior_pack_range": "GP741-GP750",
            "reference_mode": "HASH_AND_IDENTIFIER_ONLY",
            "redaction_profile": "tower-safe",
        },
    }

    request.update(
        overrides
    )

    return service.seal_authorization_decision_gate(
        **request
    )


def test_gp751_760_seals_decision_gate(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

    assert receipt.recommendation == CURRENT_RECOMMENDATION
    assert receipt.gate_state == GATE_STATE

    assert receipt.gate_sealed is True
    assert receipt.authorization_decision_recorded is False
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

    payload = service.get_gate(
        receipt.gate_id
    )["gate_payload"]

    expected_packs = {
        "gp751_gate_shell": "GP751",
        "gp752_preparation_lineage_gate": "GP752",
        "gp753_decision_request_gate": "GP753",
        "gp754_scope_binding_decision_gate": "GP754",
        "gp755_lifetime_decision_gate": "GP755",
        "gp756_replay_decision_gate": "GP756",
        "gp757_authentication_decision_gate": "GP757",
        "gp758_step_up_decision_gate": "GP758",
        "gp759_decision_blocker_matrix": "GP759",
        "gp760_checkpoint": "GP760",
    }

    for key, pack in expected_packs.items():
        assert payload[key]["pack"] == pack


def test_gp751_760_request_remains_unreleased(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

    gate = service.get_gate(
        receipt.gate_id
    )["decision_request_gate"]

    assert gate["destination"] == "TOWER"
    assert gate["decision_authority"] == "TOWER"

    assert gate["request_prepared"] is True
    assert gate["request_sent"] is False
    assert gate["request_delivered"] is False
    assert gate["request_accepted"] is False

    assert gate["decision_recording_authorized"] is False
    assert gate["authorization_decision_recorded"] is False
    assert gate["authorization_granted"] is False


@pytest.mark.parametrize(
    "gate_name",
    [
        "scope_binding_decision_gate",
        "lifetime_decision_gate",
        "replay_decision_gate",
        "authentication_decision_gate",
        "step_up_decision_gate",
    ],
)
def test_gp751_760_decision_requirements_remain_blocked(
    tmp_path: Path,
    gate_name: str,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

    gate = service.get_gate(
        receipt.gate_id
    )[gate_name]

    assert gate["authorization_decision_blocked"] is True

    satisfied_fields = [
        field
        for field in gate
        if field.endswith(
            "_decision_requirement_satisfied"
        )
    ]

    for field in satisfied_fields:
        assert gate[field] is False


def test_gp751_760_blocker_matrix_remains_false(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

    matrix = service.get_gate(
        receipt.gate_id
    )["decision_blocker_matrix"]

    assert matrix["preparation_reference_present"] is True
    assert matrix["preparation_hash_present"] is True
    assert matrix["authorization_decision_request_prepared"] is True

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
        "authorization_decision_recording_authorized",
        "authorization_decision_may_be_recorded",
        "authorization_decision_recorded",
        "owner_session_creation_authorization_granted",
        "tower_owner_session_creation_authorization_granted",
        "owner_session_creation_authorized",
        "tower_owner_session_creation_authorized",
        "session_creation_may_proceed",
        "recording_gate_may_open",
    )

    for field in false_fields:
        assert matrix[field] is False


def test_gp751_760_safety_state_is_all_false(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

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


def test_gp751_760_exact_idempotent_replay(
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

    assert first.gate_id == second.gate_id
    assert first.gate_hash == second.gate_hash

    assert first.idempotent_replay is False
    assert second.idempotent_replay is True

    assert len(
        service.list_events(
            first.gate_id
        )
    ) == 1


def test_gp751_760_rejects_changed_idempotent_input(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    _seal(
        service
    )

    with pytest.raises(
        OwnerSessionCreationAuthorizationDecisionGateError,
        match="different immutable",
    ):
        _seal(
            service,
            target_environment="PRODUCTION",
        )


def test_gp751_760_requires_prepared_not_granted_lineage(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        OwnerSessionCreationAuthorizationDecisionGateError,
        match="OWNER_SESSION_CREATION_AUTHORIZATION_PREPARATION",
    ):
        _seal(
            service,
            authorization_preparation_state=(
                "AUTHORIZATION_GRANTED"
            ),
        )


@pytest.mark.parametrize(
    "operation",
    [
        "SEND_AUTHORIZATION_DECISION_REQUEST",
        "DELIVER_AUTHORIZATION_DECISION_REQUEST",
        "ACCEPT_AUTHORIZATION_DECISION_REQUEST",
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
        "CREATE_TOWER_OWNER_SESSION",
        "START_TOWER_OWNER_SESSION",
        "ISSUE_TOWER_OWNER_SESSION",
        "ACTIVATE_TOWER_OWNER_SESSION",
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
def test_gp751_760_rejects_prohibited_operations(
    tmp_path: Path,
    operation: str,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        OwnerSessionCreationAuthorizationDecisionGateError,
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
        {"credentials": {"username": "x"}},
        {"nested": {"private_key": "x"}},
        {"raw_material": {"content": "x"}},
        {"provider_secret": "x"},
    ],
)
def test_gp751_760_rejects_sensitive_metadata(
    tmp_path: Path,
    safe_metadata,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        OwnerSessionCreationAuthorizationDecisionGateError,
        match="prohibited",
    ):
        _seal(
            service,
            safe_metadata=safe_metadata,
        )


def test_gp751_760_verification_passes(
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
    assert result["authorization_preparation_lineage_valid"] is True

    assert result["gate_sealed"] is True

    assert result["authorization_decision_request_prepared"] is True
    assert result["authorization_decision_request_sent"] is False
    assert result["authorization_decision_request_delivered"] is False
    assert result["authorization_decision_request_accepted"] is False

    assert result["authorization_decision_recording_authorized"] is False
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


def test_gp751_760_records_are_immutable(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

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
                    vault_gp751_760_owner_session_creation_authorization_decision_gates
                SET gate_state = 'DECISION_RECORDED'
                WHERE gate_id = ?
                """,
                (receipt.gate_id,),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp751_760_records_are_append_only(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

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
                    vault_gp751_760_owner_session_creation_authorization_decision_gates
                WHERE gate_id = ?
                """,
                (receipt.gate_id,),
            )

        connection.rollback()

    finally:
        connection.close()
