from __future__ import annotations

from pathlib import Path

import pytest

from tower.tower_ob_managed_staging_runtime import (
    MANAGED_START_COMMAND,
    MANAGED_WSGI_TARGET,
    build_no_call_dry_run_plan,
    build_provider_authorization_packet,
    configure_app_for_managed_staging,
    dependency_graph,
    environment_reference_contract,
    evaluate_managed_staging_environment,
    provider_capability_resolution,
    resolve_repository_runtime,
)


ROOT = Path(__file__).resolve().parents[1]


def safe_environment() -> dict[str, str]:
    return {
        "SIMPLEE_DEPLOYMENT_ENVIRONMENT": "staging",
        "TOWER_HOSTED_MODE": "true",
        "SIMPLEE_MANAGED_HOST_PROVIDER": "provider-example",
        "SIMPLEE_MANAGED_HOST_ACCOUNT_OR_TEAM": "team-example",
        "SIMPLEE_STAGING_DEPLOYMENT_REGION": "region-example",
        "SIMPLEE_PROVIDER_OWNER_APPROVAL": "APPROVED",
        "TOWER_SESSION_SECRET": "s" * 64,
        "TOWER_OWNER_USERNAME": "owner",
        "TOWER_OWNER_PASSWORD_HASH": (
            "scrypt:32768:8:1$example$hashed-value"
        ),
        "TOWER_OWNER_ID": "simplee_owner",
        "TOWER_LOCAL_WALKTHROUGH_MODE": "false",
    }


def test_repository_runtime_resolves():
    contract = resolve_repository_runtime(ROOT)

    assert contract["resolved"] is True
    assert contract["managed_wsgi_target"] == (
        "web.managed_staging:app"
    )
    assert contract[
        "separate_observatory_service_required"
    ] is False


def test_runtime_topology_is_one_tower_fronted_service():
    resolution = provider_capability_resolution()

    assert resolution["topology"] == (
        "single_tower_fronted_managed_python_web_service"
    )
    assert resolution["network_boundary"][
        "tower_is_only_browser_front_door"
    ] is True
    assert resolution["network_boundary"][
        "observatory_separate_public_service"
    ] is False


def test_dependency_graph_binds_native_gp046():
    graph = dependency_graph()

    assert graph["runtime_target"] == (
        MANAGED_WSGI_TARGET
    )
    assert {
        (edge["from"], edge["to"])
        for edge in graph["edges"]
    } >= {
        ("managed_wsgi", "source_app"),
        ("source_app", "human_login"),
        ("human_login", "native_gp046"),
    }


def test_environment_contract_contains_names_not_values():
    contract = environment_reference_contract()
    rendered = str(contract)

    assert "TOWER_SESSION_SECRET" in rendered
    assert "TOWER_OWNER_PASSWORD_HASH" in rendered
    assert "raw_secrets_in_git" in rendered
    assert "s" * 32 not in rendered
    assert contract["rules"]["values_in_contract"] is False


def test_missing_environment_fails_closed():
    report = evaluate_managed_staging_environment({})

    assert report["runtime_ready"] is False
    assert report["authorization_review_ready"] is False
    assert report["provider_calls_authorized"] is False
    assert report["deployment_authorized"] is False


def test_safe_environment_is_ready_for_review():
    report = evaluate_managed_staging_environment(
        safe_environment()
    )

    assert report["runtime_ready"] is True
    assert report["provider_inputs_complete"] is True
    assert report["authorization_review_ready"] is True
    assert report["raw_values_returned"] is False


def test_local_walkthrough_mode_is_rejected():
    environment = safe_environment()
    environment[
        "TOWER_LOCAL_WALKTHROUGH_MODE"
    ] = "true"

    report = evaluate_managed_staging_environment(
        environment
    )

    assert report["runtime_ready"] is False
    assert report["runtime_checks"][
        "local_walkthrough_mode_disabled"
    ] is False


def test_plaintext_local_password_is_rejected():
    environment = safe_environment()
    environment[
        "TOWER_LOCAL_OWNER_PASSWORD"
    ] = "not-allowed"

    report = evaluate_managed_staging_environment(
        environment
    )

    assert report["runtime_ready"] is False
    assert report["runtime_checks"][
        "local_plaintext_password_absent"
    ] is False


def test_weak_session_secret_is_rejected():
    environment = safe_environment()
    environment["TOWER_SESSION_SECRET"] = "short"

    report = evaluate_managed_staging_environment(
        environment
    )

    assert report["runtime_ready"] is False
    assert report["runtime_checks"][
        "session_secret_minimum_length"
    ] is False


def test_app_configuration_uses_environment_secret():
    class FakeApp:
        def __init__(self):
            self.secret_key = "development"
            self.config = {}

    app = FakeApp()
    configured = configure_app_for_managed_staging(
        app,
        safe_environment(),
    )

    assert configured is app
    assert configured.secret_key == "s" * 64
    assert configured.config[
        "SESSION_COOKIE_SECURE"
    ] is True
    assert configured.config["DEBUG"] is False


def test_unresolved_provider_packet_remains_held():
    packet = build_provider_authorization_packet(
        ROOT,
        {},
    )

    assert packet["runtime_resolved"] is True
    assert packet[
        "ready_for_separate_authorization_review"
    ] is False
    assert packet["blocking_requirement_count"] == 4
    assert packet["provider_calls_authorized"] is False
    assert packet["deployment_authorized"] is False


def test_complete_packet_only_opens_separate_review():
    packet = build_provider_authorization_packet(
        ROOT,
        safe_environment(),
    )

    assert packet[
        "ready_for_separate_authorization_review"
    ] is True
    assert packet["blocking_requirement_count"] == 0
    assert packet["final_decision"] == (
        "READY_FOR_SEPARATE_PROVIDER_PROVISIONING_AUTHORIZATION_REVIEW"
    )
    assert packet["provider_calls_authorized"] is False
    assert packet["resource_creation_authorized"] is False


def test_no_call_plan_is_inert():
    plan = build_no_call_dry_run_plan(
        ROOT,
        {},
    )

    assert plan["command_template"] == (
        MANAGED_START_COMMAND
    )
    assert plan["dry_run"] is True
    assert plan["shell_invoked"] is False
    assert plan["command_executed"] is False
    assert plan["provider_api_invoked"] is False
    assert plan["deployment_performed"] is False


def test_wsgi_wrapper_does_not_directly_import_source_app():
    wrapper = (
        ROOT
        / "web"
        / "managed_staging.py"
    ).read_text(encoding="utf-8")

    assert "create_managed_staging_app" in wrapper
    assert "from web.app import app" not in wrapper
