"""Controlled provider-provisioning execution-session preparation contracts.

This layer prepares a later, separately authorized Tower-controlled provider
session. It binds the frozen Step 090 execution authorization to non-secret
session references, an authorization-contained time window, provider/account/
region fingerprints, duplicate-resource stop gates, one inert Tower-fronted
service-shell request, environment-name and secret-reference registration
sequences, health/log/manual-control/rollback checks, and an ordered receipt
chain.

This module never opens a provider session, authenticates to a provider,
invokes browser automation, CLI, API, HTTP, or shell actions, creates resources,
registers or reads secret values, builds or deploys the application, changes
DNS, creates a database or object storage, or performs an official Observatory
walkthrough.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping

from tower.tower_ob_managed_staging_provider_provisioning_execution_authorization import (
    blank_current_inputs as blank_execution_authorization_inputs,
    build_execution_authorization_decision,
    build_inert_controlled_execution_session_plan,
    freeze_execution_authorization_record,
)
from tower.tower_ob_managed_staging_runtime import (
    HOSTED_MODE_ENV,
    MANAGED_HOST_ACCOUNT_OR_TEAM_ENV,
    MANAGED_HOST_PROVIDER_ENV,
    MANAGED_START_COMMAND,
    MANAGED_WSGI_TARGET,
    PROVIDER_OWNER_APPROVAL_ENV,
    STAGING_DEPLOYMENT_REGION_ENV,
    TOWER_OWNER_ID_ENV,
    TOWER_OWNER_PASSWORD_HASH_ENV,
    TOWER_OWNER_USERNAME_ENV,
    TOWER_SESSION_SECRET_ENV,
    TOWER_STEP_UP_MINUTES_ENV,
    payload_hash,
)

SCHEMA_VERSION = (
    "simplee.tower_ob.controlled_provider_provisioning_execution_session_preparation.v1"
)

READY_DECISION = (
    "GO_READY_FOR_SEPARATE_CONTROLLED_PROVIDER_SESSION_OPENING_AUTHORIZATION"
)
HOLD_PROVIDER_INPUTS = "NO_GO_HOLD_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION_REQUIRED"
HOLD_EXECUTION_AUTHORIZATION = "NO_GO_HOLD_EXECUTION_AUTHORIZATION_REQUIRED"
HOLD_SESSION_PREPARATION = "NO_GO_HOLD_CONTROLLED_SESSION_PREPARATION_REQUIRED"

REQUIRED_SESSION_PREPARATION_ATTESTATIONS = (
    "staging_only_scope_confirmed",
    "single_tower_fronted_service_confirmed",
    "tower_only_public_ingress_confirmed",
    "observatory_separate_service_not_required",
    "frozen_execution_authorization_hash_confirmed",
    "execution_authorization_window_confirmed",
    "authorized_source_commit_confirmed",
    "monthly_cost_ceiling_confirmed",
    "owner_controlled_session_receipt_confirmed",
    "provider_account_team_binding_confirmed",
    "provider_region_binding_confirmed",
    "duplicate_resource_lookup_before_creation_confirmed",
    "stop_if_duplicate_or_ambiguous_resource_confirmed",
    "one_inert_web_service_shell_limit_confirmed",
    "repository_branch_and_commit_binding_confirmed",
    "non_secret_environment_names_only_confirmed",
    "secret_references_without_readback_confirmed",
    "secret_values_never_written_to_git_confirmed",
    "health_check_configuration_reviewed",
    "deployment_logs_configuration_reviewed",
    "access_logs_configuration_reviewed",
    "manual_deployment_control_reviewed",
    "rollback_target_reviewed",
    "receipt_chain_order_reviewed",
    "stop_before_build_confirmed",
    "stop_before_deployment_confirmed",
    "database_creation_not_authorized",
    "object_storage_creation_not_authorized",
    "dns_changes_not_authorized",
    "official_walkthrough_not_authorized",
    "production_manual_live_not_authorized",
    "broker_submission_not_authorized",
    "real_capital_movement_not_authorized",
    "direct_vault_upload_not_authorized",
    "live_auto_remains_locked",
    "no_provider_session_login_or_calls_performed_during_preparation",
)

NON_SECRET_ENVIRONMENT_NAMES = (
    HOSTED_MODE_ENV,
    MANAGED_HOST_PROVIDER_ENV,
    MANAGED_HOST_ACCOUNT_OR_TEAM_ENV,
    STAGING_DEPLOYMENT_REGION_ENV,
    PROVIDER_OWNER_APPROVAL_ENV,
    TOWER_OWNER_USERNAME_ENV,
    TOWER_OWNER_ID_ENV,
    TOWER_STEP_UP_MINUTES_ENV,
)

SECRET_REFERENCE_NAMES = (
    TOWER_SESSION_SECRET_ENV,
    TOWER_OWNER_PASSWORD_HASH_ENV,
)

_SAFE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+ #(),-]{1,299}$")
_COMMIT_REF = re.compile(r"^(?:commit/)?[0-9a-f]{40}$", re.I)
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

_EXECUTION_AUTHORIZATION_HANDOFF_CACHE: dict[str, dict[str, Any]] = {}
_SESSION_PREPARATION_PARTS_CACHE: dict[str, tuple[dict[str, Any], ...]] = {}


def _clone_json(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, default=str))



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


def _contains_sensitive_material(value: Any) -> bool:
    rendered = json.dumps(value, sort_keys=True, default=str)
    return any(pattern.search(rendered) for pattern in _SENSITIVE_PATTERNS)


def _normalize_commit_ref(value: Any) -> str:
    normalized = _text(value)
    if normalized.lower().startswith("commit/"):
        normalized = normalized.split("/", 1)[1]
    return normalized.lower()


def build_execution_authorization_handoff(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
    preparation_inputs: Mapping[str, Any] | None,
    execution_authorization_decision: Mapping[str, Any] | None,
) -> dict[str, Any]:
    cache_key = payload_hash({
        "repository_root": str(Path(repository_root).resolve()),
        "provider_inputs": provider_inputs or {},
        "provider_review_owner_decision": provider_review_owner_decision or {},
        "review_inputs": review_inputs or {},
        "provisioning_decision": provisioning_decision or {},
        "preparation_inputs": preparation_inputs or {},
        "execution_authorization_decision": execution_authorization_decision or {},
    })
    cached = _EXECUTION_AUTHORIZATION_HANDOFF_CACHE.get(cache_key)
    if cached is not None:
        return _clone_json(cached)

    authorization = build_execution_authorization_decision(
        repository_root,
        provider_inputs or {},
        provider_review_owner_decision or {},
        review_inputs or {},
        provisioning_decision or {},
        preparation_inputs or {},
        execution_authorization_decision or {},
    )
    frozen = freeze_execution_authorization_record(
        repository_root,
        provider_inputs or {},
        provider_review_owner_decision or {},
        review_inputs or {},
        provisioning_decision or {},
        preparation_inputs or {},
        execution_authorization_decision or {},
    )
    inert_plan = build_inert_controlled_execution_session_plan(
        repository_root,
        provider_inputs or {},
        provider_review_owner_decision or {},
        review_inputs or {},
        provisioning_decision or {},
        preparation_inputs or {},
        execution_authorization_decision or {},
    )
    execution_authorization_ready = bool(
        authorization[
            "ready_for_separate_controlled_provider_provisioning_execution_session"
        ]
        and frozen["approval_valid"]
        and inert_plan["ready_for_later_session"]
    )
    handoff = {
        "schema_version": SCHEMA_VERSION,
        "handoff_type": "completed_execution_authorization_to_session_preparation",
        "execution_authorization_decision_hash": authorization["decision_hash"],
        "frozen_execution_authorization_record_hash": frozen[
            "frozen_execution_authorization_record_hash"
        ],
        "inert_controlled_execution_session_plan_hash": inert_plan["plan_hash"],
        "execution_authorization_valid": authorization[
            "execution_authorization_valid"
        ],
        "execution_authorization_ready": execution_authorization_ready,
        "authorized_source_commit_ref": _text(
            (execution_authorization_decision or {}).get(
                "authorized_source_commit_ref"
            )
        ),
        "execution_window_starts_at": _text(
            (execution_authorization_decision or {}).get(
                "execution_window_starts_at"
            )
        ),
        "execution_window_expires_at": _text(
            (execution_authorization_decision or {}).get(
                "execution_window_expires_at"
            )
        ),
        "monthly_cost_ceiling_usd": _text(
            (execution_authorization_decision or {}).get(
                "monthly_cost_ceiling_usd"
            )
        ),
        "provider_slug_sha256": _fingerprint(
            (provider_inputs or {}).get("provider_slug")
        ),
        "account_or_team_ref_sha256": _fingerprint(
            (provider_inputs or {}).get("account_or_team_ref")
        ),
        "deployment_region_sha256": _fingerprint(
            (provider_inputs or {}).get("deployment_region")
        ),
        "provider_login_authorized_for_later_session": execution_authorization_ready,
        "provider_calls_authorized_for_later_session": execution_authorization_ready,
        "one_inert_web_service_creation_authorized_for_later_session": execution_authorization_ready,
        "secret_reference_registration_authorized_for_later_session": execution_authorization_ready,
        "database_creation_authorized": False,
        "object_storage_creation_authorized": False,
        "dns_changes_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
        "final_decision": authorization["final_decision"],
    }
    handoff["handoff_hash"] = payload_hash(handoff)
    _EXECUTION_AUTHORIZATION_HANDOFF_CACHE[cache_key] = _clone_json(handoff)
    return handoff


def controlled_session_preparation_input_template(
    handoff: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "controlled_provider_provisioning_session_preparation_inputs",
        "frozen_execution_authorization_record_hash": _text(
            handoff.get("frozen_execution_authorization_record_hash")
        ),
        "execution_authorization_decision_hash": _text(
            handoff.get("execution_authorization_decision_hash")
        ),
        "authorized_source_commit_ref": _text(
            handoff.get("authorized_source_commit_ref")
        ),
        "monthly_cost_ceiling_usd": _text(
            handoff.get("monthly_cost_ceiling_usd")
        ),
        "session_window_starts_at": _text(
            handoff.get("execution_window_starts_at")
        ),
        "session_window_expires_at": _text(
            handoff.get("execution_window_expires_at")
        ),
        "owner_execution_session_receipt_ref": "",
        "provider_console_access_preflight_ref": "",
        "provider_account_team_binding_ref": "",
        "provider_region_binding_ref": "",
        "duplicate_resource_lookup_plan_ref": "",
        "service_creation_form_review_ref": "",
        "repository_binding_review_ref": "",
        "non_secret_environment_registration_review_ref": "",
        "secret_reference_registration_review_ref": "",
        "health_logging_review_ref": "",
        "manual_deployment_control_review_ref": "",
        "rollback_review_ref": "",
        "cost_ceiling_review_ref": "",
        "receipt_chain_review_ref": "",
        "stop_conditions_review_ref": "",
        "prepared_by": "",
        "prepared_at": "",
        "attestations": {
            name: False for name in REQUIRED_SESSION_PREPARATION_ATTESTATIONS
        },
        "notes": [
            "Use non-secret references only.",
            "Do not place passwords, tokens, API keys, cookies, private keys, or connection strings in this file.",
            "Completing this worksheet does not open a provider session or authorize provider actions.",
            "A later corridor must separately authorize session opening after revalidation.",
        ],
    }
    payload["template_hash"] = payload_hash(payload)
    return payload


def validate_controlled_session_preparation_inputs(
    preparation_inputs: Mapping[str, Any] | None,
    *,
    handoff: Mapping[str, Any],
) -> dict[str, Any]:
    payload = dict(preparation_inputs or {})
    checks: dict[str, bool] = {}
    checks["execution_authorization_ready"] = bool(
        handoff.get("execution_authorization_ready")
    )
    checks["frozen_execution_authorization_record_hash_matches"] = (
        _text(payload.get("frozen_execution_authorization_record_hash"))
        == _text(handoff.get("frozen_execution_authorization_record_hash"))
        and bool(_text(handoff.get("frozen_execution_authorization_record_hash")))
    )
    checks["execution_authorization_decision_hash_matches"] = (
        _text(payload.get("execution_authorization_decision_hash"))
        == _text(handoff.get("execution_authorization_decision_hash"))
        and bool(_text(handoff.get("execution_authorization_decision_hash")))
    )
    checks["authorized_source_commit_format_valid"] = bool(
        _COMMIT_REF.fullmatch(_text(payload.get("authorized_source_commit_ref")))
    )
    checks["authorized_source_commit_matches"] = (
        _normalize_commit_ref(payload.get("authorized_source_commit_ref"))
        == _normalize_commit_ref(handoff.get("authorized_source_commit_ref"))
        and bool(_normalize_commit_ref(handoff.get("authorized_source_commit_ref")))
    )
    checks["monthly_cost_ceiling_valid"] = _valid_money(
        payload.get("monthly_cost_ceiling_usd")
    )
    checks["monthly_cost_ceiling_matches"] = (
        _text(payload.get("monthly_cost_ceiling_usd"))
        == _text(handoff.get("monthly_cost_ceiling_usd"))
        and bool(_text(handoff.get("monthly_cost_ceiling_usd")))
    )

    session_start = _parse_utc(payload.get("session_window_starts_at"))
    session_end = _parse_utc(payload.get("session_window_expires_at"))
    authorized_start = _parse_utc(handoff.get("execution_window_starts_at"))
    authorized_end = _parse_utc(handoff.get("execution_window_expires_at"))
    checks["session_window_starts_at_is_utc_iso"] = session_start is not None
    checks["session_window_expires_at_is_utc_iso"] = session_end is not None
    checks["session_window_ordered"] = bool(
        session_start and session_end and session_start < session_end
    )
    checks["session_window_within_execution_authorization"] = bool(
        session_start
        and session_end
        and authorized_start
        and authorized_end
        and authorized_start <= session_start < session_end <= authorized_end
    )

    required_refs = (
        "owner_execution_session_receipt_ref",
        "provider_console_access_preflight_ref",
        "provider_account_team_binding_ref",
        "provider_region_binding_ref",
        "duplicate_resource_lookup_plan_ref",
        "service_creation_form_review_ref",
        "repository_binding_review_ref",
        "non_secret_environment_registration_review_ref",
        "secret_reference_registration_review_ref",
        "health_logging_review_ref",
        "manual_deployment_control_review_ref",
        "rollback_review_ref",
        "cost_ceiling_review_ref",
        "receipt_chain_review_ref",
        "stop_conditions_review_ref",
        "prepared_by",
    )
    for field in required_refs:
        checks[f"{field}_present"] = bool(
            _SAFE_REF.fullmatch(_text(payload.get(field)))
        )
    checks["prepared_at_is_utc_iso"] = (
        _parse_utc(payload.get("prepared_at")) is not None
    )

    attestations = payload.get("attestations")
    if not isinstance(attestations, Mapping):
        attestations = {}
    for name in REQUIRED_SESSION_PREPARATION_ATTESTATIONS:
        checks[f"attestations.{name}"] = _bool(attestations.get(name))

    checks["contains_sensitive_material"] = _contains_sensitive_material(payload)
    errors: list[dict[str, str]] = []
    for name, passed in checks.items():
        if name == "contains_sensitive_material":
            if passed:
                errors.append({
                    "field": name,
                    "code": "sensitive_material_prohibited",
                })
        elif not passed:
            errors.append({"field": name, "code": "required_check_failed"})

    valid = not errors
    report = {
        "schema_version": SCHEMA_VERSION,
        "report_type": "controlled_session_preparation_validation",
        "valid": valid,
        "checks": checks,
        "errors": errors,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    report["report_hash"] = payload_hash(report)
    return report


def build_provider_session_identity_binding(
    provider_inputs: Mapping[str, Any] | None,
    preparation_inputs: Mapping[str, Any] | None,
    *,
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "provider_session_identity_binding",
        "validation_report_hash": validation["report_hash"],
        "binding_valid": bool(validation["valid"]),
        "provider_slug_sha256": _fingerprint(
            (provider_inputs or {}).get("provider_slug")
        ),
        "account_or_team_ref_sha256": _fingerprint(
            (provider_inputs or {}).get("account_or_team_ref")
        ),
        "deployment_region_sha256": _fingerprint(
            (provider_inputs or {}).get("deployment_region")
        ),
        "owner_execution_session_receipt_ref_sha256": _fingerprint(
            (preparation_inputs or {}).get(
                "owner_execution_session_receipt_ref"
            )
        ),
        "raw_provider_values_recorded": False,
        "raw_owner_values_recorded": False,
        "raw_secret_values_recorded": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
    }
    payload["binding_hash"] = payload_hash(payload)
    return payload


def build_duplicate_resource_lookup_preflight(
    *,
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": "duplicate_resource_lookup_preflight",
        "validation_report_hash": validation["report_hash"],
        "ready_for_later_manual_lookup": bool(validation["valid"]),
        "required_lookup_keys": [
            "provider account or team",
            "deployment region",
            "service name simplee-tower-ob-staging",
            "repository LeeTheLilBee/SimpleeMrkTrade",
            "branch tower-ob-integration-dev",
        ],
        "stop_conditions": [
            "matching service already exists",
            "service ownership is ambiguous",
            "region differs from frozen authorization",
            "account or team differs from frozen authorization",
            "monthly cost would exceed the frozen ceiling",
            "authorization window is expired or not yet open",
        ],
        "provider_cli_commands": [],
        "provider_api_requests": [],
        "http_requests": [],
        "browser_actions": [],
        "shell_commands": [],
        "dry_run_only": True,
        "lookup_performed": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
    }
    payload["plan_hash"] = payload_hash(payload)
    return payload


def build_one_service_shell_request(
    preparation_inputs: Mapping[str, Any] | None,
    *,
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "request_type": "one_inert_tower_fronted_staging_service_shell_request",
        "validation_report_hash": validation["report_hash"],
        "request_ready_for_later_separate_session": bool(validation["valid"]),
        "service_name": "simplee-tower-ob-staging",
        "environment_name": "staging",
        "runtime_target": MANAGED_WSGI_TARGET,
        "start_command": MANAGED_START_COMMAND,
        "repository_ref": "LeeTheLilBee/SimpleeMrkTrade",
        "source_branch": "tower-ob-integration-dev",
        "source_commit_sha256": _fingerprint(
            (preparation_inputs or {}).get("authorized_source_commit_ref")
        ),
        "resource_ceiling": {
            "managed_web_service_shells": 1,
            "databases": 0,
            "object_storage_buckets": 0,
            "dns_records": 0,
            "builds": 0,
            "deployments": 0,
        },
        "public_ingress": "tower_only",
        "observatory_separate_service_required": False,
        "auto_deploy": False,
        "build_authorized": False,
        "deployment_authorized": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
    }
    payload["request_hash"] = payload_hash(payload)
    return payload


def build_environment_and_secret_registration_sequence(
    *,
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": "non_secret_environment_and_secret_reference_registration_sequence",
        "validation_report_hash": validation["report_hash"],
        "ready_for_later_separate_session": bool(validation["valid"]),
        "non_secret_environment_names": list(NON_SECRET_ENVIRONMENT_NAMES),
        "secret_reference_names": list(SECRET_REFERENCE_NAMES),
        "environment_values": {},
        "secret_values": {},
        "secret_readback_allowed": False,
        "secret_values_allowed_in_git": False,
        "registration_sequence": [
            "revalidate frozen execution authorization and session window",
            "confirm environment variable names",
            "register non-secret values manually in the provider console",
            "register secret references without reading values back",
            "capture fingerprints and non-secret provider references only",
            "stop before build or deployment",
        ],
        "provider_cli_commands": [],
        "provider_api_requests": [],
        "http_requests": [],
        "browser_actions": [],
        "shell_commands": [],
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "secrets_registered": False,
    }
    payload["plan_hash"] = payload_hash(payload)
    return payload


def build_operational_control_rehearsal(
    *,
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "rehearsal_type": "health_logging_manual_control_and_rollback_rehearsal",
        "validation_report_hash": validation["report_hash"],
        "ready_for_later_separate_session": bool(validation["valid"]),
        "health_check_path": "/tower/healthz",
        "required_controls": [
            "provider health checks configured",
            "deployment logs enabled",
            "access logs enabled",
            "automatic deployment disabled",
            "manual deployment control confirmed",
            "rollback target bound to authorized source commit",
            "Tower remains the only browser front door",
            "Observatory remains mounted inside the Tower-fronted service",
        ],
        "stop_conditions": [
            "health path differs",
            "automatic deploy cannot be disabled",
            "logs unavailable",
            "rollback target unavailable",
            "Tower-only ingress cannot be preserved",
            "provider attempts to build or deploy automatically",
        ],
        "provider_cli_commands": [],
        "provider_api_requests": [],
        "http_requests": [],
        "browser_actions": [],
        "shell_commands": [],
        "rehearsal_only": True,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    payload["rehearsal_hash"] = payload_hash(payload)
    return payload


def build_receipt_chain_and_stop_gate(
    *,
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "contract_type": "controlled_session_receipt_chain_and_stop_gate",
        "validation_report_hash": validation["report_hash"],
        "required_receipt_order": [
            "session_opening_authorization_receipt",
            "provider_session_opened_receipt",
            "provider_login_receipt",
            "duplicate_resource_lookup_receipt",
            "service_shell_selected_or_created_receipt",
            "repository_binding_receipt",
            "non_secret_environment_registration_receipt",
            "secret_reference_registration_receipt",
            "health_logging_manual_control_receipt",
            "rollback_binding_receipt",
            "stop_before_build_and_deployment_receipt",
            "controlled_session_closeout_receipt",
        ],
        "mandatory_stop_receipt": True,
        "hash_chain_required": True,
        "raw_secret_values_prohibited": True,
        "build_receipt_allowed": False,
        "deployment_receipt_allowed": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    payload["contract_hash"] = payload_hash(payload)
    return payload


def _freeze_from_parts(
    handoff: Mapping[str, Any],
    validation: Mapping[str, Any],
    identity: Mapping[str, Any],
    lookup: Mapping[str, Any],
    service: Mapping[str, Any],
    environment: Mapping[str, Any],
    operational: Mapping[str, Any],
    receipt: Mapping[str, Any],
    controlled_session_preparation_inputs: Mapping[str, Any] | None,
) -> dict[str, Any]:
    frozen = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "frozen_controlled_provider_session_preparation",
        "execution_authorization_handoff_hash": handoff["handoff_hash"],
        "frozen_execution_authorization_record_hash": handoff[
            "frozen_execution_authorization_record_hash"
        ],
        "execution_authorization_decision_hash": handoff[
            "execution_authorization_decision_hash"
        ],
        "session_preparation_validation_report_hash": validation["report_hash"],
        "provider_session_identity_binding_hash": identity["binding_hash"],
        "duplicate_resource_lookup_preflight_hash": lookup["plan_hash"],
        "one_service_shell_request_hash": service["request_hash"],
        "environment_and_secret_registration_sequence_hash": environment[
            "plan_hash"
        ],
        "operational_control_rehearsal_hash": operational["rehearsal_hash"],
        "receipt_chain_and_stop_gate_hash": receipt["contract_hash"],
        "preparation_valid": validation["valid"],
        "provider_slug_sha256": identity["provider_slug_sha256"],
        "account_or_team_ref_sha256": identity["account_or_team_ref_sha256"],
        "deployment_region_sha256": identity["deployment_region_sha256"],
        "owner_execution_session_receipt_ref_sha256": identity[
            "owner_execution_session_receipt_ref_sha256"
        ],
        "authorized_source_commit_sha256": _fingerprint(
            (controlled_session_preparation_inputs or {}).get(
                "authorized_source_commit_ref"
            )
        ),
        "prepared_by_sha256": _fingerprint(
            (controlled_session_preparation_inputs or {}).get("prepared_by")
        ),
        "raw_provider_values_recorded": False,
        "raw_owner_values_recorded": False,
        "raw_review_values_recorded": False,
        "raw_secret_values_recorded": False,
        "frozen": True,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    frozen["frozen_session_preparation_packet_hash"] = payload_hash(frozen)
    return frozen


def _decision_from_parts(
    handoff: Mapping[str, Any],
    frozen: Mapping[str, Any],
) -> dict[str, Any]:
    if not handoff["execution_authorization_ready"]:
        final_decision = handoff["final_decision"] or HOLD_EXECUTION_AUTHORIZATION
    elif not frozen["preparation_valid"]:
        final_decision = HOLD_SESSION_PREPARATION
    else:
        final_decision = READY_DECISION

    ready = bool(
        handoff["execution_authorization_ready"]
        and frozen["preparation_valid"]
    )
    decision = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "controlled_provider_session_preparation_decision",
        "execution_authorization_handoff_hash": handoff["handoff_hash"],
        "frozen_session_preparation_packet_hash": frozen[
            "frozen_session_preparation_packet_hash"
        ],
        "session_preparation_valid": frozen["preparation_valid"],
        "ready_for_separate_controlled_provider_session_opening_authorization": ready,
        "provider_session_opening_authorized": False,
        "provider_login_authorized": False,
        "provider_calls_authorized": False,
        "one_inert_web_service_creation_authorized": False,
        "secret_reference_registration_authorized": False,
        "database_creation_authorized": False,
        "object_storage_creation_authorized": False,
        "dns_changes_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
        "official_walkthrough_performed": False,
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
        "final_decision": final_decision,
    }
    decision["decision_hash"] = payload_hash(decision)
    return decision


def _plan_from_decision(
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    plan = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": "inert_controlled_provider_session_opening_authorization_plan",
        "session_preparation_decision_hash": decision["decision_hash"],
        "ready_for_later_separate_authorization": decision[
            "ready_for_separate_controlled_provider_session_opening_authorization"
        ],
        "future_authorization_sequence": [
            "revalidate the frozen Step 090 execution authorization",
            "revalidate the frozen Step 100 session-preparation packet",
            "obtain a fresh Tower owner step-up receipt and challenge confirmation",
            "bind a new session-opening authorization to the remaining time window",
            "open a later controlled provider session only after authorization",
            "stop before build or deployment",
        ],
        "provider_cli_commands": [],
        "provider_api_requests": [],
        "http_requests": [],
        "browser_actions": [],
        "shell_commands": [],
        "dry_run_only": True,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
        "final_decision": decision["final_decision"],
    }
    plan["plan_hash"] = payload_hash(plan)
    return plan


def _build_preparation_parts(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
    execution_preparation_inputs: Mapping[str, Any] | None,
    execution_authorization_decision: Mapping[str, Any] | None,
    controlled_session_preparation_inputs: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], ...]:
    cache_key = payload_hash({
        "repository_root": str(Path(repository_root).resolve()),
        "provider_inputs": provider_inputs or {},
        "provider_review_owner_decision": provider_review_owner_decision or {},
        "review_inputs": review_inputs or {},
        "provisioning_decision": provisioning_decision or {},
        "execution_preparation_inputs": execution_preparation_inputs or {},
        "execution_authorization_decision": execution_authorization_decision or {},
        "controlled_session_preparation_inputs": controlled_session_preparation_inputs or {},
    })
    cached = _SESSION_PREPARATION_PARTS_CACHE.get(cache_key)
    if cached is not None:
        return tuple(_clone_json(item) for item in cached)

    handoff = build_execution_authorization_handoff(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
        execution_preparation_inputs,
        execution_authorization_decision,
    )
    validation = validate_controlled_session_preparation_inputs(
        controlled_session_preparation_inputs,
        handoff=handoff,
    )
    identity = build_provider_session_identity_binding(
        provider_inputs,
        controlled_session_preparation_inputs,
        validation=validation,
    )
    lookup = build_duplicate_resource_lookup_preflight(
        validation=validation
    )
    service = build_one_service_shell_request(
        controlled_session_preparation_inputs,
        validation=validation,
    )
    environment = build_environment_and_secret_registration_sequence(
        validation=validation
    )
    operational = build_operational_control_rehearsal(
        validation=validation
    )
    receipt = build_receipt_chain_and_stop_gate(validation=validation)
    frozen = _freeze_from_parts(
        handoff,
        validation,
        identity,
        lookup,
        service,
        environment,
        operational,
        receipt,
        controlled_session_preparation_inputs,
    )
    decision = _decision_from_parts(handoff, frozen)
    plan = _plan_from_decision(decision)
    parts = (
        handoff,
        validation,
        identity,
        lookup,
        service,
        environment,
        operational,
        receipt,
        frozen,
        decision,
        plan,
    )
    _SESSION_PREPARATION_PARTS_CACHE[cache_key] = tuple(
        _clone_json(item) for item in parts
    )
    return parts


def freeze_controlled_session_preparation_packet(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
    execution_preparation_inputs: Mapping[str, Any] | None,
    execution_authorization_decision: Mapping[str, Any] | None,
    controlled_session_preparation_inputs: Mapping[str, Any] | None,
) -> dict[str, Any]:
    return _build_preparation_parts(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
        execution_preparation_inputs,
        execution_authorization_decision,
        controlled_session_preparation_inputs,
    )[8]


def build_controlled_session_preparation_decision(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
    execution_preparation_inputs: Mapping[str, Any] | None,
    execution_authorization_decision: Mapping[str, Any] | None,
    controlled_session_preparation_inputs: Mapping[str, Any] | None,
) -> dict[str, Any]:
    return _build_preparation_parts(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
        execution_preparation_inputs,
        execution_authorization_decision,
        controlled_session_preparation_inputs,
    )[9]


def build_inert_session_opening_authorization_plan(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
    execution_preparation_inputs: Mapping[str, Any] | None,
    execution_authorization_decision: Mapping[str, Any] | None,
    controlled_session_preparation_inputs: Mapping[str, Any] | None,
) -> dict[str, Any]:
    return _build_preparation_parts(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
        execution_preparation_inputs,
        execution_authorization_decision,
        controlled_session_preparation_inputs,
    )[10]


def build_current_controlled_session_preparation_state(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None = None,
    provider_review_owner_decision: Mapping[str, Any] | None = None,
    review_inputs: Mapping[str, Any] | None = None,
    provisioning_decision: Mapping[str, Any] | None = None,
    execution_preparation_inputs: Mapping[str, Any] | None = None,
    execution_authorization_decision: Mapping[str, Any] | None = None,
    controlled_session_preparation_inputs: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    (
        handoff,
        validation,
        _identity,
        _lookup,
        _service,
        _environment,
        _operational,
        _receipt,
        _frozen,
        decision,
        plan,
    ) = _build_preparation_parts(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
        execution_preparation_inputs,
        execution_authorization_decision,
        controlled_session_preparation_inputs,
    )

    blockers: list[dict[str, str]] = []
    if not handoff["execution_authorization_ready"]:
        blockers.append({
            "requirement": "completed_execution_authorization",
            "status": "valid_execution_authorization_required",
        })
    for error in validation["errors"]:
        blockers.append({
            "requirement": error["field"],
            "status": error["code"],
        })

    state = {
        "schema_version": SCHEMA_VERSION,
        "closed_layer": "MANAGED_STAGING_CONTROLLED_PROVIDER_PROVISIONING_EXECUTION_SESSION_PREPARATION",
        "closed_through_step": 100,
        "runtime_target": MANAGED_WSGI_TARGET,
        "runtime_topology": "single_tower_fronted_managed_python_web_service",
        "execution_authorization_handoff_hash": handoff["handoff_hash"],
        "session_preparation_validation_report_hash": validation["report_hash"],
        "session_preparation_decision_hash": decision["decision_hash"],
        "inert_session_opening_authorization_plan_hash": plan["plan_hash"],
        "execution_authorization_ready": handoff[
            "execution_authorization_ready"
        ],
        "session_preparation_inputs_valid": validation["valid"],
        "ready_for_separate_controlled_provider_session_opening_authorization": decision[
            "ready_for_separate_controlled_provider_session_opening_authorization"
        ],
        "blocking_requirements": blockers,
        "blocking_requirement_count": len(blockers),
        "provider_session_opening_authorized": False,
        "provider_login_authorized": False,
        "provider_calls_authorized": False,
        "one_inert_web_service_creation_authorized": False,
        "secret_reference_registration_authorized": False,
        "database_creation_authorized": False,
        "object_storage_creation_authorized": False,
        "dns_changes_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
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
        "next_boundary": "managed_staging_controlled_provider_provisioning_execution_session_opening_authorization",
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


def write_controlled_session_preparation_worksheets(
    output_directory: str | Path,
    *,
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None = None,
    provider_review_owner_decision: Mapping[str, Any] | None = None,
    review_inputs: Mapping[str, Any] | None = None,
    provisioning_decision: Mapping[str, Any] | None = None,
    execution_preparation_inputs: Mapping[str, Any] | None = None,
    execution_authorization_decision: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    output = Path(output_directory).resolve()
    root = Path(repository_root).resolve()
    if output == root or root in output.parents:
        raise ValueError(
            "Controlled session-preparation worksheets must be written outside the repository."
        )
    handoff = build_execution_authorization_handoff(
        root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
        execution_preparation_inputs,
        execution_authorization_decision,
    )
    preparation_path = write_json(
        output / "tower_ob_controlled_provider_session_preparation.json",
        controlled_session_preparation_input_template(handoff),
    )
    opening_placeholder = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "controlled_provider_session_opening_authorization_placeholder",
        "decision": "HOLD",
        "frozen_session_preparation_packet_hash": "",
        "owner_id": "",
        "tower_step_up_receipt_ref": "",
        "challenge_id": "",
        "challenge_phrase_confirmation": "",
        "authorized_session_starts_at": "",
        "authorized_session_expires_at": "",
        "provider_session_opening_authorized": False,
        "provider_login_authorized": False,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "secret_reference_registration_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
        "notes": [
            "This placeholder is not a provider session or authorization.",
            "A later corridor must bind a fresh Tower owner decision to the frozen Step 100 preparation packet.",
        ],
    }
    opening_placeholder["template_hash"] = payload_hash(opening_placeholder)
    opening_path = write_json(
        output / "tower_ob_controlled_provider_session_opening_authorization_placeholder.json",
        opening_placeholder,
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "controlled_session_preparation_path": str(preparation_path),
        "session_opening_authorization_placeholder_path": str(opening_path),
        "execution_authorization_ready": handoff[
            "execution_authorization_ready"
        ],
        "contains_secret_values": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    manifest_path = write_json(output / "worksheet_manifest.json", manifest)
    return {
        "controlled_session_preparation_path": str(preparation_path),
        "session_opening_authorization_placeholder_path": str(opening_path),
        "manifest_path": str(manifest_path),
    }


def blank_current_inputs(
    repository_root: str | Path,
) -> tuple[dict, dict, dict, dict, dict, dict, dict]:
    (
        provider,
        review_owner,
        review,
        provisioning,
        execution_preparation,
        execution_authorization,
    ) = blank_execution_authorization_inputs(repository_root)
    handoff = build_execution_authorization_handoff(
        repository_root,
        provider,
        review_owner,
        review,
        provisioning,
        execution_preparation,
        execution_authorization,
    )
    session_preparation = controlled_session_preparation_input_template(handoff)
    return (
        provider,
        review_owner,
        review,
        provisioning,
        execution_preparation,
        execution_authorization,
        session_preparation,
    )


__all__ = [
    "HOLD_EXECUTION_AUTHORIZATION",
    "HOLD_PROVIDER_INPUTS",
    "HOLD_SESSION_PREPARATION",
    "NON_SECRET_ENVIRONMENT_NAMES",
    "READY_DECISION",
    "REQUIRED_SESSION_PREPARATION_ATTESTATIONS",
    "SCHEMA_VERSION",
    "SECRET_REFERENCE_NAMES",
    "blank_current_inputs",
    "build_controlled_session_preparation_decision",
    "build_current_controlled_session_preparation_state",
    "build_duplicate_resource_lookup_preflight",
    "build_environment_and_secret_registration_sequence",
    "build_execution_authorization_handoff",
    "build_inert_session_opening_authorization_plan",
    "build_one_service_shell_request",
    "build_operational_control_rehearsal",
    "build_provider_session_identity_binding",
    "build_receipt_chain_and_stop_gate",
    "controlled_session_preparation_input_template",
    "freeze_controlled_session_preparation_packet",
    "validate_controlled_session_preparation_inputs",
    "write_controlled_session_preparation_worksheets",
]
