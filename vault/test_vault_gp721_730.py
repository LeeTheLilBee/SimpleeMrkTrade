from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from vault.recovery_commit_owner_decision_tower_handoff_delivery_authorization_decision_recording_owner_session_preparation_layer_service import (
    CURRENT_RECOMMENDATION,
    OwnerSessionPreparationError,
    PREPARATION_STATE,
    RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionPreparationLayerService,
    SAFETY_STATE_FIELDS,
)


def _service(
    tmp_path: Path,
) -> RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionPreparationLayerService:
    return (
        RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionPreparationLayerService(
            tmp_path / "gp721_730.sqlite3"
        )
    )


def _seal(
    service,
    **overrides,
):
    request = {
        "idempotency_key": "gp721-730-case-001",
        "recovery_case_id": "recovery-case-001",
        "owner_decision_record_id": "owner-decision-record-001",
        "owner_session_requirement_gate_id": (
            "vault-gp711-720-gate-001"
        ),
        "owner_session_requirement_gate_hash": "a" * 64,
        "owner_session_requirement_gate_state": (
            "OWNER_SESSION_REQUIREMENT_GATE_"
            "SEALED_SESSION_ABSENT"
        ),
        "tower_authority_id": "tower-authority-001",
        "tower_delivery_target_id": "tower-delivery-target-001",
        "target_environment": "STAGING",
        "safe_metadata": {
            "prior_pack_range": "GP711-GP720",
            "reference_mode": "HASH_AND_IDENTIFIER_ONLY",
            "redaction_profile": "tower-safe",
        },
    }

    request.update(overrides)

    return service.seal_owner_session_preparation(
        **request
    )


