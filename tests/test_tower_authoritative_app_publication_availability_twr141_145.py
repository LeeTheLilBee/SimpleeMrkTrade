from __future__ import annotations

import copy
import json
from datetime import datetime, timedelta, timezone

import pytest

from tower.access_home_owner_launches import (
    access_home_owner_launch_summary,
)
from tower.app_publication_authority import (
    APP_PUBLICATION_SCHEMA_VERSION,
    AppPublicationAuthorityError,
    ENVIRONMENT_AVAILABLE,
    HEALTH_VERIFIED,
    IMPLEMENTED,
    PUBLISHED as PUBLICATION_DIMENSION,
    app_dimension_truth,
    app_publication_authority_snapshot,
    publication_document,
    publication_integrity_sha256,
    validate_publication_document,
)
from tower.app_truth_projection import (
    app_truth_by_id,
    future_registered_apps,
    registered_app_truth_projection,
    verified_launchable_app_ids,
)
from tower.truth_contract import (
    AVAILABLE,
    AUTHORIZED,
    ENTITLED,
    ENABLED,
    LOCKED,
    NOT_CONFIGURED,
    PUBLISHED,
    REGISTERED,
    STALE,
    UNAVAILABLE,
    UNKNOWN,
    VERIFIED,
)


PROVIDER_ENV = (
    "TOWER_APP_PUBLICATION_STATE_PATH"
)


def _clear_owner_identity(monkeypatch):

    for name in (
        "TOWER_OWNER_USERNAME",
        "TOWER_OWNER_PASSWORD_HASH",
        "TOWER_OWNER_ID",
        "TOWER_OWNER_DISPLAY_NAME",
        "TOWER_LOCAL_WALKTHROUGH_MODE",
        "TOWER_ORGANIZATION_ID",
        "TOWER_ORGANIZATION_NAME",
    ):
        monkeypatch.delenv(
            name,
            raising=False,
        )


def _configure_owner(monkeypatch):

    monkeypatch.setenv(
        "TOWER_OWNER_USERNAME",
        "owner@example.invalid",
    )

    monkeypatch.setenv(
        "TOWER_OWNER_PASSWORD_HASH",
        "sha256:configured-but-never-projected",
    )

    monkeypatch.setenv(
        "TOWER_OWNER_ID",
        "tower_owner_test",
    )

    monkeypatch.delenv(
        "TOWER_LOCAL_WALKTHROUGH_MODE",
        raising=False,
    )


def _fresh_times():

    now = datetime.now(
        timezone.utc
    )

    return (
        (
            now
            - timedelta(
                minutes=1
            )
        ).isoformat(),

        (
            now
            + timedelta(
                minutes=15
            )
        ).isoformat(),
    )


def _stale_times():

    now = datetime.now(
        timezone.utc
    )

    return (
        (
            now
            - timedelta(
                minutes=30
            )
        ).isoformat(),

        (
            now
            - timedelta(
                minutes=5
            )
        ).isoformat(),
    )


def _app_record(
    app_id,
    *,
    implemented=True,
    published=True,
    available=True,
    healthy=True,
    stale_availability=False,
    stale_health=False,
):

    fresh_observed, fresh_until = (
        _fresh_times()
    )

    stale_observed, stale_until = (
        _stale_times()
    )

    return {
        "app_id":
            app_id,

        "implemented": {
            "value":
                implemented,

            "evidence_id":
                f"{app_id}-implementation-evidence",
        },

        "published": {
            "value":
                published,

            "evidence_id":
                f"{app_id}-publication-evidence",
        },

        "environment_available": {
            "value":
                available,

            "receipt_id":
                f"{app_id}-availability-receipt",

            "observed_at_utc":
                (
                    stale_observed
                    if stale_availability
                    else fresh_observed
                ),

            "fresh_until_utc":
                (
                    stale_until
                    if stale_availability
                    else fresh_until
                ),
        },

        "health_verified": {
            "value":
                healthy,

            "receipt_id":
                f"{app_id}-health-receipt",

            "observed_at_utc":
                (
                    stale_observed
                    if stale_health
                    else fresh_observed
                ),

            "fresh_until_utc":
                (
                    stale_until
                    if stale_health
                    else fresh_until
                ),
        },
    }


