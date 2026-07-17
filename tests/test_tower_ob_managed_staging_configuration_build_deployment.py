
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tower.tower_ob_managed_staging_configuration_build_deployment import (
    BUILD_COMMAND,
    DEPLOY_APPROVAL_PHRASE,
    FINAL_DECISION_DEPLOYED,
    FINAL_DECISION_HOLD,
    HEALTH_PATH,
    NEXT_BOUNDARY,
    PROVIDER_SLUG,
    RUNTIME_TARGET,
    SCHEMA_VERSION,
    SERVICE_NAME,
    SOURCE_BRANCH,
    START_COMMAND,
    RenderAPIClient,
    RenderAPIError,
    build_configuration_deployment_state,
    build_render_service_patch,
    build_render_service_payload,
    build_step_evidence,
    choose_workspace,
    deployment_contract,
    discover_requirement_lines,
    expected_static_file_payloads,
    health_check,
    poll_deploy,
    provider_binding_record,
    render_api_contract,
    render_blueprint_text,
    requirements_text,
    runtime_env_vars,
    sanitize_provider_payload,
    validate_existing_service,
    validate_operator_inputs,
)


def valid_inputs() -> dict[str, str]:
    return {
        "RENDER_API_KEY": "rnd_" + "x" * 30,
        "SIMPLEE_STAGING_DEPLOY_APPROVAL": DEPLOY_APPROVAL_PHRASE,
        "TOWER_OWNER_USERNAME": "owner",
        "TOWER_OWNER_PASSWORD_HASH": "scrypt:32768:8:1$abc$" + "f" * 64,
        "TOWER_OWNER_ID": "tower-owner-1",
        "SIMPLEE_STAGING_REGION": "virginia",
        "SIMPLEE_STAGING_PLAN": "free",
    }


def prior_checkpoint(root: Path) -> None:
    path = root / (
        "integration_checkpoints/20260717T002435Z_"
        "tower_ob_managed_staging_service_creation/resume_checkpoint.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"closed_through_step": 150, "service_shell_created": True}),
        encoding="utf-8",
    )


def write_configuration_files(root: Path, commit: str, requirements: str) -> str:
    deploy_root = root / "deploy/managed_staging"
    deploy_root.mkdir(parents=True, exist_ok=True)
    req_path = deploy_root / "requirements.txt"
    req_path.write_text(requirements, encoding="utf-8")
    req_hash = hashlib.sha256(req_path.read_bytes()).hexdigest()
    for relative, content in expected_static_file_payloads(commit, req_hash).items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return req_hash


class FakeHTTPResponse:
    status = 200

    def __init__(self, payload: dict):
        self._body = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_constants_lock_one_staging_service():
    assert SERVICE_NAME == "simplee-tower-ob-staging"
    assert PROVIDER_SLUG == "render"
    assert RUNTIME_TARGET == "web.managed_staging:app"


def test_blueprint_has_one_web_service():
    text = render_blueprint_text()
    assert text.count("- type: web") == 1
    assert f"name: {SERVICE_NAME}" in text


def test_blueprint_disables_autodeploy():
    assert "autoDeploy: false" in render_blueprint_text()


def test_blueprint_contains_build_start_and_health():
    text = render_blueprint_text()
    assert BUILD_COMMAND in text
    assert START_COMMAND in text
    assert HEALTH_PATH in text


def test_api_contract_uses_only_required_provider_endpoints():
    contract = render_api_contract()
    assert contract["provider"] == "render"
    assert contract["database_endpoint_used"] is False
    assert contract["object_storage_endpoint_used"] is False
    assert contract["dns_endpoint_used"] is False


def test_deployment_contract_is_staging_only():
    contract = deployment_contract("a" * 40, "b" * 64)
    assert contract["service_count"] == 1
    assert contract["production_deployment_allowed"] is False
    assert contract["live_auto_locked"] is True


def test_static_payloads_include_render_and_contracts():
    files = expected_static_file_payloads("a" * 40, "b" * 64)
    assert set(files) == {
        "render.yaml",
        "deploy/managed_staging/deployment_contract.json",
        "deploy/managed_staging/render_api_contract.json",
        "deploy/managed_staging/DEPLOYMENT.md",
    }


def test_blank_operator_inputs_fail_closed():
    report = validate_operator_inputs({})
    assert report["valid"] is False
    assert report["blocking_requirement_count"] >= 5


def test_complete_operator_inputs_validate():
    report = validate_operator_inputs(valid_inputs())
    assert report["valid"] is True
    assert report["blocking_requirement_count"] == 0


def test_exact_approval_phrase_is_required():
    values = valid_inputs()
    values["SIMPLEE_STAGING_DEPLOY_APPROVAL"] = "yes"
    assert validate_operator_inputs(values)["checks"]["deployment_approval_exact"] is False