def test_gp721_730_seals_owner_session_preparation(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    assert receipt.recommendation == CURRENT_RECOMMENDATION
    assert receipt.preparation_state == PREPARATION_STATE

    assert receipt.preparation_sealed is True
    assert receipt.tower_session_request_prepared is True
    assert receipt.owner_session_required is True

    assert receipt.owner_session_created is False
    assert receipt.owner_session_started is False
    assert receipt.tower_owner_session_created is False
    assert receipt.tower_owner_session_started is False

    assert receipt.recording_gate_open is False
    assert receipt.owner_decision_recorded is False

    assert receipt.immutable is True
    assert receipt.append_only is True
    assert receipt.idempotent_replay is False

    payload = service.get_preparation(
        receipt.preparation_id
    )["preparation_payload"]

    expected_packs = {
        "gp721_preparation_shell": "GP721",
        "gp722_requirement_gate_intake_board": "GP722",
        "gp723_tower_session_request_envelope": "GP723",
        "gp724_session_scope_binding_board": "GP724",
        "gp725_session_lifetime_board": "GP725",
        "gp726_session_replay_protection_board": "GP726",
        "gp727_owner_authentication_requirement_board": "GP727",
        "gp728_owner_step_up_requirement_board": "GP728",
        "gp729_creation_prerequisite_board": "GP729",
        "gp730_checkpoint": "GP730",
    }

    for key, pack in expected_packs.items():
        assert payload[key]["pack"] == pack


def test_gp721_730_prepares_but_does_not_send_tower_session_request(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    envelope = service.get_preparation(
        receipt.preparation_id
    )["tower_session_request_envelope"]

    assert envelope["destination"] == "TOWER"
    assert envelope["session_authority"] == "TOWER"

    assert envelope["request_prepared"] is True
    assert envelope["request_sent"] is False
    assert envelope["request_delivered"] is False
    assert envelope["request_accepted"] is False

    assert envelope["session_created"] is False
    assert envelope["session_started"] is False
    assert envelope["session_reference"] is None


def test_gp721_730_prepares_scope_binding_requirements(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    board = service.get_preparation(
        receipt.preparation_id
    )["session_scope_binding_board"]

    assert board["recovery_case_binding_required"] is True
    assert board["owner_decision_binding_required"] is True
    assert board["environment_binding_required"] is True
    assert board["tower_authority_binding_required"] is True
    assert board["delivery_target_binding_required"] is True

    assert board["cross_case_use_allowed"] is False
    assert board["cross_owner_decision_use_allowed"] is False
    assert board["cross_environment_use_allowed"] is False

    assert board["binding_receipt_present"] is False
    assert board["bindings_verified"] is False


def test_gp721_730_prepares_session_lifetime_requirements(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    board = service.get_preparation(
        receipt.preparation_id
    )["session_lifetime_board"]

    assert board["explicit_issued_at_required"] is True
    assert board["explicit_not_before_required"] is True
    assert board["explicit_expires_at_required"] is True
    assert board["short_lived_session_required"] is True

    assert board["indefinite_session_allowed"] is False
    assert board["expired_session_rejected"] is True
    assert board["premature_session_rejected"] is True
    assert board["missing_expiry_rejected"] is True

    assert board["lifetime_verified"] is False


def test_gp721_730_prepares_replay_protection_requirements(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    board = service.get_preparation(
        receipt.preparation_id
    )["session_replay_protection_board"]

    assert board["nonce_reference_required"] is True
    assert board["single_active_use_boundary_required"] is True
    assert board["replay_detection_required"] is True

    assert board["duplicate_use_rejected"] is True
    assert board["consumed_session_reuse_rejected"] is True
    assert board["cross_case_replay_rejected"] is True
    assert board["cross_owner_decision_replay_rejected"] is True
    assert board["cross_environment_replay_rejected"] is True

    assert board["nonce_reference"] is None
    assert board["consumption_receipt_reference"] is None
    assert board["replay_protection_verified"] is False


def test_gp721_730_owner_authentication_and_step_up_remain_unsatisfied(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    record = service.get_preparation(
        receipt.preparation_id
    )

    auth = record["owner_authentication_requirement_board"]
    step_up = record["owner_step_up_requirement_board"]

    assert auth["tower_authentication_required"] is True
    assert auth["anonymous_session_allowed"] is False
    assert auth["vault_authentication_allowed"] is False
    assert auth["teller_authentication_authority_allowed"] is False
    assert auth["owner_authenticated"] is False
    assert auth["authentication_receipt_reference"] is None
    assert auth["authentication_verified"] is False

    assert step_up["tower_step_up_required"] is True
    assert step_up["purpose_bound_step_up_required"] is True
    assert step_up["recovery_case_bound_step_up_required"] is True
    assert step_up["owner_decision_bound_step_up_required"] is True
    assert step_up["fresh_step_up_required"] is True
    assert step_up["vault_step_up_allowed"] is False
    assert step_up["teller_step_up_authority_allowed"] is False
    assert step_up["owner_stepped_up"] is False
    assert step_up["step_up_receipt_reference"] is None
    assert step_up["step_up_verified"] is False


def test_gp721_730_creation_prerequisites_remain_unsatisfied(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    board = service.get_preparation(
        receipt.preparation_id
    )["creation_prerequisite_board"]

    assert board["requirement_gate_reference_present"] is True
    assert board["requirement_gate_hash_present"] is True
    assert board["tower_session_request_prepared"] is True

    assert board["session_scope_binding_receipt_present"] is False
    assert board["session_scope_bindings_verified"] is False
    assert board["session_lifetime_verified"] is False
    assert board["session_replay_protection_verified"] is False
    assert board["owner_authentication_verified"] is False
    assert board["owner_step_up_verified"] is False

    assert board["owner_session_creation_authorized"] is False
    assert board["tower_owner_session_creation_authorized"] is False

    assert board["owner_session_created"] is False
    assert board["owner_session_started"] is False
    assert board["tower_owner_session_created"] is False
    assert board["tower_owner_session_started"] is False

    assert board["all_creation_prerequisites_satisfied"] is False
    assert board["session_creation_may_proceed"] is False
    assert board["recording_gate_may_open"] is False


def test_gp721_730_safety_state_is_all_false(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    safety_state = service.get_preparation(
        receipt.preparation_id
    )["checkpoint"]["safety_state"]

    assert set(safety_state) == set(SAFETY_STATE_FIELDS)

    assert all(
        value is False
        for value in safety_state.values()
    )


def test_gp721_730_exact_idempotent_replay(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    first = _seal(service)
    second = _seal(service)

    assert first.preparation_id == second.preparation_id
    assert first.preparation_hash == second.preparation_hash

    assert first.idempotent_replay is False
    assert second.idempotent_replay is True

    events = service.list_events(
        first.preparation_id
    )

    assert len(events) == 1


def test_gp721_730_rejects_changed_idempotent_inputs(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    _seal(service)

    with pytest.raises(
        OwnerSessionPreparationError,
        match="different immutable",
    ):
        _seal(
            service,
            target_environment="PRODUCTION",
        )


def test_gp721_730_requires_sealed_absent_session_gate_lineage(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        OwnerSessionPreparationError,
        match="OWNER_SESSION_REQUIREMENT_GATE",
    ):
        _seal(
            service,
            owner_session_requirement_gate_state=(
                "OWNER_SESSION_CREATED"
            ),
        )


@pytest.mark.parametrize(
    "operation",
    [
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
def test_gp721_730_rejects_prohibited_operations(
    tmp_path: Path,
    operation: str,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        OwnerSessionPreparationError,
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
        {"credentials": {"username": "x"}},
        {"nested": {"private_key": "x"}},
        {"raw_material": {"content": "x"}},
        {"provider_secret": "x"},
    ],
)
def test_gp721_730_rejects_raw_secret_or_session_metadata(
    tmp_path: Path,
    safe_metadata,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        OwnerSessionPreparationError,
        match="prohibited",
    ):
        _seal(
            service,
            safe_metadata=safe_metadata,
        )


def test_gp721_730_verification_passes(
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
    assert result["requirement_gate_lineage_valid"] is True

    assert result["preparation_sealed"] is True
    assert result["tower_session_request_prepared"] is True
    assert result["tower_session_request_sent"] is False

    assert result["owner_session_required"] is True

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
    assert result["session_lifetime_verified"] is False
    assert result["session_replay_protection_verified"] is False

    assert result["owner_authenticated"] is False
    assert result["owner_stepped_up"] is False

    assert result["recording_gate_open"] is False
    assert result["owner_decision_recorded"] is False

    assert result["go_decision_granted"] is False
    assert result["recovery_authorization_granted"] is False
    assert result["authorization_token_issued"] is False

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


def test_gp721_730_preparations_are_immutable(
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
                UPDATE vault_gp721_730_owner_session_preparations
                SET preparation_state = 'SESSION_CREATED'
                WHERE preparation_id = ?
                """,
                (receipt.preparation_id,),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp721_730_preparations_are_append_only(
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
                DELETE FROM vault_gp721_730_owner_session_preparations
                WHERE preparation_id = ?
                """,
                (receipt.preparation_id,),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp721_730_events_are_immutable_and_append_only(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _seal(service)

    event = service.list_events(
        receipt.preparation_id
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
                UPDATE vault_gp721_730_owner_session_preparation_events
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
                DELETE FROM vault_gp721_730_owner_session_preparation_events
                WHERE event_id = ?
                """,
                (event["event_id"],),
            )

        connection.rollback()

    finally:
        connection.close()
