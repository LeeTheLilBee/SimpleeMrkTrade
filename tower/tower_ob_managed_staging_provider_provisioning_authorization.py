"""Provider provisioning authorization decision contracts for Tower/Observatory.

This layer binds a second Tower owner step-up decision to the completed,
frozen no-call provider-provisioning review packet. A valid approval may
authorize a tightly scoped future provider-provisioning execution-preparation
corridor. This module never authenticates to a provider, invokes a provider
API/CLI, creates resources, creates or reads secrets, deploys the application,
changes DNS, or performs an Observatory walkthrough.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping

from tower.tower_ob_managed_staging_no_call_provisioning_review import (
    build_authorization_handoff,
    build_no_call_provisioning_review_decision,
    freeze_no_call_provisioning_review_packet,
    no_call_review_input_template,
)
from tower.tower_ob_managed_staging_provider_authorization import (
    provider_input_template,
)
from tower.tower_ob_managed_staging_runtime import (
    MANAGED_START_COMMAND,
    MANAGED_WSGI_TARGET,
    payload_hash,
)

SCHEMA_VERSION = (
    "simplee.tower_ob.provider_provisioning_authorization_decision.v1"
)

AUTHORIZE_DECISION = "AUTHORIZE_PROVISIONING_EXECUTION_PREPARATION"
HOLD_DECISION = "HOLD"
REJECT_DECISION = "REJECT"
ALLOWED_DECISIONS = frozenset({
    AUTHORIZE_DECISION,
    HOLD_DECISION,
    REJECT_DECISION,
})

REQUIRED_SCOPE_ATTESTATIONS = (
    "staging_only_scope_confirmed",
    "single_tower_fronted_service_confirmed",
    "tower_only_public_ingress_confirmed",
    "observatory_separate_service_not_required",
    "one_web_service_resource_limit_confirmed",
    "provider_console_manual_control_confirmed",
    "secret_values_never_recorded_in_git_confirmed",
    "secret_readback_prohibited_confirmed",
    "database_creation_not_authorized",
    "object_storage_creation_not_authorized",
    "dns_changes_not_authorized",
    "deployment_not_authorized",
    "official_walkthrough_not_authorized",
    "production_manual_live_not_authorized",
    "broker_submission_not_authorized",
    "real_capital_movement_not_authorized",
    "direct_vault_upload_not_authorized",
    "live_auto_remains_locked",
    "no_provider_calls_performed_during_decision",
)

_SAFE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+ #(),-]{1,299}$")
_ISO_UTC = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
)
_MONEY = re.compile(r"^\d{1,6}(?:\.\d{1,2})?$")
_SENSITIVE_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
    re.compile(
        r"\b(?:api[_-]?key|access[_-]?token|token|secret|password)"
        r"\s*[:=]\s*\S+",
        re.I,
    ),
    re.compile(
        r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?)://"
        r"[^/\s]+:[^@\s]+@",
        re.I,
    ),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
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


def _parse_utc(value: Any) -> datetime | None:
    normalized = _text(value)
    if not _ISO_UTC.fullmatch(normalized):
        return None
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc)


def _valid_money(value: Any) -> bool:
    normalized = _text(value)
    if not _MONEY.fullmatch(normalized):
        return False
    try:
        amount = Decimal(normalized)
    except InvalidOperation:
        return False
    return Decimal("0") < amount <= Decimal("10000")


def build_completed_review_handoff(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
) -> dict[str, Any]:
    authorization_handoff = build_authorization_handoff(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
    )
    review_packet = freeze_no_call_provisioning_review_packet(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
    )
    review_decision = build_no_call_provisioning_review_decision(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
    )
    ready = bool(
        authorization_handoff["ready_for_no_call_review"]
        and review_packet["review_inputs_valid"]
        and review_decision[
            "ready_for_separate_provider_provisioning_authorization_decision"
        ]
    )
    handoff = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "completed_no_call_provisioning_review_handoff",
        "authorization_handoff_hash": authorization_handoff["handoff_hash"],
        "frozen_provider_packet_hash": review_packet[
            "frozen_provider_packet_hash"
        ],
        "owner_authorization_record_hash": review_packet[
            "owner_authorization_record_hash"
        ],
        "frozen_review_packet_hash": review_packet[
            "frozen_review_packet_hash"
        ],
        "review_decision_hash": review_decision["decision_hash"],
        "provider_inputs_valid": authorization_handoff[
            "provider_inputs_valid"
        ],
        "provider_review_owner_approval_valid": authorization_handoff[
            "owner_approval_valid"
        ],
        "review_inputs_valid": review_packet["review_inputs_valid"],
        "completed_review_ready": ready,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "secret_reference_registration_authorized": False,
        "deployment_authorized": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_created_or_read": False,
        "deployment_performed": False,
    }
    handoff["handoff_hash"] = payload_hash(handoff)
    return handoff


def build_provisioning_authorization_challenge(
    handoff: Mapping[str, Any],
) -> dict[str, Any]:
    packet_hash = _text(handoff.get("frozen_review_packet_hash")) or ("0" * 64)
    challenge_id = hashlib.sha256(
        (
            "simplee:tower-ob:managed-staging:"
            "provider-provisioning-execution-preparation:"
            + packet_hash
        ).encode("utf-8")
    ).hexdigest()[:24]
    phrase = (
        "AUTHORIZE TOWER OB STAGING PROVISIONING PREPARATION "
        + challenge_id.upper()
    )
    challenge = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "provider_provisioning_authorization_challenge",
        "challenge_id": challenge_id,
        "challenge_phrase": phrase,
        "frozen_review_packet_hash": packet_hash,
        "review_decision_hash": _text(handoff.get("review_decision_hash")),
        "required_decision": AUTHORIZE_DECISION,
        "tower_owner_session_required": True,
        "tower_step_up_receipt_required": True,
        "completed_review_required": True,
        "provider_calls_performed": False,
        "resources_created": False,
        "deployment_performed": False,
    }
    challenge["challenge_hash"] = payload_hash(challenge)
    return challenge


def provisioning_authorization_decision_template(
    handoff: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source = dict(handoff or {})
    challenge = build_provisioning_authorization_challenge(source)
    challenge_ready = bool(source.get("completed_review_ready"))
    template = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "provider_provisioning_authorization_decision",
        "decision": HOLD_DECISION,
        "frozen_review_packet_hash": _text(
            source.get("frozen_review_packet_hash")
        ),
        "review_decision_hash": _text(source.get("review_decision_hash")),
        "owner_id": "",
        "tower_step_up_receipt_ref": "",
        "challenge_ready": challenge_ready,
        "challenge_id": challenge["challenge_id"] if challenge_ready else "",
        "expected_challenge_phrase": (
            challenge["challenge_phrase"] if challenge_ready else ""
        ),
        "challenge_phrase_confirmation": "",
        "decided_at": "",
        "authorization_expires_at": "",
        "monthly_cost_ceiling_usd": "",
        "authorized_scope": {
            "provider_console_access": False,
            "create_one_managed_web_service": False,
            "configure_non_secret_environment_names": False,
            "register_secret_references_without_readback": False,
            "configure_health_checks": False,
            "configure_deployment_and_access_logs": False,
            "configure_manual_deployment_control": False,
            "configure_rollback_target": False,
        },
        "scope_attestations": {
            name: False for name in REQUIRED_SCOPE_ATTESTATIONS
        },
        "notes": [
            "Do not include passwords, tokens, API keys, cookies, private keys, connection strings, or secret values.",
            "Approval authorizes only a separate no-call provisioning execution-preparation corridor.",
            "Approval does not authorize deployment, DNS changes, databases, object storage, an official walkthrough, or production operation.",
        ],
    }
    template["template_hash"] = payload_hash(template)
    return template


def validate_provisioning_authorization_decision(
    decision: Mapping[str, Any] | None,
    *,
    handoff: Mapping[str, Any],
    challenge: Mapping[str, Any],
) -> dict[str, Any]:
    source = dict(decision or {})
    normalized_decision = _text(source.get("decision")).upper() or HOLD_DECISION
    errors: list[dict[str, str]] = []

    checks = {
        "completed_review_ready": bool(handoff.get("completed_review_ready")),
        "decision_allowed": normalized_decision in ALLOWED_DECISIONS,
        "frozen_review_packet_hash_matches": (
            _text(source.get("frozen_review_packet_hash"))
            == _text(handoff.get("frozen_review_packet_hash"))
        ),
        "review_decision_hash_matches": (
            _text(source.get("review_decision_hash"))
            == _text(handoff.get("review_decision_hash"))
        ),
        "owner_id_present": bool(_text(source.get("owner_id"))),
        "tower_step_up_receipt_ref_present": bool(
            _text(source.get("tower_step_up_receipt_ref"))
        ),
        "challenge_id_matches": (
            _text(source.get("challenge_id"))
            == _text(challenge.get("challenge_id"))
        ),
        "challenge_phrase_matches": (
            _text(source.get("challenge_phrase_confirmation"))
            == _text(challenge.get("challenge_phrase"))
        ),
        "decided_at_is_utc_iso": _parse_utc(source.get("decided_at"))
        is not None,
        "authorization_expires_at_is_utc_iso": _parse_utc(
            source.get("authorization_expires_at")
        )
        is not None,
        "monthly_cost_ceiling_valid": _valid_money(
            source.get("monthly_cost_ceiling_usd")
        ),
    }

    decided_at = _parse_utc(source.get("decided_at"))
    expires_at = _parse_utc(source.get("authorization_expires_at"))
    checks["authorization_window_ordered"] = bool(
        decided_at and expires_at and expires_at > decided_at
    )

    scope = dict(source.get("authorized_scope") or {})
    required_scope = {
        "provider_console_access": True,
        "create_one_managed_web_service": True,
        "configure_non_secret_environment_names": True,
        "register_secret_references_without_readback": True,
        "configure_health_checks": True,
        "configure_deployment_and_access_logs": True,
        "configure_manual_deployment_control": True,
        "configure_rollback_target": True,
    }
    scope_checks = {
        name: _bool(scope.get(name)) is expected
        for name, expected in required_scope.items()
    }

    attestations = dict(source.get("scope_attestations") or {})
    attestation_checks = {
        name: _bool(attestations.get(name))
        for name in REQUIRED_SCOPE_ATTESTATIONS
    }

    for name, valid in checks.items():
        if not valid:
            errors.append({"field": name, "code": "required_check_failed"})
    for name, valid in scope_checks.items():
        if not valid:
            errors.append({
                "field": f"authorized_scope.{name}",
                "code": "required_scope_not_authorized",
            })
    for name, valid in attestation_checks.items():
        if not valid:
            errors.append({
                "field": f"scope_attestations.{name}",
                "code": "attestation_required",
            })

    for field in ("owner_id", "tower_step_up_receipt_ref"):
        value = _text(source.get(field))
        if value and not _SAFE_REF.fullmatch(value):
            errors.append({
                "field": field,
                "code": "invalid_reference_format",
            })

    sensitive_material_detected = _contains_sensitive_material(source)
    if sensitive_material_detected:
        errors.append({
            "field": "payload",
            "code": "sensitive_material_prohibited",
        })

    approval_valid = bool(
        normalized_decision == AUTHORIZE_DECISION
        and not errors
        and all(checks.values())
        and all(scope_checks.values())
        and all(attestation_checks.values())
    )
    rejected = normalized_decision == REJECT_DECISION
    report = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "provider_provisioning_authorization_validation",
        "decision": normalized_decision,
        "approval_valid": approval_valid,
        "rejected": rejected,
        "checks": checks,
        "scope_checks": scope_checks,
        "attestation_checks": attestation_checks,
        "error_count": len(errors),
        "errors": errors,
        "sensitive_material_detected": sensitive_material_detected,
        "owner_id_sha256": _fingerprint(source.get("owner_id")),
        "tower_step_up_receipt_ref_sha256": _fingerprint(
            source.get("tower_step_up_receipt_ref")
        ),
        "monthly_cost_ceiling_usd": (
            _text(source.get("monthly_cost_ceiling_usd"))
            if _valid_money(source.get("monthly_cost_ceiling_usd"))
            else None
        ),
        "raw_owner_values_recorded": False,
        "raw_secret_values_recorded": False,
    }
    report["report_hash"] = payload_hash(report)
    return report


def build_provider_action_scope_manifest(
    decision: Mapping[str, Any] | None,
    *,
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    approved = bool(validation.get("approval_valid"))
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "provider_provisioning_authorized_action_scope",
        "environment": "staging",
        "runtime_target": MANAGED_WSGI_TARGET,
        "start_command": MANAGED_START_COMMAND,
        "service_count_ceiling": 1,
        "public_ingress_owner": "tower",
        "observatory_public_ingress_allowed": False,
        "allowed_future_actions": [
            "authenticate to the selected managed hosting provider",
            "open the authorized staging account or team",
            "create one managed Python web-service shell",
            "bind the authorized repository and staging branch",
            "configure non-secret environment variable names",
            "register secret references without secret readback",
            "configure health checks, logs, manual deployment control, and rollback",
            "stop before build, deploy, DNS, database, or object-storage actions",
        ] if approved else [],
        "prohibited_actions": [
            "application deployment",
            "automatic deployment",
            "DNS or public-route change",
            "database creation",
            "object storage creation",
            "production environment access",
            "production data or secret reuse",
            "official Observatory walkthrough",
            "production Manual Live",
            "broker submission",
            "real capital movement",
            "direct Vault upload",
            "Live Auto unlock",
        ],
        "provider_calls_authorized_for_future_execution_preparation": approved,
        "one_web_service_creation_authorized_for_future_execution_preparation": approved,
        "secret_reference_registration_authorized": approved,
        "deployment_authorized": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_created_or_read": False,
        "deployment_performed": False,
    }
    manifest["manifest_hash"] = payload_hash(manifest)
    return manifest


def build_resource_and_cost_ceiling_manifest(
    decision: Mapping[str, Any] | None,
    *,
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    approved = bool(validation.get("approval_valid"))
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "provider_provisioning_resource_and_cost_ceiling",
        "environment": "staging",
        "managed_web_service_count_ceiling": 1 if approved else 0,
        "database_count_ceiling": 0,
        "object_storage_bucket_count_ceiling": 0,
        "dns_change_count_ceiling": 0,
        "monthly_cost_ceiling_usd": validation.get(
            "monthly_cost_ceiling_usd"
        ) if approved else None,
        "automatic_spend_authorized": False,
        "automatic_scaling_authorized": False,
        "production_billing_reuse_authorized": False,
        "billing_credentials_recorded": False,
        "resource_creation_performed": False,
    }
    manifest["manifest_hash"] = payload_hash(manifest)
    return manifest


def build_secret_custody_authorization_manifest(
    *,
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    approved = bool(validation.get("approval_valid"))
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "provider_provisioning_secret_custody_authorization",
        "secret_environment_names": [
            "TOWER_SESSION_SECRET",
            "TOWER_OWNER_PASSWORD_HASH",
        ],
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
        "provider_secret_reference_registration_authorized": approved,
        "secret_value_generation_authorized": False,
        "secret_value_readback_authorized": False,
        "plaintext_secret_entry_into_git_authorized": False,
        "production_secret_reuse_authorized": False,
        "raw_secret_values_recorded": False,
        "secrets_created_or_read": False,
    }
    manifest["manifest_hash"] = payload_hash(manifest)
    return manifest


def build_execution_preconditions_manifest(
    *,
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    approved = bool(validation.get("approval_valid"))
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "provider_provisioning_execution_preconditions",
        "authorization_valid": approved,
        "required_before_any_future_provider_action": [
            "re-read the frozen review and authorization hashes",
            "verify the Tower owner step-up receipt reference",
            "verify authorization remains inside its time window",
            "verify the staging account/team and region match the frozen provider packet",
            "verify the one-service and cost ceilings",
            "verify provider console manual control and stop controls",
            "prepare a rollback target before any deployment",
            "record provider-side identifiers without credentials or secret values",
        ],
        "mandatory_stop_points": [
            "stop after provider authentication verification",
            "stop before resource creation if any hash, account, region, cost, or scope mismatch exists",
            "stop immediately after creating the inert web-service shell",
            "stop before build or deployment",
            "stop before database, object storage, or DNS changes",
        ],
        "rollback_execution_authorized": False,
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


def freeze_provisioning_authorization_record(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
) -> dict[str, Any]:
    handoff = build_completed_review_handoff(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
    )
    challenge = build_provisioning_authorization_challenge(handoff)
    validation = validate_provisioning_authorization_decision(
        provisioning_decision,
        handoff=handoff,
        challenge=challenge,
    )
    scope = build_provider_action_scope_manifest(
        provisioning_decision,
        validation=validation,
    )
    ceilings = build_resource_and_cost_ceiling_manifest(
        provisioning_decision,
        validation=validation,
    )
    secrets = build_secret_custody_authorization_manifest(
        validation=validation,
    )
    preconditions = build_execution_preconditions_manifest(
        validation=validation,
    )
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "frozen_provider_provisioning_authorization",
        "completed_review_handoff_hash": handoff["handoff_hash"],
        "frozen_review_packet_hash": handoff["frozen_review_packet_hash"],
        "review_decision_hash": handoff["review_decision_hash"],
        "authorization_challenge_hash": challenge["challenge_hash"],
        "authorization_validation_report_hash": validation["report_hash"],
        "provider_action_scope_manifest_hash": scope["manifest_hash"],
        "resource_and_cost_ceiling_manifest_hash": ceilings[
            "manifest_hash"
        ],
        "secret_custody_manifest_hash": secrets["manifest_hash"],
        "execution_preconditions_manifest_hash": preconditions[
            "manifest_hash"
        ],
        "approval_valid": validation["approval_valid"],
        "rejected": validation["rejected"],
        "owner_id_sha256": validation["owner_id_sha256"],
        "tower_step_up_receipt_ref_sha256": validation[
            "tower_step_up_receipt_ref_sha256"
        ],
        "authorization_expires_at_sha256": _fingerprint(
            (provisioning_decision or {}).get("authorization_expires_at")
        ),
        "raw_provider_values_recorded": False,
        "raw_owner_values_recorded": False,
        "raw_review_values_recorded": False,
        "raw_secret_values_recorded": False,
        "frozen": True,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_created_or_read": False,
        "deployment_performed": False,
    }
    record["frozen_authorization_record_hash"] = payload_hash(record)
    return record


def build_provisioning_authorization_decision(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
) -> dict[str, Any]:
    prior = build_no_call_provisioning_review_decision(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
    )
    handoff = build_completed_review_handoff(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
    )
    challenge = build_provisioning_authorization_challenge(handoff)
    validation = validate_provisioning_authorization_decision(
        provisioning_decision,
        handoff=handoff,
        challenge=challenge,
    )
    record = freeze_provisioning_authorization_record(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
    )

    if not handoff["completed_review_ready"]:
        final_decision = prior["final_decision"]
    elif validation["rejected"]:
        final_decision = (
            "NO_GO_OWNER_REJECTED_PROVIDER_PROVISIONING_AUTHORIZATION"
        )
    elif not validation["approval_valid"]:
        final_decision = (
            "NO_GO_HOLD_PROVIDER_PROVISIONING_AUTHORIZATION_REQUIRED"
        )
    else:
        final_decision = (
            "AUTHORIZED_FOR_SEPARATE_NO_CALL_PROVIDER_PROVISIONING_"
            "EXECUTION_PREPARATION"
        )

    approved = bool(validation["approval_valid"])
    decision = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "provider_provisioning_authorization_decision",
        "completed_review_handoff_hash": handoff["handoff_hash"],
        "frozen_authorization_record_hash": record[
            "frozen_authorization_record_hash"
        ],
        "authorization_valid": approved,
        "ready_for_separate_no_call_provider_provisioning_execution_preparation": approved,
        "final_decision": final_decision,
        "provider_calls_authorized_for_future_execution_preparation": approved,
        "one_web_service_creation_authorized_for_future_execution_preparation": approved,
        "secret_reference_registration_authorized": approved,
        "database_creation_authorized": False,
        "object_storage_creation_authorized": False,
        "dns_changes_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_created_or_read": False,
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


def build_no_call_execution_preparation_plan(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
) -> dict[str, Any]:
    decision = build_provisioning_authorization_decision(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
    )
    plan = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": "no_call_provider_provisioning_execution_preparation",
        "authorization_decision_hash": decision["decision_hash"],
        "ready": decision[
            "ready_for_separate_no_call_provider_provisioning_execution_preparation"
        ],
        "preparation_steps": [
            "load only frozen hashes and non-secret provider identifiers",
            "revalidate owner authorization and expiry",
            "prepare provider-specific command previews without executing them",
            "prepare one-service creation receipt schema",
            "prepare provider identifier capture without credentials",
            "prepare stop, rollback, and incident hold receipts",
            "prepare a separate owner execution-window decision",
        ],
        "dry_run_only": True,
        "shell_invoked": False,
        "provider_api_invoked": False,
        "provider_cli_invoked": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_created_or_read": False,
        "build_performed": False,
        "deployment_performed": False,
        "final_decision": decision["final_decision"],
    }
    plan["plan_hash"] = payload_hash(plan)
    return plan


def build_current_provisioning_authorization_state(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None = None,
    provider_review_owner_decision: Mapping[str, Any] | None = None,
    review_inputs: Mapping[str, Any] | None = None,
    provisioning_decision: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    handoff = build_completed_review_handoff(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
    )
    challenge = build_provisioning_authorization_challenge(handoff)
    validation = validate_provisioning_authorization_decision(
        provisioning_decision,
        handoff=handoff,
        challenge=challenge,
    )
    authorization = build_provisioning_authorization_decision(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
    )
    plan = build_no_call_execution_preparation_plan(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
    )

    blockers: list[dict[str, str]] = []
    if not handoff["provider_inputs_valid"]:
        blockers.append({
            "requirement": "provider_inputs",
            "status": "provider_inputs_required",
        })
    if not handoff["provider_review_owner_approval_valid"]:
        blockers.append({
            "requirement": "provider_review_owner_authorization",
            "status": "owner_step_up_and_decision_required",
        })
    if not handoff["review_inputs_valid"]:
        blockers.append({
            "requirement": "no_call_review_evidence",
            "status": "completed_review_required",
        })
    for error in validation["errors"]:
        blockers.append({
            "requirement": error["field"],
            "status": error["code"],
        })

    state = {
        "schema_version": SCHEMA_VERSION,
        "closed_layer": (
            "MANAGED_STAGING_PROVIDER_PROVISIONING_AUTHORIZATION_DECISION"
        ),
        "closed_through_step": 70,
        "runtime_target": MANAGED_WSGI_TARGET,
        "runtime_topology": (
            "single_tower_fronted_managed_python_web_service"
        ),
        "completed_review_handoff_hash": handoff["handoff_hash"],
        "authorization_challenge_hash": challenge["challenge_hash"],
        "authorization_decision_hash": authorization["decision_hash"],
        "no_call_execution_preparation_plan_hash": plan["plan_hash"],
        "provider_inputs_valid": handoff["provider_inputs_valid"],
        "provider_review_owner_approval_valid": handoff[
            "provider_review_owner_approval_valid"
        ],
        "review_inputs_valid": handoff["review_inputs_valid"],
        "provisioning_authorization_valid": authorization[
            "authorization_valid"
        ],
        "ready_for_separate_no_call_provider_provisioning_execution_preparation": authorization[
            "ready_for_separate_no_call_provider_provisioning_execution_preparation"
        ],
        "blocking_requirements": blockers,
        "blocking_requirement_count": len(blockers),
        "provider_calls_authorized_for_future_execution_preparation": authorization[
            "provider_calls_authorized_for_future_execution_preparation"
        ],
        "one_web_service_creation_authorized_for_future_execution_preparation": authorization[
            "one_web_service_creation_authorized_for_future_execution_preparation"
        ],
        "secret_reference_registration_authorized": authorization[
            "secret_reference_registration_authorized"
        ],
        "database_creation_authorized": False,
        "object_storage_creation_authorized": False,
        "dns_changes_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_created_or_read": False,
        "deployment_performed": False,
        "official_walkthrough_performed": False,
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
        "permanent_main_modified": False,
        "final_decision": authorization["final_decision"],
        "next_boundary": (
            "managed_staging_no_call_provider_provisioning_"
            "execution_preparation"
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


def write_provisioning_authorization_worksheets(
    output_directory: str | Path,
    *,
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None = None,
    provider_review_owner_decision: Mapping[str, Any] | None = None,
    review_inputs: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    root = Path(output_directory)
    root.mkdir(parents=True, exist_ok=True)
    handoff = build_completed_review_handoff(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
    )
    decision_template = provisioning_authorization_decision_template(handoff)
    decision_path = write_json(
        root / "tower_ob_provider_provisioning_authorization_decision.json",
        decision_template,
    )
    execution_placeholder = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "provider_provisioning_execution_preparation_placeholder",
        "decision": "HOLD",
        "frozen_authorization_record_hash": "",
        "owner_execution_window_receipt_ref": "",
        "notes": [
            "This placeholder is not an execution authorization.",
            "A later corridor must revalidate the frozen authorization and create only no-call execution-preparation artifacts.",
        ],
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "deployment_performed": False,
    }
    execution_placeholder["template_hash"] = payload_hash(
        execution_placeholder
    )
    placeholder_path = write_json(
        root / "tower_ob_provider_provisioning_execution_preparation_placeholder.json",
        execution_placeholder,
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "authorization_decision_path": str(decision_path),
        "execution_preparation_placeholder_path": str(placeholder_path),
        "completed_review_ready": handoff["completed_review_ready"],
        "contains_secret_values": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "deployment_performed": False,
    }
    manifest_path = write_json(root / "worksheet_manifest.json", manifest)
    return {
        "authorization_decision_path": str(decision_path),
        "execution_preparation_placeholder_path": str(placeholder_path),
        "manifest_path": str(manifest_path),
    }


def blank_current_inputs(
    repository_root: str | Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    provider_inputs = provider_input_template()
    provider_review_owner_decision: dict[str, Any] = {}
    handoff = build_authorization_handoff(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
    )
    review_inputs = no_call_review_input_template(handoff)
    provisioning_decision = provisioning_authorization_decision_template(
        build_completed_review_handoff(
            repository_root,
            provider_inputs,
            provider_review_owner_decision,
            review_inputs,
        )
    )
    return (
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
    )


__all__ = [
    "ALLOWED_DECISIONS",
    "AUTHORIZE_DECISION",
    "HOLD_DECISION",
    "REJECT_DECISION",
    "REQUIRED_SCOPE_ATTESTATIONS",
    "blank_current_inputs",
    "build_completed_review_handoff",
    "build_current_provisioning_authorization_state",
    "build_execution_preconditions_manifest",
    "build_no_call_execution_preparation_plan",
    "build_provider_action_scope_manifest",
    "build_provisioning_authorization_challenge",
    "build_provisioning_authorization_decision",
    "build_resource_and_cost_ceiling_manifest",
    "build_secret_custody_authorization_manifest",
    "freeze_provisioning_authorization_record",
    "provisioning_authorization_decision_template",
    "validate_provisioning_authorization_decision",
    "write_provisioning_authorization_worksheets",
]