def _write_provider(
    tmp_path,
    monkeypatch,
    apps,
):

    document = publication_document(
        apps
    )

    path = (
        tmp_path
        / "app-publication-authority.json"
    )

    path.write_text(
        json.dumps(
            document,
            sort_keys=True,
            indent=2,
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv(
        PROVIDER_ENV,
        str(path),
    )

    return path


def test_twr141_provider_requires_explicit_configuration(monkeypatch):

    monkeypatch.delenv(
        PROVIDER_ENV,
        raising=False,
    )

    snapshot = (
        app_publication_authority_snapshot()
    )

    assert snapshot[
        "configured"
    ] is False

    assert snapshot[
        "verification_state"
    ] == NOT_CONFIGURED

    assert snapshot[
        "apps"
    ] is None

    assert snapshot[
        "provider_path_exposed"
    ] is False


def test_twr141_registry_alone_does_not_publish_future_apps(monkeypatch):

    monkeypatch.delenv(
        PROVIDER_ENV,
        raising=False,
    )

    future = (
        future_registered_apps()
    )

    assert len(
        future
    ) == 4

    for app in future:

        assert app[
            "states"
        ][PUBLISHED][
            "value"
        ] is None

        assert app[
            "states"
        ][PUBLISHED][
            "verification_state"
        ] == NOT_CONFIGURED

        assert app[
            "states"
        ][AVAILABLE][
            "verification_state"
        ] == NOT_CONFIGURED

        assert app[
            "launchable"
        ] is False


def test_twr141_registry_alone_does_not_publish_observatory(monkeypatch):

    monkeypatch.delenv(
        PROVIDER_ENV,
        raising=False,
    )

    ob = app_truth_by_id(
        "observatory"
    )

    assert ob[
        "states"
    ][REGISTERED][
        "value"
    ] is True

    assert ob[
        "states"
    ][PUBLISHED][
        "value"
    ] is None

    assert ob[
        "states"
    ][PUBLISHED][
        "verification_state"
    ] == NOT_CONFIGURED

    assert ob[
        "states"
    ][AVAILABLE][
        "verification_state"
    ] == NOT_CONFIGURED

    assert ob[
        "launchable"
    ] is False


def test_twr141_integrity_is_deterministic():

    apps = {
        "observatory":
            _app_record(
                "observatory"
            )
    }

    first = publication_document(
        apps
    )

    second = publication_document(
        copy.deepcopy(
            apps
        )
    )

    assert first[
        "integrity_sha256"
    ] == second[
        "integrity_sha256"
    ]

    assert (
        first[
            "integrity_sha256"
        ]
        == publication_integrity_sha256(
            first
        )
    )


def test_twr141_valid_provider_is_verified(
    tmp_path,
    monkeypatch,
):

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory"
                )
        },
    )

    snapshot = (
        app_publication_authority_snapshot()
    )

    assert snapshot[
        "verification_state"
    ] == VERIFIED

    assert snapshot[
        "configured"
    ] is True

    assert snapshot[
        "apps"
    ][
        "observatory"
    ][
        "app_id"
    ] == "observatory"

    assert snapshot[
        "provider_path_exposed"
    ] is False


def test_twr141_tampered_provider_fails_closed(
    tmp_path,
    monkeypatch,
):

    path = _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory"
                )
        },
    )

    document = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    document[
        "apps"
    ][
        "observatory"
    ][
        "published"
    ][
        "value"
    ] = False

    path.write_text(
        json.dumps(
            document
        ),
        encoding="utf-8",
    )

    snapshot = (
        app_publication_authority_snapshot()
    )

    assert snapshot[
        "verification_state"
    ] != VERIFIED

    assert snapshot[
        "apps"
    ] is None

    published = app_dimension_truth(
        "observatory",
        PUBLICATION_DIMENSION,
    )

    assert published[
        "verification_state"
    ] if isinstance(published, dict) else (
        published.verification_state
    ) == UNAVAILABLE


