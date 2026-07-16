from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from tower.tower_ob_managed_staging_provider_provisioning_authorization import (
    blank_current_inputs as blank_authorization_inputs,
    build_provisioning_authorization_decision,
    freeze_provisioning_authorization_record,
)

SCHEMA_VERSION = "simplee.tower_ob.no_call_provisioning_execution_preparation.v1"

REQUIRED_PREPARATION_ATTESTATIONS = (
    "provider_console_manual_session_planned",
    "single_tower_fronted_service_confirmed",
    "tower_only_public_ingress_confirmed",
    "observatory_separate_service_not_required",
    "source_branch_and_commit_reviewed",
    "runtime_target_and_start_command_reviewed",
    "non_secret_environment_names_reviewed",
    "secret_reference_registration_without_readback_reviewed",
    "health_check_configuration_reviewed",
    "deployment_and_access_logging_reviewed",
    "manual_deployment_control_reviewed",
    "rollback_target_reviewed",
    "monthly_cost_ceiling_reviewed",
    "one_web_service_resource_limit_confirmed",
    "idempotency_and_duplicate_creation_guard_reviewed",
    "stop_conditions_reviewed",
    "database_creation_not_authorized",
    "object_storage_creation_not_authorized",
    "dns_changes_not_authorized",
    "build_not_authorized",
    "deployment_not_authorized",
    "official_walkthrough_not_authorized",
    "production_manual_live_not_authorized",
    "broker_submission_not_authorized",
    "real_capital_movement_not_authorized",
    "direct_vault_upload_not_authorized",
    "live_auto_remains_locked",
    "no_provider_login_or_calls_performed",
)

_SAFE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]{2,255}$")
_ISO_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
_SENSITIVE_PATTERNS = (
    "postgresql://", "mysql://", "mongodb://", "redis://", "api_key=",
    "token=", "password=", "secret=", "-----begin private key-----",
    "ghp_", "github_pat_", "sk_live_", "sk_test_",
)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _bool(value: Any) -> bool:
    return value is True


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_text(value).encode("utf-8")).hexdigest()


def payload_hash(payload: Any) -> str:
    rendered = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _contains_sensitive_material(value: Any) -> bool:
    rendered = json.dumps(value, sort_keys=True).lower()
    return any(pattern in rendered for pattern in _SENSITIVE_PATTERNS)


def build_provisioning_authorization_handoff(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
) -> dict[str, Any]:
    authorization = build_provisioning_authorization_decision(
        repository_root,
        provider_inputs or {},
        provider_review_owner_decision or {},
        review_inputs or {},
        provisioning_decision or {},
    )
    frozen = freeze_provisioning_authorization_record(
        repository_root,
        provider_inputs or {},
        provider_review_owner_decision or {},
        review_inputs or {},
        provisioning_decision or {},
    )
    ready = bool(
        authorization.get("authorization_valid")
        and authorization.get(
            "ready_for_separate_no_call_provider_provisioning_execution_preparation"
        )
    )
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "provider_provisioning_authorization_handoff",
        "provisioning_authorization_record_hash": frozen.get(
            "frozen_authorization_record_hash", ""
        ),
        "authorization_decision_hash": authorization.get(
            "authorization_decision_hash", ""
        ),
        "provider_inputs_valid": bool(authorization.get("provider_inputs_valid")),
        "provider_review_owner_approval_valid": bool(
            authorization.get("provider_review_owner_approval_valid")
        ),
        "review_inputs_valid": bool(authorization.get("review_inputs_valid")),
        "provisioning_authorization_valid": bool(
            authorization.get("authorization_valid")
        ),
        "handoff_ready": ready,
        "provider_calls_authorized": False,
        "provider_login_authorized": False,
        "resource_creation_authorized": False,
        "secret_registration_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
        "provider_calls_performed": False,
        "resources_created": False,
    }
    record["handoff_hash"] = payload_hash(record)
    return record


