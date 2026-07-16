"""Provider-input and owner-authorization contracts for Tower/Observatory staging.

This module prepares, validates, fingerprints, freezes, and reviews managed
staging provider inputs without calling a hosting provider, creating resources,
storing raw secrets, or authorizing deployment.

The authorization produced here is intentionally narrow: even a complete and
owner-approved packet may only advance to a separate no-call provisioning
review. Provider calls and resource creation remain prohibited.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from tower.tower_ob_managed_staging_runtime import (
    MANAGED_START_COMMAND,
    MANAGED_WSGI_TARGET,
    build_provider_authorization_packet,
    canonical_json,
    payload_hash,
    provider_capability_resolution,
    resolve_repository_runtime,
)

SCHEMA_VERSION = "simplee.tower_ob.provider_authorization.v1"

OWNER_APPROVAL_DECISION = "APPROVE_FOR_PROVISIONING_REVIEW"
OWNER_HOLD_DECISION = "HOLD"
OWNER_REJECT_DECISION = "REJECT"

ALLOWED_OWNER_DECISIONS = frozenset({
    OWNER_APPROVAL_DECISION,
    OWNER_HOLD_DECISION,
    OWNER_REJECT_DECISION,
})

REQUIRED_CAPABILITIES = (
    "managed_python_web_service",
    "provider_supplied_port_binding",
    "https_termination",
    "encrypted_environment_secret_store",
    "health_checks",
    "deployment_logs",
    "access_logs",
    "manual_deployment_control",
    "rollback_support",
)

OPTIONAL_EXTERNAL_SERVICE_CAPABILITIES = (
    "managed_postgresql_or_compatible_external_postgresql",
    "private_s3_compatible_object_storage",
)

PROVIDER_INPUT_FIELDS = (
    "provider_slug",
    "account_or_team_ref",
    "deployment_region",
    "billing_owner_ref",
    "service_name",
    "repository_ref",
    "source_branch",
)

OWNER_DECISION_FIELDS = (
    "decision",
    "owner_id",
    "tower_step_up_receipt_ref",
    "challenge_id",
    "challenge_phrase_confirmation",
    "decided_at",
)

_SAFE_SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{1,79}$")
_SAFE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+ -]{1,199}$")
_SAFE_REGION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/ -]{1,99}$")
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


def _safe_filename(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "_", _text(value))
    return normalized.strip("._") or "simplee_provider_authorization"


def provider_input_template() -> dict[str, Any]:
    """Return a blank, non-secret worksheet for provider selection inputs."""

    template = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "managed_staging_provider_inputs",
        "provider_slug": "",
        "account_or_team_ref": "",
        "deployment_region": "",
        "billing_owner_ref": "",
        "service_name": "simplee-tower-ob-staging",
        "repository_ref": "LeeTheLilBee/SimpleeMrkTrade",
        "source_branch": "tower-ob-integration-dev",
        "environment_name": "staging",
        "runtime_target": MANAGED_WSGI_TARGET,
        "start_command": MANAGED_START_COMMAND,
        "health_check_path": "/tower/healthz",
        "capability_attestations": {
            name: False for name in REQUIRED_CAPABILITIES
        },
        "external_service_capability_attestations": {
            name: False
            for name in OPTIONAL_EXTERNAL_SERVICE_CAPABILITIES
        },
        "notes": [
            "Do not place passwords, API keys, tokens, secret values, or full connection strings in this file.",
            "Use provider-visible labels or non-secret references only.",
            "Completing this worksheet does not authorize provider calls or deployment.",
        ],
    }
    template["template_hash"] = payload_hash(template)
    return template


def owner_decision_template(
    frozen_packet: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    packet = dict(frozen_packet or {})
    challenge_ready = bool(
        packet.get("provider_inputs_valid")
        and _text(packet.get("frozen_packet_hash"))
    )
    challenge = (
        build_owner_authorization_challenge(
            packet_hash=_text(packet.get("frozen_packet_hash")),
        )
        if challenge_ready
        else {}
    )
    template = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "managed_staging_owner_authorization_decision",
        "decision": OWNER_HOLD_DECISION,
        "owner_id": "",
        "tower_step_up_receipt_ref": "",
        "challenge_ready": challenge_ready,
        "challenge_id": _text(challenge.get("challenge_id")),
        "challenge_phrase_confirmation": "",
        "decided_at": "",
        "allowed_decisions": sorted(ALLOWED_OWNER_DECISIONS),
        "expected_challenge_phrase": _text(
            challenge.get("challenge_phrase")
        ),
        "notes": [
            "Complete and validate the provider-input worksheet before generating the bound owner-decision worksheet.",
            "Use an actual Tower owner step-up receipt reference before approval.",
            "Do not put credentials, passwords, session cookies, or tokens in this file.",
            "Approval only opens a separate no-call provisioning review.",
        ],
    }
    template["template_hash"] = payload_hash(template)
    return template


def validate_provider_inputs(
    payload: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(payload or {})
    errors: list[dict[str, str]] = []

    for field in PROVIDER_INPUT_FIELDS:
        if not _text(source.get(field)):
            errors.append({
                "field": field,
                "code": "required",
            })

    provider_slug = _text(source.get("provider_slug")).lower()
    if provider_slug and not _SAFE_SLUG.fullmatch(provider_slug):
        errors.append({
            "field": "provider_slug",
            "code": "invalid_provider_slug",
        })

    for field in (
        "account_or_team_ref",
        "billing_owner_ref",
        "service_name",
        "repository_ref",
        "source_branch",
    ):
        value = _text(source.get(field))
        if value and not _SAFE_REF.fullmatch(value):
            errors.append({
                "field": field,
                "code": "invalid_reference_format",
            })

    region = _text(source.get("deployment_region"))
    if region and not _SAFE_REGION.fullmatch(region):
        errors.append({
            "field": "deployment_region",
            "code": "invalid_region_format",
        })

    fixed_checks = {
        "environment_name_is_staging": (
            _text(source.get("environment_name")).lower() == "staging"
        ),
        "runtime_target_matches": (
            _text(source.get("runtime_target")) == MANAGED_WSGI_TARGET
        ),
        "start_command_matches": (
            _text(source.get("start_command")) == MANAGED_START_COMMAND
        ),
        "health_check_path_matches": (
            _text(source.get("health_check_path")) == "/tower/healthz"
        ),
        "source_branch_is_integration_branch": (
            _text(source.get("source_branch"))
            == "tower-ob-integration-dev"
        ),
    }

    for check_name, passed in fixed_checks.items():
        if not passed:
            errors.append({
                "field": check_name,
                "code": "fixed_contract_mismatch",
            })

    attestations = source.get("capability_attestations")
    if not isinstance(attestations, Mapping):
        attestations = {}
        errors.append({
            "field": "capability_attestations",
            "code": "mapping_required",
        })

    capability_checks = {
        name: _bool(attestations.get(name))
        for name in REQUIRED_CAPABILITIES
    }
    for name, passed in capability_checks.items():
        if not passed:
            errors.append({
                "field": f"capability_attestations.{name}",
                "code": "required_capability_not_attested",
            })

    prohibited_markers = (
        "password=",
        "token=",
        "secret=",
        "api_key=",
        "apikey=",
        "authorization:",
        "postgresql://",
        "postgres://",
        "mongodb://",
        "redis://",
        "-----begin private key-----",
    )
    sensitive_material_detected = False
    for value in source.values():
        if isinstance(value, (dict, list, tuple, set)):
            rendered = canonical_json(value).lower()
        else:
            rendered = _text(value).lower()
        if any(marker in rendered for marker in prohibited_markers):
            sensitive_material_detected = True
            break

    if sensitive_material_detected:
        errors.append({
            "field": "payload",
            "code": "possible_sensitive_material_detected",
        })

    report = {
        "schema_version": SCHEMA_VERSION,
        "valid": not errors,
        "error_count": len(errors),
        "errors": errors,
        "fixed_contract_checks": fixed_checks,
        "capability_checks": capability_checks,
        "required_capability_count": len(REQUIRED_CAPABILITIES),
        "attested_required_capability_count": sum(
            1 for value in capability_checks.values() if value
        ),
        "sensitive_material_detected": sensitive_material_detected,
        "raw_values_returned": False,
        "input_fingerprints": {
            field + "_sha256": _fingerprint(source.get(field))
            for field in PROVIDER_INPUT_FIELDS
        },
    }
    report["report_hash"] = payload_hash(report)
    return report


def build_provider_selection_record(
    payload: Mapping[str, Any] | None,
) -> dict[str, Any]:
    validation = validate_provider_inputs(payload)
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "managed_staging_provider_selection",
        "selection_valid": validation["valid"],
        "validation_report_hash": validation["report_hash"],
        "provider_slug_sha256": validation["input_fingerprints"][
            "provider_slug_sha256"
        ],
        "service_name_sha256": validation["input_fingerprints"][
            "service_name_sha256"
        ],
        "repository_ref_sha256": validation["input_fingerprints"][
            "repository_ref_sha256"
        ],
        "source_branch_sha256": validation["input_fingerprints"][
            "source_branch_sha256"
        ],
        "runtime_target": MANAGED_WSGI_TARGET,
        "start_command": MANAGED_START_COMMAND,
        "health_check_path": "/tower/healthz",
        "topology": "single_tower_fronted_managed_python_web_service",
        "observatory_separate_service": False,
        "raw_provider_name_recorded": False,
        "raw_account_or_team_recorded": False,
        "provider_calls_authorized": False,
        "resources_created": False,
    }
    record["record_hash"] = payload_hash(record)
    return record


def build_capability_attestation_record(
    payload: Mapping[str, Any] | None,
) -> dict[str, Any]:
    validation = validate_provider_inputs(payload)
    upstream = provider_capability_resolution()
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "managed_staging_provider_capability_attestation",
        "required_capabilities": list(REQUIRED_CAPABILITIES),
        "capability_checks": validation["capability_checks"],
        "all_required_capabilities_attested": all(
            validation["capability_checks"].values()
        ),
        "upstream_capability_resolution_hash": upstream["resolution_hash"],
        "composite_stack_allowed": True,
        "provider_calls_authorized": False,
        "claims_verified_against_provider_api": False,
    }
    record["record_hash"] = payload_hash(record)
    return record


def build_account_team_binding(
    payload: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(payload or {})
    account_ref = _text(source.get("account_or_team_ref"))
    repository_ref = _text(source.get("repository_ref"))
    billing_owner_ref = _text(source.get("billing_owner_ref"))
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "managed_staging_account_team_binding",
        "account_or_team_present": bool(account_ref),
        "account_or_team_ref_sha256": _fingerprint(account_ref),
        "repository_ref_sha256": _fingerprint(repository_ref),
        "billing_owner_ref_sha256": _fingerprint(billing_owner_ref),
        "binding_complete": all((account_ref, repository_ref, billing_owner_ref)),
        "raw_account_or_team_recorded": False,
        "raw_billing_owner_recorded": False,
        "cross_environment_account_reuse_authorized": False,
        "production_resource_binding_authorized": False,
    }
    record["record_hash"] = payload_hash(record)
    return record


def build_region_binding(
    payload: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(payload or {})
    region = _text(source.get("deployment_region"))
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "managed_staging_region_binding",
        "deployment_region_present": bool(region),
        "deployment_region_sha256": _fingerprint(region),
        "environment_name": "staging",
        "region_verified_against_provider": False,
        "data_residency_legal_review_completed": False,
        "provider_region_availability_verified": False,
        "region_binding_ready_for_review": bool(region),
        "provider_calls_authorized": False,
    }
    record["record_hash"] = payload_hash(record)
    return record


def build_billing_boundary(
    payload: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(payload or {})
    billing_ref = _text(source.get("billing_owner_ref"))
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "managed_staging_billing_boundary",
        "billing_owner_reference_present": bool(billing_ref),
        "billing_owner_ref_sha256": _fingerprint(billing_ref),
        "staging_budget_limit_recorded": False,
        "automatic_scale_up_authorized": False,
        "automatic_paid_addons_authorized": False,
        "production_billing_reuse_authorized": False,
        "owner_cost_review_required_before_resource_creation": True,
        "resource_creation_authorized": False,
    }
    record["record_hash"] = payload_hash(record)
    return record


def build_secret_custody_plan() -> dict[str, Any]:
    plan = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "managed_staging_secret_custody_plan",
        "required_secret_references": [
            "TOWER_SESSION_SECRET",
            "TOWER_OWNER_PASSWORD_HASH",
            "database_connection_reference",
            "object_storage_access_reference",
        ],
        "non_secret_environment_references": [
            "SIMPLEE_DEPLOYMENT_ENVIRONMENT",
            "TOWER_HOSTED_MODE",
            "SIMPLEE_MANAGED_HOST_PROVIDER",
            "SIMPLEE_MANAGED_HOST_ACCOUNT_OR_TEAM",
            "SIMPLEE_STAGING_DEPLOYMENT_REGION",
            "TOWER_OWNER_USERNAME",
            "TOWER_OWNER_ID",
        ],
        "rules": {
            "provider_secret_store_required": True,
            "raw_secret_values_in_git": False,
            "raw_secret_values_in_checkpoint_evidence": False,
            "production_secret_reuse_in_staging": False,
            "plaintext_owner_password_allowed": False,
            "secret_creation_in_this_layer": False,
            "secret_readback_in_this_layer": False,
        },
        "secrets_created": False,
        "secrets_read": False,
        "provider_calls_authorized": False,
    }
    plan["plan_hash"] = payload_hash(plan)
    return plan


def build_owner_authorization_challenge(
    *,
    packet_hash: str | None,
) -> dict[str, Any]:
    normalized_hash = _text(packet_hash) or ("0" * 64)
    challenge_id = hashlib.sha256(
        (
            "simplee:tower-ob:managed-staging:provider-review:"
            + normalized_hash
        ).encode("utf-8")
    ).hexdigest()[:24]
    phrase = (
        "AUTHORIZE TOWER OB STAGING PROVIDER REVIEW "
        + challenge_id.upper()
    )
    challenge = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "managed_staging_owner_authorization_challenge",
        "challenge_id": challenge_id,
        "challenge_phrase": phrase,
        "frozen_packet_hash": normalized_hash,
        "required_owner_decision": OWNER_APPROVAL_DECISION,
        "tower_owner_session_required": True,
        "tower_step_up_receipt_required": True,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "deployment_authorized": False,
    }
    challenge["challenge_hash"] = payload_hash(challenge)
    return challenge


def validate_owner_decision(
    decision: Mapping[str, Any] | None,
    *,
    challenge: Mapping[str, Any],
) -> dict[str, Any]:
    source = dict(decision or {})
    normalized_decision = _text(source.get("decision")).upper() or OWNER_HOLD_DECISION
    expected_challenge_id = _text(challenge.get("challenge_id"))
    expected_phrase = _text(challenge.get("challenge_phrase"))

    checks = {
        "decision_allowed": normalized_decision in ALLOWED_OWNER_DECISIONS,
        "owner_id_present": bool(_text(source.get("owner_id"))),
        "tower_step_up_receipt_ref_present": bool(
            _text(source.get("tower_step_up_receipt_ref"))
        ),
        "challenge_id_matches": (
            _text(source.get("challenge_id")) == expected_challenge_id
        ),
        "challenge_phrase_matches": (
            _text(source.get("challenge_phrase_confirmation")) == expected_phrase
        ),
        "decided_at_is_utc_iso": bool(
            _ISO_UTC.fullmatch(_text(source.get("decided_at")))
        ),
    }

    approval_checks = {
        key: value
        for key, value in checks.items()
        if key != "decision_allowed"
    }
    approval_valid = (
        normalized_decision == OWNER_APPROVAL_DECISION
        and checks["decision_allowed"]
        and all(approval_checks.values())
    )

    report = {
        "schema_version": SCHEMA_VERSION,
        "decision": normalized_decision,
        "decision_allowed": checks["decision_allowed"],
        "checks": checks,
        "approval_valid": approval_valid,
        "owner_rejected": normalized_decision == OWNER_REJECT_DECISION,
        "owner_held": normalized_decision == OWNER_HOLD_DECISION,
        "owner_id_sha256": _fingerprint(source.get("owner_id")),
        "tower_step_up_receipt_ref_sha256": _fingerprint(
            source.get("tower_step_up_receipt_ref")
        ),
        "raw_owner_id_recorded": False,
        "raw_step_up_receipt_recorded": False,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "deployment_authorized": False,
    }
    report["report_hash"] = payload_hash(report)
    return report


def freeze_provider_authorization_packet(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
) -> dict[str, Any]:
    runtime = resolve_repository_runtime(repository_root)
    validation = validate_provider_inputs(provider_inputs)
    selection = build_provider_selection_record(provider_inputs)
    capabilities = build_capability_attestation_record(provider_inputs)
    account_binding = build_account_team_binding(provider_inputs)
    region_binding = build_region_binding(provider_inputs)
    billing = build_billing_boundary(provider_inputs)
    secret_plan = build_secret_custody_plan()

    packet = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "managed_staging_frozen_provider_authorization",
        "runtime_resolved": runtime["resolved"],
        "runtime_contract_hash": runtime["contract_hash"],
        "managed_wsgi_target": MANAGED_WSGI_TARGET,
        "managed_start_command": MANAGED_START_COMMAND,
        "provider_inputs_valid": validation["valid"],
        "provider_validation_report_hash": validation["report_hash"],
        "provider_selection_record_hash": selection["record_hash"],
        "capability_attestation_record_hash": capabilities["record_hash"],
        "account_team_binding_hash": account_binding["record_hash"],
        "region_binding_hash": region_binding["record_hash"],
        "billing_boundary_hash": billing["record_hash"],
        "secret_custody_plan_hash": secret_plan["plan_hash"],
        "provider_input_fingerprints": validation["input_fingerprints"],
        "raw_provider_values_recorded": False,
        "raw_secrets_recorded": False,
        "frozen": True,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "deployment_authorized": False,
    }
    packet["frozen_packet_hash"] = payload_hash(packet)
    return packet


def build_owner_authorization_record(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    owner_decision: Mapping[str, Any] | None,
) -> dict[str, Any]:
    frozen = freeze_provider_authorization_packet(
        repository_root,
        provider_inputs,
    )
    challenge = build_owner_authorization_challenge(
        packet_hash=frozen["frozen_packet_hash"],
    )
    decision_report = validate_owner_decision(
        owner_decision,
        challenge=challenge,
    )

    ready = (
        frozen["runtime_resolved"]
        and frozen["provider_inputs_valid"]
        and decision_report["approval_valid"]
    )

    if decision_report["owner_rejected"]:
        final_decision = "NO_GO_OWNER_REJECTED_PROVIDER_AUTHORIZATION"
    elif not frozen["provider_inputs_valid"]:
        final_decision = (
            "NO_GO_HOLD_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION_REQUIRED"
        )
    elif not decision_report["approval_valid"]:
        final_decision = "NO_GO_HOLD_OWNER_AUTHORIZATION_REQUIRED"
    else:
        final_decision = "READY_FOR_SEPARATE_NO_CALL_PROVISIONING_REVIEW"

    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "managed_staging_owner_authorization_record",
        "frozen_packet_hash": frozen["frozen_packet_hash"],
        "challenge_id": challenge["challenge_id"],
        "challenge_hash": challenge["challenge_hash"],
        "decision_report_hash": decision_report["report_hash"],
        "provider_inputs_valid": frozen["provider_inputs_valid"],
        "owner_approval_valid": decision_report["approval_valid"],
        "ready_for_separate_no_call_provisioning_review": ready,
        "final_decision": final_decision,
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
    record["record_hash"] = payload_hash(record)
    return record


def build_no_call_provisioning_readiness(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    owner_decision: Mapping[str, Any] | None,
) -> dict[str, Any]:
    authorization = build_owner_authorization_record(
        repository_root,
        provider_inputs,
        owner_decision,
    )
    prior_packet = build_provider_authorization_packet(
        repository_root,
        {},
    )
    plan = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": "managed_staging_no_call_provisioning_readiness",
        "owner_authorization_record_hash": authorization["record_hash"],
        "prior_runtime_authorization_packet_hash": prior_packet["packet_hash"],
        "ready_for_separate_no_call_provisioning_review": authorization[
            "ready_for_separate_no_call_provisioning_review"
        ],
        "future_review_sequence": [
            "verify provider inputs against provider documentation",
            "verify account/team access without recording credentials",
            "verify region availability and owner cost boundary",
            "verify secret-store capability and staging-only separation",
            "prepare inert resource manifests",
            "perform provider-console dry-run review",
            "request separate owner provisioning authorization",
        ],
        "prohibited_actions": [
            "provider API call",
            "provider CLI login",
            "resource creation",
            "secret creation or readback",
            "database creation",
            "object storage creation",
            "web service deployment",
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
        "official_walkthrough_performed": False,
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
        "final_decision": authorization["final_decision"],
    }
    plan["plan_hash"] = payload_hash(plan)
    return plan


def build_current_provider_authorization_state(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None = None,
    owner_decision: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    frozen = freeze_provider_authorization_packet(
        repository_root,
        provider_inputs,
    )
    challenge = build_owner_authorization_challenge(
        packet_hash=frozen["frozen_packet_hash"],
    )
    decision = validate_owner_decision(
        owner_decision,
        challenge=challenge,
    )
    authorization = build_owner_authorization_record(
        repository_root,
        provider_inputs,
        owner_decision,
    )
    readiness = build_no_call_provisioning_readiness(
        repository_root,
        provider_inputs,
        owner_decision,
    )

    blockers: list[dict[str, str]] = []
    validation = validate_provider_inputs(provider_inputs)
    for error in validation["errors"]:
        blockers.append({
            "requirement": error["field"],
            "status": error["code"],
        })

    if not decision["approval_valid"]:
        blockers.append({
            "requirement": "tower_owner_authorization",
            "status": (
                "owner_rejected"
                if decision["owner_rejected"]
                else "owner_step_up_and_decision_required"
            ),
        })

    state = {
        "schema_version": SCHEMA_VERSION,
        "closed_layer": "MANAGED_STAGING_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION",
        "closed_through_step": 50,
        "runtime_target": MANAGED_WSGI_TARGET,
        "frozen_packet_hash": frozen["frozen_packet_hash"],
        "challenge_id": challenge["challenge_id"],
        "owner_decision_report_hash": decision["report_hash"],
        "owner_authorization_record_hash": authorization["record_hash"],
        "provisioning_readiness_plan_hash": readiness["plan_hash"],
        "provider_inputs_valid": frozen["provider_inputs_valid"],
        "owner_approval_valid": decision["approval_valid"],
        "ready_for_separate_no_call_provisioning_review": authorization[
            "ready_for_separate_no_call_provisioning_review"
        ],
        "blocking_requirements": blockers,
        "blocking_requirement_count": len(blockers),
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
        "official_walkthrough_performed": False,
        "permanent_main_modified": False,
        "final_decision": authorization["final_decision"],
        "next_boundary": (
            "managed_staging_no_call_provider_provisioning_review"
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




def write_bound_owner_decision_worksheet(
    output_path: str | Path,
    *,
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any],
) -> Path:
    frozen = freeze_provider_authorization_packet(
        repository_root,
        provider_inputs,
    )
    if not frozen["provider_inputs_valid"]:
        raise ValueError(
            "Provider inputs must validate before an owner challenge is generated."
        )
    return write_json(
        output_path,
        owner_decision_template(frozen),
    )


def write_operator_worksheets(
    output_directory: str | Path,
    *,
    repository_root: str | Path,
) -> dict[str, str]:
    root = Path(output_directory)
    root.mkdir(parents=True, exist_ok=True)
    inputs = provider_input_template()
    frozen = freeze_provider_authorization_packet(
        repository_root,
        inputs,
    )
    owner = owner_decision_template(frozen)
    input_path = write_json(
        root / "tower_ob_managed_staging_provider_inputs.json",
        inputs,
    )
    owner_path = write_json(
        root / "tower_ob_managed_staging_owner_decision.json",
        owner,
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "provider_input_path": str(input_path),
        "owner_decision_path": str(owner_path),
        "contains_secret_values": False,
        "provider_calls_performed": False,
    }
    manifest_path = write_json(
        root / "worksheet_manifest.json",
        manifest,
    )
    return {
        "provider_input_path": str(input_path),
        "owner_decision_path": str(owner_path),
        "manifest_path": str(manifest_path),
    }


__all__ = [
    "ALLOWED_OWNER_DECISIONS",
    "OWNER_APPROVAL_DECISION",
    "OWNER_HOLD_DECISION",
    "OWNER_REJECT_DECISION",
    "REQUIRED_CAPABILITIES",
    "build_account_team_binding",
    "build_billing_boundary",
    "build_capability_attestation_record",
    "build_current_provider_authorization_state",
    "build_no_call_provisioning_readiness",
    "build_owner_authorization_challenge",
    "build_owner_authorization_record",
    "build_provider_selection_record",
    "build_region_binding",
    "build_secret_custody_plan",
    "freeze_provider_authorization_packet",
    "owner_decision_template",
    "provider_input_template",
    "validate_owner_decision",
    "validate_provider_inputs",
    "write_bound_owner_decision_worksheet",
    "write_operator_worksheets",
]