def test_twr141_unknown_app_provider_records_rejected():

    document = publication_document({
        "not-a-real-app":
            _app_record(
                "not-a-real-app"
            )
    })

    with pytest.raises(
        AppPublicationAuthorityError
    ):
        validate_publication_document(
            document
        )


def test_twr141_non_boolean_dimension_rejected():

    record = _app_record(
        "observatory"
    )

    record[
        "published"
    ][
        "value"
    ] = "yes"

    document = publication_document({
        "observatory":
            record
    })

    with pytest.raises(
        AppPublicationAuthorityError
    ):
        validate_publication_document(
            document
        )


def test_twr141_temporal_receipt_requires_timezone():

    record = _app_record(
        "observatory"
    )

    record[
        "environment_available"
    ][
        "observed_at_utc"
    ] = "2026-09-01T10:00:00"

    document = publication_document({
        "observatory":
            record
    })

    with pytest.raises(
        AppPublicationAuthorityError
    ):
        validate_publication_document(
            document
        )


def test_twr141_fresh_until_cannot_precede_observation():

    record = _app_record(
        "observatory"
    )

    record[
        "health_verified"
    ][
        "observed_at_utc"
    ] = "2026-09-01T10:00:00+00:00"

    record[
        "health_verified"
    ][
        "fresh_until_utc"
    ] = "2026-09-01T09:59:00+00:00"

    document = publication_document({
        "observatory":
            record
    })

    with pytest.raises(
        AppPublicationAuthorityError
    ):
        validate_publication_document(
            document
        )


def test_twr142_registered_implemented_and_published_are_independent(
    tmp_path,
    monkeypatch,
):

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory",
                    implemented=False,
                    published=True,
                )
        },
    )

    ob = app_truth_by_id(
        "observatory"
    )

    assert ob[
        "dimensions"
    ][
        "registered"
    ][
        "value"
    ] is True

    assert ob[
        "dimensions"
    ][
        "implemented"
    ][
        "value"
    ] is False

    assert ob[
        "dimensions"
    ][
        "published"
    ][
        "value"
    ] is True

    assert ob[
        "launchable"
    ] is False


def test_twr142_published_true_does_not_imply_environment_available(
    tmp_path,
    monkeypatch,
):

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory",
                    published=True,
                    available=False,
                )
        },
    )

    ob = app_truth_by_id(
        "observatory"
    )

    assert ob[
        "dimensions"
    ][
        "published"
    ][
        "value"
    ] is True

    assert ob[
        "dimensions"
    ][
        "environment_available"
    ][
        "value"
    ] is False

    assert ob[
        "launchable"
    ] is False


def test_twr142_available_true_does_not_imply_health(
    tmp_path,
    monkeypatch,
):

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory",
                    available=True,
                    healthy=False,
                )
        },
    )

    ob = app_truth_by_id(
        "observatory"
    )

    assert ob[
        "dimensions"
    ][
        "environment_available"
    ][
        "value"
    ] is True

    assert ob[
        "dimensions"
    ][
        "health_verified"
    ][
        "value"
    ] is False

    assert ob[
        "launchable"
    ] is False


def test_twr142_stale_availability_cannot_satisfy_launchability(
    tmp_path,
    monkeypatch,
):

    _configure_owner(
        monkeypatch
    )

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory",
                    stale_availability=True,
                )
        },
    )

    ob = app_truth_by_id(
        "observatory"
    )

    assert ob[
        "display_dimensions"
    ][
        "environment_available"
    ][
        "display_state"
    ] == STALE

    assert ob[
        "launchable"
    ] is False


def test_twr142_stale_health_cannot_satisfy_launchability(
    tmp_path,
    monkeypatch,
):

    _configure_owner(
        monkeypatch
    )

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory",
                    stale_health=True,
                )
        },
    )

    ob = app_truth_by_id(
        "observatory"
    )

    assert ob[
        "display_dimensions"
    ][
        "health_verified"
    ][
        "display_state"
    ] == STALE

    assert ob[
        "launchable"
    ] is False