def test_owner_password_must_appear_hashed():
    values = valid_inputs()
    values["TOWER_OWNER_PASSWORD_HASH"] = "plaintext-password"
    assert validate_operator_inputs(values)["checks"]["tower_owner_password_appears_hashed"] is False


def test_region_is_allowlisted():
    values = valid_inputs()
    values["SIMPLEE_STAGING_REGION"] = "moon"
    assert validate_operator_inputs(values)["checks"]["region_allowed"] is False


def test_plan_is_allowlisted():
    values = valid_inputs()
    values["SIMPLEE_STAGING_PLAN"] = "unlimited"
    assert validate_operator_inputs(values)["checks"]["plan_allowed"] is False


def test_validation_report_never_returns_secret_values():
    values = valid_inputs()
    report = validate_operator_inputs(values)
    rendered = json.dumps(report)
    assert values["RENDER_API_KEY"] not in rendered
    assert values["TOWER_OWNER_PASSWORD_HASH"] not in rendered


def test_runtime_environment_names_are_exact():
    entries = runtime_env_vars("tea-123", valid_inputs())
    keys = {entry["key"] for entry in entries}
    assert keys == {
        "SIMPLEE_DEPLOYMENT_ENVIRONMENT",
        "TOWER_HOSTED_MODE",
        "SIMPLEE_MANAGED_HOST_PROVIDER",
        "SIMPLEE_MANAGED_HOST_ACCOUNT_OR_TEAM",
        "SIMPLEE_STAGING_DEPLOYMENT_REGION",
        "SIMPLEE_PROVIDER_OWNER_APPROVAL",
        "TOWER_SESSION_SECRET",
        "TOWER_OWNER_USERNAME",
        "TOWER_OWNER_PASSWORD_HASH",
        "TOWER_OWNER_ID",
        "PYTHON_VERSION",
    }


def test_runtime_session_secret_is_provider_generated():
    entries = runtime_env_vars("tea-123", valid_inputs())
    session = next(item for item in entries if item["key"] == "TOWER_SESSION_SECRET")
    assert session == {"key": "TOWER_SESSION_SECRET", "generateValue": True}


def test_create_payload_is_one_web_service():
    payload = build_render_service_payload("tea-123", "a" * 40, valid_inputs())
    assert payload["type"] == "web_service"
    assert payload["ownerId"] == "tea-123"
    assert payload["serviceDetails"]["numInstances"] == 1


def test_create_payload_locks_database_storage_and_dns_by_absence():
    payload = build_render_service_payload("tea-123", "a" * 40, valid_inputs())
    rendered = json.dumps(payload).lower()
    assert "postgres" not in rendered
    assert "database" not in rendered
    assert "disk" not in rendered
    assert "dns" not in rendered


def test_create_service_strips_internal_commit_marker():
    calls = []

    def transport(method, path, payload):
        calls.append((method, path, payload))
        return 201, {"service": {"id": "srv-1"}}

    client = RenderAPIClient("rnd_test", transport=transport)
    payload = build_render_service_payload("tea-1", "a" * 40, valid_inputs())
    assert client.create_service(payload)["id"] == "srv-1"
    assert "_sourceCommitForExplicitDeploy" not in calls[0][2]


def test_update_patch_preserves_manual_release():
    patch = build_render_service_patch()
    assert patch["autoDeploy"] == "no"
    assert patch["serviceDetails"]["healthCheckPath"] == HEALTH_PATH


def test_sanitizer_redacts_common_secret_fields():
    value = sanitize_provider_payload({
        "token": "rnd_secret",
        "password": "hidden",
        "normal": "safe",
    })
    assert value == {"token": "<redacted>", "password": "<redacted>", "normal": "safe"}


def test_sanitizer_redacts_nested_env_values():
    value = sanitize_provider_payload({
        "envVars": [{"key": "TOWER_OWNER_PASSWORD_HASH", "value": "secret"}]
    })
    assert value["envVars"][0]["value"] == "<redacted>"


def test_render_api_error_sanitizes_payload():
    error = RenderAPIError(400, "bad", {"api_key": "rnd_secret"})
    assert error.payload["api_key"] == "<redacted>"


def test_render_client_requires_api_key():
    with pytest.raises(ValueError):
        RenderAPIClient("")


def test_render_client_lists_workspaces():
    client = RenderAPIClient(
        "rnd_test",
        transport=lambda method, path, payload: (
            200,
            [{"owner": {"id": "tea-1", "name": "Simplee"}}],
        ),
    )
    assert client.list_workspaces() == [{"id": "tea-1", "name": "Simplee"}]


