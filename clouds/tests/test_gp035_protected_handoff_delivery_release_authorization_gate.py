from dataclasses import replace

import pytest

from clouds.protected_handoff_delivery_release_service import (
    get_clouds_gp035_status_payload,
    get_gp035_authorized_fixture,
    get_gp035_declined_fixture,
    get_protected_handoff_release_authorization_surface,
    get_protected_handoff_release_authorization_surface_payload,
    record_delivery_release_decision,
)

from clouds.protected_handoff_package_service import (
    get_gp034_protected_handoff_package,
)


def test_gp035_authorize_release_path():
    record = (
        get_gp035_authorized_fixture()
    )

    assert (
        record.owner_release_decision
        == "authorize_release"
    )

    assert (
        record.release_state
        == "authorized_for_release"
    )

    assert (
        record.delivery_release_authorized
        is True
    )


def test_gp035_decline_release_path():
    record = (
        get_gp035_declined_fixture()
    )

    assert (
        record.owner_release_decision
        == "decline_release"
    )

    assert (
        record.release_state
        == "declined"
    )

    assert (
        record.delivery_release_authorized
        is False
    )


def test_gp035_invalid_decision_fails_closed():
    package = (
        get_gp034_protected_handoff_package()
    )

    with pytest.raises(ValueError):
        record_delivery_release_decision(
            package,
            "maybe",
        )


def test_gp035_requires_prepared_package():
    package = (
        get_gp034_protected_handoff_package()
    )

    bad = replace(
        package,
        package_state="blocked",
    )

    with pytest.raises(ValueError):
        record_delivery_release_decision(
            bad,
            "authorize_release",
        )


def test_gp035_requires_preparation_authorization():
    package = (
        get_gp034_protected_handoff_package()
    )

    bad = replace(
        package,
        preparation_authorized=False,
    )

    with pytest.raises(ValueError):
        record_delivery_release_decision(
            bad,
            "authorize_release",
        )


def test_gp035_rejects_already_authorized_package_state():
    package = (
        get_gp034_protected_handoff_package()
    )

    bad = replace(
        package,
        delivery_authorized=True,
    )

    with pytest.raises(ValueError):
        record_delivery_release_decision(
            bad,
            "authorize_release",
        )


def test_gp035_rejects_already_released_package():
    package = (
        get_gp034_protected_handoff_package()
    )

    bad = replace(
        package,
        delivery_released=True,
    )

    with pytest.raises(ValueError):
        record_delivery_release_decision(
            bad,
            "authorize_release",
        )


def test_gp035_rejects_already_delivered_package():
    package = (
        get_gp034_protected_handoff_package()
    )

    bad = replace(
        package,
        handoff_delivered=True,
    )

    with pytest.raises(ValueError):
        record_delivery_release_decision(
            bad,
            "authorize_release",
        )


def test_gp035_tampered_hash_fails_closed():
    package = (
        get_gp034_protected_handoff_package()
    )

    bad = replace(
        package,
        package_integrity_hash=(
            "0" * 64
        ),
    )

    with pytest.raises(ValueError):
        record_delivery_release_decision(
            bad,
            "authorize_release",
        )


def test_gp035_tampered_selected_option_fails_closed():
    package = (
        get_gp034_protected_handoff_package()
    )

    bad = replace(
        package,
        selected_option_kind="tampered",
    )

    with pytest.raises(ValueError):
        record_delivery_release_decision(
            bad,
            "authorize_release",
        )


def test_gp035_tampered_delivery_target_fails_closed():
    package = (
        get_gp034_protected_handoff_package()
    )

    bad = replace(
        package,
        delivery_target_id="tampered-target",
    )

    with pytest.raises(ValueError):
        record_delivery_release_decision(
            bad,
            "authorize_release",
        )


def test_gp035_credentials_remain_excluded():
    record = (
        get_gp035_authorized_fixture()
    )

    assert (
        record.credentials_included
        is False
    )


def test_gp035_tower_session_material_remains_excluded():
    record = (
        get_gp035_authorized_fixture()
    )

    assert (
        record
        .tower_session_material_included
        is False
    )


def test_gp035_raw_evidence_remains_excluded():
    record = (
        get_gp035_authorized_fixture()
    )

    assert (
        record.raw_evidence_included
        is False
    )


def test_gp035_preserves_package_hash():
    package = (
        get_gp034_protected_handoff_package()
    )

    record = (
        get_gp035_authorized_fixture()
    )

    assert (
        record.package_integrity_hash
        == package.package_integrity_hash
    )

    assert (
        record.package_integrity_verified
        is True
    )


def test_gp035_preserves_package_binding():
    record = (
        get_gp035_authorized_fixture()
    )

    assert (
        record.package_binding_verified
        is True
    )


def test_gp035_preserves_selected_option():
    package = (
        get_gp034_protected_handoff_package()
    )

    record = (
        get_gp035_authorized_fixture()
    )

    assert (
        record.selected_option_id
        == package.selected_option_id
    )

    assert (
        record.selected_option_kind
        == package.selected_option_kind
    )

    assert (
        record.selected_option_label
        == package.selected_option_label
    )


