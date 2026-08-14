from dataclasses import replace

import pytest

from clouds.handoff_authorization_decision_service import (
    get_gp033_authorized_fixture,
    get_gp033_declined_fixture,
)

from clouds.protected_handoff_package_service import (
    build_protected_handoff_package,
    get_clouds_gp034_status_payload,
    get_gp034_protected_handoff_package,
    get_protected_handoff_preparation_surface,
    get_protected_handoff_preparation_surface_payload,
)


def test_gp034_builds_one_prepared_package():
    package = (
        get_gp034_protected_handoff_package()
    )

    assert (
        package.package_state
        == "prepared"
    )

    assert (
        package.delivery_prepared
        is True
    )


def test_gp034_requires_owner_confirmation():
    authorized = (
        get_gp033_authorized_fixture()
    )

    bad = replace(
        authorized,
        owner_confirmation_recorded=False,
    )

    with pytest.raises(ValueError):
        build_protected_handoff_package(
            bad
        )


def test_gp034_decline_fails_closed():
    declined = (
        get_gp033_declined_fixture()
    )

    with pytest.raises(ValueError):
        build_protected_handoff_package(
            declined
        )


def test_gp034_requires_authorized_preparation_state():
    authorized = (
        get_gp033_authorized_fixture()
    )

    bad = replace(
        authorized,
        authorization_state="declined",
        handoff_authorized=False,
    )

    with pytest.raises(ValueError):
        build_protected_handoff_package(
            bad
        )


def test_gp034_rejects_already_delivered_record():
    authorized = (
        get_gp033_authorized_fixture()
    )

    bad = replace(
        authorized,
        handoff_delivered=True,
    )

    with pytest.raises(ValueError):
        build_protected_handoff_package(
            bad
        )


def test_gp034_preserves_authorization_binding():
    authorized = (
        get_gp033_authorized_fixture()
    )

    package = (
        get_gp034_protected_handoff_package()
    )

    assert (
        package.authorization_record_id
        == authorized.authorization_record_id
    )

    assert (
        package.intent_review_id
        == authorized.intent_review_id
    )

    assert (
        package.choice_record_id
        == authorized.choice_record_id
    )


def test_gp034_preserves_selected_option():
    authorized = (
        get_gp033_authorized_fixture()
    )

    package = (
        get_gp034_protected_handoff_package()
    )

    assert (
        package.selected_option_id
        == authorized.selected_option_id
    )

    assert (
        package.selected_option_kind
        == authorized.selected_option_kind
    )

    assert (
        package.selected_option_label
        == authorized.selected_option_label
    )


def test_gp034_preserves_owning_application():
    authorized = (
        get_gp033_authorized_fixture()
    )

    package = (
        get_gp034_protected_handoff_package()
    )

    assert (
        package.owning_application_id
        == authorized.owning_application_id
    )

    assert (
        package.owning_application_label
        == authorized.owning_application_label
    )


def test_gp034_preserves_tower_mediation():
    authorized = (
        get_gp033_authorized_fixture()
    )

    package = (
        get_gp034_protected_handoff_package()
    )

    assert (
        package.requires_tower_mediation
        == authorized.requires_tower_mediation
    )

    if (
        package.requires_tower_mediation
    ):
        assert (
            package.delivery_target_kind
            == "tower_mediated"
        )

        assert (
            package.delivery_target_id
            == "tower"
        )


def test_gp034_hash_is_present():
    package = (
        get_gp034_protected_handoff_package()
    )

    assert (
        len(
            package.package_integrity_hash
        )
        == 64
    )


def test_gp034_hash_is_deterministic():
    first = (
        get_gp034_protected_handoff_package()
    )

    second = (
        get_gp034_protected_handoff_package()
    )

    assert (
        first.package_integrity_hash
        == second.package_integrity_hash
    )


def test_gp034_excludes_credentials():
    package = (
        get_gp034_protected_handoff_package()
    )

    assert (
        package.credentials_included
        is False
    )


def test_gp034_excludes_tower_session_material():
    package = (
        get_gp034_protected_handoff_package()
    )

    assert (
        package
        .tower_session_material_included
        is False
    )


def test_gp034_excludes_raw_evidence():
    package = (
        get_gp034_protected_handoff_package()
    )

    assert (
        package.raw_evidence_included
        is False
    )


def test_gp034_delivery_is_not_authorized():
    package = (
        get_gp034_protected_handoff_package()
    )

    assert (
        package.delivery_authorized
        is False
    )


def test_gp034_delivery_is_not_released():
    package = (
        get_gp034_protected_handoff_package()
    )

    assert (
        package.delivery_released
        is False
    )


def test_gp034_handoff_not_delivered():
    package = (
        get_gp034_protected_handoff_package()
    )

    assert (
        package.handoff_delivered
        is False
    )


def test_gp034_no_approval():
    package = (
        get_gp034_protected_handoff_package()
    )

    assert (
        package.approval_performed
        is False
    )


def test_gp034_no_capital_movement():
    package = (
        get_gp034_protected_handoff_package()
    )

    assert (
        package.capital_movement_performed
        is False
    )


def test_gp034_no_downstream_execution():
    package = (
        get_gp034_protected_handoff_package()
    )

    assert (
        package
        .downstream_execution_performed
        is False
    )


def test_gp034_soulaana_explains_package():
    package = (
        get_gp034_protected_handoff_package()
    )

    assert (
        package.soulaana_package_summary
    )

    assert (
        package.soulaana_why_it_matters
    )

    assert (
        package
        .soulaana_delivery_boundary
    )

    assert (
        package.soulaana_next_step
    )


def test_gp034_surface_counts():
    surface = (
        get_protected_handoff_preparation_surface()
    )

    assert (
        surface.package_count
        == 1
    )

    assert (
        surface.prepared_count
        == 1
    )

    assert (
        surface.blocked_count
        == 0
    )


def test_gp034_surface_not_released():
    surface = (
        get_protected_handoff_preparation_surface()
    )

    assert (
        surface.delivery_prepared
        is True
    )

    assert (
        surface.delivery_authorized
        is False
    )

    assert (
        surface.delivery_released
        is False
    )

    assert (
        surface.handoff_delivered
        is False
    )


def test_gp034_payload_serializes():
    payload = (
        get_protected_handoff_preparation_surface_payload()
    )

    assert (
        payload["package_count"]
        == len(
            payload["packages"]
        )
    )


def test_gp034_status_ready():
    status = (
        get_clouds_gp034_status_payload()
    )

    assert (
        status["pack"]
        == "GP034"
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
        status["package_count"]
        == 1
    )

    assert (
        status["prepared_count"]
        == 1
    )

    assert (
        status["blocked_count"]
        == 0
    )

    assert (
        status[
            "integrity_hash_present"
        ]
        is True
    )

    assert (
        status[
            "integrity_hash_deterministic"
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
        status[
            "preparation_authorized"
        ]
        is True
    )

    assert (
        status["delivery_prepared"]
        is True
    )

    assert (
        status["delivery_authorized"]
        is False
    )

    assert (
        status["delivery_released"]
        is False
    )

    assert (
        status["handoff_delivered"]
        is False
    )

    assert (
        status["credentials_included"]
        is False
    )

    assert (
        status[
            "tower_session_material_included"
        ]
        is False
    )

    assert (
        status["raw_evidence_included"]
        is False
    )

    assert (
        status["approval_performed"]
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
            "GP035 — PROTECTED HANDOFF DELIVERY RELEASE / "
            "AUTHORIZATION GATE"
        )
    )
