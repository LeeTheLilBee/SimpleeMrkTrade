from __future__ import annotations

import os

import web.managed_staging as managed


def test_runtime_manifest_route_registered():

    rules = {
        rule.rule
        for rule
        in managed.app.url_map.iter_rules()
    }

    assert (
        "/tower/runtime-manifest.json"
        in rules
    )


def test_runtime_manifest_is_unique():

    rules = [
        rule.rule
        for rule
        in managed.app.url_map.iter_rules()
    ]

    assert (
        rules.count(
            "/tower/runtime-manifest.json"
        )
        == 1
    )


def test_manifest_identifies_real_entrypoint():

    payload = (
        managed.managed_staging_runtime_manifest()
    )

    assert (
        payload[
            "entrypoint"
        ]
        == "web.managed_staging:app"
    )


def test_manifest_tracks_archive_vault_routes():

    payload = (
        managed.managed_staging_runtime_manifest()
    )

    critical = (
        payload[
            "critical_routes"
        ]
    )

    assert (
        critical[
            "archive_vault_acceptance_records"
        ]
        is True
    )

    assert (
        critical[
            "archive_vault_intake"
        ]
        is True
    )

    assert (
        critical[
            "person_archive_vault_queue"
        ]
        is True
    )


def test_manifest_tracks_core_tower_and_ob_routes():

    critical = (
        managed
        .managed_staging_runtime_manifest()[
            "critical_routes"
        ]
    )

    assert (
        critical[
            "tower_login"
        ]
        is True
    )

    assert (
        critical[
            "tower_owner_dashboard"
        ]
        is True
    )

    assert (
        critical[
            "ob_dashboard"
        ]
        is True
    )

    assert (
        critical[
            "ob_market_map"
        ]
        is True
    )


def test_manifest_has_no_secret_environment_dump():

    payload = (
        managed.managed_staging_runtime_manifest()
    )

    forbidden = {
        "environment",
        "env",
        "github_token",
        "render_deploy_hook_url",
        "secret",
        "password",
    }

    assert not (
        forbidden
        & set(
            str(
                key
            ).lower()
            for key in payload.keys()
        )
    )


def test_revision_prefers_render_environment(
    monkeypatch,
):

    monkeypatch.setenv(
        "RENDER_GIT_COMMIT",
        "render-test-sha-123",
    )

    revision, source = (
        managed
        ._simplee_runtime_revision()
    )

    assert (
        revision
        == "render-test-sha-123"
    )

    assert (
        source
        == "environment:RENDER_GIT_COMMIT"
    )


def test_runtime_manifest_endpoint():

    client = (
        managed.app.test_client()
    )

    response = client.get(
        "/tower/runtime-manifest.json"
    )

    assert (
        response.status_code
        == 200
    )

    data = (
        response.get_json()
    )

    assert (
        data[
            "status"
        ]
        == "tower_managed_staging_runtime_manifest_ready"
    )

    assert (
        "revision"
        in data
    )

    assert (
        data[
            "critical_routes"
        ][
            "archive_vault_acceptance_records"
        ]
        is True
    )


def test_runtime_identity_headers_present():

    client = (
        managed.app.test_client()
    )

    response = client.get(
        "/tower/healthz"
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        response.headers.get(
            "X-Simplee-Entrypoint"
        )
        == "web.managed_staging:app"
    )

    assert (
        response.headers.get(
            "X-Simplee-Revision"
        )
    )

    assert (
        response.headers.get(
            "X-Simplee-Revision-Source"
        )
    )


def test_safety_flags_remain_closed():

    payload = (
        managed.managed_staging_runtime_manifest()
    )

    assert (
        payload[
            "production_deployment"
        ]
        is False
    )

    assert (
        payload[
            "broker_submission"
        ]
        is False
    )

    assert (
        payload[
            "capital_movement"
        ]
        is False
    )

    assert (
        payload[
            "manual_live_authorized"
        ]
        is False
    )

    assert (
        payload[
            "live_auto_authorized"
        ]
        is False
    )



def test_runtime_identity_headers_on_manifest_and_login():

    client = (
        managed.app.test_client()
    )

    paths = [
        "/tower/healthz",
        "/tower/runtime-manifest.json",
        "/tower/login",
    ]

    for path in paths:

        response = client.get(
            path,
            follow_redirects=False,
        )

        assert (
            response.headers.get(
                "X-Simplee-Entrypoint"
            )
            == "web.managed_staging:app"
        ), path

        assert (
            response.headers.get(
                "X-Simplee-Revision"
            )
        ), path

        assert (
            response.headers.get(
                "X-Simplee-Revision-Source"
            )
        ), path


def test_runtime_identity_middleware_is_outside_health_middleware():

    wrapped = (
        managed.app.wsgi_app
    )

    assert (
        wrapped.__class__.__name__
        == "_SimpleeRuntimeIdentityHeadersMiddleware"
    )

    inner = (
        wrapped.wrapped
    )

    assert (
        inner.__class__.__name__
        == "_SimpleeManagedStagingHealthMiddleware"
    )
