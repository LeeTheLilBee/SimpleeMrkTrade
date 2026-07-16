from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from vault.recovery_commit_owner_decision_tower_handoff_delivery_authorization_decision_recording_owner_session_creation_authorization_decision_preparation_layer_service import (
    CURRENT_RECOMMENDATION,
    OwnerSessionCreationAuthorizationDecisionPreparationError,
    PREPARATION_STATE,
    RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionPreparationLayerService,
    SAFETY_STATE_FIELDS,
)


def _service(
    tmp_path: Path,
) -> RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionPreparationLayerService:
    return (
        RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionPreparationLayerService(
            tmp_path / "gp761_770.sqlite3"
        )
    )


def _seal(
    service,
    **overrides,
):
    request = {
        "idempotency_key": "gp761-770-case-001",
        "recovery_case_id": "recovery-case-001",
        "owner_decision_record_id": "owner-decision-record-001",
        "authorization_decision_gate_id": (
            "vault-gp751-760-gate-001"
        ),
        "authorization_decision_gate_hash": "a" * 64,
        "authorization_decision_gate_state": (
            "OWNER_SESSION_CREATION_AUTHORIZATION_"
            "DECISION_GATE_SEALED_DECISION_NOT_RECORDED"
        ),
        "tower_authority_id": "tower-authority-001",
        "tower_delivery_target_id": "tower-delivery-target-001",
        "target_environment": "STAGING",
        "safe_metadata": {
            "prior_pack_range": "GP751-GP760",
            "reference_mode": "HASH_AND_IDENTIFIER_ONLY",
            "redaction_profile": "tower-safe",
        },
    }

    request.update(
        overrides
    )

    return service.seal_decision_preparation(
        **request
    )


