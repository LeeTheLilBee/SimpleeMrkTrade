from __future__ import annotations

import json
from pathlib import Path

import pytest

from tower.tower_ob_managed_staging_service_creation import (
    DEPLOY_ROOT_RELATIVE,
    FINAL_DECISION,
    HEALTH_PATH,
    MANAGED_START_COMMAND,
    MANAGED_WSGI_TARGET,
    NEXT_BOUNDARY,
    SERVICE_NAME,
    build_service_creation_state,
    build_step_evidence,
    environment_names_manifest,
    expected_file_payloads,
    previous_checkpoint_handoff,
    provider_binding_template,
    release_policy,
    service_spec,
    validate_service_shell,
    write_operator_worksheets,
)

ROOT = Path(__file__).resolve().parents[1]


def test_service_spec_is_one_tower_fronted_service():
    spec = service_spec()
    assert spec["runtime_topology"] == "single_tower_fronted_managed_python_web_service"
    assert spec["public_ingress"]["tower_only_browser_front_door"] is True


def test_service_spec_uses_managed_wsgi_target():
    assert service_spec()["runtime_target"] == MANAGED_WSGI_TARGET == "web.managed_staging:app"


def test_service_name_is_staging_only():
    assert service_spec()["service_name"] == SERVICE_NAME
    assert service_spec()["environment"] == "staging"


def test_start_command_is_gunicorn_port_bound():
    assert service_spec()["start_command"] == MANAGED_START_COMMAND
    assert "$PORT" in MANAGED_START_COMMAND


def test_health_path_is_tower_healthz():
    assert service_spec()["health_check_path"] == HEALTH_PATH == "/tower/healthz"


def test_exactly_one_service_shell_is_created():
    assert service_spec()["resource_scope"]["web_service_shell_count"] == 1


def test_production_resource_creation_is_locked():
    assert service_spec()["resource_scope"]["production_resource_created_in_this_pack"] is False


def test_database_creation_is_locked():
    assert service_spec()["resource_scope"]["database_created_in_this_pack"] is False


def test_object_storage_creation_is_locked():
    assert service_spec()["resource_scope"]["object_storage_created_in_this_pack"] is False


def test_dns_change_is_locked():
    assert service_spec()["resource_scope"]["dns_changed_in_this_pack"] is False


def test_live_safety_locks_remain_closed():
    safety = service_spec()["safety"]
    assert safety["production_manual_live_authorized"] is False
    assert safety["broker_submission_enabled"] is False
    assert safety["real_capital_movement_enabled"] is False
    assert safety["direct_vault_upload_enabled"] is False
    assert safety["live_auto_locked"] is True


def test_environment_manifest_contains_required_runtime_names():
    manifest = environment_names_manifest()
    assert "TOWER_SESSION_SECRET" in manifest["required_runtime_names"]
    assert "SIMPLEE_DEPLOYMENT_ENVIRONMENT" in manifest["required_runtime_names"]


def test_environment_manifest_contains_provider_binding_names():
    manifest = environment_names_manifest()
    assert "SIMPLEE_MANAGED_HOST_PROVIDER" in manifest["required_provider_binding_names"]
    assert "SIMPLEE_STAGING_DEPLOYMENT_REGION" in manifest["required_provider_binding_names"]


def test_environment_manifest_contains_names_not_values():
    manifest = environment_names_manifest()
    assert manifest["values_in_manifest"] is False
    assert manifest["secret_values_in_git"] is False


def test_provider_binding_template_is_blank_and_held():
    packet = provider_binding_template()
    assert packet["provider_slug"] == ""
    assert packet["account_or_team_ref"] == ""
    assert packet["binding_complete"] is False


def test_provider_binding_template_contains_no_secret_value_fields():
    packet = provider_binding_template()
    forbidden = {"password", "password_value", "api_key", "token", "cookie", "connection_string", "secret_value"}
    assert forbidden.isdisjoint(packet.keys())


def test_provider_binding_template_does_not_authorize_calls():
    packet = provider_binding_template()
    assert packet["provider_calls_authorized"] is False
    assert packet["deployment_authorized"] is False


def test_release_policy_is_manual_only():
    policy = release_policy()
    assert policy["manual_deployment_only"] is True
    assert policy["automatic_production_promotion"] is False


def test_release_policy_requires_rollback():
    policy = release_policy()
    assert policy["rollback"]["required"] is True
    assert policy["rollback"]["stop_on_failed_health_check"] is True


def test_release_policy_locks_database_storage_dns_and_production():
    locked = release_policy()["locked_resources"]
    assert all(locked.values())


def test_expected_start_script_is_fail_closed():
    script = expected_file_payloads()[f"{DEPLOY_ROOT_RELATIVE}/start.sh"]
    assert "set -eu" in script
    assert "${PORT:?PORT is required}" in script
    assert "exec gunicorn" in script