def test_render_client_filters_named_services():
    calls = []

    def transport(method, path, payload):
        calls.append(path)
        return 200, [{"service": {"id": "srv-1"}}]

    client = RenderAPIClient("rnd_test", transport=transport)
    assert client.list_named_services("tea-1")[0]["id"] == "srv-1"
    assert "name=simplee-tower-ob-staging" in calls[0]
    assert "ownerId=tea-1" in calls[0]


def test_render_client_unwraps_create_response():
    client = RenderAPIClient(
        "rnd_test",
        transport=lambda method, path, payload: (
            201,
            {"service": {"id": "srv-1", "name": SERVICE_NAME}},
        ),
    )
    assert client.create_service({"name": SERVICE_NAME})["id"] == "srv-1"


def test_render_client_updates_service():
    calls = []

    def transport(method, path, payload):
        calls.append((method, path, payload))
        return 200, {"service": {"id": "srv-1"}}

    client = RenderAPIClient("rnd_test", transport=transport)
    client.update_service("srv-1", {"autoDeploy": "no"})
    assert calls == [("PATCH", "/services/srv-1", {"autoDeploy": "no"})]


def test_render_client_updates_plain_environment_variable():
    calls = []

    def transport(method, path, payload):
        calls.append((method, path, payload))
        return 200, {"key": "A"}

    client = RenderAPIClient("rnd_test", transport=transport)
    client.update_env_var("srv-1", {"key": "A", "value": "B"})
    assert calls == [("PUT", "/services/srv-1/env-vars/A", {"value": "B"})]


def test_render_client_requests_generated_environment_variable():
    calls = []

    def transport(method, path, payload):
        calls.append((method, path, payload))
        return 200, {"key": "TOWER_SESSION_SECRET"}

    client = RenderAPIClient("rnd_test", transport=transport)
    client.update_env_var("srv-1", {"key": "TOWER_SESSION_SECRET", "generateValue": True})
    assert calls[0][2] == {"generateValue": True}


def test_trigger_deploy_is_commit_pinned_without_invalid_deploy_mode():
    calls = []

    def transport(method, path, payload):
        calls.append((method, path, payload))
        return 201, {"deploy": {"id": "dep-1", "status": "created"}}

    client = RenderAPIClient("rnd_test", transport=transport)
    client.trigger_deploy("srv-1", "a" * 40)
    assert calls[0][2]["commitId"] == "a" * 40
    assert "deployMode" not in calls[0][2]


def test_render_client_lists_deploys():
    client = RenderAPIClient(
        "rnd_test",
        transport=lambda method, path, payload: (
            200,
            [{"deploy": {"id": "dep-1", "status": "live"}}],
        ),
    )
    assert client.list_deploys("srv-1")[0]["status"] == "live"


def test_choose_workspace_by_explicit_id():
    chosen = choose_workspace(
        [{"id": "tea-1"}, {"id": "tea-2"}],
        "tea-2",
    )
    assert chosen["id"] == "tea-2"


def test_choose_only_accessible_workspace():
    assert choose_workspace([{"id": "tea-1"}])["id"] == "tea-1"


def test_workspace_ambiguity_fails_closed():
    with pytest.raises(RuntimeError):
        choose_workspace([{"id": "tea-1"}, {"id": "tea-2"}])


def test_existing_service_validation_accepts_expected_service():
    report = validate_existing_service(
        {
            "id": "srv-1",
            "name": SERVICE_NAME,
            "owner": {"id": "tea-1"},
            "type": "web_service",
            "repo": "https://github.com/LeeTheLilBee/SimpleeMrkTrade.git",
            "branch": SOURCE_BRANCH,
            "serviceDetails": {"runtime": "python", "url": "https://example.onrender.com"},
        },
        "tea-1",
    )
    assert report["valid"] is True


def test_existing_service_wrong_owner_fails_closed():
    report = validate_existing_service(
        {
            "id": "srv-1",
            "name": SERVICE_NAME,
            "owner": {"id": "tea-other"},
            "type": "web_service",
            "serviceDetails": {"runtime": "python"},
        },
        "tea-1",
    )
    assert report["valid"] is False


def test_poll_deploy_returns_live_record():
    statuses = iter(["queued", "build_in_progress", "live"])

    class Client:
        def list_deploys(self, service_id):
            return [{"id": "dep-1", "status": next(statuses)}]

    clock = [0.0]

    def monotonic():
        clock[0] += 1.0
        return clock[0]

    result = poll_deploy(
        Client(),
        "srv-1",
        "dep-1",
        timeout_seconds=20,
        interval_seconds=0,
        sleep=lambda _: None,
        monotonic=monotonic,
    )
    assert result["status"] == "live"


