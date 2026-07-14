from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from vault.recovery_commit_owner_decision_tower_handoff_delivery_authorization_decision_recording_owner_session_creation_authorization_gate_service import (
    CURRENT_RECOMMENDATION,
    GATE_STATE,
    OwnerSessionCreationAuthorizationGateError,
    RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationGateService,
    SAFETY_STATE_FIELDS,
)


def _service(
    tmp_path: Path,
) -> RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationGateService:
    return (
        RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationGateService(
            tmp_path / "gp731_740.sqlite3"
        )
    )


def _seal(
    service,
    **overrides,
):
    request = {
        "idempotency_key": "gp731-740-case-001",
        "recovery_case_id": "recovery-case-001",
        "owner_decision_record_id": "owner-decision-record-001",
        "owner_session_preparation_id": (
            "vault-gp721-730-preparation-001"
        ),
        "owner_session_preparation_hash": "a" * 64,
        "owner_session_preparation_state": (
            "OWNER_SESSION_PREPARATION_SEALED_"
            "SESSION_NOT_CREATED"
        ),
        "tower_authority_id": "tower-authority-001",
        "tower_delivery_target_id": "tower-delivery-target-001",
        "target_environment": "STAGING",
        "safe_metadata": {
            "prior_pack_range": "GP721-GP730",
            "reference_mode": "HASH_AND_IDENTIFIER_ONLY",
            "redaction_profile": "tower-safe",
        },
    }

    request.update(overrides)

    return service.seal_owner_session_creation_authorization_gate(
        **request
    )


