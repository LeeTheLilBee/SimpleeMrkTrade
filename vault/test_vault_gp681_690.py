from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from vault.recovery_commit_owner_decision_tower_handoff_delivery_authorization_decision_preparation_layer_service import (
    AuthorizationDecisionPreparationError,
    CURRENT_RECOMMENDATION,
    DECISION_OPTIONS,
    PREPARATION_STATE,
    RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionPreparationService,
    SAFETY_STATE_FIELDS,
)


def _service(
    tmp_path: Path,
) -> RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionPreparationService:
    return (
        RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionPreparationService(
            tmp_path / "gp681_690.sqlite3"
        )
    )


def _prepare(
    service,
    **overrides,
):
    request = {
        "idempotency_key": "gp681-690-case-001",
        "recovery_case_id": "recovery-case-001",
        "owner_decision_record_id": (
            "owner-decision-record-001"
        ),
        "authorization_gate_id": (
            "vault-gp671-680-gate-001"
        ),
        "authorization_gate_hash": (
            "a" * 64
        ),
        "authorization_gate_state": (
            "AUTHORIZATION_GATE_SEALED_"
            "AUTHORIZATION_NOT_GRANTED"
        ),
        "tower_authority_id": (
            "tower-authority-001"
        ),
        "tower_delivery_target_id": (
            "tower-delivery-target-001"
        ),
        "target_environment": (
            "STAGING"
        ),
        "safe_metadata": {
            "prior_pack_range": "GP671-GP680",
            "reference_mode": (
                "HASH_AND_IDENTIFIER_ONLY"
            ),
            "redaction_profile": (
                "tower-safe"
            ),
        },
    }

    request.update(
        overrides
    )

    return service.prepare_authorization_decision(
        **request
    )


