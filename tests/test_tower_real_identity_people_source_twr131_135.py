
from __future__ import annotations

import json
from pathlib import Path

from werkzeug.security import (
    generate_password_hash,
)

from tower.identity_authority import (
    TOWER_LOCAL_WALKTHROUGH_MODE_ENV,
    TOWER_ORGANIZATION_ID_ENV,
    TOWER_ORGANIZATION_NAME_ENV,
    TOWER_OWNER_DISPLAY_NAME_ENV,
    TOWER_OWNER_ID_ENV,
    TOWER_OWNER_PASSWORD_HASH_ENV,
    TOWER_OWNER_USERNAME_ENV,
    hosted_owner_identity_authority,
    hosted_owner_identity_config_status,
)
from tower.owner_dashboard_service import (
    build_tower_owner_dashboard,
    owner_dashboard_status_cards,
)
from tower.owner_dashboard_web import (
    _owner_people_html,
)
from tower.owner_people_registry import (
    active_people,
    owner_people_authority_snapshot,
    owner_people_records,
    person_by_id,
)
from tower.truth_contract import (
    NOT_CONFIGURED,
    UNKNOWN,
    VERIFIED,
)


REPO = Path(
    "/content/SimpleeMrkTrade"
)


IDENTITY_ENV = (
    TOWER_OWNER_USERNAME_ENV,
    TOWER_OWNER_PASSWORD_HASH_ENV,
    TOWER_OWNER_ID_ENV,
    TOWER_LOCAL_WALKTHROUGH_MODE_ENV,
    TOWER_OWNER_DISPLAY_NAME_ENV,
    TOWER_ORGANIZATION_ID_ENV,
    TOWER_ORGANIZATION_NAME_ENV,
    "TOWER_LOCAL_OWNER_PASSWORD",
)


def clear_identity_environment(
    monkeypatch,
):
    for name in IDENTITY_ENV:
        monkeypatch.delenv(
            name,
            raising=False,
        )


def configure_hosted_owner(
    monkeypatch,
    *,
    include_owner_id=True,
    include_organization=True,
):
    clear_identity_environment(
        monkeypatch
    )

    credential_hash = (
        generate_password_hash(
            "twr131-test-credential"
        )
    )

    monkeypatch.setenv(
        TOWER_OWNER_USERNAME_ENV,
        "tower-owner-test",
    )

    monkeypatch.setenv(
        TOWER_OWNER_PASSWORD_HASH_ENV,
        credential_hash,
    )

    monkeypatch.setenv(
        TOWER_OWNER_DISPLAY_NAME_ENV,
        "Configured Tower Owner",
    )

    if include_owner_id:
        monkeypatch.setenv(
            TOWER_OWNER_ID_ENV,
            "owner-test-id",
        )

    if include_organization:
        monkeypatch.setenv(
            TOWER_ORGANIZATION_ID_ENV,
            "simplee-world-test",
        )

        monkeypatch.setenv(
            TOWER_ORGANIZATION_NAME_ENV,
            "Simplee World Test",
        )

    return credential_hash


def test_twr131_missing_hosted_credentials_stays_not_configured(
    monkeypatch,
):
    clear_identity_environment(
        monkeypatch
    )

    status = (
        hosted_owner_identity_config_status()
    )

    authority = (
        hosted_owner_identity_authority()
    )

    assert status["configured"] is False
    assert status["verification_state"] == NOT_CONFIGURED

    assert authority["configured"] is False
    assert authority["record"] is None
    assert authority["verification_state"] == NOT_CONFIGURED


def test_twr131_local_mode_never_becomes_product_people_truth(
    monkeypatch,
):
    clear_identity_environment(
        monkeypatch
    )

    monkeypatch.setenv(
        TOWER_OWNER_USERNAME_ENV,
        "local-owner",
    )

    monkeypatch.setenv(
        TOWER_OWNER_PASSWORD_HASH_ENV,
        generate_password_hash(
            "local-test-credential"
        ),
    )

    monkeypatch.setenv(
        TOWER_LOCAL_WALKTHROUGH_MODE_ENV,
        "1",
    )

    authority = (
        hosted_owner_identity_authority()
    )

    assert authority["configured"] is False
    assert authority["record"] is None
    assert (
        authority["configuration"][
            "local_mode_excluded"
        ]
        is True
    )