def test_poll_deploy_times_out_fail_closed():
    class Client:
        def list_deploys(self, service_id):
            return [{"id": "dep-1", "status": "queued"}]

    clock = [0.0]

    def monotonic():
        clock[0] += 5.0
        return clock[0]

    with pytest.raises(TimeoutError):
        poll_deploy(
            Client(),
            "srv-1",
            "dep-1",
            timeout_seconds=5,
            interval_seconds=0,
            sleep=lambda _: None,
            monotonic=monotonic,
        )


def test_health_check_requires_healthy_https_response():
    def opener(request, timeout):
        assert request.full_url == "https://staging.example.com/tower/healthz"
        return FakeHTTPResponse({"ok": True})

    receipt = health_check("https://staging.example.com", opener=opener)
    assert receipt["ok"] is True
    assert receipt["status_code"] == 200


def test_health_check_rejects_plain_http():
    with pytest.raises(ValueError):
        health_check("http://staging.example.com")


def test_provider_binding_record_is_non_secret():
    record = provider_binding_record(
        workspace={"id": "tea-1", "name": "Simplee"},
        service={
            "id": "srv-1",
            "name": SERVICE_NAME,
            "serviceDetails": {"url": "https://staging.example.com"},
        },
        deploy={"id": "dep-1", "status": "live"},
        source_commit="a" * 40,
        region="virginia",
        plan="free",
        health={"ok": True},
    )
    assert record["deploy_status"] == "live"
    assert record["database_created"] is False


def test_provider_binding_record_excludes_api_key_and_secrets():
    record = provider_binding_record(
        workspace={"id": "tea-1"},
        service={"id": "srv-1", "serviceDetails": {"url": "https://staging.example.com"}},
        deploy={"id": "dep-1", "status": "live"},
        source_commit="a" * 40,
        region="virginia",
        plan="free",
        health={"ok": True},
    )
    rendered = json.dumps(record).lower()
    assert "rnd_" not in rendered
    assert "scrypt:" not in rendered
    assert "cookie" not in rendered
    assert record["api_key_included"] is False


def test_state_holds_without_configuration_or_provider(tmp_path):
    prior_checkpoint(tmp_path)
    state = build_configuration_deployment_state(
        tmp_path,
        source_commit="a" * 40,
        requirements_sha256="b" * 64,
    )
    assert state["final_decision"] == FINAL_DECISION_HOLD
    assert state["deployment_performed"] is False


def test_state_closes_deployed_when_all_evidence_is_present(tmp_path):
    prior_checkpoint(tmp_path)
    requirements = "Flask==3.1.0\ngunicorn==23.0.0\nWerkzeug==3.1.0\n"
    req_hash = write_configuration_files(tmp_path, "a" * 40, requirements)
    provider = {
        "deploy_status": "live",
        "health_check": {"ok": True},
        "source_commit": "a" * 40,
    }
    state = build_configuration_deployment_state(
        tmp_path,
        source_commit="a" * 40,
        requirements_sha256=req_hash,
        provider_record=provider,
    )
    assert state["final_decision"] == FINAL_DECISION_DEPLOYED
    assert state["next_boundary"] == NEXT_BOUNDARY
    assert state["blocking_requirement_count"] == 0


def test_step_evidence_contains_ten_ordered_steps():
    state = {"deployment_performed": True, "provider_calls_performed": True, "final_decision": FINAL_DECISION_DEPLOYED}
    records = build_step_evidence(state)
    assert [item["step_number"] for item in records] == list(range(151, 161))


def test_step_evidence_receipt_chain_is_contiguous():
    records = build_step_evidence({"deployment_performed": False, "provider_calls_performed": False, "final_decision": FINAL_DECISION_HOLD})
    assert records[0]["previous_receipt_hash"] == ""
    for previous, current in zip(records, records[1:]):
        assert current["previous_receipt_hash"] == previous["receipt_hash"]


def test_requirement_discovery_is_deterministic(tmp_path):
    (tmp_path / "app.py").write_text("import flask\nimport werkzeug\n", encoding="utf-8")
    package_map = {"flask": ["Flask"], "werkzeug": ["Werkzeug"]}
    versions = {"Flask": "3.1.0", "Werkzeug": "3.1.0", "gunicorn": "23.0.0"}
    first = discover_requirement_lines(
        tmp_path,
        package_map=package_map,
        versions=versions,
        stdlib_names=set(),
    )
    second = discover_requirement_lines(
        tmp_path,
        package_map=package_map,
        versions=versions,
        stdlib_names=set(),
    )
    assert first == second
    assert "Flask==3.1.0" in first
    assert "gunicorn==23.0.0" in first


def test_requirements_text_contains_no_credentials():
    rendered = requirements_text(["Flask==3.1.0", "gunicorn==23.0.0"])
    assert "Flask==3.1.0" in rendered
    assert "token" not in rendered.lower()
    assert "password" not in rendered.lower()