def test_gp681_690_prepares_decision_packet_without_selecting_decision(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _prepare(
        service
    )

    assert (
        receipt.recommendation
        == CURRENT_RECOMMENDATION
    )

    assert (
        receipt.preparation_state
        == PREPARATION_STATE
    )

    assert receipt.decision_packet_prepared is True
    assert receipt.owner_decision_selected is False
    assert receipt.owner_decision_recorded is False
    assert receipt.authorization_granted is False
    assert receipt.authorization_token_issued is False
    assert receipt.immutable is True
    assert receipt.append_only is True
    assert receipt.idempotent_replay is False

    record = service.get_preparation(
        receipt.preparation_id
    )

    payload = record[
        "preparation_payload"
    ]

    assert (
        payload[
            "gp681_decision_preparation_shell"
        ]["pack"]
        == "GP681"
    )

    assert (
        payload[
            "gp682_gate_lineage_intake"
        ]["pack"]
        == "GP682"
    )

    assert (
        payload[
            "gp683_decision_context_board"
        ]["pack"]
        == "GP683"
    )

    assert (
        payload[
            "gp684_prerequisite_summary"
        ]["pack"]
        == "GP684"
    )

    assert (
        payload[
            "gp685_blocker_summary"
        ]["pack"]
        == "GP685"
    )

    assert (
        payload[
            "gp686_decision_option_board"
        ]["pack"]
        == "GP686"
    )

    assert (
        payload[
            "gp687_decision_packet"
        ]["pack"]
        == "GP687"
    )

    assert (
        payload[
            "gp688_decision_receipt_draft"
        ]["pack"]
        == "GP688"
    )

    assert (
        payload[
            "gp689_safety_blocker_board"
        ]["pack"]
        == "GP689"
    )

    assert (
        payload[
            "gp690_checkpoint"
        ]["pack"]
        == "GP690"
    )


def test_gp681_690_decision_options_are_non_authorizing_and_unselected(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _prepare(
        service
    )

    record = service.get_preparation(
        receipt.preparation_id
    )

    option_board = record[
        "decision_option_board"
    ]

    assert (
        tuple(
            option_board["options"]
        )
        == DECISION_OPTIONS
    )

    assert option_board["default_option"] is None
    assert option_board["recommended_option"] is None
    assert option_board["selected_option"] is None

    assert (
        option_board["selection_inferred"]
        is False
    )

    assert (
        option_board["selection_recorded"]
        is False
    )

    assert (
        option_board["authorization_option_exposed"]
        is False
    )


def test_gp681_690_safety_state_is_all_false(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _prepare(
        service
    )

    record = service.get_preparation(
        receipt.preparation_id
    )

    safety_state = record[
        "safety_blocker_board"
    ]["safety_state"]

    assert (
        set(safety_state)
        == set(SAFETY_STATE_FIELDS)
    )

    assert all(
        value is False
        for value in safety_state.values()
    )


def test_gp681_690_exact_idempotent_replay(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    first = _prepare(
        service
    )

    second = _prepare(
        service
    )

    assert (
        first.preparation_id
        == second.preparation_id
    )

    assert (
        first.preparation_hash
        == second.preparation_hash
    )

    assert (
        first.idempotent_replay
        is False
    )

    assert (
        second.idempotent_replay
        is True
    )

    events = service.list_events(
        first.preparation_id
    )

    assert len(events) == 1


def test_gp681_690_rejects_changed_idempotent_inputs(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    _prepare(
        service
    )

    with pytest.raises(
        AuthorizationDecisionPreparationError,
        match="different immutable",
    ):
        _prepare(
            service,
            target_environment="PRODUCTION",
        )


def test_gp681_690_requires_not_granted_authorization_gate_lineage(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        AuthorizationDecisionPreparationError,
        match="AUTHORIZATION_GATE_SEALED",
    ):
        _prepare(
            service,
            authorization_gate_state=(
                "AUTHORIZED"
            ),
        )


@pytest.mark.parametrize(
    "operation",
    [
        "SELECT_OWNER_DECISION",
        "INVENT_OWNER_DECISION",
        "RECORD_OWNER_DECISION",
        "OPEN_OWNER_DECISION_RECORDING_GATE",
        "AUTHENTICATE_OWNER",
        "STEP_UP_OWNER",
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
def test_gp681_690_rejects_prohibited_operations(
    tmp_path: Path,
    operation: str,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        AuthorizationDecisionPreparationError,
        match="prohibited operation",
    ):
        _prepare(
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
        {
            "raw_path": "/tmp/raw"
        },
        {
            "raw_url": "https://example.test/raw"
        },
        {
            "token": "do-not-store"
        },
        {
            "authorization_token": "do-not-store"
        },
        {
            "credentials": {
                "username": "x"
            }
        },
        {
            "nested": {
                "private_key": "x"
            }
        },
        {
            "raw_material": {
                "content": "x"
            }
        },
        {
            "provider_secret": "x"
        },
    ],
)
def test_gp681_690_rejects_raw_or_secret_metadata(
    tmp_path: Path,
    safe_metadata,
) -> None:
    service = _service(
        tmp_path
    )

    with pytest.raises(
        AuthorizationDecisionPreparationError,
        match="prohibited",
    ):
        _prepare(
            service,
            safe_metadata=safe_metadata,
        )


def test_gp681_690_verification_passes(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _prepare(
        service
    )

    result = service.verify_preparation(
        receipt.preparation_id
    )

    assert result["verified"] is True
    assert result["preparation_hash_valid"] is True
    assert result["event_chain_valid"] is True
    assert result["tower_destination_only"] is True

    assert (
        result[
            "authorization_gate_not_granted_lineage"
        ]
        is True
    )

    assert (
        result["decision_packet_prepared"]
        is True
    )

    assert (
        result["owner_decision_selected"]
        is False
    )

    assert (
        result["owner_decision_invented"]
        is False
    )

    assert (
        result["owner_decision_recorded"]
        is False
    )

    assert (
        result[
            "owner_decision_recording_gate_opened"
        ]
        is False
    )

    assert (
        result["owner_authenticated"]
        is False
    )

    assert (
        result["owner_stepped_up"]
        is False
    )

    assert (
        result["owner_admin_approval_granted"]
        is False
    )

    assert (
        result["dual_receipt_satisfied"]
        is False
    )

    assert (
        result["second_authority_review_granted"]
        is False
    )

    assert (
        result["go_decision_granted"]
        is False
    )

    assert (
        result["recovery_authorization_granted"]
        is False
    )

    assert (
        result["authorization_token_issued"]
        is False
    )

    assert (
        result["handoff_delivered"]
        is False
    )

    assert (
        result["recovery_commit_command_issued"]
        is False
    )

    assert (
        result["recovery_commit_executed"]
        is False
    )

    assert result["restore_occurred"] is False

    assert (
        result["production_mount_occurred"]
        is False
    )

    assert (
        result["production_write_occurred"]
        is False
    )

    assert (
        result["provider_connection_occurred"]
        is False
    )

    assert (
        result["raw_material_exposed"]
        is False
    )

    assert (
        result["destructive_action_occurred"]
        is False
    )

    assert (
        result["unsafe_completed_actions"]
        == []
    )


def test_gp681_690_records_are_immutable(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _prepare(
        service
    )

    connection = sqlite3.connect(
        str(
            service.database_path
        )
    )

    try:
        with pytest.raises(
            sqlite3.IntegrityError,
            match="immutable",
        ):
            connection.execute(
                """
                UPDATE vault_gp681_690_authorization_decision_preparations
                SET preparation_state = 'DECISION_RECORDED'
                WHERE preparation_id = ?
                """,
                (
                    receipt.preparation_id,
                ),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp681_690_records_are_append_only(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _prepare(
        service
    )

    connection = sqlite3.connect(
        str(
            service.database_path
        )
    )

    try:
        with pytest.raises(
            sqlite3.IntegrityError,
            match="append-only",
        ):
            connection.execute(
                """
                DELETE FROM vault_gp681_690_authorization_decision_preparations
                WHERE preparation_id = ?
                """,
                (
                    receipt.preparation_id,
                ),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp681_690_events_are_immutable_and_append_only(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path
    )

    receipt = _prepare(
        service
    )

    event = service.list_events(
        receipt.preparation_id
    )[0]

    connection = sqlite3.connect(
        str(
            service.database_path
        )
    )

    try:
        with pytest.raises(
            sqlite3.IntegrityError,
            match="immutable",
        ):
            connection.execute(
                """
                UPDATE vault_gp681_690_authorization_decision_preparation_events
                SET event_type = 'MUTATED'
                WHERE event_id = ?
                """,
                (
                    event["event_id"],
                ),
            )

        connection.rollback()

        with pytest.raises(
            sqlite3.IntegrityError,
            match="append-only",
        ):
            connection.execute(
                """
                DELETE FROM vault_gp681_690_authorization_decision_preparation_events
                WHERE event_id = ?
                """,
                (
                    event["event_id"],
                ),
            )

        connection.rollback()

    finally:
        connection.close()