def test_twr131_hosted_owner_projection_is_real_and_secret_free(
    monkeypatch,
):
    credential_hash = (
        configure_hosted_owner(
            monkeypatch
        )
    )

    authority = (
        hosted_owner_identity_authority()
    )

    assert authority["configured"] is True
    assert authority["verification_state"] == VERIFIED

    record = authority["record"]

    assert record is not None
    assert record["person_id"] == "owner-test-id"
    assert record["username"] == "tower-owner-test"
    assert record["display_name"] == "Configured Tower Owner"
    assert record["role"] == "owner"

    assert (
        record["account_state"]
        == "AUTHENTICATION_CONFIGURED"
    )

    assert (
        record["account_lifecycle_state"]
        == NOT_CONFIGURED
    )

    serialized = json.dumps(
        authority,
        sort_keys=True,
    )

    assert credential_hash not in serialized
    assert "twr131-test-credential" not in serialized

    assert (
        authority[
            "credential_hash_value_exposed"
        ]
        is False
    )

    assert (
        authority[
            "plaintext_password_exposed"
        ]
        is False
    )

    assert (
        authority[
            "session_secret_exposed"
        ]
        is False
    )


def test_twr131_owner_id_is_stable_derived_truth_when_not_explicit(
    monkeypatch,
):
    configure_hosted_owner(
        monkeypatch,
        include_owner_id=False,
    )

    first = (
        hosted_owner_identity_authority()[
            "record"
        ]
    )

    second = (
        hosted_owner_identity_authority()[
            "record"
        ]
    )

    assert first["person_id"] == second["person_id"]

    assert first[
        "person_id_source_class"
    ] == "DERIVED"

    assert first[
        "session_subject_alignment"
    ] == UNKNOWN


def test_twr132_role_is_current_owner_policy_truth(
    monkeypatch,
):
    configure_hosted_owner(
        monkeypatch
    )

    authority = (
        hosted_owner_identity_authority()
    )

    role = authority[
        "role_assignment"
    ]

    assert role["role"] == "owner"
    assert role["verification_state"] == VERIFIED
    assert role["source_class"] == "DERIVED"


def test_twr132_explicit_organization_membership_is_verified(
    monkeypatch,
):
    configure_hosted_owner(
        monkeypatch,
        include_organization=True,
    )

    authority = (
        hosted_owner_identity_authority()
    )

    organization = authority[
        "organization_membership"
    ]

    assert (
        organization[
            "verification_state"
        ]
        == VERIFIED
    )

    assert organization[
        "organization"
    ] == {
        "organization_id":
            "simplee-world-test",

        "organization_name":
            "Simplee World Test",

        "role":
            "owner",
    }


def test_twr132_missing_organization_is_not_fabricated(
    monkeypatch,
):
    configure_hosted_owner(
        monkeypatch,
        include_organization=False,
    )

    record = (
        hosted_owner_identity_authority()[
            "record"
        ]
    )

    assert record["organization"] is None

    assert (
        record[
            "organization_membership_state"
        ]
        == NOT_CONFIGURED
    )


def test_twr133_authentication_configuration_does_not_fake_account_lifecycle(
    monkeypatch,
):
    configure_hosted_owner(
        monkeypatch
    )

    record = (
        hosted_owner_identity_authority()[
            "record"
        ]
    )

    assert (
        record["authentication_state"]
        == "CONFIGURED"
    )

    assert (
        record["authentication_state_verification"]
        == VERIFIED
    )

    assert (
        record["account_lifecycle_state"]
        == NOT_CONFIGURED
    )

    assert record["suspension_state"] is None