def test_gp731_740_seals_creation_authorization_gate(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    assert receipt.recommendation == CURRENT_RECOMMENDATION
    assert receipt.gate_state == GATE_STATE

    assert receipt.gate_sealed is True
    assert receipt.authorization_granted is False

    assert receipt.owner_session_creation_authorized is False
    assert receipt.tower_owner_session_creation_authorized is False

    assert receipt.owner_session_created is False
    assert receipt.owner_session_started is False
    assert receipt.tower_owner_session_created is False
    assert receipt.tower_owner_session_started is False

    assert receipt.recording_gate_open is False
    assert receipt.owner_decision_recorded is False

    assert receipt.immutable is True
    assert receipt.append_only is True
    assert receipt.idempotent_replay is False

    payload = service.get_gate(
        receipt.gate_id
    )["gate_payload"]

    expected_packs = {
        "gp731_gate_shell": "GP731",
        "gp732_preparation_lineage_gate": "GP732",
        "gp733_tower_session_request_gate": "GP733",
        "gp734_scope_binding_authorization_gate": "GP734",
        "gp735_lifetime_authorization_gate": "GP735",
        "gp736_replay_protection_authorization_gate": "GP736",
        "gp737_owner_authentication_authorization_gate": "GP737",
        "gp738_owner_step_up_authorization_gate": "GP738",
        "gp739_authorization_prerequisite_matrix": "GP739",
        "gp740_checkpoint": "GP740",
    }

    for key, pack in expected_packs.items():
        assert payload[key]["pack"] == pack


def test_gp731_740_tower_session_request_remains_unreleased(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    board = service.get_gate(
        receipt.gate_id
    )["tower_session_request_gate"]

    assert board["destination"] == "TOWER"
    assert board["session_authority"] == "TOWER"

    assert board["request_prepared"] is True
    assert board["request_sent"] is False
    assert board["request_delivered"] is False
    assert board["request_accepted"] is False

    assert board["request_authorized_for_creation"] is False
    assert board["session_creation_authorized"] is False


def test_gp731_740_scope_binding_authorization_remains_blocked(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    board = service.get_gate(
        receipt.gate_id
    )["scope_binding_authorization_gate"]

    assert board["binding_receipt_required"] is True
    assert board["binding_receipt_present"] is False
    assert board["bindings_verified"] is False

    assert board["scope_binding_authorization_satisfied"] is False
    assert board["creation_authorization_blocked"] is True


def test_gp731_740_lifetime_authorization_remains_blocked(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    board = service.get_gate(
        receipt.gate_id
    )["lifetime_authorization_gate"]

    assert board["issued_at_required"] is True
    assert board["not_before_required"] is True
    assert board["expires_at_required"] is True
    assert board["short_lived_session_required"] is True
    assert board["indefinite_session_allowed"] is False

    assert board["lifetime_receipt_required"] is True
    assert board["lifetime_receipt_present"] is False
    assert board["lifetime_verified"] is False

    assert board["lifetime_authorization_satisfied"] is False
    assert board["creation_authorization_blocked"] is True


def test_gp731_740_replay_authorization_remains_blocked(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    board = service.get_gate(
        receipt.gate_id
    )["replay_protection_authorization_gate"]

    assert board["nonce_reference_required"] is True
    assert board["single_active_use_boundary_required"] is True
    assert board["replay_detection_required"] is True

    assert board["replay_protection_receipt_required"] is True
    assert board["replay_protection_receipt_present"] is False
    assert board["replay_protection_verified"] is False

    assert board["replay_protection_authorization_satisfied"] is False
    assert board["creation_authorization_blocked"] is True


def test_gp731_740_owner_authentication_authorization_remains_blocked(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    board = service.get_gate(
        receipt.gate_id
    )["owner_authentication_authorization_gate"]

    assert board["tower_authentication_required"] is True
    assert board["anonymous_session_allowed"] is False
    assert board["vault_authentication_allowed"] is False

    assert board["authentication_receipt_required"] is True
    assert board["authentication_receipt_present"] is False

    assert board["owner_authenticated"] is False
    assert board["authentication_verified"] is False
    assert board["authentication_authorization_satisfied"] is False
    assert board["creation_authorization_blocked"] is True


def test_gp731_740_owner_step_up_authorization_remains_blocked(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    board = service.get_gate(
        receipt.gate_id
    )["owner_step_up_authorization_gate"]

    assert board["tower_step_up_required"] is True
    assert board["purpose_bound_step_up_required"] is True
    assert board["recovery_case_bound_step_up_required"] is True
    assert board["owner_decision_bound_step_up_required"] is True
    assert board["fresh_step_up_required"] is True

    assert board["step_up_receipt_required"] is True
    assert board["step_up_receipt_present"] is False

    assert board["owner_stepped_up"] is False
    assert board["step_up_verified"] is False
    assert board["step_up_authorization_satisfied"] is False
    assert board["creation_authorization_blocked"] is True


def test_gp731_740_creation_authorization_matrix_remains_false(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    matrix = service.get_gate(
        receipt.gate_id
    )["authorization_prerequisite_matrix"]

    assert matrix["preparation_reference_present"] is True
    assert matrix["preparation_hash_present"] is True
    assert matrix["tower_session_request_prepared"] is True

    false_fields = (
        "scope_binding_receipt_present",
        "scope_bindings_verified",
        "lifetime_receipt_present",
        "session_lifetime_verified",
        "replay_protection_receipt_present",
        "session_replay_protection_verified",
        "authentication_receipt_present",
        "owner_authenticated",
        "owner_authentication_verified",
        "step_up_receipt_present",
        "owner_stepped_up",
        "owner_step_up_verified",
        "owner_session_creation_authorization_granted",
        "tower_owner_session_creation_authorization_granted",
        "owner_session_creation_authorized",
        "tower_owner_session_creation_authorized",
        "owner_session_created",
        "owner_session_started",
        "tower_owner_session_created",
        "tower_owner_session_started",
        "all_creation_authorization_prerequisites_satisfied",
        "session_creation_authorization_may_be_granted",
        "session_creation_may_proceed",
        "recording_gate_may_open",
    )

    for field in false_fields:
        assert matrix[field] is False


def test_gp731_740_safety_state_is_all_false(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    safety_state = service.get_gate(
        receipt.gate_id
    )["checkpoint"]["safety_state"]

    assert set(safety_state) == set(SAFETY_STATE_FIELDS)

    assert all(
        value is False
        for value in safety_state.values()
    )


def test_gp731_740_exact_idempotent_replay(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    first = _seal(service)
    second = _seal(service)

    assert first.gate_id == second.gate_id
    assert first.gate_hash == second.gate_hash

    assert first.idempotent_replay is False
    assert second.idempotent_replay is True

    events = service.list_events(
        first.gate_id
    )

    assert len(events) == 1


def test_gp731_740_rejects_changed_idempotent_inputs(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    _seal(service)

    with pytest.raises(
        OwnerSessionCreationAuthorizationGateError,
        match="different immutable",
    ):
        _seal(
            service,
            target_environment="PRODUCTION",
        )


def test_gp731_740_requires_prepared_not_created_lineage(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        OwnerSessionCreationAuthorizationGateError,
        match="OWNER_SESSION_PREPARATION",
    ):
        _seal(
            service,
            owner_session_preparation_state=(
                "OWNER_SESSION_CREATED"
            ),
        )


@pytest.mark.parametrize(
    "operation",
    [
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
def test_gp731_740_rejects_prohibited_operations(
    tmp_path: Path,
    operation: str,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        OwnerSessionCreationAuthorizationGateError,
        match="prohibited operation",
    ):
        _seal(
            service,
            idempotency_key=(
                "prohibited-"
                + operation.lower()
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
        {"session_cookie": "do-not-store"},
        {"session_secret": "do-not-store"},
        {"session_id": "do-not-store"},
        {"owner_session_id": "do-not-store"},
        {"credentials": {"username": "x"}},
        {"nested": {"private_key": "x"}},
        {"raw_material": {"content": "x"}},
        {"provider_secret": "x"},
    ],
)
def test_gp731_740_rejects_raw_secret_or_session_metadata(
    tmp_path: Path,
    safe_metadata,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        OwnerSessionCreationAuthorizationGateError,
        match="prohibited",
    ):
        _seal(
            service,
            safe_metadata=safe_metadata,
        )


def test_gp731_740_verification_passes(
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
    assert result["owner_session_preparation_lineage_valid"] is True

    assert result["gate_sealed"] is True
    assert result["authorization_granted"] is False

    assert result["tower_session_request_prepared"] is True
    assert result["tower_session_request_sent"] is False

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

    assert result["tower_owner_session_created"] is False
    assert result["tower_owner_session_started"] is False
    assert result["tower_owner_session_issued"] is False
    assert result["tower_owner_session_activated"] is False

    assert result["session_binding_receipt_present"] is False
    assert result["session_bindings_verified"] is False

    assert result["session_lifetime_receipt_present"] is False
    assert result["session_lifetime_verified"] is False

    assert result["session_replay_protection_receipt_present"] is False
    assert result["session_replay_protection_verified"] is False

    assert result["owner_authentication_receipt_present"] is False
    assert result["owner_authenticated"] is False
    assert result["owner_authentication_verified"] is False

    assert result["owner_step_up_receipt_present"] is False
    assert result["owner_stepped_up"] is False
    assert result["owner_step_up_verified"] is False

    assert result["recording_gate_open"] is False

    assert result["owner_decision_recorded"] is False

    assert result["go_decision_granted"] is False

    assert result["recovery_authorization_issued"] is False
    assert result["recovery_authorization_granted"] is False

    assert result["authorization_token_issued"] is False
    assert result["authorization_token_minted"] is False

    assert result["handoff_delivered"] is False

    assert result["recovery_commit_command_issued"] is False
    assert result["recovery_commit_executed"] is False

    assert result["restore_occurred"] is False
    assert result["production_mount_occurred"] is False
    assert result["production_write_occurred"] is False

    assert result["provider_connection_occurred"] is False
    assert result["raw_material_exposed"] is False
    assert result["destructive_action_occurred"] is False

    assert result["unsafe_completed_actions"] == []


def test_gp731_740_gate_records_are_immutable(
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
                    vault_gp731_740_owner_session_creation_authorization_gates
                SET gate_state = 'AUTHORIZED'
                WHERE gate_id = ?
                """,
                (receipt.gate_id,),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp731_740_gate_records_are_append_only(
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
                    vault_gp731_740_owner_session_creation_authorization_gates
                WHERE gate_id = ?
                """,
                (receipt.gate_id,),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp731_740_events_are_immutable_and_append_only(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    event = service.list_events(
        receipt.gate_id
    )[0]

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
                    vault_gp731_740_owner_session_creation_authorization_gate_events
                SET event_type = 'MUTATED'
                WHERE event_id = ?
                """,
                (event["event_id"],),
            )

        connection.rollback()

        with pytest.raises(
            sqlite3.IntegrityError,
            match="append-only",
        ):
            connection.execute(
                """
                DELETE FROM
                    vault_gp731_740_owner_session_creation_authorization_gate_events
                WHERE event_id = ?
                """,
                (event["event_id"],),
            )

        connection.rollback()

    finally:
        connection.close()