def execution_preparation_input_template(
    handoff: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    handoff = dict(handoff or {})
    payload = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "managed_staging_no_call_execution_preparation_inputs",
        "provisioning_authorization_record_hash": _text(
            handoff.get("provisioning_authorization_record_hash")
        ),
        "authorization_handoff_hash": _text(handoff.get("handoff_hash")),
        "provider_console_session_ref": "",
        "provider_service_form_ref": "",
        "source_commit_ref": "",
        "runtime_review_ref": "",
        "environment_name_review_ref": "",
        "secret_reference_custody_ref": "",
        "health_logging_review_ref": "",
        "rollback_review_ref": "",
        "cost_guardrail_review_ref": "",
        "idempotency_guard_ref": "",
        "prepared_by": "",
        "prepared_at": "",
        "attestations": {
            name: False for name in REQUIRED_PREPARATION_ATTESTATIONS
        },
        "notes": [
            "Use non-secret labels, documentation references, or screenshot references only.",
            "Do not include passwords, tokens, cookies, API keys, private keys, or connection strings.",
            "Do not log into, call, or modify a provider while completing this worksheet.",
            "Completion opens only a separate provider provisioning execution authorization decision.",
        ],
    }
    payload["template_hash"] = payload_hash(payload)
    return payload


def validate_execution_preparation_inputs(
    payload: Mapping[str, Any] | None,
    *,
    handoff: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    data = dict(payload or {})
    handoff = dict(handoff or {})
    errors: list[dict[str, str]] = []
    reference_fields = (
        "provider_console_session_ref", "provider_service_form_ref",
        "source_commit_ref", "runtime_review_ref", "environment_name_review_ref",
        "secret_reference_custody_ref", "health_logging_review_ref",
        "rollback_review_ref", "cost_guardrail_review_ref", "idempotency_guard_ref",
        "prepared_by",
    )
    for field in reference_fields:
        value = _text(data.get(field))
        if not value or not _SAFE_REF.fullmatch(value):
            errors.append({"code": f"{field}_required", "field": field})
    prepared_at = _text(data.get("prepared_at"))
    if not _ISO_UTC.fullmatch(prepared_at):
        errors.append({"code": "prepared_at_must_be_utc_iso", "field": "prepared_at"})
    expected_auth_hash = _text(handoff.get("provisioning_authorization_record_hash"))
    expected_handoff_hash = _text(handoff.get("handoff_hash"))
    if _text(data.get("provisioning_authorization_record_hash")) != expected_auth_hash:
        errors.append({"code": "provisioning_authorization_hash_mismatch", "field": "provisioning_authorization_record_hash"})
    if _text(data.get("authorization_handoff_hash")) != expected_handoff_hash:
        errors.append({"code": "authorization_handoff_hash_mismatch", "field": "authorization_handoff_hash"})
    attestations = data.get("attestations") if isinstance(data.get("attestations"), Mapping) else {}
    for name in REQUIRED_PREPARATION_ATTESTATIONS:
        if not _bool(attestations.get(name)):
            errors.append({"code": f"attestation_required:{name}", "field": f"attestations.{name}"})
    sensitive = _contains_sensitive_material(data)
    if sensitive:
        errors.append({"code": "sensitive_material_detected", "field": "payload"})
    valid = bool(handoff.get("handoff_ready")) and not errors
    report = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "execution_preparation_validation_report",
        "authorization_handoff_ready": bool(handoff.get("handoff_ready")),
        "valid": valid,
        "error_count": len(errors),
        "errors": errors,
        "completed_attestation_count": sum(
            1 for name in REQUIRED_PREPARATION_ATTESTATIONS if _bool(attestations.get(name))
        ),
        "required_attestation_count": len(REQUIRED_PREPARATION_ATTESTATIONS),
        "sensitive_material_detected": sensitive,
        "provider_login_performed": False,
        "provider_calls_performed": False,
    }
    report["report_hash"] = payload_hash(report)
    return report