def test_twr134_owner_observatory_policy_is_granted_without_runtime_claim(
    monkeypatch,
):
    configure_hosted_owner(
        monkeypatch
    )

    record = (
        hosted_owner_identity_authority()[
            "record"
        ]
    )

    entitlements = record[
        "app_entitlements"
    ]

    assert [
        item["app_id"]
        for item in entitlements
    ] == [
        "observatory",
    ]

    observatory = entitlements[0]

    assert (
        observatory["access_policy"]
        == "GRANTED"
    )

    assert (
        observatory["verification_state"]
        == VERIFIED
    )

    assert (
        observatory["runtime_availability"]
        is None
    )

    assert (
        observatory[
            "runtime_availability_state"
        ]
        == UNKNOWN
    )


def test_twr134_future_apps_are_not_granted_by_people_authority(
    monkeypatch,
):
    configure_hosted_owner(
        monkeypatch
    )

    record = (
        hosted_owner_identity_authority()[
            "record"
        ]
    )

    app_ids = {
        item["app_id"]
        for item in record[
            "app_entitlements"
        ]
    }

    assert "teller" not in app_ids
    assert "vault" not in app_ids
    assert "clouds" not in app_ids
    assert "grounds" not in app_ids


def test_twr135_people_registry_projects_one_real_configured_identity(
    monkeypatch,
):
    configure_hosted_owner(
        monkeypatch
    )

    authority = (
        owner_people_authority_snapshot()
    )

    people = (
        owner_people_records()
    )

    assert (
        authority["verification_state"]
        == VERIFIED
    )

    assert (
        authority[
            "authoritative_provider_configured"
        ]
        is True
    )

    assert len(people) == 1

    assert (
        authority[
            "people"
        ][
            "verification_state"
        ]
        == VERIFIED
    )

    assert (
        authority[
            "role_assignments"
        ][
            "verification_state"
        ]
        == VERIFIED
    )

    assert (
        authority[
            "app_entitlements"
        ][
            "verification_state"
        ]
        == VERIFIED
    )

    # Separate workflows remain honest.
    assert (
        authority[
            "invitations"
        ][
            "verification_state"
        ]
        == NOT_CONFIGURED
    )

    assert (
        authority[
            "access_control"
        ][
            "verification_state"
        ]
        == NOT_CONFIGURED
    )


def test_twr135_person_lookup_uses_real_projected_identifier(
    monkeypatch,
):
    configure_hosted_owner(
        monkeypatch
    )

    person = person_by_id(
        "owner-test-id"
    )

    assert person is not None
    assert person["username"] == "tower-owner-test"

    assert (
        person_by_id(
            "invented-person"
        )
        is None
    )


def test_twr135_active_people_does_not_fake_lifecycle_active(
    monkeypatch,
):
    configure_hosted_owner(
        monkeypatch
    )

    assert active_people() == []


def test_twr135_owner_hq_counts_only_verified_people(
    monkeypatch,
):
    configure_hosted_owner(
        monkeypatch
    )

    dashboard = (
        build_tower_owner_dashboard()
    )

    summary = dashboard[
        "summary"
    ]

    assert (
        summary["status"]
        == "tower_owner_dashboard_identity_authority_verified"
    )

    assert summary["people_count"] == 1

    # Missing lifecycle providers are not zero.
    assert summary["invitation_count"] is None
    assert summary["pending_access_count"] is None

    assert (
        summary[
            "people_authority_state"
        ]
        == VERIFIED
    )

    assert (
        summary[
            "entitlement_authority_state"
        ]
        == VERIFIED
    )

    assert (
        summary[
            "invitation_authority_state"
        ]
        == NOT_CONFIGURED
    )

    assert (
        summary[
            "access_authority_state"
        ]
        == NOT_CONFIGURED
    )

    assert dashboard[
        "role_counts"
    ] == {
        "owner": 1,
    }

    assert (
        dashboard[
            "app_attention"
        ][
            "observatory"
        ][
            "owner_access_policy"
        ]
        == "GRANTED"
    )

    assert (
        dashboard[
            "app_attention"
        ][
            "observatory"
        ][
            "runtime_availability_state"
        ]
        == UNKNOWN
    )