def test_expected_start_script_uses_managed_wsgi():
    script = expected_file_payloads()[f"{DEPLOY_ROOT_RELATIVE}/start.sh"]
    assert "web.managed_staging:app" in script


def test_health_probe_uses_only_health_endpoint():
    probe = expected_file_payloads()[f"{DEPLOY_ROOT_RELATIVE}/health_probe.py"]
    assert "/tower/healthz" in probe
    assert "/dashboard" not in probe
    assert "/ob/" not in probe


def test_health_probe_reads_no_credentials():
    probe = expected_file_payloads()[f"{DEPLOY_ROOT_RELATIVE}/health_probe.py"].lower()
    assert "password" not in probe
    assert "token" not in probe
    assert "cookie" not in probe


def test_previous_checkpoint_handoff_is_ready():
    handoff = previous_checkpoint_handoff(ROOT)
    assert handoff["handoff_ready"] is True
    assert handoff["closed_through_step"] == 140


def test_validate_service_shell_passes_for_repository():
    report = validate_service_shell(ROOT)
    assert report["valid"] is True
    assert all(report["checks"].values())


def test_validate_service_shell_fails_when_files_missing(tmp_path):
    report = validate_service_shell(tmp_path)
    assert report["valid"] is False


def test_service_creation_state_closes_step_150():
    state = build_service_creation_state(ROOT)
    assert state["closed_layer"] == "MANAGED_STAGING_SERVICE_CREATION"
    assert state["closed_through_step"] == 150


def test_service_creation_state_records_shell_created():
    state = build_service_creation_state(ROOT)
    assert state["service_shell_created"] is True


def test_service_creation_state_holds_for_provider_binding():
    state = build_service_creation_state(ROOT)
    assert state["provider_binding_complete"] is False
    assert state["final_decision"] == FINAL_DECISION


def test_service_creation_state_points_to_configuration_build_deployment():
    assert build_service_creation_state(ROOT)["next_boundary"] == NEXT_BOUNDARY


def test_service_creation_state_has_one_remaining_blocker():
    state = build_service_creation_state(ROOT)
    assert state["blocking_requirement_count"] == 1
    assert state["blocking_requirements"][0]["requirement"] == "managed_host_provider_binding"


def test_service_creation_state_performs_no_provider_action():
    state = build_service_creation_state(ROOT)
    assert state["provider_login_performed"] is False
    assert state["provider_calls_performed"] is False
    assert state["provider_resource_created"] is False


def test_service_creation_state_performs_no_secret_build_or_deploy():
    state = build_service_creation_state(ROOT)
    assert state["secrets_created_or_read_or_registered"] is False
    assert state["build_performed"] is False
    assert state["deployment_performed"] is False


def test_service_creation_state_keeps_external_resources_locked():
    state = build_service_creation_state(ROOT)
    assert state["database_created"] is False
    assert state["object_storage_created"] is False
    assert state["dns_changed"] is False


def test_step_evidence_contains_steps_141_through_150():
    records = build_step_evidence(ROOT)
    assert [item["step_number"] for item in records] == list(range(141, 151))


def test_step_evidence_forms_receipt_chain():
    records = build_step_evidence(ROOT)
    for previous, current in zip(records, records[1:]):
        assert current["previous_receipt_hash"] == previous["receipt_hash"]


def test_step_evidence_records_no_provider_actions():
    records = build_step_evidence(ROOT)
    assert all(item["provider_calls_performed"] is False for item in records)
    assert all(item["deployment_performed"] is False for item in records)


def test_operator_worksheets_are_outside_repository(tmp_path):
    output = tmp_path / "worksheets"
    result = write_operator_worksheets(ROOT, output)
    assert Path(result["manifest_path"]).is_file()
    assert ROOT not in Path(result["manifest_path"]).parents


def test_operator_manifest_reports_no_actions(tmp_path):
    result = write_operator_worksheets(ROOT, tmp_path / "worksheets")
    assert result["provider_calls_performed"] is False
    assert result["provider_resource_created"] is False
    assert result["deployment_performed"] is False


def test_repository_service_spec_matches_contract():
    stored = json.loads((ROOT / DEPLOY_ROOT_RELATIVE / "service_spec.json").read_text())
    assert stored == service_spec()


def test_repository_readme_states_tower_front_door():
    text = (ROOT / DEPLOY_ROOT_RELATIVE / "README.md").read_text()
    assert "Tower remains the only browser front door" in text


def test_repository_deployment_files_contain_no_github_token_patterns():
    rendered = "\n".join(expected_file_payloads().values())
    assert "ghp_" not in rendered
    assert "Authorization: Basic" not in rendered