def build_provider_console_session_plan(handoff: Mapping[str, Any] | None = None) -> dict[str, Any]:
    plan = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": "manual_provider_console_session_plan",
        "authorization_handoff_ready": bool((handoff or {}).get("handoff_ready")),
        "session_mode": "manual_owner_controlled_future_execution_only",
        "login_performed": False,
        "session_created": False,
        "browser_automation_allowed": False,
        "provider_cli_allowed": False,
        "provider_api_allowed": False,
        "credentials_recorded": False,
        "cookies_recorded": False,
        "mfa_material_recorded": False,
    }
    plan["plan_hash"] = payload_hash(plan)
    return plan


def build_one_service_execution_manifest() -> dict[str, Any]:
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "one_tower_fronted_service_execution_manifest",
        "service_count_ceiling": 1,
        "service_name": "simplee-tower-ob-staging",
        "environment_name": "staging",
        "source_branch": "tower-ob-integration-dev",
        "runtime_target": "web.managed_staging:app",
        "start_command": "gunicorn --bind 0.0.0.0:$PORT web.managed_staging:app",
        "public_ingress_owner": "tower",
        "observatory_public_ingress_allowed": False,
        "separate_observatory_service_required": False,
        "database_creation_allowed": False,
        "object_storage_creation_allowed": False,
        "dns_changes_allowed": False,
        "build_allowed": False,
        "deployment_allowed": False,
        "manifest_only": True,
        "resource_created": False,
    }
    manifest["manifest_hash"] = payload_hash(manifest)
    return manifest


def build_non_secret_environment_registration_plan() -> dict[str, Any]:
    plan = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": "non_secret_environment_name_registration_plan",
        "non_secret_environment_names": [
            "SIMPLEE_ENVIRONMENT", "SIMPLEE_DEPLOYMENT_MODE",
            "SIMPLEE_MANAGED_HOST_PROVIDER", "SIMPLEE_MANAGED_HOST_ACCOUNT_OR_TEAM",
            "SIMPLEE_STAGING_DEPLOYMENT_REGION", "SIMPLEE_PROVIDER_OWNER_APPROVAL",
            "TOWER_OWNER_USERNAME", "TOWER_OWNER_ID", "TOWER_STEP_UP_MINUTES",
        ],
        "environment_values_recorded": False,
        "registration_performed": False,
        "provider_calls_performed": False,
    }
    plan["plan_hash"] = payload_hash(plan)
    return plan


def build_secret_reference_registration_plan() -> dict[str, Any]:
    plan = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": "secret_reference_registration_without_readback_plan",
        "secret_environment_names": ["TOWER_SESSION_SECRET", "TOWER_OWNER_PASSWORD_HASH"],
        "secret_values_recorded": False,
        "secret_values_generated": False,
        "secret_values_read": False,
        "secret_readback_allowed": False,
        "git_storage_allowed": False,
        "production_secret_reuse_allowed": False,
        "registration_performed": False,
        "provider_calls_performed": False,
    }
    plan["plan_hash"] = payload_hash(plan)
    return plan


def build_health_logging_control_plan() -> dict[str, Any]:
    plan = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": "health_logging_manual_control_plan",
        "health_check_path": "/tower/healthz",
        "deployment_logs_required": True,
        "access_logs_required": True,
        "secret_redaction_required": True,
        "manual_deployment_control_required": True,
        "automatic_deployment_allowed": False,
        "configuration_performed": False,
        "provider_calls_performed": False,
    }
    plan["plan_hash"] = payload_hash(plan)
    return plan