def test_gp761_770_seals_decision_preparation(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

    assert receipt.recommendation == CURRENT_RECOMMENDATION
    assert receipt.preparation_state == PREPARATION_STATE

    assert receipt.preparation_sealed is True
    assert receipt.decision_recording_request_prepared is True
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

    payload = service.get_preparation(
        receipt.preparation_id
    )["preparation_payload"]

    expected_packs = {
        "gp761_preparation_shell": "GP761",
        "gp762_gate_lineage_intake": "GP762",
        "gp763_recording_request_envelope": "GP763",
        "gp764_decision_value_contract": "GP764",
        "gp765_decision_reason_board": "GP765",
        "gp766_evidence_binding_board": "GP766",
        "gp767_authority_requirement_board": "GP767",
        "gp768_replay_protection_board": "GP768",
        "gp769_recording_prerequisite_board": "GP769",
        "gp770_checkpoint": "GP770",
    }

    for key, pack in expected_packs.items():
        assert payload[key]["pack"] == pack


def test_gp761_770_recording_request_remains_unsent(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

    envelope = service.get_preparation(
        receipt.preparation_id
    )["recording_request_envelope"]

    assert envelope["destination"] == "TOWER"
    assert envelope["recording_authority"] == "TOWER"

    assert envelope["request_prepared"] is True
    assert envelope["request_sent"] is False
    assert envelope["request_delivered"] is False
    assert envelope["request_accepted"] is False

    assert envelope["decision_recording_authorized"] is False
    assert envelope["authorization_decision_recorded"] is False
    assert envelope["authorization_granted"] is False


def test_gp761_770_no_decision_value_is_selected(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

    contract = service.get_preparation(
        receipt.preparation_id
    )["decision_value_contract"]

    assert contract["allowed_decision_values"] == [
        "GRANT",
        "DENY",
        "HOLD",
    ]

    assert contract["decision_value_required"] is True
    assert contract["decision_value_present"] is False
    assert contract["decision_value_selected"] is False
    assert contract["decision_value_invented"] is False

    assert contract["default_decision_allowed"] is False
    assert contract["implicit_grant_allowed"] is False
    assert contract["implicit_deny_allowed"] is False
    assert contract["implicit_hold_allowed"] is False

    assert contract["authorization_decision_ready"] is False


def test_gp761_770_authority_requirements_unsatisfied(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

    board = service.get_preparation(
        receipt.preparation_id
    )["authority_requirement_board"]

    assert board["tower_decision_authority_required"] is True
    assert board["tower_owner_session_required"] is True
    assert board["tower_owner_authentication_required"] is True
    assert board["tower_owner_step_up_required"] is True
    assert board["owner_admin_approval_required"] is True
    assert board["second_authority_review_required"] is True
    assert board["dual_receipt_required"] is True

    assert board["tower_owner_session_present"] is False
    assert board["owner_authenticated"] is False
    assert board["owner_stepped_up"] is False
    assert board["owner_admin_approval_granted"] is False
    assert board["second_authority_review_granted"] is False
    assert board["dual_receipt_satisfied"] is False

    assert board["authorization_decision_ready"] is False


def test_gp761_770_recording_prerequisites_remain_false(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

    board = service.get_preparation(
        receipt.preparation_id
    )["recording_prerequisite_board"]

    assert board["prior_gate_reference_present"] is True
    assert board["prior_gate_hash_present"] is True
    assert board["decision_recording_request_prepared"] is True

    false_fields = (
        "decision_value_present",
        "decision_value_selected",
        "decision_reason_present",
        "decision_reason_reference_present",
        "evidence_package_reference_present",
        "evidence_bindings_verified",
        "tower_owner_session_present",
        "owner_authenticated",
        "owner_stepped_up",
        "owner_admin_approval_granted",
        "second_authority_review_granted",
        "dual_receipt_satisfied",
        "decision_nonce_reference_present",
        "replay_protection_verified",
        "all_decision_recording_prerequisites_satisfied",
        "authorization_decision_recording_authorized",
        "authorization_decision_may_be_recorded",
        "authorization_decision_recorded",
        "authorization_granted",
        "owner_session_creation_authorized",
        "tower_owner_session_creation_authorized",
        "session_creation_may_proceed",
        "recording_gate_may_open",
    )

    for field in false_fields:
        assert board[field] is False


def test_gp761_770_safety_state_is_all_false(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

    state = service.get_preparation(
        receipt.preparation_id
    )["checkpoint"]["safety_state"]

    assert set(state) == set(
        SAFETY_STATE_FIELDS
    )

    assert all(
        value is False
        for value in state.values()
    )


def test_gp761_770_exact_idempotent_replay(
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

    assert first.preparation_id == second.preparation_id
    assert first.preparation_hash == second.preparation_hash

    assert first.idempotent_replay is False
    assert second.idempotent_replay is True

    assert len(
        service.list_events(
            first.preparation_id
        )
    ) == 1


def test_gp761_770_rejects_changed_idempotent_input(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    _seal(
        service
    )

    with pytest.raises(
        OwnerSessionCreationAuthorizationDecisionPreparationError,
        match="different immutable",
    ):
        _seal(
            service,
            target_environment="PRODUCTION",
        )


def test_gp761_770_requires_unrecorded_gate_lineage(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        OwnerSessionCreationAuthorizationDecisionPreparationError,
        match="OWNER_SESSION_CREATION_AUTHORIZATION_DECISION",
    ):
        _seal(
            service,
            authorization_decision_gate_state=(
                "AUTHORIZATION_DECISION_RECORDED"
            ),
        )


@pytest.mark.parametrize(
    "operation",
    [
        "SEND_DECISION_RECORDING_REQUEST",
        "DELIVER_DECISION_RECORDING_REQUEST",
        "ACCEPT_DECISION_RECORDING_REQUEST",
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
def test_gp761_770_rejects_prohibited_operations(
    tmp_path: Path,
    operation: str,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        OwnerSessionCreationAuthorizationDecisionPreparationError,
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
        {"credentials": {"username": "x"}},
        {"nested": {"private_key": "x"}},
        {"raw_material": {"content": "x"}},
        {"provider_secret": "x"},
    ],
)
def test_gp761_770_rejects_sensitive_or_decision_metadata(
    tmp_path: Path,
    safe_metadata,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        OwnerSessionCreationAuthorizationDecisionPreparationError,
        match="prohibited",
    ):
        _seal(
            service,
            safe_metadata=safe_metadata,
        )


def test_gp761_770_verification_passes(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _seal(
        service
    )

    result = service.verify_preparation(
        receipt.preparation_id
    )

    assert result["verified"] is True
    assert result["preparation_hash_valid"] is True
    assert result["event_chain_valid"] is True
    assert result["tower_destination_only"] is True
    assert result["authorization_decision_gate_lineage_valid"] is True

    assert result["preparation_sealed"] is True

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

    assert result["authorization_decision_recording_authorized"] is False
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


def test_gp761_770_records_are_immutable(
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
                    vault_gp761_770_owner_session_creation_authorization_decision_preparations
                SET preparation_state = 'DECISION_RECORDED'
                WHERE preparation_id = ?
                """,
                (receipt.preparation_id,),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp761_770_records_are_append_only(
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
                    vault_gp761_770_owner_session_creation_authorization_decision_preparations
                WHERE preparation_id = ?
                """,
                (receipt.preparation_id,),
            )

        connection.rollback()

    finally:
        connection.close()
