from dataclasses import replace

import pytest

from clouds.protected_handoff_delivery_release_service import (
    get_gp035_authorized_fixture,
    get_gp035_declined_fixture,
)

from clouds.protected_handoff_release_record_service import (
    build_protected_handoff_delivery_envelope,
    build_protected_handoff_release_record,
    get_clouds_gp036_status_payload,
    get_gp036_delivery_envelope,
    get_gp036_release_record,
    get_protected_handoff_release_preparation_surface,
    get_protected_handoff_release_preparation_surface_payload,
)


def test_gp036_builds_release_record():
    record = (
        get_gp036_release_record()
    )

    assert (
        record.release_record_state
        == "prepared"
    )

    assert (
        record.release_record_prepared
        is True
    )


def test_gp036_requires_authorized_release():
    authorization = (
        get_gp035_authorized_fixture()
    )

    bad = replace(
        authorization,
        delivery_release_authorized=False,
    )

    with pytest.raises(ValueError):
        build_protected_handoff_release_record(
            bad
        )


def test_gp036_declined_release_fails_closed():
    declined = (
        get_gp035_declined_fixture()
    )

    with pytest.raises(ValueError):
        build_protected_handoff_release_record(
            declined
        )


def test_gp036_tampered_package_hash_fails_closed():
    authorization = (
        get_gp035_authorized_fixture()
    )

    bad = replace(
        authorization,
        package_integrity_hash=(
            "0" * 64
        ),
    )

    with pytest.raises(ValueError):
        build_protected_handoff_release_record(
            bad
        )


def test_gp036_tampered_target_fails_closed():
    authorization = (
        get_gp035_authorized_fixture()
    )

    bad = replace(
        authorization,
        delivery_target_id="tampered",
    )

    with pytest.raises(ValueError):
        build_protected_handoff_release_record(
            bad
        )


def test_gp036_release_record_hash_present():
    record = (
        get_gp036_release_record()
    )

    assert (
        len(
            record
            .release_record_integrity_hash
        )
        == 64
    )


def test_gp036_release_record_hash_deterministic():
    first = (
        get_gp036_release_record()
    )

    second = (
        get_gp036_release_record()
    )

    assert (
        first.release_record_integrity_hash
        == second.release_record_integrity_hash
    )


def test_gp036_preserves_package_hash():
    authorization = (
        get_gp035_authorized_fixture()
    )

    record = (
        get_gp036_release_record()
    )

    assert (
        record.package_integrity_hash
        == authorization.package_integrity_hash
    )


def test_gp036_preserves_selected_option():
    authorization = (
        get_gp035_authorized_fixture()
    )

    record = (
        get_gp036_release_record()
    )

    assert (
        record.selected_option_id
        == authorization.selected_option_id
    )

    assert (
        record.selected_option_kind
        == authorization.selected_option_kind
    )

    assert (
        record.selected_option_label
        == authorization.selected_option_label
    )


def test_gp036_preserves_owning_application():
    authorization = (
        get_gp035_authorized_fixture()
    )

    record = (
        get_gp036_release_record()
    )

    assert (
        record.owning_application_id
        == authorization.owning_application_id
    )


def test_gp036_preserves_tower_mediation():
    authorization = (
        get_gp035_authorized_fixture()
    )

    record = (
        get_gp036_release_record()
    )

    assert (
        record.requires_tower_mediation
        == authorization.requires_tower_mediation
    )


def test_gp036_preserves_delivery_target():
    authorization = (
        get_gp035_authorized_fixture()
    )

    record = (
        get_gp036_release_record()
    )

    assert (
        record.delivery_target_kind
        == authorization.delivery_target_kind
    )

    assert (
        record.delivery_target_id
        == authorization.delivery_target_id
    )


def test_gp036_builds_delivery_envelope():
    envelope = (
        get_gp036_delivery_envelope()
    )

    assert (
        envelope.envelope_state
        == "prepared"
    )

    assert (
        envelope.envelope_prepared
        is True
    )


def test_gp036_envelope_binds_release_record():
    record = (
        get_gp036_release_record()
    )

    envelope = (
        get_gp036_delivery_envelope()
    )

    assert (
        envelope.release_record_id
        == record.release_record_id
    )

    assert (
        envelope
        .release_record_integrity_hash
        == record
        .release_record_integrity_hash
    )


def test_gp036_tampered_release_record_hash_fails_closed():
    record = (
        get_gp036_release_record()
    )

    bad = replace(
        record,
        release_record_integrity_hash=(
            "0" * 64
        ),
    )

    with pytest.raises(ValueError):
        build_protected_handoff_delivery_envelope(
            bad
        )


def test_gp036_envelope_hash_present():
    envelope = (
        get_gp036_delivery_envelope()
    )

    assert (
        len(
            envelope
            .delivery_envelope_integrity_hash
        )
        == 64
    )


def test_gp036_envelope_hash_deterministic():
    first = (
        get_gp036_delivery_envelope()
    )

    second = (
        get_gp036_delivery_envelope()
    )

    assert (
        first.delivery_envelope_integrity_hash
        == second.delivery_envelope_integrity_hash
    )


def test_gp036_credentials_excluded():
    envelope = (
        get_gp036_delivery_envelope()
    )

    assert (
        envelope.credentials_included
        is False
    )