def build_rollback_and_stop_condition_plan() -> dict[str, Any]:
    plan = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": "rollback_and_execution_stop_condition_plan",
        "rollback_target_required": True,
        "stop_conditions": [
            "authorization missing, invalid, expired, or hash-mismatched",
            "provider account, team, region, or cost differs from frozen inputs",
            "more than one web service would be created",
            "database, object storage, DNS, build, or deployment is requested",
            "secret value readback or Git storage is requested",
            "Tower-only ingress cannot be preserved",
            "Observatory would receive separate public ingress",
            "health, logging, manual control, or rollback cannot be configured",
        ],
        "rollback_executed": False,
        "provider_calls_performed": False,
    }
    plan["plan_hash"] = payload_hash(plan)
    return plan


def build_cost_idempotency_guardrail(
    provisioning_decision: Mapping[str, Any] | None,
) -> dict[str, Any]:
    decision = dict(provisioning_decision or {})
    ceiling = _text(decision.get("monthly_cost_ceiling_usd"))
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "resource_cost_and_idempotency_guardrail",
        "service_count_ceiling": 1,
        "monthly_cost_ceiling_usd": ceiling,
        "automatic_spend_allowed": False,
        "duplicate_service_creation_allowed": False,
        "idempotency_key_source": "frozen_provisioning_authorization_hash",
        "idempotency_key_sha256": _fingerprint(
            decision.get("frozen_review_packet_hash") or decision.get("challenge_id")
        ),
        "resource_lookup_performed": False,
        "provider_calls_performed": False,
    }
    record["record_hash"] = payload_hash(record)
    return record


def build_inert_execution_command_manifest() -> dict[str, Any]:
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "inert_provider_execution_command_manifest",
        "provider_slug": None,
        "provider_cli_commands": [],
        "provider_api_requests": [],
        "shell_commands": [],
        "http_requests": [],
        "browser_actions": [],
        "dry_run_only": True,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    manifest["manifest_hash"] = payload_hash(manifest)
    return manifest


def freeze_execution_preparation_packet(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
    preparation_inputs: Mapping[str, Any] | None,
) -> dict[str, Any]:
    handoff = build_provisioning_authorization_handoff(
        repository_root, provider_inputs, provider_review_owner_decision,
        review_inputs, provisioning_decision,
    )
    validation = validate_execution_preparation_inputs(preparation_inputs, handoff=handoff)
    packet = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "frozen_no_call_provider_provisioning_execution_preparation",
        "authorization_handoff_hash": handoff["handoff_hash"],
        "provisioning_authorization_record_hash": handoff[
            "provisioning_authorization_record_hash"
        ],
        "preparation_inputs_valid": validation["valid"],
        "preparation_validation_report_hash": validation["report_hash"],
        "provider_console_session_plan_hash": build_provider_console_session_plan(handoff)["plan_hash"],
        "one_service_execution_manifest_hash": build_one_service_execution_manifest()["manifest_hash"],
        "environment_registration_plan_hash": build_non_secret_environment_registration_plan()["plan_hash"],
        "secret_reference_plan_hash": build_secret_reference_registration_plan()["plan_hash"],
        "health_logging_control_plan_hash": build_health_logging_control_plan()["plan_hash"],
        "rollback_stop_plan_hash": build_rollback_and_stop_condition_plan()["plan_hash"],
        "cost_idempotency_guardrail_hash": build_cost_idempotency_guardrail(provisioning_decision)["record_hash"],
        "execution_command_manifest_hash": build_inert_execution_command_manifest()["manifest_hash"],
        "frozen": True,
        "provider_login_authorized": False,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "secret_registration_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
        "provider_calls_performed": False,
        "resources_created": False,
    }
    packet["frozen_execution_preparation_packet_hash"] = payload_hash(packet)
    return packet