def test_twr135_owner_hq_cards_are_truthful(
    monkeypatch,
):
    configure_hosted_owner(
        monkeypatch
    )

    cards = (
        owner_dashboard_status_cards()
    )

    by_id = {
        card["card_id"]:
            card
        for card in cards
    }

    assert (
        by_id[
            "owner-card-people"
        ][
            "value"
        ]
        == "1 VERIFIED"
    )

    assert (
        by_id[
            "owner-card-observatory-policy"
        ][
            "value"
        ]
        == "GRANTED"
    )

    assert (
        by_id[
            "owner-card-invitations"
        ][
            "value"
        ]
        == NOT_CONFIGURED
    )

    assert (
        by_id[
            "owner-card-access"
        ][
            "value"
        ]
        == NOT_CONFIGURED
    )

    assert (
        by_id[
            "owner-card-danger-locks"
        ][
            "value"
        ]
        == "LOCKED"
    )


def test_twr135_owner_hq_people_panel_shows_real_identity_not_secrets(
    monkeypatch,
):
    credential_hash = (
        configure_hosted_owner(
            monkeypatch
        )
    )

    dashboard = (
        build_tower_owner_dashboard()
    )

    html = (
        _owner_people_html(
            dashboard
        )
    )

    assert "Configured Tower Owner" in html
    assert "tower-owner-test" in html
    assert "OWNER" in html
    assert "AUTHENTICATION_CONFIGURED" in html
    assert "OBSERVATORY · GRANTED" in html

    assert credential_hash not in html
    assert "twr131-test-credential" not in html

    assert "Future Manager Seat" not in html
    assert "Future Family / Friend Seat" not in html


def test_twr135_identity_contract_matches_existing_login_env_names():
    from tower.tower_human_login_ob_launch import (
        TOWER_LOCAL_WALKTHROUGH_MODE_ENV as LOGIN_LOCAL_MODE_ENV,
        TOWER_OWNER_ID_ENV as LOGIN_OWNER_ID_ENV,
        TOWER_OWNER_PASSWORD_HASH_ENV as LOGIN_PASSWORD_HASH_ENV,
        TOWER_OWNER_USERNAME_ENV as LOGIN_USERNAME_ENV,
    )

    assert (
        TOWER_OWNER_USERNAME_ENV
        == LOGIN_USERNAME_ENV
    )

    assert (
        TOWER_OWNER_PASSWORD_HASH_ENV
        == LOGIN_PASSWORD_HASH_ENV
    )

    assert (
        TOWER_OWNER_ID_ENV
        == LOGIN_OWNER_ID_ENV
    )

    assert (
        TOWER_LOCAL_WALKTHROUGH_MODE_ENV
        == LOGIN_LOCAL_MODE_ENV
    )


def test_twr135_deferred_launcher_and_release_sources_are_not_pack_targets():
    pack_targets = {
        "tower/identity_authority.py",
        "tower/owner_people_registry.py",
        "tower/owner_dashboard_service.py",
        "tower/owner_dashboard_web.py",
        "tests/test_tower_real_identity_people_source_twr131_135.py",
        (
            "ob_evidence/owner_experience_simplification/"
            "tower_real_identity_people_source_twr131_135.json"
        ),
        (
            "ob_evidence/owner_experience_simplification/"
            "tower_real_identity_people_source_twr131_135_handoff.md"
        ),
    }

    assert (
        "tower/tower_human_login_ob_launch.py"
        not in pack_targets
    )

    assert (
        "tower/hosted_owner_release_walkthrough_web.py"
        not in pack_targets
    )


def test_twr135_product_truth_audit_first_wave_remains_zero():
    from tower.truth_surface_audit import (
        RETIREMENT_FOCUS_SURFACES,
        audit_product_surfaces,
    )

    report = audit_product_surfaces(
        REPO,
        relative_paths=RETIREMENT_FOCUS_SURFACES,
    )

    assert report["finding_count"] == 0