def test_gp036_tower_session_material_excluded():
    envelope = (
        get_gp036_delivery_envelope()
    )

    assert (
        envelope
        .tower_session_material_included
        is False
    )


def test_gp036_raw_evidence_excluded():
    envelope = (
        get_gp036_delivery_envelope()
    )

    assert (
        envelope.raw_evidence_included
        is False
    )


def test_gp036_release_not_executed():
    envelope = (
        get_gp036_delivery_envelope()
    )

    assert (
        envelope.delivery_release_executed
        is False
    )

    assert (
        envelope.delivery_released
        is False
    )


def test_gp036_delivery_not_attempted():
    envelope = (
        get_gp036_delivery_envelope()
    )

    assert (
        envelope.delivery_attempted
        is False
    )

    assert (
        envelope.handoff_delivered
        is False
    )


def test_gp036_no_approval():
    assert (
        get_gp036_delivery_envelope()
        .approval_performed
        is False
    )


def test_gp036_no_capital_movement():
    assert (
        get_gp036_delivery_envelope()
        .capital_movement_performed
        is False
    )


def test_gp036_no_downstream_execution():
    assert (
        get_gp036_delivery_envelope()
        .downstream_execution_performed
        is False
    )


def test_gp036_soulaana_explains_release_record():
    record = (
        get_gp036_release_record()
    )

    assert (
        record
        .soulaana_release_record_summary
    )

    assert (
        record.soulaana_why_it_matters
    )

    assert (
        record.soulaana_release_boundary
    )

    assert (
        record.soulaana_next_step
    )


def test_gp036_soulaana_explains_envelope():
    envelope = (
        get_gp036_delivery_envelope()
    )

    assert (
        envelope.soulaana_envelope_summary
    )

    assert (
        envelope.soulaana_why_it_matters
    )

    assert (
        envelope
        .soulaana_delivery_boundary
    )

    assert (
        envelope.soulaana_next_step
    )


def test_gp036_surface_counts():
    surface = (
        get_protected_handoff_release_preparation_surface()
    )

    assert (
        surface.release_record_count
        == 1
    )

    assert (
        surface.prepared_release_record_count
        == 1
    )

    assert (
        surface.delivery_envelope_count
        == 1
    )

    assert (
        surface
        .prepared_delivery_envelope_count
        == 1
    )

    assert (
        surface.blocked_count
        == 0
    )


def test_gp036_surface_executes_nothing():
    surface = (
        get_protected_handoff_release_preparation_surface()
    )

    assert (
        surface.delivery_release_authorized
        is True
    )

    assert (
        surface.delivery_release_executed
        is False
    )

    assert (
        surface.delivery_released
        is False
    )

    assert (
        surface.delivery_attempted
        is False
    )

    assert (
        surface.handoff_delivered
        is False
    )

    assert (
        surface.approval_performed
        is False
    )

    assert (
        surface.capital_movement_performed
        is False
    )

    assert (
        surface
        .downstream_execution_performed
        is False
    )


def test_gp036_payload_serializes():
    payload = (
        get_protected_handoff_release_preparation_surface_payload()
    )

    assert (
        payload["release_record_count"]
        == len(
            payload["release_records"]
        )
    )

    assert (
        payload["delivery_envelope_count"]
        == len(
            payload["delivery_envelopes"]
        )
    )


def test_gp036_status_ready():
    status = (
        get_clouds_gp036_status_payload()
    )

    assert (
        status["pack"]
        == "GP036"
    )

    assert (
        status["phase"]
        == "CLOUDS_PHASE_II"
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status["safe_to_continue"]
        is True
    )

    assert (
        status["release_record_count"]
        == 1
    )

    assert (
        status["prepared_release_record_count"]
        == 1
    )

    assert (
        status["delivery_envelope_count"]
        == 1
    )

    assert (
        status[
            "prepared_delivery_envelope_count"
        ]
        == 1
    )

    assert (
        status[
            "release_record_integrity_hash_present"
        ]
        is True
    )

    assert (
        status[
            "release_record_integrity_hash_deterministic"
        ]
        is True
    )

    assert (
        status[
            "delivery_envelope_integrity_hash_present"
        ]
        is True
    )

    assert (
        status[
            "delivery_envelope_integrity_hash_deterministic"
        ]
        is True
    )

    assert (
        status[
            "decline_path_fails_closed"
        ]
        is True
    )

    assert (
        status["delivery_release_authorized"]
        is True
    )

    assert (
        status["release_record_prepared"]
        is True
    )

    assert (
        status["delivery_envelope_prepared"]
        is True
    )

    assert (
        status["delivery_release_executed"]
        is False
    )

    assert (
        status["delivery_released"]
        is False
    )

    assert (
        status["delivery_attempted"]
        is False
    )

    assert (
        status["handoff_delivered"]
        is False
    )

    assert (
        status["approval_performed"]
        is False
    )

    assert (
        status["capital_movement_performed"]
        is False
    )

    assert (
        status["downstream_execution_performed"]
        is False
    )

    assert (
        status["next_pack"]
        == (
            "GP037 — PROTECTED HANDOFF RELEASE EXECUTION / "
            "DELIVERY ATTEMPT BOUNDARY"
        )
    )