def build_execution_preparation_decision(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
    preparation_inputs: Mapping[str, Any] | None,
) -> dict[str, Any]:
    auth = build_provisioning_authorization_decision(
        repository_root, provider_inputs or {}, provider_review_owner_decision or {},
        review_inputs or {}, provisioning_decision or {},
    )
    handoff = build_provisioning_authorization_handoff(
        repository_root, provider_inputs, provider_review_owner_decision,
        review_inputs, provisioning_decision,
    )
    validation = validate_execution_preparation_inputs(preparation_inputs, handoff=handoff)
    blockers: list[dict[str, str]] = []
    if not auth.get("provider_inputs_valid"):
        blockers.append({"requirement": "provider_inputs", "status": "provider_inputs_required"})
    if not auth.get("provider_review_owner_approval_valid"):
        blockers.append({"requirement": "provider_review_owner_authorization", "status": "owner_step_up_and_decision_required"})
    if not auth.get("review_inputs_valid"):
        blockers.append({"requirement": "no_call_review_evidence", "status": "completed_review_required"})
    if not auth.get("authorization_valid"):
        blockers.append({"requirement": "provisioning_authorization", "status": "second_owner_authorization_required"})
    for error in validation["errors"]:
        blockers.append({"requirement": error["code"], "status": "required_check_failed"})
    ready = bool(handoff["handoff_ready"] and validation["valid"])
    if ready:
        final_decision = "READY_FOR_SEPARATE_PROVIDER_PROVISIONING_EXECUTION_AUTHORIZATION"
    else:
        final_decision = auth.get("final_decision") or "NO_GO_HOLD_EXECUTION_PREPARATION_REQUIRED"
        if auth.get("authorization_valid") and not validation["valid"]:
            final_decision = "NO_GO_HOLD_NO_CALL_EXECUTION_PREPARATION_EVIDENCE_REQUIRED"
    decision = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "no_call_provider_provisioning_execution_preparation_decision",
        "provider_inputs_valid": bool(auth.get("provider_inputs_valid")),
        "provider_review_owner_approval_valid": bool(auth.get("provider_review_owner_approval_valid")),
        "review_inputs_valid": bool(auth.get("review_inputs_valid")),
        "provisioning_authorization_valid": bool(auth.get("authorization_valid")),
        "preparation_inputs_valid": validation["valid"],
        "ready_for_separate_provider_provisioning_execution_authorization": ready,
        "blocking_requirement_count": len(blockers),
        "blocking_requirements": blockers,
        "provider_login_authorized": False,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "secret_registration_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
        "final_decision": final_decision,
    }
    decision["decision_hash"] = payload_hash(decision)
    return decision


def build_no_call_execution_rehearsal(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
    preparation_inputs: Mapping[str, Any] | None,
) -> dict[str, Any]:
    decision = build_execution_preparation_decision(
        repository_root, provider_inputs, provider_review_owner_decision,
        review_inputs, provisioning_decision, preparation_inputs,
    )
    rehearsal = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "no_call_provider_provisioning_execution_rehearsal",
        "decision_hash": decision["decision_hash"],
        "dry_run_only": True,
        "shell_invoked": False,
        "browser_invoked": False,
        "provider_login_performed": False,
        "provider_cli_invoked": False,
        "provider_api_invoked": False,
        "http_requests_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "secrets_read": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    rehearsal["rehearsal_hash"] = payload_hash(rehearsal)
    return rehearsal


