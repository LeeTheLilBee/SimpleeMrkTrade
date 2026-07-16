"""Offline provider-provisioning review contracts for Tower/Observatory staging.

This layer reviews a previously frozen provider-input and Tower owner-approval
packet without contacting a hosting provider, authenticating to a provider,
creating resources, storing secret values, or authorizing deployment.

A complete review may only advance to a separate provider-provisioning
authorization decision. It never authorizes provider calls by itself.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from tower.tower_ob_managed_staging_provider_authorization import (
    OWNER_APPROVAL_DECISION,
    build_owner_authorization_record,
    build_owner_authorization_challenge,
    freeze_provider_authorization_packet,
    validate_owner_decision,
    validate_provider_inputs,
)
from tower.tower_ob_managed_staging_runtime import (
    MANAGED_START_COMMAND,
    MANAGED_WSGI_TARGET,
    payload_hash,
    resolve_repository_runtime,
)

SCHEMA_VERSION = "simplee.tower_ob.no_call_provisioning_review.v1"

REVIEW_REFERENCE_FIELDS = (
    "provider_documentation_ref",
    "account_access_evidence_ref",
    "region_availability_evidence_ref",
    "cost_review_ref",
    "secret_store_evidence_ref",
    "health_check_evidence_ref",
    "deployment_logging_evidence_ref",
    "access_logging_evidence_ref",
    "rollback_evidence_ref",
    "reviewed_by",
    "reviewed_at",
)

REQUIRED_REVIEW_ATTESTATIONS = (
    "provider_documentation_reviewed",
    "account_team_access_confirmed",
    "region_availability_reviewed",
    "staging_cost_boundary_reviewed",
    "encrypted_secret_store_reviewed",
    "health_check_support_reviewed",
    "deployment_logs_reviewed",
    "access_logs_reviewed",
    "manual_deployment_control_reviewed",
    "rollback_support_reviewed",
    "staging_only_scope_confirmed",
    "tower_only_ingress_confirmed",
    "observatory_separate_service_not_required",
    "no_provider_calls_performed",
)

_SENSITIVE_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
    re.compile(r"\b(?:api[_-]?key|access[_-]?token|token|secret|password)\s*[:=]\s*\S+", re.I),
    re.compile(r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?)://[^/\s]+:[^@\s]+@", re.I),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
)
_SAFE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+ #(),-]{1,299}$")
_ISO_UTC = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return _text(value).lower() in {
        "1", "true", "yes", "on", "enabled", "attested",
    }


def _fingerprint(value: Any) -> str | None:
    normalized = _text(value)
    if not normalized:
        return None
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _contains_sensitive_material(value: Any) -> bool:
    rendered = json.dumps(value, sort_keys=True, default=str)
    return any(pattern.search(rendered) for pattern in _SENSITIVE_PATTERNS)


def build_authorization_handoff(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    owner_decision: Mapping[str, Any] | None,
) -> dict[str, Any]:
    runtime = resolve_repository_runtime(repository_root)
    provider_validation = validate_provider_inputs(provider_inputs)
    frozen = freeze_provider_authorization_packet(
        repository_root,
        provider_inputs,
    )
    challenge = build_owner_authorization_challenge(
        packet_hash=frozen["frozen_packet_hash"],
    )
    owner_validation = validate_owner_decision(
        owner_decision,
        challenge=challenge,
    )
    authorization = build_owner_authorization_record(
        repository_root,
        provider_inputs,
        owner_decision,
    )
    ready = bool(
        runtime["resolved"]
        and provider_validation["valid"]
        and owner_validation["approval_valid"]
        and authorization["ready_for_separate_no_call_provisioning_review"]
    )
    handoff = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "managed_staging_no_call_review_authorization_handoff",
        "runtime_resolved": runtime["resolved"],
        "runtime_contract_hash": runtime["contract_hash"],
        "frozen_provider_packet_hash": frozen["frozen_packet_hash"],
        "owner_authorization_record_hash": authorization["record_hash"],
        "owner_challenge_id": challenge["challenge_id"],
        "provider_inputs_valid": provider_validation["valid"],
        "owner_approval_valid": owner_validation["approval_valid"],
        "owner_decision_expected": OWNER_APPROVAL_DECISION,
        "ready_for_no_call_review": ready,
        "raw_provider_values_recorded": False,
        "raw_owner_values_recorded": False,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "secret_creation_authorized": False,
        "deployment_authorized": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_created": False,
        "deployment_performed": False,
    }
    handoff["handoff_hash"] = payload_hash(handoff)
    return handoff


def no_call_review_input_template(
    handoff: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source = dict(handoff or {})
    template = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "managed_staging_no_call_provisioning_review_inputs",
        "frozen_provider_packet_hash": _text(
            source.get("frozen_provider_packet_hash")
        ),
        "owner_authorization_record_hash": _text(
            source.get("owner_authorization_record_hash")
        ),
        "provider_documentation_ref": "",
        "account_access_evidence_ref": "",
        "region_availability_evidence_ref": "",
        "cost_review_ref": "",
        "secret_store_evidence_ref": "",
        "health_check_evidence_ref": "",
        "deployment_logging_evidence_ref": "",
        "access_logging_evidence_ref": "",
        "rollback_evidence_ref": "",
        "reviewed_by": "",
        "reviewed_at": "",
        "attestations": {
            name: False for name in REQUIRED_REVIEW_ATTESTATIONS
        },
        "notes": [
            "Use non-secret references to provider documentation or screenshots only.",
            "Do not include passwords, tokens, API keys, cookies, private keys, or connection strings.",
            "Do not log into or call a provider from this utility.",
            "Completing this review does not authorize provider calls, resource creation, secrets, or deployment.",
        ],
    }
    template["template_hash"] = payload_hash(template)
    return template


def validate_no_call_review_inputs(
    payload: Mapping[str, Any] | None,
    *,
    handoff: Mapping[str, Any],
) -> dict[str, Any]:
    source = dict(payload or {})
    errors: list[dict[str, str]] = []

    expected_packet_hash = _text(
        handoff.get("frozen_provider_packet_hash")
    )
    expected_owner_hash = _text(
        handoff.get("owner_authorization_record_hash")
    )

    if _text(source.get("frozen_provider_packet_hash")) != expected_packet_hash:
        errors.append({
            "field": "frozen_provider_packet_hash",
            "code": "authorization_packet_hash_mismatch",
        })
    if _text(source.get("owner_authorization_record_hash")) != expected_owner_hash:
        errors.append({
            "field": "owner_authorization_record_hash",
            "code": "owner_authorization_hash_mismatch",
        })

    for field in REVIEW_REFERENCE_FIELDS:
        if not _text(source.get(field)):
            errors.append({"field": field, "code": "required"})

    for field in REVIEW_REFERENCE_FIELDS:
        if field == "reviewed_at":
            continue
        value = _text(source.get(field))
        if value and not _SAFE_REF.fullmatch(value):
            errors.append({
                "field": field,
                "code": "invalid_reference_format",
            })

    if _text(source.get("reviewed_at")) and not _ISO_UTC.fullmatch(
        _text(source.get("reviewed_at"))
    ):
        errors.append({
            "field": "reviewed_at",
            "code": "must_be_utc_iso_timestamp",
        })

    attestations = dict(source.get("attestations") or {})
    attestation_checks = {
        name: _bool(attestations.get(name))
        for name in REQUIRED_REVIEW_ATTESTATIONS
    }
    for name, valid in attestation_checks.items():
        if not valid:
            errors.append({
                "field": f"attestations.{name}",
                "code": "attestation_required",
            })

    sensitive_material_detected = _contains_sensitive_material(source)
    if sensitive_material_detected:
        errors.append({
            "field": "payload",
            "code": "sensitive_material_prohibited",
        })

    valid = bool(
        handoff.get("ready_for_no_call_review")
        and not errors
        and all(attestation_checks.values())
    )
    report = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "managed_staging_no_call_review_validation",
        "valid": valid,
        "authorization_handoff_ready": bool(
            handoff.get("ready_for_no_call_review")
        ),
        "error_count": len(errors),
        "errors": errors,
        "attestation_checks": attestation_checks,
        "required_attestation_count": len(REQUIRED_REVIEW_ATTESTATIONS),
        "completed_attestation_count": sum(
            1 for value in attestation_checks.values() if value
        ),
        "sensitive_material_detected": sensitive_material_detected,
        "raw_values_returned": False,
        "reference_fingerprints": {
            field + "_sha256": _fingerprint(source.get(field))
            for field in REVIEW_REFERENCE_FIELDS
        },
    }
    report["report_hash"] = payload_hash(report)
    return report


def build_provider_documentation_review(
    review_inputs: Mapping[str, Any] | None,
    *,
    handoff: Mapping[str, Any],
) -> dict[str, Any]:
    validation = validate_no_call_review_inputs(
        review_inputs,
        handoff=handoff,
    )
    fingerprints = validation["reference_fingerprints"]
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "managed_staging_provider_documentation_review",
        "provider_documentation_ref_sha256": fingerprints[
            "provider_documentation_ref_sha256"
        ],
        "secret_store_evidence_ref_sha256": fingerprints[
            "secret_store_evidence_ref_sha256"
        ],
        "health_check_evidence_ref_sha256": fingerprints[
            "health_check_evidence_ref_sha256"
        ],
        "deployment_logging_evidence_ref_sha256": fingerprints[
            "deployment_logging_evidence_ref_sha256"
        ],
        "access_logging_evidence_ref_sha256": fingerprints[
            "access_logging_evidence_ref_sha256"
        ],
        "rollback_evidence_ref_sha256": fingerprints[
            "rollback_evidence_ref_sha256"
        ],
        "documentation_review_complete": validation["valid"],
        "claims_verified_by_provider_api": False,
        "provider_calls_authorized": False,
        "provider_calls_performed": False,
        "raw_documentation_refs_recorded": False,
    }
    record["record_hash"] = payload_hash(record)
    return record


def build_account_region_cost_review(
    review_inputs: Mapping[str, Any] | None,
    *,
    handoff: Mapping[str, Any],
) -> dict[str, Any]:
    validation = validate_no_call_review_inputs(
        review_inputs,
        handoff=handoff,
    )
    fingerprints = validation["reference_fingerprints"]
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "managed_staging_account_region_cost_review",
        "account_access_evidence_ref_sha256": fingerprints[
            "account_access_evidence_ref_sha256"
        ],
        "region_availability_evidence_ref_sha256": fingerprints[
            "region_availability_evidence_ref_sha256"
        ],
        "cost_review_ref_sha256": fingerprints["cost_review_ref_sha256"],
        "reviewed_by_sha256": fingerprints["reviewed_by_sha256"],
        "reviewed_at_sha256": fingerprints["reviewed_at_sha256"],
        "review_complete": validation["valid"],
        "budget_amount_recorded": False,
        "billing_credentials_recorded": False,
        "automatic_spend_authorized": False,
        "automatic_scale_up_authorized": False,
        "production_billing_reuse_authorized": False,
        "provider_calls_authorized": False,
        "resources_created": False,
    }
    record["record_hash"] = payload_hash(record)
    return record


def build_inert_web_service_manifest(
    handoff: Mapping[str, Any],
) -> dict[str, Any]:
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "managed_staging_inert_web_service",
        "environment": "staging",
        "service_count": 1,
        "service_role": "tower_front_door_and_observatory_runtime",
        "runtime_target": MANAGED_WSGI_TARGET,
        "start_command": MANAGED_START_COMMAND,
        "source_branch": "tower-ob-integration-dev",
        "health_check_path": "/tower/healthz",
        "public_ingress_owner": "tower",
        "observatory_public_ingress_allowed": False,
        "separate_observatory_service_required": False,
        "build_command": None,
        "build_command_status": "provider_specific_review_required",
        "authorization_handoff_hash": handoff.get("handoff_hash"),
        "manifest_only": True,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "deployment_authorized": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "deployment_performed": False,
    }
    manifest["manifest_hash"] = payload_hash(manifest)
    return manifest


def build_environment_secret_reference_manifest() -> dict[str, Any]:
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "managed_staging_environment_secret_references",
        "non_secret_environment_names": [
            "SIMPLEE_DEPLOYMENT_ENVIRONMENT",
            "TOWER_HOSTED_MODE",
            "SIMPLEE_MANAGED_HOST_PROVIDER",
            "SIMPLEE_MANAGED_HOST_ACCOUNT_OR_TEAM",
            "SIMPLEE_STAGING_DEPLOYMENT_REGION",
            "SIMPLEE_PROVIDER_OWNER_APPROVAL",
            "TOWER_OWNER_USERNAME",
            "TOWER_OWNER_ID",
            "TOWER_STEP_UP_MINUTES",
        ],
        "secret_environment_names": [
            "TOWER_SESSION_SECRET",
            "TOWER_OWNER_PASSWORD_HASH",
        ],
        "future_external_secret_references": [
            "database_connection_reference",
            "object_storage_access_reference",
        ],
        "raw_secret_values_recorded": False,
        "secret_generation_in_this_layer": False,
        "secret_readback_in_this_layer": False,
        "production_secret_reuse_authorized": False,
        "plaintext_owner_password_allowed": False,
        "provider_secret_store_required": True,
        "provider_calls_authorized": False,
        "secrets_created": False,
        "secrets_read": False,
    }
    manifest["manifest_hash"] = payload_hash(manifest)
    return manifest


def build_external_data_service_boundary() -> dict[str, Any]:
    boundary = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "managed_staging_external_data_service_boundary",
        "web_service_database_dependency_confirmed": False,
        "database_requirement_status": "separate_review_required",
        "database_resource_selected": False,
        "database_resource_created": False,
        "object_storage_requirement_status": "separate_review_required",
        "object_storage_resource_selected": False,
        "object_storage_resource_created": False,
        "vault_direct_upload_allowed": False,
        "vault_raw_object_url_exposure_allowed": False,
        "production_data_reuse_authorized": False,
        "staging_data_migration_authorized": False,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "resources_created": False,
    }
    boundary["boundary_hash"] = payload_hash(boundary)
    return boundary


def build_operational_safeguard_manifest() -> dict[str, Any]:
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "managed_staging_operational_safeguards",
        "required_checks": [
            "health endpoint responds only after managed environment validation",
            "deployment logs available to authorized operators",
            "access logs available without exposing secret values",
            "manual deployment control enabled",
            "rollback target retained",
            "incident stop and owner hold available",
            "Tower-only ingress preserved",
            "Observatory routes remain behind Tower authentication and step-up",
        ],
        "official_walkthrough_required_after_separate_deployment": True,
        "rollback_execution_authorized": False,
        "incident_execution_authorized": False,
        "provider_calls_authorized": False,
        "deployment_authorized": False,
        "official_walkthrough_authorized": False,
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
    }
    manifest["manifest_hash"] = payload_hash(manifest)
    return manifest


def freeze_no_call_provisioning_review_packet(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
) -> dict[str, Any]:
    handoff = build_authorization_handoff(
        repository_root,
        provider_inputs,
        owner_decision,
    )
    validation = validate_no_call_review_inputs(
        review_inputs,
        handoff=handoff,
    )
    documentation = build_provider_documentation_review(
        review_inputs,
        handoff=handoff,
    )
    access_cost = build_account_region_cost_review(
        review_inputs,
        handoff=handoff,
    )
    service = build_inert_web_service_manifest(handoff)
    environment = build_environment_secret_reference_manifest()
    data_boundary = build_external_data_service_boundary()
    safeguards = build_operational_safeguard_manifest()

    packet = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "managed_staging_frozen_no_call_provisioning_review",
        "authorization_handoff_hash": handoff["handoff_hash"],
        "frozen_provider_packet_hash": handoff[
            "frozen_provider_packet_hash"
        ],
        "owner_authorization_record_hash": handoff[
            "owner_authorization_record_hash"
        ],
        "authorization_handoff_ready": handoff["ready_for_no_call_review"],
        "review_inputs_valid": validation["valid"],
        "review_validation_report_hash": validation["report_hash"],
        "provider_documentation_review_hash": documentation["record_hash"],
        "account_region_cost_review_hash": access_cost["record_hash"],
        "web_service_manifest_hash": service["manifest_hash"],
        "environment_secret_manifest_hash": environment["manifest_hash"],
        "external_data_boundary_hash": data_boundary["boundary_hash"],
        "operational_safeguard_manifest_hash": safeguards["manifest_hash"],
        "raw_provider_values_recorded": False,
        "raw_owner_values_recorded": False,
        "raw_review_values_recorded": False,
        "raw_secrets_recorded": False,
        "frozen": True,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "secret_creation_authorized": False,
        "deployment_authorized": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_created": False,
        "deployment_performed": False,
    }
    packet["frozen_review_packet_hash"] = payload_hash(packet)
    return packet


def build_no_call_provisioning_review_decision(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
) -> dict[str, Any]:
    handoff = build_authorization_handoff(
        repository_root,
        provider_inputs,
        owner_decision,
    )
    packet = freeze_no_call_provisioning_review_packet(
        repository_root,
        provider_inputs,
        owner_decision,
        review_inputs,
    )

    if not handoff["provider_inputs_valid"]:
        final_decision = (
            "NO_GO_HOLD_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION_REQUIRED"
        )
    elif not handoff["owner_approval_valid"]:
        final_decision = "NO_GO_HOLD_OWNER_AUTHORIZATION_REQUIRED"
    elif not packet["review_inputs_valid"]:
        final_decision = (
            "NO_GO_HOLD_NO_CALL_PROVISIONING_REVIEW_EVIDENCE_REQUIRED"
        )
    else:
        final_decision = (
            "READY_FOR_SEPARATE_PROVIDER_PROVISIONING_AUTHORIZATION_DECISION"
        )

    ready = bool(
        handoff["ready_for_no_call_review"]
        and packet["review_inputs_valid"]
    )
    decision = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "managed_staging_no_call_provisioning_review_decision",
        "authorization_handoff_hash": handoff["handoff_hash"],
        "frozen_review_packet_hash": packet["frozen_review_packet_hash"],
        "review_complete": ready,
        "ready_for_separate_provider_provisioning_authorization_decision": ready,
        "final_decision": final_decision,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "secret_creation_authorized": False,
        "deployment_authorized": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_created": False,
        "deployment_performed": False,
        "official_walkthrough_performed": False,
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
    }
    decision["decision_hash"] = payload_hash(decision)
    return decision


def build_no_call_console_dry_run_plan(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
) -> dict[str, Any]:
    decision = build_no_call_provisioning_review_decision(
        repository_root,
        provider_inputs,
        owner_decision,
        review_inputs,
    )
    plan = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": "managed_staging_provider_console_no_call_dry_run",
        "review_decision_hash": decision["decision_hash"],
        "dry_run_steps": [
            "open provider documentation outside this utility",
            "compare managed Python service capability to inert manifest",
            "compare account/team access to fingerprinted evidence reference",
            "compare region availability and staging cost boundary",
            "compare encrypted secret-store capability to reference manifest",
            "compare health, logging, manual deploy, and rollback capabilities",
            "close provider console without creating or changing resources",
            "request a separate Tower owner provisioning authorization decision",
        ],
        "prohibited_actions": [
            "provider API call",
            "provider CLI login",
            "provider resource creation",
            "secret creation or readback",
            "database creation",
            "object storage creation",
            "web service deployment",
            "DNS or public-route change",
            "official Observatory walkthrough",
            "production Manual Live",
            "broker submission",
            "real capital movement",
            "direct Vault upload",
            "Live Auto unlock",
        ],
        "dry_run_only": True,
        "shell_invoked": False,
        "provider_api_invoked": False,
        "provider_cli_invoked": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_created": False,
        "deployment_performed": False,
        "final_decision": decision["final_decision"],
    }
    plan["plan_hash"] = payload_hash(plan)
    return plan


def build_current_no_call_provisioning_review_state(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None = None,
    owner_decision: Mapping[str, Any] | None = None,
    review_inputs: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    handoff = build_authorization_handoff(
        repository_root,
        provider_inputs,
        owner_decision,
    )
    review_validation = validate_no_call_review_inputs(
        review_inputs,
        handoff=handoff,
    )
    packet = freeze_no_call_provisioning_review_packet(
        repository_root,
        provider_inputs,
        owner_decision,
        review_inputs,
    )
    decision = build_no_call_provisioning_review_decision(
        repository_root,
        provider_inputs,
        owner_decision,
        review_inputs,
    )
    dry_run = build_no_call_console_dry_run_plan(
        repository_root,
        provider_inputs,
        owner_decision,
        review_inputs,
    )

    blockers: list[dict[str, str]] = []
    if not handoff["provider_inputs_valid"]:
        blockers.append({
            "requirement": "provider_inputs",
            "status": "provider_inputs_required",
        })
    if not handoff["owner_approval_valid"]:
        blockers.append({
            "requirement": "tower_owner_authorization",
            "status": "owner_step_up_and_decision_required",
        })
    for error in review_validation["errors"]:
        blockers.append({
            "requirement": error["field"],
            "status": error["code"],
        })

    state = {
        "schema_version": SCHEMA_VERSION,
        "closed_layer": "MANAGED_STAGING_NO_CALL_PROVIDER_PROVISIONING_REVIEW",
        "closed_through_step": 60,
        "runtime_target": MANAGED_WSGI_TARGET,
        "runtime_topology": "single_tower_fronted_managed_python_web_service",
        "authorization_handoff_hash": handoff["handoff_hash"],
        "frozen_review_packet_hash": packet["frozen_review_packet_hash"],
        "review_decision_hash": decision["decision_hash"],
        "no_call_dry_run_plan_hash": dry_run["plan_hash"],
        "provider_inputs_valid": handoff["provider_inputs_valid"],
        "owner_approval_valid": handoff["owner_approval_valid"],
        "review_inputs_valid": packet["review_inputs_valid"],
        "ready_for_separate_provider_provisioning_authorization_decision": decision[
            "ready_for_separate_provider_provisioning_authorization_decision"
        ],
        "blocking_requirements": blockers,
        "blocking_requirement_count": len(blockers),
        "raw_provider_values_recorded": False,
        "raw_owner_values_recorded": False,
        "raw_review_values_recorded": False,
        "raw_secrets_recorded": False,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "secret_creation_authorized": False,
        "deployment_authorized": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_created": False,
        "deployment_performed": False,
        "official_walkthrough_performed": False,
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
        "permanent_main_modified": False,
        "final_decision": decision["final_decision"],
        "next_boundary": (
            "managed_staging_provider_provisioning_authorization_decision"
        ),
    }
    state["state_hash"] = payload_hash(state)
    return state


def write_json(path: str | Path, payload: Mapping[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target


def write_no_call_review_worksheets(
    output_directory: str | Path,
    *,
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None = None,
    owner_decision: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    root = Path(output_directory)
    root.mkdir(parents=True, exist_ok=True)
    handoff = build_authorization_handoff(
        repository_root,
        provider_inputs,
        owner_decision,
    )
    review = no_call_review_input_template(handoff)
    review_path = write_json(
        root / "tower_ob_no_call_provisioning_review.json",
        review,
    )
    authorization_placeholder = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "provider_provisioning_authorization_placeholder",
        "decision": "HOLD",
        "frozen_review_packet_hash": "",
        "owner_id": "",
        "tower_step_up_receipt_ref": "",
        "decided_at": "",
        "notes": [
            "This placeholder is not an authorization.",
            "A later corridor must bind a separate Tower owner decision to a completed frozen review packet.",
        ],
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "deployment_authorized": False,
    }
    authorization_placeholder["template_hash"] = payload_hash(
        authorization_placeholder
    )
    auth_path = write_json(
        root / "tower_ob_provider_provisioning_authorization_placeholder.json",
        authorization_placeholder,
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "review_input_path": str(review_path),
        "authorization_placeholder_path": str(auth_path),
        "authorization_handoff_ready": handoff["ready_for_no_call_review"],
        "contains_secret_values": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "deployment_performed": False,
    }
    manifest_path = write_json(
        root / "worksheet_manifest.json",
        manifest,
    )
    return {
        "review_input_path": str(review_path),
        "authorization_placeholder_path": str(auth_path),
        "manifest_path": str(manifest_path),
    }


__all__ = [
    "REQUIRED_REVIEW_ATTESTATIONS",
    "REVIEW_REFERENCE_FIELDS",
    "build_account_region_cost_review",
    "build_authorization_handoff",
    "build_current_no_call_provisioning_review_state",
    "build_environment_secret_reference_manifest",
    "build_external_data_service_boundary",
    "build_inert_web_service_manifest",
    "build_no_call_console_dry_run_plan",
    "build_no_call_provisioning_review_decision",
    "build_operational_safeguard_manifest",
    "build_provider_documentation_review",
    "freeze_no_call_provisioning_review_packet",
    "no_call_review_input_template",
    "validate_no_call_review_inputs",
    "write_no_call_review_worksheets",
]
