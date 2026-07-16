"""Controlled provider-session opening execution-authorization contracts.

This layer records a fresh Tower owner decision for a later controlled provider
session-opening execution-preparation operation. It performs no provider login,
browser automation, CLI/API/HTTP calls, resource creation, secret registration,
build, deployment, DNS change, database/object-storage creation, or official
Observatory walkthrough.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping

from tower.tower_ob_managed_staging_controlled_provider_provisioning_execution_session_opening_preparation import (
    blank_current_inputs as blank_session_opening_preparation_inputs,
    build_session_opening_preparation_decision,
    freeze_session_opening_preparation_packet,
)
from tower.tower_ob_managed_staging_runtime import MANAGED_WSGI_TARGET, payload_hash

SCHEMA_VERSION = "simplee.tower_ob.controlled_provider_session_opening_execution_authorization.v1"
AUTHORIZE_DECISION = "AUTHORIZE_SEPARATE_CONTROLLED_PROVIDER_SESSION_OPENING_EXECUTION_PREPARATION"
REJECT_DECISION = "REJECT_CONTROLLED_PROVIDER_SESSION_OPENING_EXECUTION"
READY_DECISION = "GO_READY_FOR_SEPARATE_CONTROLLED_PROVIDER_SESSION_OPENING_EXECUTION_PREPARATION"
HOLD_PROVIDER_INPUTS = "NO_GO_HOLD_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION_REQUIRED"
HOLD_OPENING_PREPARATION = "NO_GO_HOLD_CONTROLLED_SESSION_OPENING_PREPARATION_REQUIRED"
HOLD_EXECUTION_AUTHORIZATION = "NO_GO_HOLD_CONTROLLED_SESSION_OPENING_EXECUTION_AUTHORIZATION_REQUIRED"
REJECTED_DECISION = "NO_GO_CONTROLLED_SESSION_OPENING_EXECUTION_REJECTED"

MAX_EXECUTION_WINDOW_MINUTES = 45
EXACT_CHALLENGE_PREFIX = "AUTHORIZE CONTROLLED PROVIDER SESSION OPENING EXECUTION PREPARATION"

REQUIRED_EXECUTION_AUTHORIZATION_ATTESTATIONS = (
    "staging_only_scope_confirmed",
    "single_tower_fronted_service_confirmed",
    "tower_only_public_ingress_confirmed",
    "observatory_separate_service_not_required",
    "frozen_session_opening_preparation_packet_hash_confirmed",
    "session_opening_preparation_decision_hash_confirmed",
    "authorized_source_commit_confirmed",
    "provider_identity_fingerprints_confirmed",
    "owner_session_opening_preparation_receipt_fingerprint_confirmed",
    "fresh_tower_owner_step_up_receipt_confirmed",
    "fresh_owner_execution_authorization_receipt_confirmed",
    "execution_window_within_prior_authorization_confirmed",
    "authorization_expiry_confirmed",
    "monthly_cost_ceiling_confirmed",
    "isolated_private_browser_session_required",
    "credential_manager_or_provider_login_ui_only",
    "credentials_cookies_tokens_not_recorded",
    "duplicate_resource_lookup_required_before_creation",
    "stop_if_duplicate_or_ambiguous_resource_confirmed",
    "one_inert_web_service_shell_limit_confirmed",
    "repository_branch_commit_binding_confirmed",
    "non_secret_environment_names_only_confirmed",
    "secret_reference_registration_without_readback_confirmed",
    "ordered_receipt_chain_confirmed",
    "session_close_logout_and_revocation_confirmed",
    "stop_before_provider_login_confirmed",
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
    "no_provider_session_login_or_calls_performed_during_authorization",
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


def build_completed_session_opening_preparation_handoff(
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
    )
    decision = build_session_opening_preparation_decision(*args)
    frozen = freeze_session_opening_preparation_packet(*args)
    ready = bool(
        decision.get("opening_preparation_valid")
        and decision.get("ready_for_separate_controlled_provider_session_opening_execution_authorization")
    )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "completed_controlled_provider_session_opening_preparation_handoff",
        "frozen_session_opening_preparation_packet_hash": frozen.get("frozen_session_opening_preparation_packet_hash", ""),
        "session_opening_preparation_decision_hash": decision.get("decision_hash", ""),
        "authorized_source_commit_sha256": frozen.get("authorized_source_commit_sha256"),
        "monthly_cost_ceiling_usd": frozen.get("monthly_cost_ceiling_usd", ""),
        "provider_slug_sha256": frozen.get("provider_slug_sha256"),
        "account_or_team_ref_sha256": frozen.get("account_or_team_ref_sha256"),
        "deployment_region_sha256": frozen.get("deployment_region_sha256"),
        "owner_session_opening_preparation_receipt_ref_sha256": frozen.get("owner_session_opening_preparation_receipt_ref_sha256"),
        "session_opening_preparation_valid": bool(decision.get("opening_preparation_valid")),
        "preparation_handoff_ready": ready,
        "provider_session_opening_authorized": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
        "final_decision": decision.get("final_decision", HOLD_OPENING_PREPARATION),
    }
    payload["handoff_hash"] = payload_hash(payload)
    return payload


def build_session_opening_execution_authorization_challenge(
    handoff: Mapping[str, Any],
) -> dict[str, Any]:
    packet_hash = _text(handoff.get("frozen_session_opening_preparation_packet_hash"))
    decision_hash = _text(handoff.get("session_opening_preparation_decision_hash"))
    challenge_phrase = (
        f"{EXACT_CHALLENGE_PREFIX} "
        f"{packet_hash[:12]} {decision_hash[:12]}"
    )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "challenge_type": "controlled_provider_session_opening_execution_authorization",
        "frozen_session_opening_preparation_packet_hash": packet_hash,
        "session_opening_preparation_decision_hash": decision_hash,
        "challenge_phrase": challenge_phrase,
        "challenge_expires_after_minutes": 15,
        "provider_session_opening_authorized": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
    }
    payload["challenge_id"] = payload_hash(payload)
    return payload


def session_opening_execution_authorization_decision_template(
    handoff: Mapping[str, Any],
) -> dict[str, Any]:
    challenge = build_session_opening_execution_authorization_challenge(handoff)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "controlled_provider_session_opening_execution_authorization_decision",
        "decision": "HOLD",
        "owner_id": "",
        "tower_step_up_receipt_ref": "",
        "owner_execution_authorization_receipt_ref": "",
        "challenge_id": challenge["challenge_id"],
        "challenge_phrase_confirmation": "",
        "frozen_session_opening_preparation_packet_hash": _text(handoff.get("frozen_session_opening_preparation_packet_hash")),
        "session_opening_preparation_decision_hash": _text(handoff.get("session_opening_preparation_decision_hash")),
        "authorized_source_commit_ref": "",
        "execution_window_starts_at": "",
        "execution_window_expires_at": "",
        "authorization_expires_at": "",
        "monthly_cost_ceiling_usd": _text(handoff.get("monthly_cost_ceiling_usd")),
        "provider_slug_sha256": _text(handoff.get("provider_slug_sha256")),
        "account_or_team_ref_sha256": _text(handoff.get("account_or_team_ref_sha256")),
        "deployment_region_sha256": _text(handoff.get("deployment_region_sha256")),
        "owner_session_opening_preparation_receipt_ref_sha256": _text(handoff.get("owner_session_opening_preparation_receipt_ref_sha256")),
        "scope_attestations": {
            name: False for name in REQUIRED_EXECUTION_AUTHORIZATION_ATTESTATIONS
        },
        "notes": [
            "This decision authorizes only a later execution-preparation layer.",
            "It does not open a provider session, log in, create resources, register secrets, build, or deploy.",
        ],
    }
    payload["template_hash"] = payload_hash(payload)
    return payload


def validate_session_opening_execution_authorization_decision(
    decision: Mapping[str, Any],
    *,
    handoff: Mapping[str, Any],
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    def error(field: str, code: str) -> None:
        errors.append({"field": field, "code": code})

    if _contains_sensitive(decision):
        error("decision", "sensitive_material_rejected")

    decision_value = _text(decision.get("decision"))
    if decision_value not in {AUTHORIZE_DECISION, REJECT_DECISION}:
        error("decision", "authorization_or_rejection_required")

    challenge = build_session_opening_execution_authorization_challenge(handoff)
    if _text(decision.get("challenge_id")) != challenge["challenge_id"]:
        error("challenge_id", "exact_challenge_id_required")
    if _text(decision.get("challenge_phrase_confirmation")) != challenge["challenge_phrase"]:
        error("challenge_phrase_confirmation", "exact_challenge_phrase_required")

    if _text(decision.get("frozen_session_opening_preparation_packet_hash")) != _text(
        handoff.get("frozen_session_opening_preparation_packet_hash")
    ):
        error("frozen_session_opening_preparation_packet_hash", "exact_hash_binding_required")
    if _text(decision.get("session_opening_preparation_decision_hash")) != _text(
        handoff.get("session_opening_preparation_decision_hash")
    ):
        error("session_opening_preparation_decision_hash", "exact_hash_binding_required")

    for field in (
        "owner_id",
        "tower_step_up_receipt_ref",
        "owner_execution_authorization_receipt_ref",
        "authorized_source_commit_ref",
    ):
        value = _text(decision.get(field))
        if not value or not _SAFE_REF.fullmatch(value):
            error(field, "safe_reference_required")

    if not _COMMIT_REF.fullmatch(_text(decision.get("authorized_source_commit_ref"))):
        error("authorized_source_commit_ref", "exact_40_character_commit_required")
    expected_commit_sha = _text(handoff.get("authorized_source_commit_sha256"))
    commit_ref = _text(decision.get("authorized_source_commit_ref"))
    candidate_commit_hashes = {
        _fingerprint(commit_ref),
        _fingerprint(_normalize_commit(commit_ref)),
        _fingerprint(f"commit/{_normalize_commit(commit_ref)}"),
    }
    if expected_commit_sha and expected_commit_sha not in candidate_commit_hashes:
        error("authorized_source_commit_ref", "source_commit_binding_mismatch")

    starts = _parse_utc(decision.get("execution_window_starts_at"))
    expires = _parse_utc(decision.get("execution_window_expires_at"))
    auth_expires = _parse_utc(decision.get("authorization_expires_at"))
    if starts is None:
        error("execution_window_starts_at", "valid_utc_timestamp_required")
    if expires is None:
        error("execution_window_expires_at", "valid_utc_timestamp_required")
    if auth_expires is None:
        error("authorization_expires_at", "valid_utc_timestamp_required")
    if starts and expires:
        duration = (expires - starts).total_seconds() / 60
        if duration <= 0 or duration > MAX_EXECUTION_WINDOW_MINUTES:
            error("execution_window_expires_at", "window_must_be_positive_and_at_most_45_minutes")
    if expires and auth_expires and expires > auth_expires:
        error("authorization_expires_at", "authorization_must_cover_execution_window")

    if not _valid_money(decision.get("monthly_cost_ceiling_usd")):
        error("monthly_cost_ceiling_usd", "positive_bounded_money_required")
    if _text(handoff.get("monthly_cost_ceiling_usd")) and _text(decision.get("monthly_cost_ceiling_usd")) != _text(handoff.get("monthly_cost_ceiling_usd")):
        error("monthly_cost_ceiling_usd", "cost_ceiling_mismatch")

    for field in (
        "provider_slug_sha256",
        "account_or_team_ref_sha256",
        "deployment_region_sha256",
        "owner_session_opening_preparation_receipt_ref_sha256",
    ):
        if _text(decision.get(field)) != _text(handoff.get(field)):
            error(field, "fingerprint_binding_mismatch")

    attestations = decision.get("scope_attestations")
    if not isinstance(attestations, Mapping):
        error("scope_attestations", "mapping_required")
        attestations = {}
    missing_attestations = [
        name for name in REQUIRED_EXECUTION_AUTHORIZATION_ATTESTATIONS
        if not _bool(attestations.get(name))
    ]
    for name in missing_attestations:
        error(f"scope_attestations.{name}", "attestation_required")

    valid = not errors and decision_value in {AUTHORIZE_DECISION, REJECT_DECISION}
    approved = valid and decision_value == AUTHORIZE_DECISION and bool(handoff.get("preparation_handoff_ready"))
    rejected = valid and decision_value == REJECT_DECISION
    report = {
        "schema_version": SCHEMA_VERSION,
        "report_type": "controlled_provider_session_opening_execution_authorization_validation",
        "valid": valid,
        "approved": approved,
        "rejected": rejected,
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


def build_session_opening_execution_scope_manifest(
    decision: Mapping[str, Any],
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    approved = bool(validation.get("approved"))
    payload = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "controlled_provider_session_opening_execution_scope",
        "authorization_approved": approved,
        "future_preparation_scope": {
            "isolated_private_browser_session_preparation": approved,
            "provider_identity_revalidation_preparation": approved,
            "provider_account_team_revalidation_preparation": approved,
            "provider_region_revalidation_preparation": approved,
            "duplicate_resource_lookup_preparation": approved,
            "one_inert_tower_fronted_service_shell_preparation": approved,
            "non_secret_environment_name_preparation": approved,
            "secret_reference_registration_preparation_without_readback": approved,
            "ordered_receipt_chain_preparation": approved,
            "session_close_logout_and_revocation_preparation": approved,
        },
        "provider_session_opening_authorized_now": False,
        "provider_login_authorized_now": False,
        "provider_calls_authorized_now": False,
        "resource_creation_authorized_now": False,
        "secret_registration_authorized_now": False,
        "build_authorized_now": False,
        "deployment_authorized_now": False,
        "database_creation_authorized": False,
        "object_storage_creation_authorized": False,
        "dns_changes_authorized": False,
    }
    payload["manifest_hash"] = payload_hash(payload)
    return payload


def build_identity_window_cost_binding(
    handoff: Mapping[str, Any],
    decision: Mapping[str, Any],
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "controlled_provider_session_opening_identity_window_cost_binding",
        "validation_approved": bool(validation.get("approved")),
        "authorized_source_commit_sha256": _fingerprint(_normalize_commit(decision.get("authorized_source_commit_ref"))),
        "execution_window_starts_at": _text(decision.get("execution_window_starts_at")),
        "execution_window_expires_at": _text(decision.get("execution_window_expires_at")),
        "authorization_expires_at": _text(decision.get("authorization_expires_at")),
        "monthly_cost_ceiling_usd": _text(decision.get("monthly_cost_ceiling_usd")),
        "provider_slug_sha256": _text(handoff.get("provider_slug_sha256")),
        "account_or_team_ref_sha256": _text(handoff.get("account_or_team_ref_sha256")),
        "deployment_region_sha256": _text(handoff.get("deployment_region_sha256")),
        "owner_id_sha256": _fingerprint(decision.get("owner_id")),
        "tower_step_up_receipt_ref_sha256": _fingerprint(decision.get("tower_step_up_receipt_ref")),
        "owner_execution_authorization_receipt_ref_sha256": _fingerprint(decision.get("owner_execution_authorization_receipt_ref")),
        "raw_provider_identity_values_recorded": False,
        "raw_credentials_recorded": False,
        "raw_tokens_or_cookies_recorded": False,
    }
    payload["binding_hash"] = payload_hash(payload)
    return payload


def build_execution_receipt_chain_and_stop_gate(
    decision: Mapping[str, Any],
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "gate_type": "controlled_provider_session_opening_execution_receipt_chain_and_stop_gate",
        "authorization_approved": bool(validation.get("approved")),
        "future_receipt_order": [
            "session_opening_execution_preparation_start_receipt",
            "identity_account_region_revalidation_receipt",
            "isolated_browser_session_preparation_receipt",
            "duplicate_resource_lookup_preparation_receipt",
            "one_service_shell_preparation_receipt",
            "environment_and_secret_reference_preparation_receipt",
            "session_close_logout_revocation_preparation_receipt",
            "execution_preparation_closeout_receipt",
        ],
        "mandatory_stop_conditions": [
            "authorization_expired_or_outside_window",
            "owner_step_up_receipt_invalid_or_stale",
            "provider_identity_account_or_region_mismatch",
            "duplicate_or_ambiguous_resource_detected",
            "credential_cookie_or_token_capture_requested",
            "more_than_one_service_requested",
            "database_object_storage_or_dns_requested",
            "secret_value_readback_requested",
            "build_or_deployment_requested",
            "manual_live_broker_capital_vault_or_live_auto_boundary_reached",
        ],
        "provider_session_opening_authorized_now": False,
        "provider_login_authorized_now": False,
        "provider_calls_authorized_now": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    payload["gate_hash"] = payload_hash(payload)
    return payload


def freeze_session_opening_execution_authorization_record(
    handoff: Mapping[str, Any],
    decision: Mapping[str, Any],
    validation: Mapping[str, Any],
    scope: Mapping[str, Any],
    binding: Mapping[str, Any],
    receipts: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "frozen_controlled_provider_session_opening_execution_authorization_record",
        "preparation_handoff_hash": _text(handoff.get("handoff_hash")),
        "frozen_session_opening_preparation_packet_hash": _text(handoff.get("frozen_session_opening_preparation_packet_hash")),
        "session_opening_preparation_decision_hash": _text(handoff.get("session_opening_preparation_decision_hash")),
        "execution_authorization_validation_report_hash": _text(validation.get("report_hash")),
        "execution_scope_manifest_hash": _text(scope.get("manifest_hash")),
        "identity_window_cost_binding_hash": _text(binding.get("binding_hash")),
        "execution_receipt_chain_and_stop_gate_hash": _text(receipts.get("gate_hash")),
        "owner_id_sha256": _fingerprint(decision.get("owner_id")),
        "tower_step_up_receipt_ref_sha256": _fingerprint(decision.get("tower_step_up_receipt_ref")),
        "owner_execution_authorization_receipt_ref_sha256": _fingerprint(decision.get("owner_execution_authorization_receipt_ref")),
        "authorization_approved": bool(validation.get("approved")),
        "authorization_rejected": bool(validation.get("rejected")),
        "raw_owner_identity_recorded": False,
        "raw_provider_identity_values_recorded": False,
        "raw_credentials_recorded": False,
        "raw_secret_values_recorded": False,
        "raw_tokens_or_cookies_recorded": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    payload["frozen_session_opening_execution_authorization_record_hash"] = payload_hash(payload)
    return payload


def build_inert_session_opening_execution_preparation_plan(
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    ready = bool(validation.get("approved"))
    payload = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": "inert_controlled_provider_session_opening_execution_preparation_plan",
        "ready_for_separate_execution_preparation": ready,
        "required_future_inputs": [
            "fresh_execution_preparation_receipt_ref",
            "exact_frozen_session_opening_execution_authorization_record_hash",
            "exact_execution_authorization_decision_hash",
            "fresh_window_revalidation_receipt_ref",
            "fresh_provider_identity_account_region_revalidation_receipts",
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
    })
    cached = _PARTS_CACHE.get(key)
    if cached is not None:
        return tuple(_clone(item) for item in cached)

    handoff = build_completed_session_opening_preparation_handoff(
        repository_root, provider_inputs, review_owner, review_inputs,
        provisioning_decision, execution_preparation_inputs,
        execution_authorization_decision, controlled_session_preparation_inputs,
        session_opening_authorization_decision, session_opening_preparation_inputs,
    )
    decision_input = session_opening_execution_authorization_decision or {}
    validation = validate_session_opening_execution_authorization_decision(decision_input, handoff=handoff)
    scope = build_session_opening_execution_scope_manifest(decision_input, validation)
    binding = build_identity_window_cost_binding(handoff, decision_input, validation)
    receipts = build_execution_receipt_chain_and_stop_gate(decision_input, validation)
    frozen = freeze_session_opening_execution_authorization_record(
        handoff, decision_input, validation, scope, binding, receipts
    )
    plan = build_inert_session_opening_execution_preparation_plan(validation)

    if not handoff.get("preparation_handoff_ready"):
        final = handoff.get("final_decision") or HOLD_OPENING_PREPARATION
    elif validation.get("rejected"):
        final = REJECTED_DECISION
    elif not validation.get("approved"):
        final = HOLD_EXECUTION_AUTHORIZATION
    else:
        final = READY_DECISION

    decision = {
        "schema_version": SCHEMA_VERSION,
        "decision_type": "controlled_provider_session_opening_execution_authorization_closeout",
        "preparation_handoff_ready": bool(handoff.get("preparation_handoff_ready")),
        "execution_authorization_valid": bool(validation.get("valid")),
        "execution_authorization_approved": bool(validation.get("approved")),
        "execution_authorization_rejected": bool(validation.get("rejected")),
        "ready_for_separate_controlled_provider_session_opening_execution_preparation": bool(validation.get("approved")),
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
    parts = (handoff, validation, scope, binding, receipts, frozen, decision, plan)
    _PARTS_CACHE[key] = tuple(_clone(item) for item in parts)
    return parts


def build_session_opening_execution_authorization_decision(*args):
    return _build_parts(*args)[6]


def build_current_session_opening_execution_authorization_state(
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
) -> dict[str, Any]:
    handoff, validation, scope, binding, receipts, frozen, decision, plan = _build_parts(
        repository_root, provider_inputs, provider_review_owner_decision, review_inputs,
        provisioning_decision, execution_preparation_inputs, execution_authorization_decision,
        controlled_session_preparation_inputs, session_opening_authorization_decision,
        session_opening_preparation_inputs, session_opening_execution_authorization_decision,
    )
    blockers = []
    if not handoff.get("preparation_handoff_ready"):
        blockers.append({"requirement": "valid_step120_session_opening_preparation", "status": "preparation_required"})
    for error in validation.get("errors", []):
        blockers.append({"requirement": error["field"], "status": error["code"]})
    state = {
        "schema_version": SCHEMA_VERSION,
        "closed_layer": "MANAGED_STAGING_CONTROLLED_PROVIDER_PROVISIONING_EXECUTION_SESSION_OPENING_EXECUTION_AUTHORIZATION",
        "closed_through_step": 130,
        "runtime_target": MANAGED_WSGI_TARGET,
        "runtime_topology": "single_tower_fronted_managed_python_web_service",
        "completed_session_opening_preparation_handoff_hash": handoff["handoff_hash"],
        "frozen_session_opening_execution_authorization_record_hash": frozen["frozen_session_opening_execution_authorization_record_hash"],
        "session_opening_execution_authorization_decision_hash": decision["decision_hash"],
        "inert_session_opening_execution_preparation_plan_hash": plan["plan_hash"],
        "session_opening_preparation_ready": bool(handoff.get("preparation_handoff_ready")),
        "session_opening_execution_authorization_valid": bool(validation.get("valid")),
        "session_opening_execution_authorization_approved": bool(validation.get("approved")),
        "ready_for_separate_controlled_provider_session_opening_execution_preparation": bool(validation.get("approved")),
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
        "next_boundary": "managed_staging_controlled_provider_provisioning_execution_session_opening_execution_preparation",
    }
    state["state_hash"] = payload_hash(state)
    return state


def write_json(path: str | Path, payload: Mapping[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_session_opening_execution_authorization_worksheets(
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
) -> dict[str, str]:
    output = Path(output_directory).resolve()
    root = Path(repository_root).resolve()
    if output == root or root in output.parents:
        raise ValueError("Session-opening execution-authorization worksheets must be written outside the repository.")
    handoff = build_completed_session_opening_preparation_handoff(
        root, provider_inputs, provider_review_owner_decision, review_inputs,
        provisioning_decision, execution_preparation_inputs, execution_authorization_decision,
        controlled_session_preparation_inputs, session_opening_authorization_decision,
        session_opening_preparation_inputs,
    )
    worksheet = write_json(
        output / "tower_ob_controlled_provider_session_opening_execution_authorization_decision.json",
        session_opening_execution_authorization_decision_template(handoff),
    )
    placeholder = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "controlled_provider_session_opening_execution_preparation_placeholder",
        "decision": "HOLD",
        "frozen_session_opening_execution_authorization_record_hash": "",
        "session_opening_execution_authorization_decision_hash": "",
        "provider_session_opening_authorized": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
        "notes": ["This placeholder is not execution preparation and performs no provider action."],
    }
    placeholder["template_hash"] = payload_hash(placeholder)
    placeholder_path = write_json(
        output / "tower_ob_controlled_provider_session_opening_execution_preparation_placeholder.json",
        placeholder,
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "session_opening_execution_authorization_decision_path": str(worksheet),
        "session_opening_execution_preparation_placeholder_path": str(placeholder_path),
        "preparation_handoff_ready": bool(handoff.get("preparation_handoff_ready")),
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
        "session_opening_execution_authorization_decision_path": str(worksheet),
        "session_opening_execution_preparation_placeholder_path": str(placeholder_path),
        "manifest_path": str(manifest_path),
    }


def blank_current_inputs(repository_root: str | Path) -> tuple[dict, ...]:
    prior = blank_session_opening_preparation_inputs(repository_root)
    handoff = build_completed_session_opening_preparation_handoff(repository_root, *prior)
    decision = session_opening_execution_authorization_decision_template(handoff)
    return (*prior, decision)


__all__ = [
    "AUTHORIZE_DECISION",
    "EXACT_CHALLENGE_PREFIX",
    "HOLD_EXECUTION_AUTHORIZATION",
    "READY_DECISION",
    "REJECT_DECISION",
    "REQUIRED_EXECUTION_AUTHORIZATION_ATTESTATIONS",
    "SCHEMA_VERSION",
    "blank_current_inputs",
    "build_completed_session_opening_preparation_handoff",
    "build_current_session_opening_execution_authorization_state",
    "build_execution_receipt_chain_and_stop_gate",
    "build_identity_window_cost_binding",
    "build_inert_session_opening_execution_preparation_plan",
    "build_session_opening_execution_authorization_challenge",
    "build_session_opening_execution_authorization_decision",
    "build_session_opening_execution_scope_manifest",
    "freeze_session_opening_execution_authorization_record",
    "session_opening_execution_authorization_decision_template",
    "validate_session_opening_execution_authorization_decision",
    "write_session_opening_execution_authorization_worksheets",
]