def test_twr143_missing_owner_identity_is_not_false_entitlement(
    tmp_path,
    monkeypatch,
):

    _clear_owner_identity(
        monkeypatch
    )

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory"
                )
        },
    )

    ob = app_truth_by_id(
        "observatory"
    )

    assert ob[
        "states"
    ][ENTITLED][
        "value"
    ] is None

    assert ob[
        "states"
    ][ENTITLED][
        "verification_state"
    ] == NOT_CONFIGURED

    assert ob[
        "launchable"
    ] is False


def test_twr143_verified_owner_ob_policy_grants_ob_entitlement(
    tmp_path,
    monkeypatch,
):

    _configure_owner(
        monkeypatch
    )

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory"
                )
        },
    )

    ob = app_truth_by_id(
        "observatory"
    )

    assert ob[
        "states"
    ][ENTITLED][
        "value"
    ] is True

    assert ob[
        "states"
    ][ENTITLED][
        "verification_state"
    ] == VERIFIED


def test_twr143_future_runtime_state_does_not_manufacture_owner_entitlement(
    tmp_path,
    monkeypatch,
):

    _configure_owner(
        monkeypatch
    )

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "teller":
                _app_record(
                    "teller"
                )
        },
    )

    teller = app_truth_by_id(
        "teller"
    )

    assert teller[
        "dimensions"
    ][
        "implemented"
    ][
        "value"
    ] is True

    assert teller[
        "dimensions"
    ][
        "published"
    ][
        "value"
    ] is True

    assert teller[
        "states"
    ][ENTITLED][
        "value"
    ] is False

    assert teller[
        "launchable"
    ] is False


def test_twr144_fully_verified_ob_is_product_launchable(
    tmp_path,
    monkeypatch,
):

    _configure_owner(
        monkeypatch
    )

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory"
                )
        },
    )

    ob = app_truth_by_id(
        "observatory"
    )

    assert ob[
        "dimensions"
    ][
        "registered"
    ][
        "value"
    ] is True

    assert ob[
        "dimensions"
    ][
        "implemented"
    ][
        "value"
    ] is True

    assert ob[
        "dimensions"
    ][
        "published"
    ][
        "value"
    ] is True

    assert ob[
        "dimensions"
    ][
        "environment_available"
    ][
        "value"
    ] is True

    assert ob[
        "dimensions"
    ][
        "health_verified"
    ][
        "value"
    ] is True

    assert ob[
        "dimensions"
    ][
        "user_entitled"
    ][
        "value"
    ] is True

    assert ob[
        "dimensions"
    ][
        "launch_route_configured"
    ][
        "value"
    ] is True

    assert ob[
        "launchable"
    ] is True


def test_twr144_launchable_does_not_equal_request_authorized(
    tmp_path,
    monkeypatch,
):

    _configure_owner(
        monkeypatch
    )

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory"
                )
        },
    )

    ob = app_truth_by_id(
        "observatory"
    )

    assert ob[
        "launchable"
    ] is True

    assert ob[
        "states"
    ][AUTHORIZED][
        "value"
    ] is None

    assert ob[
        "states"
    ][AUTHORIZED][
        "verification_state"
    ] == UNKNOWN

    assert ob[
        "request_authorization_required"
    ] is True

    assert ob[
        "owner_session_gate_bypassed"
    ] is False

    assert ob[
        "step_up_gate_bypassed"
    ] is False


def test_twr144_teller_placeholder_route_prevents_launchability(
    tmp_path,
    monkeypatch,
):

    _configure_owner(
        monkeypatch
    )

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "teller":
                _app_record(
                    "teller"
                )
        },
    )

    teller = app_truth_by_id(
        "teller"
    )

    assert teller[
        "dimensions"
    ][
        "launch_route_configured"
    ][
        "value"
    ] is False

    assert teller[
        "launchable"
    ] is False