def build_current_execution_preparation_state(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
    preparation_inputs: Mapping[str, Any] | None,
) -> dict[str, Any]:
    handoff = build_provisioning_authorization_handoff(
        repository_root, provider_inputs, provider_review_owner_decision,
        review_inputs, provisioning_decision,
    )
    frozen = freeze_execution_preparation_packet(
        repository_root, provider_inputs, provider_review_owner_decision,
        review_inputs, provisioning_decision, preparation_inputs,
    )
    decision = build_execution_preparation_decision(
        repository_root, provider_inputs, provider_review_owner_decision,
        review_inputs, provisioning_decision, preparation_inputs,
    )
    rehearsal = build_no_call_execution_rehearsal(
        repository_root, provider_inputs, provider_review_owner_decision,
        review_inputs, provisioning_decision, preparation_inputs,
    )
    state = {
        "schema_version": SCHEMA_VERSION,
        "closed_layer": "MANAGED_STAGING_NO_CALL_PROVIDER_PROVISIONING_EXECUTION_PREPARATION",
        "closed_through_step": 80,
        "runtime_target": "web.managed_staging:app",
        "runtime_topology": "single_tower_fronted_managed_python_web_service",
        "authorization_handoff_hash": handoff["handoff_hash"],
        "frozen_execution_preparation_packet_hash": frozen[
            "frozen_execution_preparation_packet_hash"
        ],
        "execution_preparation_decision_hash": decision["decision_hash"],
        "no_call_execution_rehearsal_hash": rehearsal["rehearsal_hash"],
        "provider_inputs_valid": decision["provider_inputs_valid"],
        "provider_review_owner_approval_valid": decision["provider_review_owner_approval_valid"],
        "review_inputs_valid": decision["review_inputs_valid"],
        "provisioning_authorization_valid": decision["provisioning_authorization_valid"],
        "preparation_inputs_valid": decision["preparation_inputs_valid"],
        "ready_for_separate_provider_provisioning_execution_authorization": decision[
            "ready_for_separate_provider_provisioning_execution_authorization"
        ],
        "blocking_requirement_count": decision["blocking_requirement_count"],
        "blocking_requirements": decision["blocking_requirements"],
        "provider_login_authorized": False,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "secret_registration_authorized": False,
        "database_creation_authorized": False,
        "object_storage_creation_authorized": False,
        "dns_changes_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_created_or_read": False,
        "build_performed": False,
        "deployment_performed": False,
        "official_walkthrough_performed": False,
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
        "permanent_main_modified": False,
        "final_decision": decision["final_decision"],
        "next_boundary": "managed_staging_provider_provisioning_execution_authorization",
    }
    state["state_hash"] = payload_hash(state)
    return state


def write_json(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_execution_preparation_worksheets(
    output_directory: str | Path,
    *,
    repository_root: str | Path,
) -> dict[str, str]:
    output = Path(output_directory).resolve()
    root = Path(repository_root).resolve()
    if output == root or root in output.parents:
        raise ValueError("Execution preparation worksheets must be written outside the repository.")
    handoff = {
        "provisioning_authorization_record_hash": "",
        "handoff_hash": "",
        "handoff_ready": False,
    }
    worksheet = output / "tower_ob_no_call_provisioning_execution_preparation.json"
    authorization_placeholder = output / "tower_ob_provider_provisioning_execution_authorization_placeholder.json"
    manifest = output / "worksheet_manifest.json"
    write_json(worksheet, execution_preparation_input_template(handoff))
    write_json(authorization_placeholder, {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "provider_provisioning_execution_authorization_placeholder",
        "decision": "HOLD",
        "frozen_execution_preparation_packet_hash": "",
        "owner_id": "",
        "tower_step_up_receipt_ref": "",
        "provider_login_authorized": False,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "secret_registration_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
        "notes": ["This placeholder is not an authorization.", "A later corridor must bind a new Tower owner step-up decision to the frozen execution-preparation packet."],
    })
    write_json(manifest, {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "execution_preparation_path": str(worksheet),
        "execution_authorization_placeholder_path": str(authorization_placeholder),
        "authorization_handoff_ready": handoff["handoff_ready"],
        "contains_secret_values": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "deployment_performed": False,
    })
    return {
        "execution_preparation_path": str(worksheet),
        "execution_authorization_placeholder_path": str(authorization_placeholder),
        "manifest_path": str(manifest),
    }


def blank_current_inputs(repository_root: str | Path) -> tuple[dict, dict, dict, dict, dict]:
    provider, review_owner, review, provisioning = blank_authorization_inputs(repository_root)
    handoff = build_provisioning_authorization_handoff(
        repository_root, provider, review_owner, review, provisioning
    )
    return provider, review_owner, review, provisioning, execution_preparation_input_template(handoff)