def test_gp035_preserves_owning_application():
    package = (
        get_gp034_protected_handoff_package()
    )

    record = (
        get_gp035_authorized_fixture()
    )

    assert (
        record.owning_application_id
        == package.owning_application_id
    )

    assert (
        record.owning_application_label
        == package.owning_application_label
    )


def test_gp035_preserves_tower_mediation():
    package = (
        get_gp034_protected_handoff_package()
    )

    record = (
        get_gp035_authorized_fixture()
    )

    assert (
        record.requires_tower_mediation
        == package.requires_tower_mediation
    )


def test_gp035_preserves_delivery_target():
    package = (
        get_gp034_protected_handoff_package()
    )

    record = (
        get_gp035_authorized_fixture()
    )

    assert (
        record.delivery_target_kind
        == package.delivery_target_kind
    )

    assert (
        record.delivery_target_id
        == package.delivery_target_id
    )


def test_gp035_authorization_does_not_release():
    record = (
        get_gp035_authorized_fixture()
    )

    assert (
        record.delivery_release_authorized
        is True
    )

    assert (
        record.delivery_released
        is False
    )


def test_gp035_authorization_does_not_deliver():
    record = (
        get_gp035_authorized_fixture()
    )

    assert (
        record.handoff_delivered
        is False
    )


def test_gp035_no_downstream_approval():
    record = (
        get_gp035_authorized_fixture()
    )

    assert (
        record.approval_performed
        is False
    )


def test_gp035_no_capital_movement():
    record = (
        get_gp035_authorized_fixture()
    )

    assert (
        record.capital_movement_performed
        is False
    )


def test_gp035_no_downstream_execution():
    record = (
        get_gp035_authorized_fixture()
    )

    assert (
        record
        .downstream_execution_performed
        is False
    )


def test_gp035_soulaana_explains_release_boundary():
    record = (
        get_gp035_authorized_fixture()
    )

    assert (
        record.soulaana_release_summary
    )

    assert (
        record.soulaana_what_this_means
    )

    assert (
        record
        .soulaana_what_did_not_happen
    )

    assert (
        record.soulaana_next_step
    )


def test_gp035_surface_counts():
    surface = (
        get_protected_handoff_release_authorization_surface()
    )

    assert (
        surface.record_count
        == 1
    )

    assert (
        surface.authorized_count
        == 1
    )

    assert (
        surface.declined_count
        == 0
    )

    assert (
        surface.blocked_count
        == 0
    )


def test_gp035_surface_authorized_but_not_released():
    surface = (
        get_protected_handoff_release_authorization_surface()
    )

    assert (
        surface
        .delivery_release_authorized
        is True
    )

    assert (
        surface.delivery_released
        is False
    )

    assert (
        surface.handoff_delivered
        is False
    )


def test_gp035_payload_serializes():
    payload = (
        get_protected_handoff_release_authorization_surface_payload()
    )

    assert (
        payload["record_count"]
        == len(
            payload["records"]
        )
    )


def test_gp035_status_ready():
    status = (
        get_clouds_gp035_status_payload()
    )

    assert (
        status["pack"]
        == "GP035"
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
        status[
            "release_authorization_record_count"
        ]
        == 1
    )

    assert (
        status["authorized_count"]
        == 1
    )

    assert (
        status["declined_count"]
        == 0
    )

    assert (
        status["blocked_count"]
        == 0
    )

    assert (
        status[
            "owner_confirmation_recorded"
        ]
        is True
    )

    assert (
        status[
            "authorize_release_path_verified"
        ]
        is True
    )

    assert (
        status[
            "decline_release_path_verified"
        ]
        is True
    )

    assert (
        status[
            "package_integrity_verified"
        ]
        is True
    )

    assert (
        status[
            "package_binding_verified"
        ]
        is True
    )

    assert (
        status[
            "schema_preserved"
        ]
        is True
    )

    assert (
        status[
            "tower_mediation_preserved"
        ]
        is True
    )

    assert (
        status[
            "delivery_target_preserved"
        ]
        is True
    )

    assert (
        status[
            "credentials_included"
        ]
        is False
    )

    assert (
        status[
            "tower_session_material_included"
        ]
        is False
    )

    assert (
        status[
            "raw_evidence_included"
        ]
        is False
    )

    assert (
        status[
            "delivery_release_authorized"
        ]
        is True
    )

    assert (
        status[
            "delivery_released"
        ]
        is False
    )

    assert (
        status[
            "handoff_delivered"
        ]
        is False
    )

    assert (
        status[
            "approval_performed"
        ]
        is False
    )

    assert (
        status[
            "capital_movement_performed"
        ]
        is False
    )

    assert (
        status[
            "downstream_execution_performed"
        ]
        is False
    )

    assert (
        status["next_pack"]
        == (
            "GP036 — PROTECTED HANDOFF RELEASE RECORD / "
            "DELIVERY ENVELOPE PREPARATION"
        )
    )
