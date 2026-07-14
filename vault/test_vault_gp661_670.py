from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from vault.recovery_commit_owner_decision_tower_handoff_delivery_preparation_layer_service import (
    CURRENT_RECOMMENDATION,
    DELIVERY_STATE,
    DeliveryPreparationError,
    RecoveryCommitOwnerDecisionTowerHandoffDeliveryPreparationService,
    SAFETY_STATE_FIELDS,
)


def _service(
    tmp_path: Path,
) -> RecoveryCommitOwnerDecisionTowerHandoffDeliveryPreparationService:
    return (
        RecoveryCommitOwnerDecisionTowerHandoffDeliveryPreparationService(
            tmp_path / "gp661_670.sqlite3"
        )
    )


def _prepare(
    service,
    **overrides,
):
    request = {
        "idempotency_key": "gp661-670-case-001",
        "recovery_case_id": "recovery-case-001",
        "owner_decision_record_id": "owner-decision-record-001",
        "acceptance_closeout_record_id": (
            "acceptance-closeout-record-001"
        ),
        "acceptance_closeout_package_hash": "a" * 64,
        "tower_authority_id": "tower-authority-001",
        "tower_delivery_target_id": "tower-delivery-target-001",
        "target_environment": "STAGING",
        "safe_metadata": {
            "prior_pack_range": "GP651-GP660",
            "evidence_reference_count": 8,
            "redaction_profile": "tower-safe",
        },
    }

    request.update(overrides)

    return service.prepare_tower_handoff_delivery(
        **request
    )


