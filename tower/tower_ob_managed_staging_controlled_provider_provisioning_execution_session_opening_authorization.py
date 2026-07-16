"""Controlled provider-session opening authorization contracts.

This layer binds a fresh Tower owner step-up decision to the frozen Step 100
controlled-session preparation packet. Even a valid authorization only opens a
later, separately prepared provider-session opening operation. This module never
opens or authenticates a provider session, invokes provider browser automation,
CLI, API, HTTP, or shell actions, creates resources, registers or reads secrets,
builds or deploys the application, changes DNS, creates databases or object
storage, or performs an official Observatory walkthrough.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping

from tower.tower_ob_managed_staging_controlled_provider_provisioning_execution_session_preparation import (
    blank_current_inputs as blank_session_preparation_inputs,
    build_controlled_session_preparation_decision,
    freeze_controlled_session_preparation_packet,
)
from tower.tower_ob_managed_staging_runtime import MANAGED_WSGI_TARGET, payload_hash

SCHEMA_VERSION = "simplee.tower_ob.controlled_provider_session_opening_authorization.v1"
AUTHORIZE_DECISION = "AUTHORIZE_CONTROLLED_PROVIDER_SESSION_OPENING_PREPARATION"
HOLD_DECISION = "HOLD"
REJECT_DECISION = "REJECT"
ALLOWED_DECISIONS = frozenset({AUTHORIZE_DECISION, HOLD_DECISION, REJECT_DECISION})
READY_DECISION = "GO_READY_FOR_SEPARATE_CONTROLLED_PROVIDER_SESSION_OPENING_PREPARATION"
HOLD_PROVIDER_INPUTS = "NO_GO_HOLD_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION_REQUIRED"
HOLD_SESSION_PREPARATION = "NO_GO_HOLD_CONTROLLED_SESSION_PREPARATION_REQUIRED"
HOLD_OPENING_AUTHORIZATION = "NO_GO_HOLD_CONTROLLED_SESSION_OPENING_AUTHORIZATION_REQUIRED"

REQUIRED_OPENING_SCOPE_ATTESTATIONS = (
    "staging_only_scope_confirmed",
    "single_tower_fronted_service_confirmed",
    "tower_only_public_ingress_confirmed",
    "observatory_separate_service_not_required",
    "frozen_session_preparation_packet_hash_confirmed",
    "session_preparation_decision_hash_confirmed",
    "authorized_source_commit_confirmed",
    "session_window_confirmed",
    "monthly_cost_ceiling_confirmed",
    "provider_account_team_fingerprint_confirmed",
    "provider_region_fingerprint_confirmed",
    "owner_session_receipt_fingerprint_confirmed",
    "fresh_tower_owner_step_up_confirmed",
    "duplicate_resource_lookup_required_before_opening",
    "stop_if_duplicate_or_ambiguous_resource_confirmed",
    "manual_provider_session_opening_control_confirmed",
    "one_inert_web_service_shell_limit_confirmed",
    "non_secret_environment_names_only_confirmed",
    "secret_reference_registration_without_readback_confirmed",
    "receipt_chain_and_stop_gate_confirmed",
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
    "no_provider_session_login_or_calls_performed_during_decision",
)

_SAFE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+ #(),-]{1,299}$")
_COMMIT_REF = re.compile(r"^(?:commit/)?[0-9a-f]{40}$", re.I)
_ISO_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
_MONEY = re.compile(r"^\d{1,6}(?:\.\d{1,2})?$")
_SENSITIVE_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
    re.compile(r"\b(?:api[_-]?key|access[_-]?token|token|secret|password)\s*[:=]\s*\S+", re.I),
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


def build_completed_session_preparation_handoff(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
    execution_preparation_inputs: Mapping[str, Any] | None,
    execution_authorization_decision: Mapping[str, Any] | None,
    controlled_session_preparation_inputs: Mapping[str, Any] | None,
) -> dict[str, Any]:
    decision = build_controlled_session_preparation_decision(
        repository_root, provider_inputs or {}, provider_review_owner_decision or {},
        review_inputs or {}, provisioning_decision or {}, execution_preparation_inputs or {},
        execution_authorization_decision or {}, controlled_session_preparation_inputs or {},
    )
    frozen = freeze_controlled_session_preparation_packet(
        repository_root, provider_inputs or {}, provider_review_owner_decision or {},
        review_inputs or {}, provisioning_decision or {}, execution_preparation_inputs or {},
        execution_authorization_decision or {}, controlled_session_preparation_inputs or {},
    )
    ready = bool(decision.get("session_preparation_valid") and decision.get("ready_for_separate_controlled_provider_session_opening_authorization"))
    handoff = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "completed_controlled_provider_session_preparation_handoff",
        "frozen_session_preparation_packet_hash": frozen.get("frozen_session_preparation_packet_hash", ""),
        "session_preparation_decision_hash": decision.get("decision_hash", ""),
        "frozen_execution_authorization_record_hash": frozen.get("frozen_execution_authorization_record_hash", ""),
        "execution_authorization_decision_hash": frozen.get("execution_authorization_decision_hash", ""),
        "authorized_source_commit_ref": _text((controlled_session_preparation_inputs or {}).get("authorized_source_commit_ref")),
        "session_window_starts_at": _text((controlled_session_preparation_inputs or {}).get("session_window_starts_at")),
        "session_window_expires_at": _text((controlled_session_preparation_inputs or {}).get("session_window_expires_at")),
        "monthly_cost_ceiling_usd": _text((controlled_session_preparation_inputs or {}).get("monthly_cost_ceiling_usd")),
        "provider_slug_sha256": frozen.get("provider_slug_sha256"),
        "account_or_team_ref_sha256": frozen.get("account_or_team_ref_sha256"),
        "deployment_region_sha256": frozen.get("deployment_region_sha256"),
        "owner_execution_session_receipt_ref_sha256": frozen.get("owner_execution_session_receipt_ref_sha256"),
        "session_preparation_valid": bool(decision.get("session_preparation_valid")),
        "completed_session_preparation_ready": ready,
        "provider_session_opening_authorized": False,
        "provider_login_authorized": False,
        "provider_calls_authorized": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
        "final_decision": decision.get("final_decision", HOLD_SESSION_PREPARATION),
    }
    handoff["handoff_hash"] = payload_hash(handoff)
    return handoff


def build_session_opening_authorization_challenge(handoff: Mapping[str, Any]) -> dict[str, Any]:
    packet_hash = _text(handoff.get("frozen_session_preparation_packet_hash"))
    seed = payload_hash({"schema_version": SCHEMA_VERSION, "packet_hash": packet_hash, "purpose": "controlled_provider_session_opening"})
    suffix = seed[:12].upper()
    challenge = {
        "schema_version": SCHEMA_VERSION,
        "challenge_type": "controlled_provider_session_opening_authorization",
        "frozen_session_preparation_packet_hash": packet_hash,
        "challenge_id": f"tower-ob-session-open-{suffix.lower()}",
        "challenge_phrase": f"AUTHORIZE CONTROLLED SESSION OPENING {suffix}",
        "challenge_ready": bool(handoff.get("completed_session_preparation_ready") and packet_hash),
        "provider_session_opened": False,
        "provider_calls_performed": False,
    }
    challenge["challenge_hash"] = payload_hash(challenge)
    return challenge


def session_opening_authorization_decision_template(handoff: Mapping[str, Any]) -> dict[str, Any]:
    challenge = build_session_opening_authorization_challenge(handoff)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "controlled_provider_session_opening_authorization_decision",
        "allowed_decisions": sorted(ALLOWED_DECISIONS),
        "decision": HOLD_DECISION,
        "frozen_session_preparation_packet_hash": _text(handoff.get("frozen_session_preparation_packet_hash")),
        "session_preparation_decision_hash": _text(handoff.get("session_preparation_decision_hash")),
        "authorized_source_commit_ref": _text(handoff.get("authorized_source_commit_ref")),
        "authorized_session_starts_at": _text(handoff.get("session_window_starts_at")),
        "authorized_session_expires_at": _text(handoff.get("session_window_expires_at")),
        "monthly_cost_ceiling_usd": _text(handoff.get("monthly_cost_ceiling_usd")),
        "owner_id": "",
        "tower_step_up_receipt_ref": "",
        "challenge_id": challenge["challenge_id"],
        "expected_challenge_phrase": challenge["challenge_phrase"],
        "challenge_phrase_confirmation": "",
        "decided_at": "",
        "authorization_expires_at": "",
        "authorized_scope": {
            "open_one_manual_provider_console_session": False,
            "authenticate_to_bound_provider_account_team": False,
            "perform_duplicate_resource_lookup": False,
            "prepare_one_inert_managed_web_service_shell": False,
            "capture_non_secret_provider_references": False,
        },
        "scope_attestations": {name: False for name in REQUIRED_OPENING_SCOPE_ATTESTATIONS},
        "notes": [
            "Use a fresh Tower owner step-up receipt reference.",
            "Do not place passwords, tokens, cookies, API keys, or secret values in this file.",
            "Approval opens only a later separately prepared session-opening operation.",
            "This decision performs no provider login, calls, resource creation, secret registration, build, or deployment.",
        ],
    }
    payload["template_hash"] = payload_hash(payload)
    return payload


def validate_session_opening_authorization_decision(decision: Mapping[str, Any] | None, *, handoff: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(decision or {})
    challenge = build_session_opening_authorization_challenge(handoff)
    checks: dict[str, bool] = {
        "completed_session_preparation_ready": bool(handoff.get("completed_session_preparation_ready")),
        "decision_allowed": _text(payload.get("decision")) in ALLOWED_DECISIONS,
        "decision_authorizes": _text(payload.get("decision")) == AUTHORIZE_DECISION,
        "frozen_session_preparation_packet_hash_matches": _text(payload.get("frozen_session_preparation_packet_hash")) == _text(handoff.get("frozen_session_preparation_packet_hash")) and bool(_text(handoff.get("frozen_session_preparation_packet_hash"))),
        "session_preparation_decision_hash_matches": _text(payload.get("session_preparation_decision_hash")) == _text(handoff.get("session_preparation_decision_hash")) and bool(_text(handoff.get("session_preparation_decision_hash"))),
        "authorized_source_commit_format_valid": bool(_COMMIT_REF.fullmatch(_text(payload.get("authorized_source_commit_ref")))),
        "authorized_source_commit_matches": _normalize_commit(payload.get("authorized_source_commit_ref")) == _normalize_commit(handoff.get("authorized_source_commit_ref")) and bool(_normalize_commit(handoff.get("authorized_source_commit_ref"))),
        "owner_id_present": bool(_SAFE_REF.fullmatch(_text(payload.get("owner_id")))),
        "tower_step_up_receipt_ref_present": bool(_SAFE_REF.fullmatch(_text(payload.get("tower_step_up_receipt_ref")))),
        "challenge_id_matches": _text(payload.get("challenge_id")) == challenge["challenge_id"],
        "challenge_phrase_matches": _text(payload.get("challenge_phrase_confirmation")) == challenge["challenge_phrase"],
        "decided_at_is_utc_iso": _parse_utc(payload.get("decided_at")) is not None,
        "monthly_cost_ceiling_valid": _valid_money(payload.get("monthly_cost_ceiling_usd")),
        "monthly_cost_ceiling_matches": _text(payload.get("monthly_cost_ceiling_usd")) == _text(handoff.get("monthly_cost_ceiling_usd")) and bool(_text(handoff.get("monthly_cost_ceiling_usd"))),
    }
    session_start = _parse_utc(payload.get("authorized_session_starts_at"))
    session_end = _parse_utc(payload.get("authorized_session_expires_at"))
    prepared_start = _parse_utc(handoff.get("session_window_starts_at"))
    prepared_end = _parse_utc(handoff.get("session_window_expires_at"))
    auth_expiry = _parse_utc(payload.get("authorization_expires_at"))
    decided_at = _parse_utc(payload.get("decided_at"))
    checks["session_window_ordered"] = bool(session_start and session_end and session_start < session_end)
    checks["session_window_matches_preparation"] = bool(session_start and session_end and prepared_start and prepared_end and session_start == prepared_start and session_end == prepared_end)
    checks["authorization_expiry_valid"] = bool(decided_at and auth_expiry and decided_at < auth_expiry <= session_end)
    scope = payload.get("authorized_scope") if isinstance(payload.get("authorized_scope"), Mapping) else {}
    for name in (
        "open_one_manual_provider_console_session", "authenticate_to_bound_provider_account_team",
        "perform_duplicate_resource_lookup", "prepare_one_inert_managed_web_service_shell",
        "capture_non_secret_provider_references",
    ):
        checks[f"authorized_scope.{name}"] = _bool(scope.get(name))
    attest = payload.get("scope_attestations") if isinstance(payload.get("scope_attestations"), Mapping) else {}
    for name in REQUIRED_OPENING_SCOPE_ATTESTATIONS:
        checks[f"scope_attestations.{name}"] = _bool(attest.get(name))
    checks["contains_sensitive_material"] = _contains_sensitive(payload)
    errors = []
    for name, passed in checks.items():
        if name == "contains_sensitive_material":
            if passed:
                errors.append({"field": name, "code": "sensitive_material_prohibited"})
        elif not passed:
            errors.append({"field": name, "code": "required_check_failed"})
    valid = not errors
    report = {"schema_version": SCHEMA_VERSION, "valid": valid, "checks": checks, "errors": errors}
    report["report_hash"] = payload_hash(report)
    return report


def build_session_opening_scope_manifest(validation: Mapping[str, Any] | None = None) -> dict[str, Any]:
    authorized = bool((validation or {}).get("valid"))
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "controlled_provider_session_opening_scope",
        "authorization_valid": authorized,
        "future_scope": {
            "open_one_manual_provider_console_session": authorized,
            "authenticate_to_bound_provider_account_team": authorized,
            "duplicate_resource_lookup": authorized,
            "prepare_one_inert_web_service_shell": authorized,
            "capture_non_secret_provider_references": authorized,
        },
        "resource_ceiling": {"managed_web_service_shells": 1 if authorized else 0, "databases": 0, "object_storage_buckets": 0, "dns_changes": 0},
        "build_authorized": False,
        "deployment_authorized": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
    }
    manifest["manifest_hash"] = payload_hash(manifest)
    return manifest


def build_session_identity_and_window_manifest(handoff: Mapping[str, Any], decision: Mapping[str, Any] | None, validation: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(decision or {})
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "controlled_provider_session_identity_and_window",
        "authorization_valid": bool((validation or {}).get("valid")),
        "provider_slug_sha256": handoff.get("provider_slug_sha256"),
        "account_or_team_ref_sha256": handoff.get("account_or_team_ref_sha256"),
        "deployment_region_sha256": handoff.get("deployment_region_sha256"),
        "owner_execution_session_receipt_ref_sha256": handoff.get("owner_execution_session_receipt_ref_sha256"),
        "owner_id_sha256": _fingerprint(payload.get("owner_id")),
        "tower_step_up_receipt_ref_sha256": _fingerprint(payload.get("tower_step_up_receipt_ref")),
        "authorized_source_commit_sha256": _fingerprint(payload.get("authorized_source_commit_ref")),
        "authorized_session_starts_at": _text(payload.get("authorized_session_starts_at")),
        "authorized_session_expires_at": _text(payload.get("authorized_session_expires_at")),
        "authorization_expires_at": _text(payload.get("authorization_expires_at")),
        "monthly_cost_ceiling_usd": _text(payload.get("monthly_cost_ceiling_usd")),
        "raw_provider_values_recorded": False,
        "raw_secret_values_recorded": False,
        "provider_session_opened": False,
    }
    manifest["manifest_hash"] = payload_hash(manifest)
    return manifest


def build_session_opening_receipt_and_stop_contract() -> dict[str, Any]:
    contract = {
        "schema_version": SCHEMA_VERSION,
        "contract_type": "controlled_provider_session_opening_receipt_and_stop_gate",
        "required_receipt_order": [
            "opening_authorization_revalidation_receipt",
            "provider_identity_fingerprint_receipt",
            "authorization_window_receipt",
            "duplicate_resource_lookup_receipt",
            "provider_session_opening_receipt",
            "provider_authentication_receipt",
            "stop_before_resource_creation_receipt",
            "session_close_receipt",
        ],
        "mandatory_stop_conditions": [
            "authorization missing invalid expired or hash mismatch",
            "provider account team or region fingerprint mismatch",
            "duplicate or ambiguous resource detected",
            "provider asks for broader scope than one inert service shell",
            "secret value readback or export requested",
            "build deployment database storage DNS or walkthrough requested",
        ],
        "provider_session_opened": False,
        "provider_calls_performed": False,
        "resources_created": False,
    }
    contract["contract_hash"] = payload_hash(contract)
    return contract


def _build_parts(repository_root: str | Path, provider_inputs, review_owner, review_inputs, provisioning_decision, execution_preparation_inputs, execution_authorization_decision, controlled_session_preparation_inputs, opening_decision):
    key = payload_hash({"root": str(Path(repository_root).resolve()), "values": [provider_inputs or {}, review_owner or {}, review_inputs or {}, provisioning_decision or {}, execution_preparation_inputs or {}, execution_authorization_decision or {}, controlled_session_preparation_inputs or {}, opening_decision or {}]})
    if key in _PARTS_CACHE:
        return tuple(_clone(item) for item in _PARTS_CACHE[key])
    handoff = build_completed_session_preparation_handoff(repository_root, provider_inputs, review_owner, review_inputs, provisioning_decision, execution_preparation_inputs, execution_authorization_decision, controlled_session_preparation_inputs)
    validation = validate_session_opening_authorization_decision(opening_decision, handoff=handoff)
    scope = build_session_opening_scope_manifest(validation)
    identity = build_session_identity_and_window_manifest(handoff, opening_decision, validation)
    receipts = build_session_opening_receipt_and_stop_contract()
    frozen = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "frozen_controlled_provider_session_opening_authorization",
        "completed_session_preparation_handoff_hash": handoff["handoff_hash"],
        "frozen_session_preparation_packet_hash": handoff["frozen_session_preparation_packet_hash"],
        "session_preparation_decision_hash": handoff["session_preparation_decision_hash"],
        "authorization_validation_report_hash": validation["report_hash"],
        "opening_scope_manifest_hash": scope["manifest_hash"],
        "identity_and_window_manifest_hash": identity["manifest_hash"],
        "receipt_and_stop_contract_hash": receipts["contract_hash"],
        "authorization_valid": validation["valid"],
        "owner_id_sha256": identity["owner_id_sha256"],
        "tower_step_up_receipt_ref_sha256": identity["tower_step_up_receipt_ref_sha256"],
        "raw_owner_values_recorded": False,
        "raw_provider_values_recorded": False,
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
    frozen["frozen_session_opening_authorization_record_hash"] = payload_hash(frozen)
    if not handoff["completed_session_preparation_ready"]:
        final = handoff["final_decision"] or HOLD_SESSION_PREPARATION
    elif not validation["valid"]:
        final = HOLD_OPENING_AUTHORIZATION
    else:
        final = READY_DECISION
    decision = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "controlled_provider_session_opening_authorization_decision",
        "frozen_session_opening_authorization_record_hash": frozen["frozen_session_opening_authorization_record_hash"],
        "authorization_valid": validation["valid"],
        "ready_for_separate_controlled_provider_session_opening_preparation": bool(handoff["completed_session_preparation_ready"] and validation["valid"]),
        "provider_session_opening_authorized_for_later_preparation": bool(validation["valid"]),
        "provider_login_authorized_for_later_preparation": bool(validation["valid"]),
        "provider_calls_authorized_for_later_preparation": bool(validation["valid"]),
        "one_inert_service_shell_scope_authorized_for_later_preparation": bool(validation["valid"]),
        "resource_creation_authorized": False,
        "secret_reference_registration_authorized": False,
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
        "final_decision": final,
    }
    decision["decision_hash"] = payload_hash(decision)
    plan = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": "inert_controlled_provider_session_opening_preparation_plan",
        "opening_authorization_decision_hash": decision["decision_hash"],
        "ready_for_later_separate_preparation": decision["ready_for_separate_controlled_provider_session_opening_preparation"],
        "future_sequence": [
            "revalidate frozen Step 100 preparation and Step 110 authorization",
            "revalidate owner step-up receipt and authorization window",
            "prepare provider identity and duplicate-resource lookup controls",
            "prepare session opening and authentication receipts",
            "stop before resource creation secret registration build or deployment",
        ],
        "provider_cli_commands": [], "provider_api_requests": [], "http_requests": [], "browser_actions": [], "shell_commands": [],
        "dry_run_only": True,
        "provider_session_opened": False, "provider_login_performed": False, "provider_calls_performed": False,
        "resources_created": False, "secrets_registered": False, "build_performed": False, "deployment_performed": False,
        "final_decision": final,
    }
    plan["plan_hash"] = payload_hash(plan)
    parts = (handoff, validation, scope, identity, receipts, frozen, decision, plan)
    _PARTS_CACHE[key] = tuple(_clone(item) for item in parts)
    return parts


def freeze_session_opening_authorization_record(repository_root, provider_inputs, review_owner, review_inputs, provisioning_decision, execution_preparation_inputs, execution_authorization_decision, controlled_session_preparation_inputs, opening_decision):
    return _build_parts(repository_root, provider_inputs, review_owner, review_inputs, provisioning_decision, execution_preparation_inputs, execution_authorization_decision, controlled_session_preparation_inputs, opening_decision)[5]


def build_session_opening_authorization_decision(repository_root, provider_inputs, review_owner, review_inputs, provisioning_decision, execution_preparation_inputs, execution_authorization_decision, controlled_session_preparation_inputs, opening_decision):
    return _build_parts(repository_root, provider_inputs, review_owner, review_inputs, provisioning_decision, execution_preparation_inputs, execution_authorization_decision, controlled_session_preparation_inputs, opening_decision)[6]


def build_inert_session_opening_preparation_plan(repository_root, provider_inputs, review_owner, review_inputs, provisioning_decision, execution_preparation_inputs, execution_authorization_decision, controlled_session_preparation_inputs, opening_decision):
    return _build_parts(repository_root, provider_inputs, review_owner, review_inputs, provisioning_decision, execution_preparation_inputs, execution_authorization_decision, controlled_session_preparation_inputs, opening_decision)[7]


def build_current_session_opening_authorization_state(repository_root: str | Path, provider_inputs=None, provider_review_owner_decision=None, review_inputs=None, provisioning_decision=None, execution_preparation_inputs=None, execution_authorization_decision=None, controlled_session_preparation_inputs=None, opening_decision=None) -> dict[str, Any]:
    handoff, validation, _scope, _identity, _receipts, frozen, decision, plan = _build_parts(repository_root, provider_inputs, provider_review_owner_decision, review_inputs, provisioning_decision, execution_preparation_inputs, execution_authorization_decision, controlled_session_preparation_inputs, opening_decision)
    blockers = []
    if not handoff["completed_session_preparation_ready"]:
        blockers.append({"requirement": "completed_controlled_session_preparation", "status": "valid_session_preparation_required"})
    for error in validation["errors"]:
        blockers.append({"requirement": error["field"], "status": error["code"]})
    state = {
        "schema_version": SCHEMA_VERSION,
        "closed_layer": "MANAGED_STAGING_CONTROLLED_PROVIDER_PROVISIONING_EXECUTION_SESSION_OPENING_AUTHORIZATION",
        "closed_through_step": 110,
        "runtime_target": MANAGED_WSGI_TARGET,
        "runtime_topology": "single_tower_fronted_managed_python_web_service",
        "completed_session_preparation_handoff_hash": handoff["handoff_hash"],
        "frozen_session_opening_authorization_record_hash": frozen["frozen_session_opening_authorization_record_hash"],
        "session_opening_authorization_decision_hash": decision["decision_hash"],
        "inert_session_opening_preparation_plan_hash": plan["plan_hash"],
        "session_preparation_ready": handoff["completed_session_preparation_ready"],
        "session_opening_authorization_valid": validation["valid"],
        "ready_for_separate_controlled_provider_session_opening_preparation": decision["ready_for_separate_controlled_provider_session_opening_preparation"],
        "blocking_requirements": blockers,
        "blocking_requirement_count": len(blockers),
        "provider_session_opening_authorized_for_later_preparation": decision["provider_session_opening_authorized_for_later_preparation"],
        "provider_login_authorized_for_later_preparation": decision["provider_login_authorized_for_later_preparation"],
        "provider_calls_authorized_for_later_preparation": decision["provider_calls_authorized_for_later_preparation"],
        "resource_creation_authorized": False, "secret_reference_registration_authorized": False,
        "database_creation_authorized": False, "object_storage_creation_authorized": False, "dns_changes_authorized": False,
        "build_authorized": False, "deployment_authorized": False,
        "provider_session_opened": False, "provider_login_performed": False, "provider_calls_performed": False,
        "resources_created": False, "secrets_registered": False, "secrets_created_or_read": False,
        "build_performed": False, "deployment_performed": False, "official_walkthrough_performed": False,
        "production_manual_live_authorized": False, "broker_submission_enabled": False, "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False, "live_auto_locked": True, "permanent_main_modified": False,
        "final_decision": decision["final_decision"],
        "next_boundary": "managed_staging_controlled_provider_provisioning_execution_session_opening_preparation",
    }
    state["state_hash"] = payload_hash(state)
    return state


def write_json(path: str | Path, payload: Mapping[str, Any]) -> Path:
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_session_opening_authorization_worksheets(output_directory: str | Path, *, repository_root: str | Path, provider_inputs=None, provider_review_owner_decision=None, review_inputs=None, provisioning_decision=None, execution_preparation_inputs=None, execution_authorization_decision=None, controlled_session_preparation_inputs=None) -> dict[str, str]:
    output = Path(output_directory).resolve(); root = Path(repository_root).resolve()
    if output == root or root in output.parents:
        raise ValueError("Session-opening authorization worksheets must be written outside the repository.")
    handoff = build_completed_session_preparation_handoff(root, provider_inputs, provider_review_owner_decision, review_inputs, provisioning_decision, execution_preparation_inputs, execution_authorization_decision, controlled_session_preparation_inputs)
    decision_path = write_json(output / "tower_ob_controlled_provider_session_opening_authorization_decision.json", session_opening_authorization_decision_template(handoff))
    placeholder = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "controlled_provider_session_opening_preparation_placeholder",
        "decision": "HOLD",
        "frozen_session_opening_authorization_record_hash": "",
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
        "notes": ["This placeholder is not a provider session.", "A later corridor must prepare session opening after a valid frozen Step 110 authorization."],
    }
    placeholder["template_hash"] = payload_hash(placeholder)
    placeholder_path = write_json(output / "tower_ob_controlled_provider_session_opening_preparation_placeholder.json", placeholder)
    manifest = {
        "schema_version": SCHEMA_VERSION, "generated_at": _utc_now(),
        "session_opening_authorization_decision_path": str(decision_path),
        "session_opening_preparation_placeholder_path": str(placeholder_path),
        "session_preparation_ready": handoff["completed_session_preparation_ready"],
        "contains_secret_values": False, "provider_session_opened": False, "provider_login_performed": False,
        "provider_calls_performed": False, "resources_created": False, "secrets_registered": False,
        "build_performed": False, "deployment_performed": False,
    }
    manifest_path = write_json(output / "worksheet_manifest.json", manifest)
    return {"session_opening_authorization_decision_path": str(decision_path), "session_opening_preparation_placeholder_path": str(placeholder_path), "manifest_path": str(manifest_path)}


def blank_current_inputs(repository_root: str | Path) -> tuple[dict, ...]:
    provider, review_owner, review, provisioning, execution_preparation, execution_authorization, session_preparation = blank_session_preparation_inputs(repository_root)
    handoff = build_completed_session_preparation_handoff(repository_root, provider, review_owner, review, provisioning, execution_preparation, execution_authorization, session_preparation)
    opening = session_opening_authorization_decision_template(handoff)
    return provider, review_owner, review, provisioning, execution_preparation, execution_authorization, session_preparation, opening


__all__ = [
    "ALLOWED_DECISIONS", "AUTHORIZE_DECISION", "HOLD_DECISION", "REJECT_DECISION", "READY_DECISION",
    "REQUIRED_OPENING_SCOPE_ATTESTATIONS", "SCHEMA_VERSION", "blank_current_inputs",
    "build_completed_session_preparation_handoff", "build_current_session_opening_authorization_state",
    "build_inert_session_opening_preparation_plan", "build_session_identity_and_window_manifest",
    "build_session_opening_authorization_challenge", "build_session_opening_authorization_decision",
    "build_session_opening_receipt_and_stop_contract", "build_session_opening_scope_manifest",
    "freeze_session_opening_authorization_record", "session_opening_authorization_decision_template",
    "validate_session_opening_authorization_decision", "write_session_opening_authorization_worksheets",
]
