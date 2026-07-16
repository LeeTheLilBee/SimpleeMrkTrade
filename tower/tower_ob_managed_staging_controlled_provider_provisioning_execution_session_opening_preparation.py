"""Controlled provider-session opening preparation contracts.

This layer prepares a later, separately authorized provider-session opening
operation from the frozen Step 110 owner authorization. It performs no provider
login, browser automation, CLI/API/HTTP calls, resource creation, secret
registration or readback, build, deployment, DNS change, database/object-storage
creation, or official Observatory walkthrough.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping

from tower.tower_ob_managed_staging_controlled_provider_provisioning_execution_session_opening_authorization import (
    blank_current_inputs as blank_session_opening_authorization_inputs,
    build_completed_session_preparation_handoff,
    build_session_opening_authorization_decision,
    freeze_session_opening_authorization_record,
)
from tower.tower_ob_managed_staging_runtime import MANAGED_WSGI_TARGET, payload_hash

SCHEMA_VERSION = "simplee.tower_ob.controlled_provider_session_opening_preparation.v1"
READY_DECISION = "GO_READY_FOR_SEPARATE_CONTROLLED_PROVIDER_SESSION_OPENING_EXECUTION_AUTHORIZATION"
HOLD_PROVIDER_INPUTS = "NO_GO_HOLD_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION_REQUIRED"
HOLD_OPENING_AUTHORIZATION = "NO_GO_HOLD_CONTROLLED_SESSION_OPENING_AUTHORIZATION_REQUIRED"
HOLD_OPENING_PREPARATION = "NO_GO_HOLD_CONTROLLED_SESSION_OPENING_PREPARATION_REQUIRED"

NON_SECRET_ENVIRONMENT_NAMES = (
    "SIMPLEE_RUNTIME_ENV",
    "SIMPLEE_TOWER_OB_MODE",
    "SIMPLEE_PUBLIC_BASE_URL",
    "SIMPLEE_SESSION_COOKIE_SECURE",
    "SIMPLEE_SESSION_COOKIE_SAMESITE",
    "SIMPLEE_MANAGED_STAGING_PROVIDER",
    "SIMPLEE_MANAGED_STAGING_REGION",
)
SECRET_REFERENCE_NAMES = (
    "SIMPLEE_SESSION_SECRET_REF",
    "SIMPLEE_OWNER_PASSWORD_HASH_REF",
    "SIMPLEE_DATABASE_URL_REF",
)

REQUIRED_OPENING_PREPARATION_ATTESTATIONS = (
    "staging_only_scope_confirmed",
    "single_tower_fronted_service_confirmed",
    "tower_only_public_ingress_confirmed",
    "observatory_separate_service_not_required",
    "frozen_session_opening_authorization_hash_confirmed",
    "session_opening_authorization_decision_hash_confirmed",
    "authorized_source_commit_confirmed",
    "session_window_confirmed",
    "authorization_expiry_confirmed",
    "monthly_cost_ceiling_confirmed",
    "provider_identity_fingerprints_confirmed",
    "owner_step_up_receipt_fingerprint_confirmed",
    "fresh_owner_session_opening_preparation_receipt_confirmed",
    "manual_provider_console_entrypoint_reviewed",
    "isolated_browser_session_required",
    "private_browsing_profile_required",
    "credential_manager_or_provider_login_ui_only",
    "credentials_must_not_enter_repository_or_worksheet",
    "cookies_and_session_tokens_must_not_be_captured",
    "provider_identity_revalidation_required_before_login",
    "account_team_revalidation_required_before_login",
    "region_revalidation_required_before_login",
    "authorization_window_revalidation_required_before_login",
    "duplicate_resource_lookup_required_after_login_before_creation",
    "stop_if_duplicate_or_ambiguous_resource_confirmed",
    "one_inert_web_service_shell_limit_confirmed",
    "repository_branch_commit_binding_confirmed",
    "non_secret_environment_names_only_confirmed",
    "secret_reference_registration_without_readback_confirmed",
    "receipt_chain_confirmed",
    "session_close_and_revocation_plan_confirmed",
    "stop_before_resource_creation_confirmed",
    "stop_before_secret_registration_confirmed",
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

_SAFE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+ #(),-]{1,299}$")
_COMMIT_REF = re.compile(r"^(?:commit/)?[0-9a-f]{40}$", re.I)
_ISO_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
_MONEY = re.compile(r"^\d{1,6}(?:\.\d{1,2})?$")
_SENSITIVE_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
    re.compile(r"\b(?:api[_-]?key|access[_-]?token|token|secret|password|cookie)\s*[:=]\s*\S+", re.I),
    re.compile(r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?)://[^/\s]+:[^@\s]+@", re.I),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
)
_PARTS_CACHE: dict[str, tuple[dict[str, Any], ...]] = {}


def _clone(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, default=str))


def _text(value: Any) -> str:
    return str(value or "").strip()


def _bool(value: Any) -> bool:
    return value if isinstance(value, bool) else _text(value).lower() in {"1", "true", "yes", "on", "enabled", "attested"}


def _fingerprint(value: Any) -> str | None:
    value = _text(value)
    return hashlib.sha256(value.encode()).hexdigest() if value else None


def _parse_utc(value: Any) -> datetime | None:
    value = _text(value)
    if not _ISO_UTC.fullmatch(value):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _valid_money(value: Any) -> bool:
    value = _text(value)
    if not _MONEY.fullmatch(value):
        return False
    try:
        amount = Decimal(value)
    except InvalidOperation:
        return False
    return Decimal("0") < amount <= Decimal("10000")


def _contains_sensitive(value: Any) -> bool:
    rendered = json.dumps(value, sort_keys=True, default=str)
    return any(pattern.search(rendered) for pattern in _SENSITIVE_PATTERNS)


def _normalize_commit(value: Any) -> str:
    value = _text(value)
    return value.split("/", 1)[1].lower() if value.lower().startswith("commit/") else value.lower()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_session_opening_authorization_handoff(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
    execution_preparation_inputs: Mapping[str, Any] | None,
    execution_authorization_decision: Mapping[str, Any] | None,
    controlled_session_preparation_inputs: Mapping[str, Any] | None,
    session_opening_authorization_decision: Mapping[str, Any] | None,
) -> dict[str, Any]:
    args = (
        repository_root,
        provider_inputs or {},
        provider_review_owner_decision or {},
        review_inputs or {},
        provisioning_decision or {},
        execution_preparation_inputs or {},
        execution_authorization_decision or {},
        controlled_session_preparation_inputs or {},
        session_opening_authorization_decision or {},
    )
    decision = build_session_opening_authorization_decision(*args)
    frozen = freeze_session_opening_authorization_record(*args)
    session_preparation_handoff = build_completed_session_preparation_handoff(
        repository_root, provider_inputs or {}, provider_review_owner_decision or {},
        review_inputs or {}, provisioning_decision or {}, execution_preparation_inputs or {},
        execution_authorization_decision or {}, controlled_session_preparation_inputs or {},
    )
    ready = bool(
        decision.get("authorization_valid")
        and decision.get("ready_for_separate_controlled_provider_session_opening_preparation")
    )
    handoff = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "controlled_provider_session_opening_authorization_handoff",
        "frozen_session_opening_authorization_record_hash": frozen.get("frozen_session_opening_authorization_record_hash", ""),
        "session_opening_authorization_decision_hash": decision.get("decision_hash", ""),
        "frozen_session_preparation_packet_hash": frozen.get("frozen_session_preparation_packet_hash", ""),
        "authorized_source_commit_ref": _text((session_opening_authorization_decision or {}).get("authorized_source_commit_ref")),
        "authorized_session_starts_at": _text((session_opening_authorization_decision or {}).get("authorized_session_starts_at")),
        "authorized_session_expires_at": _text((session_opening_authorization_decision or {}).get("authorized_session_expires_at")),
        "authorization_expires_at": _text((session_opening_authorization_decision or {}).get("authorization_expires_at")),
        "monthly_cost_ceiling_usd": _text((session_opening_authorization_decision or {}).get("monthly_cost_ceiling_usd")),
        "provider_slug_sha256": session_preparation_handoff.get("provider_slug_sha256"),
        "account_or_team_ref_sha256": session_preparation_handoff.get("account_or_team_ref_sha256"),
        "deployment_region_sha256": session_preparation_handoff.get("deployment_region_sha256"),
        "owner_id_sha256": frozen.get("owner_id_sha256"),
        "tower_step_up_receipt_ref_sha256": frozen.get("tower_step_up_receipt_ref_sha256"),
        "session_opening_authorization_valid": bool(decision.get("authorization_valid")),
        "authorization_handoff_ready": ready,
        "provider_session_opening_authorized": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
        "final_decision": decision.get("final_decision", HOLD_OPENING_AUTHORIZATION),
    }
    handoff["handoff_hash"] = payload_hash(handoff)
    return handoff


def session_opening_preparation_input_template(handoff: Mapping[str, Any]) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "controlled_provider_session_opening_preparation_inputs",
        "frozen_session_opening_authorization_record_hash": _text(handoff.get("frozen_session_opening_authorization_record_hash")),
        "session_opening_authorization_decision_hash": _text(handoff.get("session_opening_authorization_decision_hash")),
        "authorized_source_commit_ref": _text(handoff.get("authorized_source_commit_ref")),
        "authorized_session_starts_at": _text(handoff.get("authorized_session_starts_at")),
        "authorized_session_expires_at": _text(handoff.get("authorized_session_expires_at")),
        "authorization_expires_at": _text(handoff.get("authorization_expires_at")),
        "monthly_cost_ceiling_usd": _text(handoff.get("monthly_cost_ceiling_usd")),
        "owner_session_opening_preparation_receipt_ref": "",
        "provider_console_entrypoint_review_ref": "",
        "provider_identity_revalidation_ref": "",
        "account_team_revalidation_ref": "",
        "region_revalidation_ref": "",
        "authorization_window_revalidation_ref": "",
        "duplicate_resource_lookup_preflight_ref": "",
        "browser_session_isolation_plan_ref": "",
        "credential_custody_preflight_ref": "",
        "one_service_shell_form_preflight_ref": "",
        "repository_binding_preflight_ref": "",
        "non_secret_environment_names_preflight_ref": "",
        "secret_reference_custody_preflight_ref": "",
        "receipt_chain_preflight_ref": "",
        "session_close_and_revocation_plan_ref": "",
        "prepared_by": "",
        "prepared_at": "",
        "attestations": {name: False for name in REQUIRED_OPENING_PREPARATION_ATTESTATIONS},
        "notes": [
            "Record references and fingerprints only; never record credentials, cookies, tokens, or secret values.",
            "This packet prepares a later execution authorization and performs no provider login or calls.",
        ],
    }
    payload["template_hash"] = payload_hash(payload)
    return payload


def validate_session_opening_preparation_inputs(
    inputs: Mapping[str, Any] | None,
    *,
    handoff: Mapping[str, Any],
) -> dict[str, Any]:
    payload = dict(inputs or {})
    checks: dict[str, bool] = {
        "authorization_handoff_ready": bool(handoff.get("authorization_handoff_ready")),
        "frozen_session_opening_authorization_record_hash_matches": _text(payload.get("frozen_session_opening_authorization_record_hash")) == _text(handoff.get("frozen_session_opening_authorization_record_hash")) and bool(_text(handoff.get("frozen_session_opening_authorization_record_hash"))),
        "session_opening_authorization_decision_hash_matches": _text(payload.get("session_opening_authorization_decision_hash")) == _text(handoff.get("session_opening_authorization_decision_hash")) and bool(_text(handoff.get("session_opening_authorization_decision_hash"))),
        "authorized_source_commit_format_valid": bool(_COMMIT_REF.fullmatch(_text(payload.get("authorized_source_commit_ref")))),
        "authorized_source_commit_matches": _normalize_commit(payload.get("authorized_source_commit_ref")) == _normalize_commit(handoff.get("authorized_source_commit_ref")) and bool(_normalize_commit(handoff.get("authorized_source_commit_ref"))),
        "monthly_cost_ceiling_valid": _valid_money(payload.get("monthly_cost_ceiling_usd")),
        "monthly_cost_ceiling_matches": _text(payload.get("monthly_cost_ceiling_usd")) == _text(handoff.get("monthly_cost_ceiling_usd")) and bool(_text(handoff.get("monthly_cost_ceiling_usd"))),
        "owner_session_opening_preparation_receipt_ref_present": bool(_SAFE_REF.fullmatch(_text(payload.get("owner_session_opening_preparation_receipt_ref")))),
        "prepared_by_present": bool(_SAFE_REF.fullmatch(_text(payload.get("prepared_by")))),
        "prepared_at_is_utc_iso": _parse_utc(payload.get("prepared_at")) is not None,
    }
    for field in (
        "provider_console_entrypoint_review_ref",
        "provider_identity_revalidation_ref",
        "account_team_revalidation_ref",
        "region_revalidation_ref",
        "authorization_window_revalidation_ref",
        "duplicate_resource_lookup_preflight_ref",
        "browser_session_isolation_plan_ref",
        "credential_custody_preflight_ref",
        "one_service_shell_form_preflight_ref",
        "repository_binding_preflight_ref",
        "non_secret_environment_names_preflight_ref",
        "secret_reference_custody_preflight_ref",
        "receipt_chain_preflight_ref",
        "session_close_and_revocation_plan_ref",
    ):
        checks[f"{field}_present"] = bool(_SAFE_REF.fullmatch(_text(payload.get(field))))

    session_start = _parse_utc(payload.get("authorized_session_starts_at"))
    session_end = _parse_utc(payload.get("authorized_session_expires_at"))
    handoff_start = _parse_utc(handoff.get("authorized_session_starts_at"))
    handoff_end = _parse_utc(handoff.get("authorized_session_expires_at"))
    auth_expiry = _parse_utc(payload.get("authorization_expires_at"))
    handoff_auth_expiry = _parse_utc(handoff.get("authorization_expires_at"))
    prepared_at = _parse_utc(payload.get("prepared_at"))
    checks["session_window_ordered"] = bool(session_start and session_end and session_start < session_end)
    checks["session_window_matches_authorization"] = bool(session_start and session_end and handoff_start and handoff_end and session_start == handoff_start and session_end == handoff_end)
    checks["authorization_expiry_matches"] = bool(auth_expiry and handoff_auth_expiry and auth_expiry == handoff_auth_expiry)
    checks["preparation_occurs_before_authorization_expiry"] = bool(prepared_at and auth_expiry and prepared_at < auth_expiry)

    attestations = payload.get("attestations") if isinstance(payload.get("attestations"), Mapping) else {}
    for name in REQUIRED_OPENING_PREPARATION_ATTESTATIONS:
        checks[f"attestations.{name}"] = _bool(attestations.get(name))
    checks["contains_sensitive_material"] = _contains_sensitive(payload)

    errors = []
    for name, passed in checks.items():
        if name == "contains_sensitive_material":
            if passed:
                errors.append({"field": name, "code": "sensitive_material_prohibited"})
        elif not passed:
            errors.append({"field": name, "code": "required_check_failed"})
    report = {"schema_version": SCHEMA_VERSION, "valid": not errors, "checks": checks, "errors": errors}
    report["report_hash"] = payload_hash(report)
    return report


def build_provider_identity_and_session_isolation_preflight(
    handoff: Mapping[str, Any],
    inputs: Mapping[str, Any] | None,
    validation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload = dict(inputs or {})
    preflight = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "provider_identity_and_session_isolation_preflight",
        "preparation_valid": bool((validation or {}).get("valid")),
        "provider_slug_sha256": handoff.get("provider_slug_sha256"),
        "account_or_team_ref_sha256": handoff.get("account_or_team_ref_sha256"),
        "deployment_region_sha256": handoff.get("deployment_region_sha256"),
        "owner_id_sha256": handoff.get("owner_id_sha256"),
        "tower_step_up_receipt_ref_sha256": handoff.get("tower_step_up_receipt_ref_sha256"),
        "owner_session_opening_preparation_receipt_ref_sha256": _fingerprint(payload.get("owner_session_opening_preparation_receipt_ref")),
        "provider_console_entrypoint_review_ref_sha256": _fingerprint(payload.get("provider_console_entrypoint_review_ref")),
        "isolated_browser_session_required": True,
        "private_browsing_profile_required": True,
        "cookies_or_session_tokens_recorded": False,
        "credentials_recorded": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
    }
    preflight["preflight_hash"] = payload_hash(preflight)
    return preflight


def build_duplicate_resource_and_binding_revalidation_preflight(
    handoff: Mapping[str, Any],
    inputs: Mapping[str, Any] | None,
    validation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload = dict(inputs or {})
    preflight = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "duplicate_resource_and_binding_revalidation_preflight",
        "preparation_valid": bool((validation or {}).get("valid")),
        "provider_identity_revalidation_ref_sha256": _fingerprint(payload.get("provider_identity_revalidation_ref")),
        "account_team_revalidation_ref_sha256": _fingerprint(payload.get("account_team_revalidation_ref")),
        "region_revalidation_ref_sha256": _fingerprint(payload.get("region_revalidation_ref")),
        "authorization_window_revalidation_ref_sha256": _fingerprint(payload.get("authorization_window_revalidation_ref")),
        "duplicate_resource_lookup_preflight_ref_sha256": _fingerprint(payload.get("duplicate_resource_lookup_preflight_ref")),
        "duplicate_lookup_must_run_after_login_before_creation": True,
        "stop_on_duplicate_or_ambiguous_result": True,
        "provider_calls_performed": False,
        "resources_created": False,
    }
    preflight["preflight_hash"] = payload_hash(preflight)
    return preflight


def build_credential_custody_and_authorization_window_preflight(
    handoff: Mapping[str, Any],
    inputs: Mapping[str, Any] | None,
    validation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload = dict(inputs or {})
    preflight = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "credential_custody_and_authorization_window_preflight",
        "preparation_valid": bool((validation or {}).get("valid")),
        "browser_session_isolation_plan_ref_sha256": _fingerprint(payload.get("browser_session_isolation_plan_ref")),
        "credential_custody_preflight_ref_sha256": _fingerprint(payload.get("credential_custody_preflight_ref")),
        "authorized_session_starts_at": _text(handoff.get("authorized_session_starts_at")),
        "authorized_session_expires_at": _text(handoff.get("authorized_session_expires_at")),
        "authorization_expires_at": _text(handoff.get("authorization_expires_at")),
        "credential_source": "provider_login_ui_or_approved_password_manager_only",
        "credential_values_recorded": False,
        "credential_readback_authorized": False,
        "session_cookie_capture_authorized": False,
        "provider_login_performed": False,
    }
    preflight["preflight_hash"] = payload_hash(preflight)
    return preflight


def build_one_inert_service_opening_request(
    inputs: Mapping[str, Any] | None,
    validation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload = dict(inputs or {})
    valid = bool((validation or {}).get("valid"))
    request = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "one_inert_tower_fronted_service_opening_request",
        "preparation_valid": valid,
        "runtime_target": MANAGED_WSGI_TARGET,
        "runtime_topology": "single_tower_fronted_managed_python_web_service",
        "future_resource_ceiling": {"managed_web_service_shells": 1 if valid else 0, "databases": 0, "object_storage_buckets": 0, "dns_changes": 0},
        "one_service_shell_form_preflight_ref_sha256": _fingerprint(payload.get("one_service_shell_form_preflight_ref")),
        "repository_binding_preflight_ref_sha256": _fingerprint(payload.get("repository_binding_preflight_ref")),
        "authorized_source_commit_sha256": _fingerprint(payload.get("authorized_source_commit_ref")),
        "public_ingress_owner": "tower_only",
        "observatory_separate_service_required": False,
        "resource_creation_authorized": False,
        "secret_registration_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
        "resources_created": False,
    }
    request["request_hash"] = payload_hash(request)
    return request


def build_environment_and_secret_reference_opening_sequence(
    inputs: Mapping[str, Any] | None,
    validation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload = dict(inputs or {})
    sequence = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "environment_and_secret_reference_opening_sequence",
        "preparation_valid": bool((validation or {}).get("valid")),
        "non_secret_environment_names": list(NON_SECRET_ENVIRONMENT_NAMES),
        "secret_reference_names": list(SECRET_REFERENCE_NAMES),
        "non_secret_environment_names_preflight_ref_sha256": _fingerprint(payload.get("non_secret_environment_names_preflight_ref")),
        "secret_reference_custody_preflight_ref_sha256": _fingerprint(payload.get("secret_reference_custody_preflight_ref")),
        "secret_values_included": False,
        "secret_readback_authorized": False,
        "repository_secret_values_authorized": False,
        "secret_registration_authorized": False,
        "secrets_registered": False,
    }
    sequence["sequence_hash"] = payload_hash(sequence)
    return sequence


def build_opening_receipt_chain_close_and_stop_gate(
    inputs: Mapping[str, Any] | None,
    validation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload = dict(inputs or {})
    gate = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "controlled_provider_session_opening_receipt_chain_close_and_stop_gate",
        "preparation_valid": bool((validation or {}).get("valid")),
        "receipt_chain_preflight_ref_sha256": _fingerprint(payload.get("receipt_chain_preflight_ref")),
        "session_close_and_revocation_plan_ref_sha256": _fingerprint(payload.get("session_close_and_revocation_plan_ref")),
        "required_receipt_order": [
            "step110_authorization_revalidation_receipt",
            "owner_session_opening_preparation_receipt",
            "provider_console_entrypoint_receipt",
            "provider_identity_revalidation_receipt",
            "provider_authentication_receipt",
            "duplicate_resource_lookup_receipt",
            "stop_before_resource_creation_receipt",
            "provider_session_close_receipt",
            "provider_session_revocation_or_logout_receipt",
        ],
        "mandatory_stop_conditions": [
            "authorization missing invalid expired or hash-mismatched",
            "provider identity account team or region differs from frozen fingerprints",
            "provider login requires credential export copy paste or recording",
            "duplicate resource exists or lookup result is ambiguous",
            "resource form exceeds one inert Tower-fronted web-service shell",
            "database object storage DNS build deployment or production access is requested",
            "secret value readback display logging or repository storage is requested",
            "receipt chain cannot be completed in order",
        ],
        "stop_before_resource_creation": True,
        "stop_before_secret_registration": True,
        "stop_before_build": True,
        "stop_before_deployment": True,
        "session_close_required_on_any_stop": True,
        "provider_session_opened": False,
    }
    gate["gate_hash"] = payload_hash(gate)
    return gate


def _build_parts(
    repository_root: str | Path,
    provider_inputs,
    review_owner,
    review_inputs,
    provisioning_decision,
    execution_preparation_inputs,
    execution_authorization_decision,
    controlled_session_preparation_inputs,
    session_opening_authorization_decision,
    session_opening_preparation_inputs,
):
    key = payload_hash({
        "root": str(Path(repository_root).resolve()),
        "provider_inputs": provider_inputs or {},
        "review_owner": review_owner or {},
        "review_inputs": review_inputs or {},
        "provisioning_decision": provisioning_decision or {},
        "execution_preparation_inputs": execution_preparation_inputs or {},
        "execution_authorization_decision": execution_authorization_decision or {},
        "controlled_session_preparation_inputs": controlled_session_preparation_inputs or {},
        "session_opening_authorization_decision": session_opening_authorization_decision or {},
        "session_opening_preparation_inputs": session_opening_preparation_inputs or {},
    })
    cached = _PARTS_CACHE.get(key)
    if cached is not None:
        return tuple(_clone(item) for item in cached)

    handoff = build_session_opening_authorization_handoff(
        repository_root, provider_inputs, review_owner, review_inputs,
        provisioning_decision, execution_preparation_inputs,
        execution_authorization_decision, controlled_session_preparation_inputs,
        session_opening_authorization_decision,
    )
    validation = validate_session_opening_preparation_inputs(
        session_opening_preparation_inputs or {}, handoff=handoff
    )
    identity = build_provider_identity_and_session_isolation_preflight(handoff, session_opening_preparation_inputs, validation)
    duplicate = build_duplicate_resource_and_binding_revalidation_preflight(handoff, session_opening_preparation_inputs, validation)
    custody = build_credential_custody_and_authorization_window_preflight(handoff, session_opening_preparation_inputs, validation)
    service = build_one_inert_service_opening_request(session_opening_preparation_inputs, validation)
    environment = build_environment_and_secret_reference_opening_sequence(session_opening_preparation_inputs, validation)
    receipts = build_opening_receipt_chain_close_and_stop_gate(session_opening_preparation_inputs, validation)

    frozen = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "frozen_controlled_provider_session_opening_preparation_packet",
        "authorization_handoff_hash": handoff["handoff_hash"],
        "frozen_session_opening_authorization_record_hash": handoff["frozen_session_opening_authorization_record_hash"],
        "session_opening_authorization_decision_hash": handoff["session_opening_authorization_decision_hash"],
        "opening_preparation_validation_report_hash": validation["report_hash"],
        "provider_identity_and_session_isolation_preflight_hash": identity["preflight_hash"],
        "duplicate_resource_and_binding_revalidation_preflight_hash": duplicate["preflight_hash"],
        "credential_custody_and_authorization_window_preflight_hash": custody["preflight_hash"],
        "one_inert_service_opening_request_hash": service["request_hash"],
        "environment_and_secret_reference_opening_sequence_hash": environment["sequence_hash"],
        "opening_receipt_chain_close_and_stop_gate_hash": receipts["gate_hash"],
        "authorized_source_commit_sha256": _fingerprint((session_opening_preparation_inputs or {}).get("authorized_source_commit_ref")),
        "monthly_cost_ceiling_usd": _text((session_opening_preparation_inputs or {}).get("monthly_cost_ceiling_usd")),
        "provider_slug_sha256": handoff.get("provider_slug_sha256"),
        "account_or_team_ref_sha256": handoff.get("account_or_team_ref_sha256"),
        "deployment_region_sha256": handoff.get("deployment_region_sha256"),
        "owner_session_opening_preparation_receipt_ref_sha256": _fingerprint((session_opening_preparation_inputs or {}).get("owner_session_opening_preparation_receipt_ref")),
        "opening_preparation_valid": validation["valid"],
        "raw_provider_values_recorded": False,
        "raw_secret_values_recorded": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    frozen["frozen_session_opening_preparation_packet_hash"] = payload_hash(frozen)

    ready = bool(handoff["authorization_handoff_ready"] and validation["valid"])
    if not handoff["authorization_handoff_ready"]:
        final = handoff.get("final_decision") or HOLD_OPENING_AUTHORIZATION
    elif not validation["valid"]:
        final = HOLD_OPENING_PREPARATION
    else:
        final = READY_DECISION
    decision = {
        "schema_version": SCHEMA_VERSION,
        "decision_type": "controlled_provider_session_opening_preparation_closeout",
        "authorization_handoff_ready": handoff["authorization_handoff_ready"],
        "opening_preparation_valid": validation["valid"],
        "ready_for_separate_controlled_provider_session_opening_execution_authorization": ready,
        "provider_session_opening_authorized": False,
        "provider_login_authorized": False,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "secret_registration_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
        "final_decision": final,
    }
    decision["decision_hash"] = payload_hash(decision)
    plan = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": "inert_controlled_provider_session_opening_execution_authorization_plan",
        "ready_for_separate_authorization": ready,
        "required_future_inputs": [
            "fresh_tower_owner_step_up_receipt_ref",
            "exact_frozen_session_opening_preparation_packet_hash",
            "exact_opening_preparation_decision_hash",
            "fresh_short_lived_execution_window",
            "exact_owner_challenge_phrase_confirmation",
        ],
        "browser_actions": [],
        "provider_cli_commands": [],
        "provider_api_requests": [],
        "http_requests": [],
        "shell_commands": [],
        "dry_run_only": True,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
        "final_decision": final,
    }
    plan["plan_hash"] = payload_hash(plan)
    parts = (handoff, validation, identity, duplicate, custody, service, environment, receipts, frozen, decision, plan)
    _PARTS_CACHE[key] = tuple(_clone(item) for item in parts)
    return parts


def freeze_session_opening_preparation_packet(repository_root, provider_inputs, review_owner, review_inputs, provisioning_decision, execution_preparation_inputs, execution_authorization_decision, controlled_session_preparation_inputs, session_opening_authorization_decision, session_opening_preparation_inputs):
    return _build_parts(repository_root, provider_inputs, review_owner, review_inputs, provisioning_decision, execution_preparation_inputs, execution_authorization_decision, controlled_session_preparation_inputs, session_opening_authorization_decision, session_opening_preparation_inputs)[8]


def build_session_opening_preparation_decision(repository_root, provider_inputs, review_owner, review_inputs, provisioning_decision, execution_preparation_inputs, execution_authorization_decision, controlled_session_preparation_inputs, session_opening_authorization_decision, session_opening_preparation_inputs):
    return _build_parts(repository_root, provider_inputs, review_owner, review_inputs, provisioning_decision, execution_preparation_inputs, execution_authorization_decision, controlled_session_preparation_inputs, session_opening_authorization_decision, session_opening_preparation_inputs)[9]


def build_inert_session_opening_execution_authorization_plan(repository_root, provider_inputs, review_owner, review_inputs, provisioning_decision, execution_preparation_inputs, execution_authorization_decision, controlled_session_preparation_inputs, session_opening_authorization_decision, session_opening_preparation_inputs):
    return _build_parts(repository_root, provider_inputs, review_owner, review_inputs, provisioning_decision, execution_preparation_inputs, execution_authorization_decision, controlled_session_preparation_inputs, session_opening_authorization_decision, session_opening_preparation_inputs)[10]


def build_current_session_opening_preparation_state(
    repository_root: str | Path,
    provider_inputs=None,
    provider_review_owner_decision=None,
    review_inputs=None,
    provisioning_decision=None,
    execution_preparation_inputs=None,
    execution_authorization_decision=None,
    controlled_session_preparation_inputs=None,
    session_opening_authorization_decision=None,
    session_opening_preparation_inputs=None,
) -> dict[str, Any]:
    handoff, validation, identity, duplicate, custody, service, environment, receipts, frozen, decision, plan = _build_parts(
        repository_root, provider_inputs, provider_review_owner_decision, review_inputs,
        provisioning_decision, execution_preparation_inputs, execution_authorization_decision,
        controlled_session_preparation_inputs, session_opening_authorization_decision,
        session_opening_preparation_inputs,
    )
    blockers = []
    if not handoff["authorization_handoff_ready"]:
        blockers.append({"requirement": "valid_step110_session_opening_authorization", "status": "authorization_required"})
    for error in validation["errors"]:
        blockers.append({"requirement": error["field"], "status": error["code"]})
    state = {
        "schema_version": SCHEMA_VERSION,
        "closed_layer": "MANAGED_STAGING_CONTROLLED_PROVIDER_PROVISIONING_EXECUTION_SESSION_OPENING_PREPARATION",
        "closed_through_step": 120,
        "runtime_target": MANAGED_WSGI_TARGET,
        "runtime_topology": "single_tower_fronted_managed_python_web_service",
        "session_opening_authorization_handoff_hash": handoff["handoff_hash"],
        "frozen_session_opening_preparation_packet_hash": frozen["frozen_session_opening_preparation_packet_hash"],
        "session_opening_preparation_decision_hash": decision["decision_hash"],
        "inert_session_opening_execution_authorization_plan_hash": plan["plan_hash"],
        "session_opening_authorization_ready": handoff["authorization_handoff_ready"],
        "session_opening_preparation_valid": validation["valid"],
        "ready_for_separate_controlled_provider_session_opening_execution_authorization": decision["ready_for_separate_controlled_provider_session_opening_execution_authorization"],
        "blocking_requirements": blockers,
        "blocking_requirement_count": len(blockers),
        "provider_session_opening_authorized": False,
        "provider_login_authorized": False,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
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
        "next_boundary": "managed_staging_controlled_provider_provisioning_execution_session_opening_execution_authorization",
    }
    state["state_hash"] = payload_hash(state)
    return state


def write_json(path: str | Path, payload: Mapping[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_session_opening_preparation_worksheets(
    output_directory: str | Path,
    *,
    repository_root: str | Path,
    provider_inputs=None,
    provider_review_owner_decision=None,
    review_inputs=None,
    provisioning_decision=None,
    execution_preparation_inputs=None,
    execution_authorization_decision=None,
    controlled_session_preparation_inputs=None,
    session_opening_authorization_decision=None,
) -> dict[str, str]:
    output = Path(output_directory).resolve()
    root = Path(repository_root).resolve()
    if output == root or root in output.parents:
        raise ValueError("Session-opening preparation worksheets must be written outside the repository.")
    handoff = build_session_opening_authorization_handoff(
        root, provider_inputs, provider_review_owner_decision, review_inputs,
        provisioning_decision, execution_preparation_inputs, execution_authorization_decision,
        controlled_session_preparation_inputs, session_opening_authorization_decision,
    )
    worksheet_path = write_json(
        output / "tower_ob_controlled_provider_session_opening_preparation.json",
        session_opening_preparation_input_template(handoff),
    )
    placeholder = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "controlled_provider_session_opening_execution_authorization_placeholder",
        "decision": "HOLD",
        "frozen_session_opening_preparation_packet_hash": "",
        "session_opening_preparation_decision_hash": "",
        "provider_session_opening_authorized": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
        "notes": ["This placeholder is not an execution authorization and performs no provider action."],
    }
    placeholder["template_hash"] = payload_hash(placeholder)
    placeholder_path = write_json(
        output / "tower_ob_controlled_provider_session_opening_execution_authorization_placeholder.json",
        placeholder,
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "session_opening_preparation_path": str(worksheet_path),
        "session_opening_execution_authorization_placeholder_path": str(placeholder_path),
        "authorization_handoff_ready": handoff["authorization_handoff_ready"],
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
        "session_opening_preparation_path": str(worksheet_path),
        "session_opening_execution_authorization_placeholder_path": str(placeholder_path),
        "manifest_path": str(manifest_path),
    }


def blank_current_inputs(repository_root: str | Path) -> tuple[dict, ...]:
    prior = blank_session_opening_authorization_inputs(repository_root)
    handoff = build_session_opening_authorization_handoff(repository_root, *prior)
    preparation = session_opening_preparation_input_template(handoff)
    return (*prior, preparation)


__all__ = [
    "HOLD_OPENING_AUTHORIZATION",
    "HOLD_OPENING_PREPARATION",
    "NON_SECRET_ENVIRONMENT_NAMES",
    "READY_DECISION",
    "REQUIRED_OPENING_PREPARATION_ATTESTATIONS",
    "SCHEMA_VERSION",
    "SECRET_REFERENCE_NAMES",
    "blank_current_inputs",
    "build_credential_custody_and_authorization_window_preflight",
    "build_current_session_opening_preparation_state",
    "build_duplicate_resource_and_binding_revalidation_preflight",
    "build_environment_and_secret_reference_opening_sequence",
    "build_inert_session_opening_execution_authorization_plan",
    "build_one_inert_service_opening_request",
    "build_opening_receipt_chain_close_and_stop_gate",
    "build_provider_identity_and_session_isolation_preflight",
    "build_session_opening_authorization_handoff",
    "build_session_opening_preparation_decision",
    "freeze_session_opening_preparation_packet",
    "session_opening_preparation_input_template",
    "validate_session_opening_preparation_inputs",
    "write_session_opening_preparation_worksheets",
]