def test_gp661_670_builds_prepared_not_sent_checkpoint(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _prepare(service)

    assert receipt.recommendation == CURRENT_RECOMMENDATION
    assert receipt.delivery_state == DELIVERY_STATE
    assert receipt.prepared is True
    assert receipt.sent is False
    assert receipt.immutable is True
    assert receipt.append_only is True
    assert receipt.idempotent_replay is False

    record = service.get_preparation(
        receipt.preparation_id
    )

    payload = record["preparation_payload"]

    assert payload["gp661_preparation_shell"]["pack"] == "GP661"
    assert payload["gp662_acceptance_intake_board"]["pack"] == "GP662"
    assert payload["gp663_tower_target_board"]["pack"] == "GP663"
    assert payload["gp664_prerequisite_board"]["pack"] == "GP664"
    assert payload["gp665_replay_board"]["pack"] == "GP665"
    assert payload["gp666_payload_envelope"]["pack"] == "GP666"
    assert payload["gp667_delivery_packet_draft"]["pack"] == "GP667"
    assert payload["gp668_delivery_receipt_draft"]["pack"] == "GP668"
    assert payload["gp669_safety_blocker_board"]["pack"] == "GP669"
    assert payload["gp670_checkpoint"]["pack"] == "GP670"

    assert (
        payload["gp661_preparation_shell"]["sent"]
        is False
    )

    assert (
        payload["gp667_delivery_packet_draft"][
            "packet_status"
        ]
        == "DRAFT_NOT_SENT"
    )

    assert (
        payload["gp668_delivery_receipt_draft"][
            "receipt_finalized"
        ]
        is False
    )

    assert (
        payload["gp670_checkpoint"]["sent"]
        is False
    )


def test_gp661_670_safety_state_remains_all_false(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _prepare(service)

    record = service.get_preparation(
        receipt.preparation_id
    )

    safety_state = record[
        "safety_blocker_board"
    ]["safety_state"]

    assert set(safety_state) == set(
        SAFETY_STATE_FIELDS
    )

    assert all(
        value is False
        for value in safety_state.values()
    )


def test_gp661_670_exact_idempotent_replay(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    first = _prepare(service)
    second = _prepare(service)

    assert first.preparation_id == second.preparation_id
    assert first.preparation_hash == second.preparation_hash
    assert first.idempotent_replay is False
    assert second.idempotent_replay is True

    events = service.list_events(
        first.preparation_id
    )

    assert len(events) == 1


def test_gp661_670_rejects_changed_idempotent_inputs(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    _prepare(service)

    with pytest.raises(
        DeliveryPreparationError,
        match="different immutable",
    ):
        _prepare(
            service,
            target_environment="PRODUCTION",
        )


@pytest.mark.parametrize(
    "operation",
    [
        "DELIVER_HANDOFF",
        "SEND_HANDOFF",
        "ACCEPT_HANDOFF",
        "RECORD_ACCEPTANCE_DECISION",
        "CREATE_TOWER_ACCEPTANCE_SESSION",
        "START_TOWER_ACCEPTANCE_SESSION",
        "CREATE_TOWER_DELIVERY_SESSION",
        "START_TOWER_DELIVERY_SESSION",
        "AUTHENTICATE_OWNER",
        "STEP_UP_OWNER",
        "GRANT_OWNER_APPROVAL",
        "GRANT_ADMIN_APPROVAL",
        "SATISFY_DUAL_RECEIPT",
        "GRANT_SECOND_AUTHORITY_REVIEW",
        "SELECT_OWNER_DECISION",
        "RECORD_OWNER_DECISION",
        "OPEN_OWNER_DECISION_RECORDING_GATE",
        "GRANT_GO_DECISION",
        "ISSUE_RECOVERY_AUTHORIZATION",
        "ISSUE_AUTHORIZATION_TOKEN",
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
def test_gp661_670_rejects_prohibited_operations(
    tmp_path: Path,
    operation: str,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        DeliveryPreparationError,
        match="prohibited operation",
    ):
        _prepare(
            service,
            idempotency_key=(
                "prohibited-" + operation.lower()
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
        {"credentials": {"username": "x"}},
        {"nested": {"private_key": "x"}},
        {"raw_material": {"content": "x"}},
        {"provider_secret": "x"},
    ],
)
def test_gp661_670_rejects_raw_or_secret_metadata(
    tmp_path: Path,
    safe_metadata,
) -> None:
    service = _service(tmp_path)

    with pytest.raises(
        DeliveryPreparationError,
        match="prohibited",
    ):
        _prepare(
            service,
            safe_metadata=safe_metadata,
        )


def test_gp661_670_verification_passes(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _prepare(service)

    result = service.verify_preparation(
        receipt.preparation_id
    )

    assert result["verified"] is True
    assert result["preparation_hash_valid"] is True
    assert result["event_chain_valid"] is True
    assert result["tower_destination_only"] is True
    assert result["prepared"] is True
    assert result["sent"] is False
    assert result["delivery_authorized"] is False
    assert result["authorization_token_issued"] is False
    assert result["go_decision_granted"] is False
    assert result["recovery_commit_command_issued"] is False
    assert result["restore_occurred"] is False
    assert result["production_write_occurred"] is False
    assert result["provider_connection_occurred"] is False
    assert result["raw_material_exposed"] is False
    assert result["destructive_action_occurred"] is False
    assert result["unsafe_completed_actions"] == []


def test_gp661_670_preparation_records_are_immutable(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _prepare(service)

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
                UPDATE vault_gp661_670_delivery_preparations
                SET delivery_state = 'SENT'
                WHERE preparation_id = ?
                """,
                (receipt.preparation_id,),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp661_670_preparation_records_are_append_only(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _prepare(service)

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
                DELETE FROM vault_gp661_670_delivery_preparations
                WHERE preparation_id = ?
                """,
                (receipt.preparation_id,),
            )

        connection.rollback()

    finally:
        connection.close()


def test_gp661_670_events_are_immutable_and_append_only(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    receipt = _prepare(service)

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
                UPDATE vault_gp661_670_delivery_preparation_events
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
                DELETE FROM vault_gp661_670_delivery_preparation_events
                WHERE event_id = ?
                """,
                (event["event_id"],),
            )

        connection.rollback()

    finally:
        connection.close()
