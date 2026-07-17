"""Repository-side managed-staging service-shell creation contracts.

Steps 141–150 stop the recursive authorization loop and create the actual,
provider-neutral deployment shell for one Tower-fronted managed Python web
service. This module writes no provider resources and performs no provider
login, API/CLI call, secret registration, build, deployment, DNS change,
database creation, object-storage creation, or official walkthrough.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from tower.tower_ob_managed_staging_runtime import (
    MANAGED_START_COMMAND,
    MANAGED_WSGI_TARGET,
    environment_reference_contract,
    payload_hash,
    resolve_repository_runtime,
)

SCHEMA_VERSION = "simplee.tower_ob.managed_staging_service_creation.v1"
SERVICE_NAME = "simplee-tower-ob-staging"
HEALTH_PATH = "/tower/healthz"
FINAL_DECISION = "STAGING_SERVICE_SHELL_CREATED_HOLD_PROVIDER_BINDING_AND_DEPLOYMENT"
NEXT_BOUNDARY = "managed_staging_configuration_build_and_deployment"
STEP140_CHECKPOINT_RELATIVE = (
    "integration_checkpoints/20260717T000848Z_"
    "tower_ob_managed_staging_controlled_provider_provisioning_execution_"
    "session_opening_execution_preparation/resume_checkpoint.json"
)
DEPLOY_ROOT_RELATIVE = "deploy/managed_staging"

SERVICE_FILES = (
    "README.md",
    "service_spec.json",
    "environment.names.json",
    "provider_binding.template.json",
    "release_policy.json",
    "start.sh",
    "health_probe.py",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def service_spec() -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "environment": "staging",
        "service_type": "managed_python_web_service",
        "runtime_topology": "single_tower_fronted_managed_python_web_service",
        "runtime_target": MANAGED_WSGI_TARGET,
        "start_command": MANAGED_START_COMMAND,
        "health_check_path": HEALTH_PATH,
        "repository_branch": "tower-ob-integration-dev",
        "public_ingress": {
            "tower_only_browser_front_door": True,
            "observatory_public_ingress_allowed": False,
            "anonymous_observatory_access_allowed": False,
        },
        "resource_scope": {
            "web_service_shell_count": 1,
            "database_created_in_this_pack": False,
            "object_storage_created_in_this_pack": False,
            "dns_changed_in_this_pack": False,
            "production_resource_created_in_this_pack": False,
        },
        "execution": {
            "provider_binding_complete": False,
            "provider_calls_performed": False,
            "resource_created_at_provider": False,
            "secret_values_registered": False,
            "build_performed": False,
            "deployment_performed": False,
        },
        "safety": {
            "production_manual_live_authorized": False,
            "broker_submission_enabled": False,
            "real_capital_movement_enabled": False,
            "direct_vault_upload_enabled": False,
            "live_auto_locked": True,
        },
    }
    payload["service_spec_hash"] = payload_hash(payload)
    return payload


def environment_names_manifest() -> dict[str, Any]:
    contract = environment_reference_contract()
    names = sorted(set(contract["runtime_required"] + contract["provider_required_before_authorization_review"] + contract["optional"]))
    payload = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "environment_names_only",
        "environment_names": names,
        "required_runtime_names": contract["runtime_required"],
        "required_provider_binding_names": contract["provider_required_before_authorization_review"],
        "optional_names": contract["optional"],
        "prohibited_names": contract["prohibited_in_hosted_staging"],
        "values_in_manifest": False,
        "production_values_reused": False,
        "secret_values_in_git": False,
    }
    payload["manifest_hash"] = payload_hash(payload)
    return payload


def provider_binding_template() -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "managed_staging_provider_binding",
        "service_name": SERVICE_NAME,
        "provider_slug": "",
        "account_or_team_ref": "",
        "deployment_region": "",
        "provider_service_id_ref": "",
        "provider_service_url_ref": "",
        "source_commit_ref": "",
        "monthly_cost_ceiling_usd": "",
        "owner_approval_receipt_ref": "",
        "capability_attestations": {
            "managed_python_web_service": False,
            "provider_supplied_port_binding": False,
            "https_termination": False,
            "encrypted_environment_secret_store": False,
            "health_checks": False,
            "deployment_logs": False,
            "access_logs": False,
            "manual_deployment_control": False,
            "rollback_support": False,
        },
        "notes": [
            "Use non-secret provider-visible references only.",
            "Do not paste passwords, API keys, tokens, cookies, or connection strings.",
            "Completing this packet does not itself build or deploy the service.",
        ],
        "binding_complete": False,
        "provider_calls_authorized": False,
        "deployment_authorized": False,
    }
    payload["template_hash"] = payload_hash(payload)
    return payload


def release_policy() -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "policy_type": "managed_staging_release_policy",
        "source_branch": "tower-ob-integration-dev",
        "runtime_target": MANAGED_WSGI_TARGET,
        "manual_deployment_only": True,
        "automatic_production_promotion": False,
        "production_deployment_authorized": False,
        "required_pre_deploy_gates": [
            "provider_binding_complete",
            "staging_environment_references_registered_by_name",
            "source_commit_frozen",
            "health_check_configured",
            "rollback_target_recorded",
            "owner_deployment_approval_recorded",
        ],
        "rollback": {
            "required": True,
            "previous_known_good_commit_required": True,
            "provider_rollback_control_required": True,
            "stop_on_failed_health_check": True,
            "stop_on_tower_login_failure": True,
            "stop_on_observatory_public_ingress": True,
        },
        "locked_resources": {
            "database_creation": True,
            "object_storage_creation": True,
            "dns_change": True,
            "production_resource_creation": True,
        },
    }
    payload["policy_hash"] = payload_hash(payload)
    return payload


def previous_checkpoint_handoff(repository_root: str | Path) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    path = root / STEP140_CHECKPOINT_RELATIVE
    if not path.is_file():
        return {
            "handoff_ready": False,
            "checkpoint_path": str(path),
            "closed_through_step": None,
            "source_commit": "",
            "step140_receipt_hash": "",
        }
    data = json.loads(path.read_text(encoding="utf-8"))
    ready = (
        data.get("closed_through_step") == 140
        and data.get("closed_layer") == "MANAGED_STAGING_CONTROLLED_PROVIDER_PROVISIONING_EXECUTION_SESSION_OPENING_EXECUTION_PREPARATION"
        and bool(data.get("step140_receipt_hash"))
    )
    return {
        "handoff_ready": ready,
        "checkpoint_path": STEP140_CHECKPOINT_RELATIVE,
        "closed_through_step": data.get("closed_through_step"),
        "source_commit": data.get("integration_commit_before_checkpoint_commit", ""),
        "step140_receipt_hash": data.get("step140_receipt_hash", ""),
        "prior_final_decision": data.get("final_decision", ""),
        "handoff_hash": payload_hash({
            "closed_through_step": data.get("closed_through_step"),
            "step140_receipt_hash": data.get("step140_receipt_hash", ""),
            "prior_final_decision": data.get("final_decision", ""),
        }),
    }


def expected_file_payloads() -> dict[str, str]:
    readme = (
        "# Managed Staging Service Shell\n\n"
        "This directory is the deployable repository-side shell for one Tower-fronted "
        "managed Python staging web service. The managed WSGI target is "
        "`web.managed_staging:app`. Tower remains the only browser front door. "
        "Observatory public ingress, production deployment, database creation, object "
        "storage creation, DNS changes, broker submission, real capital movement, and "
        "Live Auto remain locked.\n"
    )
    start = "#!/usr/bin/env sh\nset -eu\nexec gunicorn --bind 0.0.0.0:${PORT:?PORT is required} web.managed_staging:app\n"
    probe = (
        "from __future__ import annotations\n\n"
        "import json\nimport os\nimport sys\nimport urllib.request\n\n"
        "base = os.environ.get('SIMPLEE_STAGING_BASE_URL', '').rstrip('/')\n"
        "if not base:\n    raise SystemExit('SIMPLEE_STAGING_BASE_URL is required')\n"
        "url = base + '/tower/healthz'\n"
        "with urllib.request.urlopen(url, timeout=15) as response:\n"
        "    body = response.read().decode('utf-8')\n"
        "    payload = json.loads(body)\n"
        "    if response.status != 200 or payload.get('ok') is not True:\n"
        "        raise SystemExit('managed staging health check failed')\n"
        "print(json.dumps({'ok': True, 'health_url': url}, sort_keys=True))\n"
    )
    return {
        f"{DEPLOY_ROOT_RELATIVE}/README.md": readme,
        f"{DEPLOY_ROOT_RELATIVE}/service_spec.json": json.dumps(service_spec(), indent=2, sort_keys=True) + "\n",
        f"{DEPLOY_ROOT_RELATIVE}/environment.names.json": json.dumps(environment_names_manifest(), indent=2, sort_keys=True) + "\n",
        f"{DEPLOY_ROOT_RELATIVE}/provider_binding.template.json": json.dumps(provider_binding_template(), indent=2, sort_keys=True) + "\n",
        f"{DEPLOY_ROOT_RELATIVE}/release_policy.json": json.dumps(release_policy(), indent=2, sort_keys=True) + "\n",
        f"{DEPLOY_ROOT_RELATIVE}/start.sh": start,
        f"{DEPLOY_ROOT_RELATIVE}/health_probe.py": probe,
    }


def validate_service_shell(repository_root: str | Path) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    expected = expected_file_payloads()
    checks: dict[str, bool] = {}
    hashes: dict[str, str] = {}
    for relative, content in expected.items():
        path = root / relative
        actual = path.read_text(encoding="utf-8") if path.is_file() else ""
        checks[f"{relative}:exists"] = path.is_file()
        checks[f"{relative}:content_matches"] = actual == content
        hashes[relative] = sha256_text(actual) if actual else ""
    runtime = resolve_repository_runtime(root)
    checks["repository_runtime_resolved"] = bool(runtime.get("resolved"))
    checks["managed_wsgi_target_matches"] = runtime.get("managed_wsgi_target") == MANAGED_WSGI_TARGET
    checks["tower_only_topology"] = runtime.get("topology") == "single_tower_fronted_managed_python_web_service"
    valid = all(checks.values())
    payload = {
        "schema_version": SCHEMA_VERSION,
        "valid": valid,
        "checks": checks,
        "file_hashes": hashes,
        "runtime_contract_hash": runtime.get("contract_hash", ""),
        "provider_calls_performed": False,
        "provider_resource_created": False,
        "secret_values_registered": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    payload["validation_hash"] = payload_hash(payload)
    return payload


def build_service_creation_state(repository_root: str | Path) -> dict[str, Any]:
    handoff = previous_checkpoint_handoff(repository_root)
    validation = validate_service_shell(repository_root)
    blockers = []
    if not handoff["handoff_ready"]:
        blockers.append({"requirement": "valid_step140_handoff", "status": "required"})
    if not validation["valid"]:
        blockers.append({"requirement": "deployable_service_shell", "status": "creation_or_repair_required"})
    binding = provider_binding_template()
    if not binding["binding_complete"]:
        blockers.append({"requirement": "managed_host_provider_binding", "status": "operator_input_required_before_deployment"})
    state = {
        "schema_version": SCHEMA_VERSION,
        "closed_layer": "MANAGED_STAGING_SERVICE_CREATION",
        "closed_through_step": 150,
        "runtime_target": MANAGED_WSGI_TARGET,
        "runtime_topology": "single_tower_fronted_managed_python_web_service",
        "service_name": SERVICE_NAME,
        "service_shell_created": bool(handoff["handoff_ready"] and validation["valid"]),
        "provider_binding_complete": False,
        "provider_resource_created": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "secrets_created_or_read_or_registered": False,
        "build_performed": False,
        "deployment_performed": False,
        "database_created": False,
        "object_storage_created": False,
        "dns_changed": False,
        "official_walkthrough_performed": False,
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
        "blocking_requirements": blockers,
        "blocking_requirement_count": len(blockers),
        "final_decision": FINAL_DECISION if handoff["handoff_ready"] and validation["valid"] else "NO_GO_HOLD_SERVICE_SHELL_CREATION_REQUIRED",
        "next_boundary": NEXT_BOUNDARY,
        "step140_handoff": handoff,
        "service_validation": validation,
    }
    state["state_hash"] = payload_hash(state)
    return state


def build_step_evidence(repository_root: str | Path) -> tuple[dict[str, Any], ...]:
    root = Path(repository_root).resolve()
    state = build_service_creation_state(root)
    payloads = [
        (141, "step140_handoff_and_staging_finish_line", {"handoff": state["step140_handoff"], "recursive_authorization_loop_stopped": True}),
        (142, "single_tower_fronted_service_spec_created", {"service_spec": service_spec()}),
        (143, "managed_wsgi_start_contract_created", {"runtime_target": MANAGED_WSGI_TARGET, "start_command": MANAGED_START_COMMAND}),
        (144, "environment_name_manifest_created", {"environment_manifest": environment_names_manifest()}),
        (145, "provider_binding_template_created", {"provider_binding_template": provider_binding_template()}),
        (146, "health_probe_and_tower_ingress_contract_created", {"health_path": HEALTH_PATH, "tower_only_front_door": True}),
        (147, "manual_release_and_rollback_policy_created", {"release_policy": release_policy()}),
        (148, "service_shell_file_integrity_verified", {"validation": state["service_validation"]}),
        (149, "configuration_build_and_deployment_handoff_prepared", {"next_boundary": NEXT_BOUNDARY, "provider_binding_complete": False}),
        (150, "managed_staging_service_creation_closeout", {"state": state}),
    ]
    previous = state["step140_handoff"].get("step140_receipt_hash", "")
    records = []
    for step, key, body in payloads:
        record = {
            "schema_version": SCHEMA_VERSION,
            "step_number": step,
            "step_key": key,
            "previous_receipt_hash": previous,
            **body,
            "provider_calls_performed": False,
            "provider_resource_created": False,
            "secret_values_registered": False,
            "build_performed": False,
            "deployment_performed": False,
        }
        record["receipt_hash"] = payload_hash(record)
        previous = record["receipt_hash"]
        records.append(record)
    return tuple(records)


def write_operator_worksheets(repository_root: str | Path, output_directory: str | Path) -> dict[str, str]:
    root = Path(repository_root).resolve()
    out = Path(output_directory).resolve()
    if out == root or root in out.parents:
        raise ValueError("Operator worksheets must be written outside the repository.")
    out.mkdir(parents=True, exist_ok=False)
    state_path = out / "tower_ob_managed_staging_service_creation_state.json"
    binding_path = out / "tower_ob_managed_staging_provider_binding.json"
    manifest_path = out / "worksheet_manifest.json"
    state_path.write_text(json.dumps(build_service_creation_state(root), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    binding_path.write_text(json.dumps(provider_binding_template(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "service_creation_state_path": str(state_path),
        "provider_binding_path": str(binding_path),
        "provider_calls_performed": False,
        "provider_resource_created": False,
        "secret_values_included": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    manifest["manifest_hash"] = payload_hash(manifest)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {**manifest, "manifest_path": str(manifest_path)}
