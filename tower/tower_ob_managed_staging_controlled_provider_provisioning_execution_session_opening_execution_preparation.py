"""Controlled provider-session opening execution-preparation contracts.

This layer prepares a later, separately authorized controlled provider-session
opening execution session. It performs no provider login, browser automation,
CLI/API/HTTP calls, resource creation, secret registration, build, deployment,
DNS change, database/object-storage creation, or official Observatory walkthrough.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping

from tower.tower_ob_managed_staging_controlled_provider_provisioning_execution_session_opening_execution_authorization import (
    blank_current_inputs as blank_session_opening_execution_authorization_inputs,
    build_current_session_opening_execution_authorization_state,
)
from tower.tower_ob_managed_staging_runtime import MANAGED_WSGI_TARGET, payload_hash

SCHEMA_VERSION = "simplee.tower_ob.controlled_provider_session_opening_execution_preparation.v1"
PREPARE_DECISION = "PREPARE_SEPARATE_CONTROLLED_PROVIDER_SESSION_OPENING_EXECUTION_SESSION_AUTHORIZATION"
READY_DECISION = "GO_READY_FOR_SEPARATE_CONTROLLED_PROVIDER_SESSION_OPENING_EXECUTION_SESSION_AUTHORIZATION"
HOLD_PROVIDER_INPUTS = "NO_GO_HOLD_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION_REQUIRED"
HOLD_EXECUTION_AUTHORIZATION = "NO_GO_HOLD_CONTROLLED_SESSION_OPENING_EXECUTION_AUTHORIZATION_REQUIRED"
HOLD_EXECUTION_PREPARATION = "NO_GO_HOLD_CONTROLLED_SESSION_OPENING_EXECUTION_PREPARATION_REQUIRED"
MAX_PREPARATION_WINDOW_MINUTES = 30

REQUIRED_EXECUTION_PREPARATION_ATTESTATIONS = (
    "staging_only_scope_confirmed",
    "single_tower_fronted_service_confirmed",
    "tower_only_public_ingress_confirmed",
    "frozen_execution_authorization_record_hash_confirmed",
    "execution_authorization_decision_hash_confirmed",
    "authorized_source_commit_confirmed",
    "provider_identity_fingerprints_confirmed",
    "owner_execution_authorization_receipt_confirmed",
    "fresh_owner_execution_preparation_receipt_confirmed",
    "preparation_window_within_authorized_window_confirmed",
    "monthly_cost_ceiling_confirmed",
    "isolated_private_browser_session_required",
    "browser_profile_ephemeral_confirmed",
    "browser_automation_not_authorized",
    "credential_manager_or_provider_login_ui_only",
    "credentials_cookies_tokens_not_recorded",
    "clipboard_capture_not_authorized",
    "screenshots_of_credentials_not_authorized",
    "duplicate_resource_lookup_required_before_creation",
    "lookup_only_no_mutation_confirmed",
    "stop_if_duplicate_or_ambiguous_resource_confirmed",
    "one_inert_web_service_shell_limit_confirmed",
    "runtime_target_web_managed_staging_confirmed",
    "repository_branch_commit_binding_confirmed",
    "non_secret_environment_names_only_confirmed",
    "secret_reference_registration_without_readback_confirmed",
    "secret_values_not_in_git_logs_or_receipts_confirmed",
    "ordered_receipt_chain_confirmed",
    "rollback_and_session_close_plan_confirmed",
    "stop_before_provider_login_confirmed",
    "stop_before_provider_calls_confirmed",
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


def build_completed_session_opening_execution_authorization_handoff(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
    execution_preparation_inputs: Mapping[str, Any] | None,
    execution_authorization_decision: Mapping[str, Any] | None,
    controlled_session_preparation_inputs: Mapping[str, Any] | None,
    session_opening_authorization_decision: Mapping[str, Any] | None,
    session_opening_preparation_inputs: Mapping[str, Any] | None,
    session_opening_execution_authorization_decision: Mapping[str, Any] | None,
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
        session_opening_preparation_inputs or {},
        session_opening_execution_authorization_decision or {},
    )
    state = build_current_session_opening_execution_authorization_state(*args)
    source = session_opening_execution_authorization_decision or {}
    ready = bool(
        state.get("session_opening_execution_authorization_valid")
        and state.get("session_opening_execution_authorization_approved")
        and state.get("ready_for_separate_controlled_provider_session_opening_execution_preparation")
    )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "completed_controlled_provider_session_opening_execution_authorization_handoff",
        "frozen_session_opening_execution_authorization_record_hash": state.get("frozen_session_opening_execution_authorization_record_hash", ""),
        "session_opening_execution_authorization_decision_hash": state.get("session_opening_execution_authorization_decision_hash", ""),
        "authorized_source_commit_sha256": _fingerprint(_normalize_commit(source.get("authorized_source_commit_ref"))),
        "monthly_cost_ceiling_usd": _text(source.get("monthly_cost_ceiling_usd")),
        "provider_slug_sha256": _text(source.get("provider_slug_sha256")),
        "account_or_team_ref_sha256": _text(source.get("account_or_team_ref_sha256")),
        "deployment_region_sha256": _text(source.get("deployment_region_sha256")),
        "owner_execution_authorization_receipt_ref_sha256": _fingerprint(source.get("owner_execution_authorization_receipt_ref")),
        "execution_window_starts_at": _text(source.get("execution_window_starts_at")),
        "execution_window_expires_at": _text(source.get("execution_window_expires_at")),
        "authorization_expires_at": _text(source.get("authorization_expires_at")),
        "execution_authorization_valid": bool(state.get("session_opening_execution_authorization_valid")),
        "execution_authorization_approved": bool(state.get("session_opening_execution_authorization_approved")),
        "execution_authorization_handoff_ready": ready,
        "provider_session_opening_authorized": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
        "final_decision": state.get("final_decision", HOLD_EXECUTION_AUTHORIZATION),
    }
    payload["handoff_hash"] = payload_hash(payload)
    return payload


def session_opening_execution_preparation_input_template(handoff: Mapping[str, Any]) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "controlled_provider_session_opening_execution_preparation_input",
        "preparation_decision": "HOLD",
        "frozen_session_opening_execution_authorization_record_hash": _text(handoff.get("frozen_session_opening_execution_authorization_record_hash")),
        "session_opening_execution_authorization_decision_hash": _text(handoff.get("session_opening_execution_authorization_decision_hash")),
        "authorized_source_commit_ref": "",
        "preparation_window_starts_at": "",
        "preparation_window_expires_at": "",
        "monthly_cost_ceiling_usd": _text(handoff.get("monthly_cost_ceiling_usd")),
        "provider_slug_sha256": _text(handoff.get("provider_slug_sha256")),
        "account_or_team_ref_sha256": _text(handoff.get("account_or_team_ref_sha256")),
        "deployment_region_sha256": _text(handoff.get("deployment_region_sha256")),
        "owner_execution_authorization_receipt_ref_sha256": _text(handoff.get("owner_execution_authorization_receipt_ref_sha256")),
        "owner_execution_preparation_receipt_ref": "",
        "provider_console_route_ref": "",
        "isolated_browser_session_ref": "",
        "duplicate_resource_lookup_receipt_ref": "",
        "one_service_request_ref": "",
        "execution_session_nonce_ref": "",
        "scope_attestations": {name: False for name in REQUIRED_EXECUTION_PREPARATION_ATTESTATIONS},
        "provider_session_opening_authorized": False,
        "provider_login_authorized": False,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "secret_registration_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
    }
    payload["template_hash"] = payload_hash(payload)
    return payload


def validate_session_opening_execution_preparation_inputs(
    inputs: Mapping[str, Any], *, handoff: Mapping[str, Any]
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    def error(field: str, code: str) -> None:
        errors.append({"field": field, "code": code})

    if _contains_sensitive(inputs):
        error("inputs", "sensitive_material_rejected")
    if _text(inputs.get("preparation_decision")) != PREPARE_DECISION:
        error("preparation_decision", "exact_prepare_decision_required")
    for field in (
        "frozen_session_opening_execution_authorization_record_hash",
        "session_opening_execution_authorization_decision_hash",
    ):
        if _text(inputs.get(field)) != _text(handoff.get(field)):
            error(field, "exact_hash_binding_required")
    for field in (
        "owner_execution_preparation_receipt_ref",
        "provider_console_route_ref",
        "isolated_browser_session_ref",
        "duplicate_resource_lookup_receipt_ref",
        "one_service_request_ref",
        "execution_session_nonce_ref",
        "authorized_source_commit_ref",
    ):
        value = _text(inputs.get(field))
        if not value or not _SAFE_REF.fullmatch(value):
            error(field, "safe_reference_required")
    commit_ref = _text(inputs.get("authorized_source_commit_ref"))
    if not _COMMIT_REF.fullmatch(commit_ref):
        error("authorized_source_commit_ref", "exact_40_character_commit_required")
    expected_commit = _text(handoff.get("authorized_source_commit_sha256"))
    candidate_hashes = {
        _fingerprint(commit_ref),
        _fingerprint(_normalize_commit(commit_ref)),
        _fingerprint(f"commit/{_normalize_commit(commit_ref)}"),
    }
    if expected_commit and expected_commit not in candidate_hashes:
        error("authorized_source_commit_ref", "source_commit_binding_mismatch")
    starts = _parse_utc(inputs.get("preparation_window_starts_at"))
    expires = _parse_utc(inputs.get("preparation_window_expires_at"))
    authorized_starts = _parse_utc(handoff.get("execution_window_starts_at"))
    authorized_expires = _parse_utc(handoff.get("execution_window_expires_at"))
    if starts is None:
        error("preparation_window_starts_at", "valid_utc_timestamp_required")
    if expires is None:
        error("preparation_window_expires_at", "valid_utc_timestamp_required")
    if starts and expires:
        minutes = (expires - starts).total_seconds() / 60
        if minutes <= 0 or minutes > MAX_PREPARATION_WINDOW_MINUTES:
            error("preparation_window_expires_at", "window_must_be_positive_and_at_most_30_minutes")
    if starts and authorized_starts and starts < authorized_starts:
        error("preparation_window_starts_at", "window_must_be_inside_execution_authorization")
    if expires and authorized_expires and expires > authorized_expires:
        error("preparation_window_expires_at", "window_must_be_inside_execution_authorization")
    if not _valid_money(inputs.get("monthly_cost_ceiling_usd")):
        error("monthly_cost_ceiling_usd", "positive_bounded_money_required")
    if _text(inputs.get("monthly_cost_ceiling_usd")) != _text(handoff.get("monthly_cost_ceiling_usd")):
        error("monthly_cost_ceiling_usd", "cost_ceiling_mismatch")
    for field in (
        "provider_slug_sha256",
        "account_or_team_ref_sha256",
        "deployment_region_sha256",
        "owner_execution_authorization_receipt_ref_sha256",
    ):
        if _text(inputs.get(field)) != _text(handoff.get(field)):
            error(field, "fingerprint_binding_mismatch")
    attestations = inputs.get("scope_attestations")
    if not isinstance(attestations, Mapping):
        error("scope_attestations", "mapping_required")
        attestations = {}
    for name in REQUIRED_EXECUTION_PREPARATION_ATTESTATIONS:
        if not _bool(attestations.get(name)):
            error(f"scope_attestations.{name}", "attestation_required")
    valid = not errors and bool(handoff.get("execution_authorization_handoff_ready"))
    report = {
        "schema_version": SCHEMA_VERSION,
        "report_type": "controlled_provider_session_opening_execution_preparation_validation",
        "valid": valid,
        "error_count": len(errors),
        "errors": errors,
        "provider_session_opening_authorized": False,
        "provider_login_authorized": False,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "secret_registration_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
    }
    report["report_hash"] = payload_hash(report)
    return report


def build_provider_identity_window_cost_revalidation(
    handoff: Mapping[str, Any], inputs: Mapping[str, Any], validation: Mapping[str, Any]
) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "provider_identity_window_cost_revalidation_preparation",
        "preparation_valid": bool(validation.get("valid")),
        "provider_slug_sha256": _text(handoff.get("provider_slug_sha256")),
        "account_or_team_ref_sha256": _text(handoff.get("account_or_team_ref_sha256")),
        "deployment_region_sha256": _text(handoff.get("deployment_region_sha256")),
        "authorized_source_commit_sha256": _text(handoff.get("authorized_source_commit_sha256")),
        "monthly_cost_ceiling_usd": _text(handoff.get("monthly_cost_ceiling_usd")),
        "preparation_window_starts_at": _text(inputs.get("preparation_window_starts_at")),
        "preparation_window_expires_at": _text(inputs.get("preparation_window_expires_at")),
        "raw_provider_identity_values_recorded": False,
        "raw_credentials_recorded": False,
        "provider_login_performed": False,
    }
    payload["record_hash"] = payload_hash(payload)
    return payload


def build_isolated_browser_and_credential_custody_manifest(validation: Mapping[str, Any]) -> dict[str, Any]:
    ready = bool(validation.get("valid"))
    payload = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "isolated_browser_and_credential_custody_preparation",
        "ready_for_later_authorized_session": ready,
        "browser_profile": "ephemeral_private_isolated",
        "browser_automation_authorized": False,
        "credential_entry_method": "credential_manager_or_provider_login_ui_only",
        "credential_values_recorded": False,
        "cookies_recorded": False,
        "tokens_recorded": False,
        "clipboard_capture_authorized": False,
        "credential_screenshots_authorized": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
    }
    payload["manifest_hash"] = payload_hash(payload)
    return payload


def build_duplicate_resource_lookup_preparation(validation: Mapping[str, Any]) -> dict[str, Any]:
    ready = bool(validation.get("valid"))
    payload = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": "duplicate_resource_lookup_preparation",
        "ready_for_later_lookup": ready,
        "lookup_mode": "read_only_provider_console_review",
        "browser_actions": [],
        "provider_cli_commands": [],
        "provider_api_requests": [],
        "http_requests": [],
        "resource_mutations": [],
        "mandatory_stop_conditions": [
            "stop_if_existing_matching_service_is_found",
            "stop_if_multiple_candidate_services_are_found",
            "stop_if_account_team_or_region_binding_is_ambiguous",
            "stop_if_lookup_requires_secret_readback",
        ],
        "lookup_performed": False,
        "resources_created": False,
    }
    payload["plan_hash"] = payload_hash(payload)
    return payload


def build_one_service_environment_secret_preparation_manifest(validation: Mapping[str, Any]) -> dict[str, Any]:
    ready = bool(validation.get("valid"))
    payload = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "one_inert_tower_fronted_service_environment_secret_preparation",
        "ready_for_later_session_authorization": ready,
        "service_limit": 1 if ready else 0,
        "runtime_target": MANAGED_WSGI_TARGET,
        "runtime_topology": "single_tower_fronted_managed_python_web_service",
        "public_ingress_owner": "tower",
        "observatory_separate_service_required": False,
        "environment_variable_names_only": True,
        "secret_references_only": True,
        "secret_values_included": False,
        "secret_readback_authorized": False,
        "provider_session_opening_authorized": False,
        "resource_creation_authorized": False,
        "secret_registration_authorized": False,
        "database_creation_authorized": False,
        "object_storage_creation_authorized": False,
        "dns_changes_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
    }
    payload["manifest_hash"] = payload_hash(payload)
    return payload


def build_execution_preparation_receipt_chain_and_stop_gate(validation: Mapping[str, Any]) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "gate_type": "controlled_provider_session_opening_execution_preparation_receipt_chain_and_stop_gate",
        "preparation_valid": bool(validation.get("valid")),
        "future_receipt_order": [
            "execution_session_authorization_start_receipt",
            "provider_identity_revalidation_receipt",
            "duplicate_resource_lookup_receipt",
            "one_service_request_review_receipt",
            "environment_name_review_receipt",
            "secret_reference_review_receipt",
            "provider_session_close_logout_receipt",
            "execution_session_authorization_closeout_receipt",
        ],
        "mandatory_stop_conditions": [
            "stop_before_provider_login_without_fresh_execution_session_authorization",
            "stop_before_any_provider_mutation",
            "stop_if_duplicate_or_ambiguous_resource_is_detected",
            "stop_if_identity_account_region_or_commit_binding_changes",
            "stop_if_authorization_window_expires",
            "stop_if_monthly_cost_ceiling_changes",
            "stop_if_secret_value_readback_is_requested",
            "stop_before_build",
            "stop_before_deployment",
        ],
        "rollback_plan": [
            "close_private_browser_session",
            "log_out_of_provider_console",
            "revoke_temporary_session_if_supported",
            "record_fail_closed_stop_receipt",
        ],
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
    }
    payload["gate_hash"] = payload_hash(payload)
    return payload


def freeze_session_opening_execution_preparation_packet(
    handoff: Mapping[str, Any],
    inputs: Mapping[str, Any],
    validation: Mapping[str, Any],
    identity: Mapping[str, Any],
    browser: Mapping[str, Any],
    duplicate: Mapping[str, Any],
    service: Mapping[str, Any],
    receipts: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "frozen_controlled_provider_session_opening_execution_preparation_packet",
        "completed_execution_authorization_handoff_hash": _text(handoff.get("handoff_hash")),
        "frozen_session_opening_execution_authorization_record_hash": _text(handoff.get("frozen_session_opening_execution_authorization_record_hash")),
        "session_opening_execution_authorization_decision_hash": _text(handoff.get("session_opening_execution_authorization_decision_hash")),
        "execution_preparation_validation_report_hash": _text(validation.get("report_hash")),
        "provider_identity_window_cost_revalidation_hash": _text(identity.get("record_hash")),
        "isolated_browser_and_credential_custody_manifest_hash": _text(browser.get("manifest_hash")),
        "duplicate_resource_lookup_preparation_hash": _text(duplicate.get("plan_hash")),
        "one_service_environment_secret_preparation_manifest_hash": _text(service.get("manifest_hash")),
        "receipt_chain_and_stop_gate_hash": _text(receipts.get("gate_hash")),
        "owner_execution_preparation_receipt_ref_sha256": _fingerprint(inputs.get("owner_execution_preparation_receipt_ref")),
        "isolated_browser_session_ref_sha256": _fingerprint(inputs.get("isolated_browser_session_ref")),
        "duplicate_resource_lookup_receipt_ref_sha256": _fingerprint(inputs.get("duplicate_resource_lookup_receipt_ref")),
        "one_service_request_ref_sha256": _fingerprint(inputs.get("one_service_request_ref")),
        "execution_session_nonce_ref_sha256": _fingerprint(inputs.get("execution_session_nonce_ref")),
        "preparation_valid": bool(validation.get("valid")),
        "contains_raw_reference_values": False,
        "contains_secret_values": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    payload["frozen_session_opening_execution_preparation_packet_hash"] = payload_hash(payload)
    return payload


def build_inert_execution_session_authorization_plan(validation: Mapping[str, Any]) -> dict[str, Any]:
    ready = bool(validation.get("valid"))
    payload = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": "inert_controlled_provider_session_opening_execution_session_authorization_plan",
        "ready_for_separate_execution_session_authorization": ready,
        "browser_actions": [],
        "provider_cli_commands": [],
        "provider_api_requests": [],
        "http_requests": [],
        "shell_commands": [],
        "resource_mutations": [],
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    payload["plan_hash"] = payload_hash(payload)
    return payload


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
    session_opening_execution_authorization_decision,
    session_opening_execution_preparation_inputs,
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
        "session_opening_execution_authorization_decision": session_opening_execution_authorization_decision or {},
        "session_opening_execution_preparation_inputs": session_opening_execution_preparation_inputs or {},
    })
    cached = _PARTS_CACHE.get(key)
    if cached is not None:
        return tuple(_clone(item) for item in cached)
    handoff = build_completed_session_opening_execution_authorization_handoff(
        repository_root, provider_inputs, review_owner, review_inputs,
        provisioning_decision, execution_preparation_inputs,
        execution_authorization_decision, controlled_session_preparation_inputs,
        session_opening_authorization_decision, session_opening_preparation_inputs,
        session_opening_execution_authorization_decision,
    )
    inputs = session_opening_execution_preparation_inputs or {}
    validation = validate_session_opening_execution_preparation_inputs(inputs, handoff=handoff)
    identity = build_provider_identity_window_cost_revalidation(handoff, inputs, validation)
    browser = build_isolated_browser_and_credential_custody_manifest(validation)
    duplicate = build_duplicate_resource_lookup_preparation(validation)
    service = build_one_service_environment_secret_preparation_manifest(validation)
    receipts = build_execution_preparation_receipt_chain_and_stop_gate(validation)
    frozen = freeze_session_opening_execution_preparation_packet(
        handoff, inputs, validation, identity, browser, duplicate, service, receipts
    )
    plan = build_inert_execution_session_authorization_plan(validation)
    if not handoff.get("execution_authorization_handoff_ready"):
        final = handoff.get("final_decision") or HOLD_EXECUTION_AUTHORIZATION
    elif not validation.get("valid"):
        final = HOLD_EXECUTION_PREPARATION
    else:
        final = READY_DECISION
    decision = {
        "schema_version": SCHEMA_VERSION,
        "decision_type": "controlled_provider_session_opening_execution_preparation_closeout",
        "execution_authorization_handoff_ready": bool(handoff.get("execution_authorization_handoff_ready")),
        "execution_preparation_valid": bool(validation.get("valid")),
        "ready_for_separate_controlled_provider_session_opening_execution_session_authorization": bool(validation.get("valid")),
        "provider_session_opening_authorized_now": False,
        "provider_login_authorized_now": False,
        "provider_calls_authorized_now": False,
        "resource_creation_authorized_now": False,
        "secret_registration_authorized_now": False,
        "build_authorized_now": False,
        "deployment_authorized_now": False,
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
    parts = (handoff, validation, identity, browser, duplicate, service, receipts, frozen, plan, decision)
    _PARTS_CACHE[key] = tuple(_clone(item) for item in parts)
    return parts


def build_session_opening_execution_preparation_decision(*args):
    return _build_parts(*args)[9]


def build_current_session_opening_execution_preparation_state(
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
    session_opening_execution_authorization_decision=None,
    session_opening_execution_preparation_inputs=None,
) -> dict[str, Any]:
    handoff, validation, identity, browser, duplicate, service, receipts, frozen, plan, decision = _build_parts(
        repository_root, provider_inputs, provider_review_owner_decision, review_inputs,
        provisioning_decision, execution_preparation_inputs, execution_authorization_decision,
        controlled_session_preparation_inputs, session_opening_authorization_decision,
        session_opening_preparation_inputs, session_opening_execution_authorization_decision,
        session_opening_execution_preparation_inputs,
    )
    blockers = []
    if not handoff.get("execution_authorization_handoff_ready"):
        blockers.append({"requirement": "valid_step130_session_opening_execution_authorization", "status": "authorization_required"})
    for error in validation.get("errors", []):
        blockers.append({"requirement": error["field"], "status": error["code"]})
    state = {
        "schema_version": SCHEMA_VERSION,
        "closed_layer": "MANAGED_STAGING_CONTROLLED_PROVIDER_PROVISIONING_EXECUTION_SESSION_OPENING_EXECUTION_PREPARATION",
        "closed_through_step": 140,
        "runtime_target": MANAGED_WSGI_TARGET,
        "runtime_topology": "single_tower_fronted_managed_python_web_service",
        "completed_execution_authorization_handoff_hash": handoff["handoff_hash"],
        "frozen_session_opening_execution_preparation_packet_hash": frozen["frozen_session_opening_execution_preparation_packet_hash"],
        "session_opening_execution_preparation_decision_hash": decision["decision_hash"],
        "inert_execution_session_authorization_plan_hash": plan["plan_hash"],
        "session_opening_execution_authorization_ready": bool(handoff.get("execution_authorization_handoff_ready")),
        "session_opening_execution_preparation_valid": bool(validation.get("valid")),
        "ready_for_separate_controlled_provider_session_opening_execution_session_authorization": bool(validation.get("valid")),
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
        "next_boundary": "managed_staging_controlled_provider_provisioning_execution_session_opening_execution_session_authorization",
    }
    state["state_hash"] = payload_hash(state)
    return state


def write_json(path: str | Path, payload: Mapping[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_session_opening_execution_preparation_worksheets(
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
    session_opening_preparation_inputs=None,
    session_opening_execution_authorization_decision=None,
) -> dict[str, str]:
    output = Path(output_directory).resolve()
    root = Path(repository_root).resolve()
    if output == root or root in output.parents:
        raise ValueError("Session-opening execution-preparation worksheets must be written outside the repository.")
    handoff = build_completed_session_opening_execution_authorization_handoff(
        root, provider_inputs, provider_review_owner_decision, review_inputs,
        provisioning_decision, execution_preparation_inputs, execution_authorization_decision,
        controlled_session_preparation_inputs, session_opening_authorization_decision,
        session_opening_preparation_inputs, session_opening_execution_authorization_decision,
    )
    worksheet = write_json(
        output / "tower_ob_controlled_provider_session_opening_execution_preparation.json",
        session_opening_execution_preparation_input_template(handoff),
    )
    placeholder = write_json(
        output / "tower_ob_controlled_provider_session_opening_execution_session_authorization_placeholder.json",
        {
            "schema_version": SCHEMA_VERSION,
            "packet_type": "controlled_provider_session_opening_execution_session_authorization_placeholder",
            "decision": "HOLD",
            "frozen_session_opening_execution_preparation_packet_hash": "",
            "owner_id": "",
            "tower_step_up_receipt_ref": "",
            "authorization_window_starts_at": "",
            "authorization_window_expires_at": "",
            "provider_session_opening_authorized": False,
            "provider_login_authorized": False,
            "provider_calls_authorized": False,
            "resource_creation_authorized": False,
            "secret_registration_authorized": False,
            "build_authorized": False,
            "deployment_authorized": False,
        },
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "session_opening_execution_preparation_path": str(worksheet),
        "execution_session_authorization_placeholder_path": str(placeholder),
        "execution_authorization_handoff_ready": bool(handoff.get("execution_authorization_handoff_ready")),
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
        "session_opening_execution_preparation_path": str(worksheet),
        "execution_session_authorization_placeholder_path": str(placeholder),
        "manifest_path": str(manifest_path),
    }


def blank_current_inputs(repository_root: str | Path) -> tuple[dict, ...]:
    prior = blank_session_opening_execution_authorization_inputs(repository_root)
    handoff = build_completed_session_opening_execution_authorization_handoff(repository_root, *prior)
    inputs = session_opening_execution_preparation_input_template(handoff)
    return (*prior, inputs)


__all__ = [
    "HOLD_EXECUTION_PREPARATION",
    "MAX_PREPARATION_WINDOW_MINUTES",
    "PREPARE_DECISION",
    "READY_DECISION",
    "REQUIRED_EXECUTION_PREPARATION_ATTESTATIONS",
    "SCHEMA_VERSION",
    "blank_current_inputs",
    "build_completed_session_opening_execution_authorization_handoff",
    "build_current_session_opening_execution_preparation_state",
    "build_duplicate_resource_lookup_preparation",
    "build_execution_preparation_receipt_chain_and_stop_gate",
    "build_inert_execution_session_authorization_plan",
    "build_isolated_browser_and_credential_custody_manifest",
    "build_one_service_environment_secret_preparation_manifest",
    "build_provider_identity_window_cost_revalidation",
    "build_session_opening_execution_preparation_decision",
    "freeze_session_opening_execution_preparation_packet",
    "session_opening_execution_preparation_input_template",
    "validate_session_opening_execution_preparation_inputs",
    "write_session_opening_execution_preparation_worksheets",
]