def test_twr144_verified_launchable_helper_returns_only_ob(
    tmp_path,
    monkeypatch,
):

    _configure_owner(
        monkeypatch
    )

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory"
                ),

            "teller":
                _app_record(
                    "teller"
                ),
        },
    )

    assert (
        verified_launchable_app_ids()
        == ["observatory"]
    )


def test_twr144_registry_safety_locks_remain_authoritative(
    tmp_path,
    monkeypatch,
):

    _configure_owner(
        monkeypatch
    )

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory"
                )
        },
    )

    ob = app_truth_by_id(
        "observatory"
    )

    assert ob[
        "states"
    ][LOCKED][
        "value"
    ] is True

    assert ob[
        "safety"
    ][
        "live_auto_locked"
    ][
        "value"
    ] is True

    assert ob[
        "safety"
    ][
        "broker_execution_enabled"
    ][
        "value"
    ] is False

    assert ob[
        "safety"
    ][
        "capital_action_enabled"
    ][
        "value"
    ] is False


def test_twr144_enabled_state_is_still_separate(
    tmp_path,
    monkeypatch,
):

    _configure_owner(
        monkeypatch
    )

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory"
                )
        },
    )

    ob = app_truth_by_id(
        "observatory"
    )

    assert ob[
        "states"
    ][ENABLED][
        "value"
    ] is None

    assert ob[
        "states"
    ][ENABLED][
        "verification_state"
    ] == UNKNOWN


def test_twr145_access_home_reports_zero_verified_launchable_without_provider(
    monkeypatch,
):

    monkeypatch.delenv(
        PROVIDER_ENV,
        raising=False,
    )

    summary = (
        access_home_owner_launch_summary()
    )

    assert summary[
        "registered_app_count"
    ] == 5

    assert summary[
        "verified_launchable_app_count"
    ] == 0

    assert summary[
        "launchable_app_ids"
    ] == []

    assert summary[
        "registered_apps_are_not_availability"
    ] is True


def test_twr145_access_home_reports_verified_ob_launchability(
    tmp_path,
    monkeypatch,
):

    _configure_owner(
        monkeypatch
    )

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory"
                )
        },
    )

    summary = (
        access_home_owner_launch_summary()
    )

    assert summary[
        "registered_app_count"
    ] == 5

    assert summary[
        "verified_launchable_app_count"
    ] == 1

    assert summary[
        "launchable_app_ids"
    ] == ["observatory"]


def test_twr145_access_home_does_not_enable_execution(
    tmp_path,
    monkeypatch,
):

    _configure_owner(
        monkeypatch
    )

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory"
                )
        },
    )

    summary = (
        access_home_owner_launch_summary()
    )

    assert summary[
        "danger_actions_enabled"
    ] is False

    assert summary[
        "live_auto"
    ] == "LOCKED"

    assert summary[
        "broker_execution"
    ] is False

    assert summary[
        "capital_action"
    ] is False


def test_twr145_publication_authority_path_is_never_projected(
    tmp_path,
    monkeypatch,
):

    path = _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory"
                )
        },
    )

    snapshot = (
        app_publication_authority_snapshot()
    )

    serialized = json.dumps(
        snapshot,
        sort_keys=True,
    )

    assert str(
        path
    ) not in serialized

    assert snapshot[
        "provider_path_exposed"
    ] is False


def test_twr145_canonical_dimension_names_are_present(
    tmp_path,
    monkeypatch,
):

    _configure_owner(
        monkeypatch
    )

    _write_provider(
        tmp_path,
        monkeypatch,
        {
            "observatory":
                _app_record(
                    "observatory"
                )
        },
    )

    ob = app_truth_by_id(
        "observatory"
    )

    assert {
        "registered",
        "implemented",
        "published",
        "environment_available",
        "health_verified",
        "user_entitled",
        "launch_route_configured",
    } == set(
        ob[
            "dimensions"
        ]
    )
