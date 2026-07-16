"""Controlled provider provisioning execution-authorization contracts.

This layer binds a fresh Tower owner step-up decision to the completed,
frozen no-call provider-provisioning execution-preparation packet. A valid
approval may open a later, separately controlled provider execution session
for exactly one inert Tower-fronted staging web-service shell. This module
never authenticates to a provider, invokes a provider API/CLI, creates a
resource, registers or reads secrets, builds or deploys the application,
changes DNS, creates databases or object storage, or performs an official
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

from tower.tower_ob_managed_staging_no_call_provisioning_execution_preparation import (
    blank_current_inputs as blank_preparation_inputs,
    build_execution_preparation_decision,
    freeze_execution_preparation_packet,
)
from tower.tower_ob_managed_staging_runtime import (
    MANAGED_START_COMMAND,
    MANAGED_WSGI_TARGET,
    payload_hash,
)

SCHEMA_VERSION = (
    "simplee.tower_ob.provider_provisioning_execution_authorization.v1"
)

AUTHORIZE_DECISION = "AUTHORIZE_CONTROLLED_PROVISIONING_EXECUTION_SESSION"
HOLD_DECISION = "HOLD"
REJECT_DECISION = "REJECT"
ALLOWED_DECISIONS = frozenset({
    AUTHORIZE_DECISION,
    HOLD_DECISION,
    REJECT_DECISION,
})

REQUIRED_EXECUTION_SCOPE_ATTESTATIONS = (
    "staging_only_scope_confirmed",
    "single_tower_fronted_service_confirmed",
    "tower_only_public_ingress_confirmed",
    "observatory_separate_service_not_required",
    "provider_account_team_matches_frozen_inputs",
    "deployment_region_matches_frozen_inputs",
    "source_commit_matches_frozen_preparation",
    "manual_owner_controlled_session_confirmed",
    "one_web_service_resource_limit_confirmed",
    "duplicate_resource_lookup_required_before_creation",
    "monthly_cost_ceiling_confirmed",
    "non_secret_environment_names_only_confirmed",
    "secret_reference_registration_without_readback_confirmed",
    "health_check_and_access_logs_confirmed",
    "manual_deployment_control_confirmed",
    "rollback_target_confirmed",
    "stop_after_inert_service_shell_confirmed",
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
    "no_provider_login_or_calls_performed_during_decision",
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


def build_completed_execution_preparation_handoff(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
    preparation_inputs: Mapping[str, Any] | None,
) -> dict[str, Any]:
    preparation_decision = build_execution_preparation_decision(
        repository_root,
        provider_inputs or {},
        provider_review_owner_decision or {},
        review_inputs or {},
        provisioning_decision or {},
        preparation_inputs or {},
    )
    frozen = freeze_execution_preparation_packet(
        repository_root,
        provider_inputs or {},
        provider_review_owner_decision or {},
        review_inputs or {},
        provisioning_decision or {},
        preparation_inputs or {},
    )
    ready = bool(
        preparation_decision.get("preparation_inputs_valid")
        and preparation_decision.get(
            "ready_for_separate_provider_provisioning_execution_authorization"
        )
    )
    handoff = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "completed_no_call_execution_preparation_handoff",
        "frozen_execution_preparation_packet_hash": frozen.get(
            "frozen_execution_preparation_packet_hash", ""
        ),
        "execution_preparation_decision_hash": preparation_decision.get(
            "decision_hash", ""
        ),
        "provisioning_authorization_record_hash": frozen.get(
            "provisioning_authorization_record_hash", ""
        ),
        "authorization_handoff_hash": frozen.get(
            "authorization_handoff_hash", ""
        ),
        "provider_inputs_valid": bool(
            preparation_decision.get("provider_inputs_valid")
        ),
        "provider_review_owner_approval_valid": bool(
            preparation_decision.get("provider_review_owner_approval_valid")
        ),
        "review_inputs_valid": bool(
            preparation_decision.get("review_inputs_valid")
        ),
        "provisioning_authorization_valid": bool(
            preparation_decision.get("provisioning_authorization_valid")
        ),
        "preparation_inputs_valid": bool(
            preparation_decision.get("preparation_inputs_valid")
        ),
        "completed_execution_preparation_ready": ready,
        "provider_login_authorized": False,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "secret_registration_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    handoff["handoff_hash"] = payload_hash(handoff)
    return handoff


def build_execution_authorization_challenge(
    handoff: Mapping[str, Any],
) -> dict[str, Any]:
    packet_hash = _text(
        handoff.get("frozen_execution_preparation_packet_hash")
    ) or ("0" * 64)
    challenge_id = hashlib.sha256(
        (
            "simplee:tower-ob:managed-staging:controlled-provider-"
            "provisioning-execution-session:" + packet_hash
        ).encode("utf-8")
    ).hexdigest()[:24]
    phrase = (
        "AUTHORIZE TOWER OB STAGING CONTROLLED PROVISIONING SESSION "
        + challenge_id.upper()
    )
    challenge = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "provider_provisioning_execution_authorization_challenge",
        "challenge_id": challenge_id,
        "challenge_phrase": phrase,
        "frozen_execution_preparation_packet_hash": packet_hash,
        "execution_preparation_decision_hash": _text(
            handoff.get("execution_preparation_decision_hash")
        ),
        "required_decision": AUTHORIZE_DECISION,
        "tower_owner_session_required": True,
        "tower_step_up_receipt_required": True,
        "completed_execution_preparation_required": True,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "deployment_performed": False,
    }
    challenge["challenge_hash"] = payload_hash(challenge)
    return challenge


def execution_authorization_decision_template(
    handoff: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source = dict(handoff or {})
    challenge = build_execution_authorization_challenge(source)
    challenge_ready = bool(source.get("completed_execution_preparation_ready"))
    template = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "provider_provisioning_execution_authorization_decision",
        "decision": HOLD_DECISION,
        "frozen_execution_preparation_packet_hash": _text(
            source.get("frozen_execution_preparation_packet_hash")
        ),
        "execution_preparation_decision_hash": _text(
            source.get("execution_preparation_decision_hash")
        ),
        "owner_id": "",
        "tower_step_up_receipt_ref": "",
        "challenge_ready": challenge_ready,
        "challenge_id": challenge["challenge_id"] if challenge_ready else "",
        "expected_challenge_phrase": (
            challenge["challenge_phrase"] if challenge_ready else ""
        ),
        "challenge_phrase_confirmation": "",
        "decided_at": "",
        "execution_window_starts_at": "",
        "execution_window_expires_at": "",
        "authorized_source_commit_ref": "",
        "monthly_cost_ceiling_usd": "",
        "authorized_scope": {
            "provider_console_login": False,
            "provider_account_team_access": False,
            "provider_region_access": False,
            "duplicate_resource_lookup": False,
            "create_one_inert_managed_web_service_shell": False,
            "bind_authorized_repository_branch_and_commit": False,
            "configure_non_secret_environment_names": False,
            "register_secret_references_without_readback": False,
            "configure_health_checks": False,
            "configure_deployment_and_access_logs": False,
            "configure_manual_deployment_control": False,
            "configure_rollback_target": False,
            "capture_non_secret_provider_resource_references": False,
        },
        "scope_attestations": {
            name: False for name in REQUIRED_EXECUTION_SCOPE_ATTESTATIONS
        },
        "notes": [
            "Do not include passwords, tokens, API keys, cookies, private keys, connection strings, or secret values.",
            "Approval opens only a later controlled provider execution session with receipt checkpoints.",
            "Approval does not itself log in, call a provider, create a resource, register a secret, build, deploy, change DNS, create a database or storage, or perform a walkthrough.",
        ],
    }
    template["template_hash"] = payload_hash(template)
    return template


def validate_execution_authorization_decision(
    decision: Mapping[str, Any] | None,
    *,
    handoff: Mapping[str, Any],
    challenge: Mapping[str, Any],
    provisioning_decision: Mapping[str, Any] | None,
    preparation_inputs: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(decision or {})
    provisioning = dict(provisioning_decision or {})
    preparation = dict(preparation_inputs or {})
    normalized_decision = _text(source.get("decision")).upper() or HOLD_DECISION
    errors: list[dict[str, str]] = []

    decided_at = _parse_utc(source.get("decided_at"))
    starts_at = _parse_utc(source.get("execution_window_starts_at"))
    expires_at = _parse_utc(source.get("execution_window_expires_at"))
    window_seconds = (
        int((expires_at - starts_at).total_seconds())
        if starts_at and expires_at and expires_at > starts_at
        else None
    )

    expected_commit = _normalize_commit_ref(
        preparation.get("source_commit_ref")
    )
    supplied_commit = _normalize_commit_ref(
        source.get("authorized_source_commit_ref")
    )
    expected_cost = _text(provisioning.get("monthly_cost_ceiling_usd"))
    supplied_cost = _text(source.get("monthly_cost_ceiling_usd"))

    checks = {
        "completed_execution_preparation_ready": bool(
            handoff.get("completed_execution_preparation_ready")
        ),
        "decision_allowed": normalized_decision in ALLOWED_DECISIONS,
        "frozen_execution_preparation_packet_hash_matches": (
            _text(source.get("frozen_execution_preparation_packet_hash"))
            == _text(handoff.get("frozen_execution_preparation_packet_hash"))
        ),
        "execution_preparation_decision_hash_matches": (
            _text(source.get("execution_preparation_decision_hash"))
            == _text(handoff.get("execution_preparation_decision_hash"))
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
        "decided_at_is_utc_iso": decided_at is not None,
        "execution_window_starts_at_is_utc_iso": starts_at is not None,
        "execution_window_expires_at_is_utc_iso": expires_at is not None,
        "execution_window_ordered": bool(
            decided_at and starts_at and expires_at
            and decided_at <= starts_at < expires_at
        ),
        "execution_window_duration_within_120_minutes": bool(
            window_seconds is not None and 0 < window_seconds <= 7200
        ),
        "authorized_source_commit_format_valid": bool(
            _COMMIT_REF.fullmatch(_text(source.get("authorized_source_commit_ref")))
        ),
        "authorized_source_commit_matches_preparation": bool(
            expected_commit and supplied_commit == expected_commit
        ),
        "monthly_cost_ceiling_valid": _valid_money(supplied_cost),
        "monthly_cost_ceiling_matches_provisioning_authorization": bool(
            expected_cost and supplied_cost == expected_cost
        ),
    }

    required_scope = {
        "provider_console_login": True,
        "provider_account_team_access": True,
        "provider_region_access": True,
        "duplicate_resource_lookup": True,
        "create_one_inert_managed_web_service_shell": True,
        "bind_authorized_repository_branch_and_commit": True,
        "configure_non_secret_environment_names": True,
        "register_secret_references_without_readback": True,
        "configure_health_checks": True,
        "configure_deployment_and_access_logs": True,
        "configure_manual_deployment_control": True,
        "configure_rollback_target": True,
        "capture_non_secret_provider_resource_references": True,
    }
    scope = dict(source.get("authorized_scope") or {})
    scope_checks = {
        name: _bool(scope.get(name)) is expected
        for name, expected in required_scope.items()
    }

    attestations = dict(source.get("scope_attestations") or {})
    attestation_checks = {
        name: _bool(attestations.get(name))
        for name in REQUIRED_EXECUTION_SCOPE_ATTESTATIONS
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
            errors.append({"field": field, "code": "invalid_reference_format"})

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
        "record_type": "provider_provisioning_execution_authorization_validation",
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
        "authorized_source_commit_sha256": _fingerprint(supplied_commit),
        "execution_window_seconds": window_seconds,
        "monthly_cost_ceiling_usd": supplied_cost if _valid_money(supplied_cost) else None,
        "raw_owner_values_recorded": False,
        "raw_secret_values_recorded": False,
    }
    report["report_hash"] = payload_hash(report)
    return report


def build_controlled_execution_scope_manifest(
    *,
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    approved = bool(validation.get("approval_valid"))
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "controlled_provider_provisioning_execution_scope",
        "environment": "staging",
        "runtime_target": MANAGED_WSGI_TARGET,
        "start_command": MANAGED_START_COMMAND,
        "service_count_ceiling": 1 if approved else 0,
        "public_ingress_owner": "tower",
        "observatory_public_ingress_allowed": False,
        "allowed_future_session_actions": [
            "authenticate manually to the selected managed hosting provider",
            "open the frozen staging account or team and region",
            "perform a duplicate-resource lookup before creation",
            "create one inert managed Python web-service shell",
            "bind the authorized repository branch and source commit",
            "configure non-secret environment variable names",
            "register secret references without readback",
            "configure health checks, access/deployment logs, manual deployment control, and rollback",
            "capture only non-secret provider resource identifiers",
            "stop before build or deployment",
        ] if approved else [],
        "prohibited_actions": [
            "application build",
            "application deployment",
            "automatic deployment",
            "DNS or public-route change",
            "database creation",
            "object storage creation",
            "production environment access",
            "production data or secret reuse",
            "secret value readback",
            "official Observatory walkthrough",
            "production Manual Live",
            "broker submission",
            "real capital movement",
            "direct Vault upload",
            "Live Auto unlock",
        ],
        "provider_login_authorized_for_future_session": approved,
        "provider_calls_authorized_for_future_session": approved,
        "one_inert_web_service_creation_authorized_for_future_session": approved,
        "secret_reference_registration_authorized_for_future_session": approved,
        "build_authorized": False,
        "deployment_authorized": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    manifest["manifest_hash"] = payload_hash(manifest)
    return manifest


def build_execution_window_and_cost_ceiling_manifest(
    decision: Mapping[str, Any] | None,
    *,
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    source = dict(decision or {})
    approved = bool(validation.get("approval_valid"))
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "controlled_execution_window_and_cost_ceiling",
        "execution_window_starts_at_sha256": _fingerprint(
            source.get("execution_window_starts_at")
        ) if approved else None,
        "execution_window_expires_at_sha256": _fingerprint(
            source.get("execution_window_expires_at")
        ) if approved else None,
        "execution_window_seconds": validation.get("execution_window_seconds") if approved else None,
        "monthly_cost_ceiling_usd": validation.get("monthly_cost_ceiling_usd") if approved else None,
        "managed_web_service_count_ceiling": 1 if approved else 0,
        "database_count_ceiling": 0,
        "object_storage_bucket_count_ceiling": 0,
        "dns_change_count_ceiling": 0,
        "automatic_spend_authorized": False,
        "automatic_scaling_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
        "resource_creation_performed": False,
    }
    manifest["manifest_hash"] = payload_hash(manifest)
    return manifest


def build_execution_receipt_contract() -> dict[str, Any]:
    contract = {
        "schema_version": SCHEMA_VERSION,
        "contract_type": "controlled_provider_execution_receipt_contract",
        "required_receipts_in_order": [
            "execution_session_opened",
            "provider_identity_and_account_verified",
            "provider_region_verified",
            "authorization_window_revalidated",
            "duplicate_resource_lookup_completed",
            "inert_web_service_shell_created_or_existing_resource_selected",
            "repository_branch_and_commit_bound",
            "non_secret_environment_names_registered",
            "secret_references_registered_without_readback",
            "health_logging_manual_control_and_rollback_configured",
            "execution_session_stopped_before_build_or_deployment",
            "execution_closeout_recorded",
        ],
        "receipt_hash_chain_required": True,
        "provider_resource_identifier_secret_values_allowed": False,
        "credentials_or_cookies_allowed": False,
        "secret_values_allowed": False,
        "build_receipt_allowed": False,
        "deployment_receipt_allowed": False,
        "provider_calls_performed": False,
    }
    contract["contract_hash"] = payload_hash(contract)
    return contract


def build_execution_session_preconditions_manifest(
    *,
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    approved = bool(validation.get("approval_valid"))
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": "controlled_provider_execution_session_preconditions",
        "execution_authorization_valid": approved,
        "required_before_session_open": [
            "re-read and hash-verify the frozen execution-preparation packet",
            "re-read and verify the Tower owner execution-authorization decision",
            "verify the owner step-up receipt reference",
            "verify current time is inside the authorized execution window",
            "verify provider, account/team, region, cost, source branch, and source commit match frozen inputs",
            "verify one-service ceiling and duplicate-resource guard",
            "verify health, logs, manual control, rollback, and stop controls remain available",
        ],
        "mandatory_stop_conditions": [
            "any hash or authorization mismatch",
            "authorization window not active or expired",
            "provider, account/team, region, cost, branch, or commit mismatch",
            "duplicate active staging resource exists without explicit selection",
            "more than one service would be created",
            "database, object storage, DNS, build, deployment, or production access is requested",
            "secret value readback or Git storage is requested",
            "Tower-only ingress or rollback cannot be preserved",
        ],
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    manifest["manifest_hash"] = payload_hash(manifest)
    return manifest


def freeze_execution_authorization_record(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
    preparation_inputs: Mapping[str, Any] | None,
    execution_authorization_decision: Mapping[str, Any] | None,
) -> dict[str, Any]:
    handoff = build_completed_execution_preparation_handoff(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
        preparation_inputs,
    )
    challenge = build_execution_authorization_challenge(handoff)
    validation = validate_execution_authorization_decision(
        execution_authorization_decision,
        handoff=handoff,
        challenge=challenge,
        provisioning_decision=provisioning_decision,
        preparation_inputs=preparation_inputs,
    )
    scope = build_controlled_execution_scope_manifest(validation=validation)
    ceilings = build_execution_window_and_cost_ceiling_manifest(
        execution_authorization_decision,
        validation=validation,
    )
    receipts = build_execution_receipt_contract()
    preconditions = build_execution_session_preconditions_manifest(
        validation=validation
    )
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "frozen_provider_provisioning_execution_authorization",
        "completed_execution_preparation_handoff_hash": handoff["handoff_hash"],
        "frozen_execution_preparation_packet_hash": handoff[
            "frozen_execution_preparation_packet_hash"
        ],
        "execution_preparation_decision_hash": handoff[
            "execution_preparation_decision_hash"
        ],
        "execution_authorization_challenge_hash": challenge["challenge_hash"],
        "execution_authorization_validation_report_hash": validation[
            "report_hash"
        ],
        "controlled_execution_scope_manifest_hash": scope["manifest_hash"],
        "execution_window_and_cost_ceiling_manifest_hash": ceilings[
            "manifest_hash"
        ],
        "execution_receipt_contract_hash": receipts["contract_hash"],
        "execution_session_preconditions_manifest_hash": preconditions[
            "manifest_hash"
        ],
        "approval_valid": validation["approval_valid"],
        "rejected": validation["rejected"],
        "owner_id_sha256": validation["owner_id_sha256"],
        "tower_step_up_receipt_ref_sha256": validation[
            "tower_step_up_receipt_ref_sha256"
        ],
        "authorized_source_commit_sha256": validation[
            "authorized_source_commit_sha256"
        ],
        "raw_provider_values_recorded": False,
        "raw_owner_values_recorded": False,
        "raw_review_values_recorded": False,
        "raw_preparation_values_recorded": False,
        "raw_secret_values_recorded": False,
        "frozen": True,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
    }
    record["frozen_execution_authorization_record_hash"] = payload_hash(record)
    return record


def build_execution_authorization_decision(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
    preparation_inputs: Mapping[str, Any] | None,
    execution_authorization_decision: Mapping[str, Any] | None,
) -> dict[str, Any]:
    prior = build_execution_preparation_decision(
        repository_root,
        provider_inputs or {},
        provider_review_owner_decision or {},
        review_inputs or {},
        provisioning_decision or {},
        preparation_inputs or {},
    )
    handoff = build_completed_execution_preparation_handoff(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
        preparation_inputs,
    )
    challenge = build_execution_authorization_challenge(handoff)
    validation = validate_execution_authorization_decision(
        execution_authorization_decision,
        handoff=handoff,
        challenge=challenge,
        provisioning_decision=provisioning_decision,
        preparation_inputs=preparation_inputs,
    )
    frozen = freeze_execution_authorization_record(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
        preparation_inputs,
        execution_authorization_decision,
    )

    if not handoff["completed_execution_preparation_ready"]:
        final_decision = prior["final_decision"]
    elif validation["rejected"]:
        final_decision = (
            "NO_GO_OWNER_REJECTED_PROVIDER_PROVISIONING_EXECUTION_AUTHORIZATION"
        )
    elif not validation["approval_valid"]:
        final_decision = (
            "NO_GO_HOLD_PROVIDER_PROVISIONING_EXECUTION_AUTHORIZATION_REQUIRED"
        )
    else:
        final_decision = (
            "AUTHORIZED_FOR_SEPARATE_CONTROLLED_PROVIDER_PROVISIONING_EXECUTION_SESSION"
        )

    approved = bool(validation["approval_valid"])
    decision = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "provider_provisioning_execution_authorization_decision",
        "completed_execution_preparation_handoff_hash": handoff["handoff_hash"],
        "frozen_execution_authorization_record_hash": frozen[
            "frozen_execution_authorization_record_hash"
        ],
        "execution_authorization_valid": approved,
        "ready_for_separate_controlled_provider_provisioning_execution_session": approved,
        "provider_login_authorized_for_future_session": approved,
        "provider_calls_authorized_for_future_session": approved,
        "one_inert_web_service_creation_authorized_for_future_session": approved,
        "secret_reference_registration_authorized_for_future_session": approved,
        "database_creation_authorized": False,
        "object_storage_creation_authorized": False,
        "dns_changes_authorized": False,
        "build_authorized": False,
        "deployment_authorized": False,
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


def build_inert_controlled_execution_session_plan(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None,
    provider_review_owner_decision: Mapping[str, Any] | None,
    review_inputs: Mapping[str, Any] | None,
    provisioning_decision: Mapping[str, Any] | None,
    preparation_inputs: Mapping[str, Any] | None,
    execution_authorization_decision: Mapping[str, Any] | None,
) -> dict[str, Any]:
    decision = build_execution_authorization_decision(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
        preparation_inputs,
        execution_authorization_decision,
    )
    plan = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": "inert_controlled_provider_provisioning_execution_session_plan",
        "execution_authorization_decision_hash": decision["decision_hash"],
        "ready_for_later_session": decision[
            "ready_for_separate_controlled_provider_provisioning_execution_session"
        ],
        "future_session_sequence": [
            "open a separately approved Tower-controlled execution session",
            "revalidate hashes, owner step-up, time window, provider, account/team, region, cost, branch, and commit",
            "authenticate manually to the provider",
            "perform duplicate-resource lookup",
            "create or select exactly one inert staging web-service shell",
            "bind repository branch and commit",
            "configure names, secret references without readback, health, logs, manual control, and rollback",
            "capture non-secret provider resource references",
            "stop before build or deployment",
            "seal the execution receipt chain",
        ],
        "provider_cli_commands": [],
        "provider_api_requests": [],
        "shell_commands": [],
        "http_requests": [],
        "browser_actions": [],
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


def build_current_execution_authorization_state(
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None = None,
    provider_review_owner_decision: Mapping[str, Any] | None = None,
    review_inputs: Mapping[str, Any] | None = None,
    provisioning_decision: Mapping[str, Any] | None = None,
    preparation_inputs: Mapping[str, Any] | None = None,
    execution_authorization_decision: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    handoff = build_completed_execution_preparation_handoff(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
        preparation_inputs,
    )
    challenge = build_execution_authorization_challenge(handoff)
    validation = validate_execution_authorization_decision(
        execution_authorization_decision,
        handoff=handoff,
        challenge=challenge,
        provisioning_decision=provisioning_decision,
        preparation_inputs=preparation_inputs,
    )
    authorization = build_execution_authorization_decision(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
        preparation_inputs,
        execution_authorization_decision,
    )
    plan = build_inert_controlled_execution_session_plan(
        repository_root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
        preparation_inputs,
        execution_authorization_decision,
    )

    blockers: list[dict[str, str]] = []
    prerequisite_checks = (
        ("provider_inputs", handoff["provider_inputs_valid"], "provider_inputs_required"),
        ("provider_review_owner_authorization", handoff["provider_review_owner_approval_valid"], "owner_step_up_and_decision_required"),
        ("no_call_review_evidence", handoff["review_inputs_valid"], "completed_review_required"),
        ("provisioning_authorization", handoff["provisioning_authorization_valid"], "second_owner_authorization_required"),
        ("execution_preparation_evidence", handoff["preparation_inputs_valid"], "completed_execution_preparation_required"),
    )
    for requirement, valid, status in prerequisite_checks:
        if not valid:
            blockers.append({"requirement": requirement, "status": status})
    for error in validation["errors"]:
        blockers.append({
            "requirement": error["field"],
            "status": error["code"],
        })

    state = {
        "schema_version": SCHEMA_VERSION,
        "closed_layer": "MANAGED_STAGING_PROVIDER_PROVISIONING_EXECUTION_AUTHORIZATION",
        "closed_through_step": 90,
        "runtime_target": MANAGED_WSGI_TARGET,
        "runtime_topology": "single_tower_fronted_managed_python_web_service",
        "completed_execution_preparation_handoff_hash": handoff["handoff_hash"],
        "execution_authorization_challenge_hash": challenge["challenge_hash"],
        "execution_authorization_decision_hash": authorization["decision_hash"],
        "inert_controlled_execution_session_plan_hash": plan["plan_hash"],
        "provider_inputs_valid": handoff["provider_inputs_valid"],
        "provider_review_owner_approval_valid": handoff[
            "provider_review_owner_approval_valid"
        ],
        "review_inputs_valid": handoff["review_inputs_valid"],
        "provisioning_authorization_valid": handoff[
            "provisioning_authorization_valid"
        ],
        "preparation_inputs_valid": handoff["preparation_inputs_valid"],
        "execution_authorization_valid": authorization[
            "execution_authorization_valid"
        ],
        "ready_for_separate_controlled_provider_provisioning_execution_session": authorization[
            "ready_for_separate_controlled_provider_provisioning_execution_session"
        ],
        "blocking_requirements": blockers,
        "blocking_requirement_count": len(blockers),
        "provider_login_authorized_for_future_session": authorization[
            "provider_login_authorized_for_future_session"
        ],
        "provider_calls_authorized_for_future_session": authorization[
            "provider_calls_authorized_for_future_session"
        ],
        "one_inert_web_service_creation_authorized_for_future_session": authorization[
            "one_inert_web_service_creation_authorized_for_future_session"
        ],
        "secret_reference_registration_authorized_for_future_session": authorization[
            "secret_reference_registration_authorized_for_future_session"
        ],
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
        "final_decision": authorization["final_decision"],
        "next_boundary": "managed_staging_controlled_provider_provisioning_execution_session_preparation",
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


def write_execution_authorization_worksheets(
    output_directory: str | Path,
    *,
    repository_root: str | Path,
    provider_inputs: Mapping[str, Any] | None = None,
    provider_review_owner_decision: Mapping[str, Any] | None = None,
    review_inputs: Mapping[str, Any] | None = None,
    provisioning_decision: Mapping[str, Any] | None = None,
    preparation_inputs: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    output = Path(output_directory).resolve()
    root = Path(repository_root).resolve()
    if output == root or root in output.parents:
        raise ValueError("Execution authorization worksheets must be written outside the repository.")
    handoff = build_completed_execution_preparation_handoff(
        root,
        provider_inputs,
        provider_review_owner_decision,
        review_inputs,
        provisioning_decision,
        preparation_inputs,
    )
    decision_path = write_json(
        output / "tower_ob_provider_provisioning_execution_authorization_decision.json",
        execution_authorization_decision_template(handoff),
    )
    session_placeholder = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "controlled_provider_provisioning_execution_session_placeholder",
        "decision": HOLD_DECISION,
        "frozen_execution_authorization_record_hash": "",
        "owner_execution_session_receipt_ref": "",
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
        "notes": [
            "This placeholder is not an execution session or provider authorization.",
            "A later corridor must revalidate the frozen execution authorization before any provider action.",
        ],
    }
    session_placeholder["template_hash"] = payload_hash(session_placeholder)
    session_path = write_json(
        output / "tower_ob_controlled_provider_provisioning_execution_session_placeholder.json",
        session_placeholder,
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "execution_authorization_decision_path": str(decision_path),
        "controlled_execution_session_placeholder_path": str(session_path),
        "completed_execution_preparation_ready": handoff[
            "completed_execution_preparation_ready"
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
        "execution_authorization_decision_path": str(decision_path),
        "controlled_execution_session_placeholder_path": str(session_path),
        "manifest_path": str(manifest_path),
    }


def blank_current_inputs(
    repository_root: str | Path,
) -> tuple[dict, dict, dict, dict, dict, dict]:
    provider, review_owner, review, provisioning, preparation = (
        blank_preparation_inputs(repository_root)
    )
    handoff = build_completed_execution_preparation_handoff(
        repository_root,
        provider,
        review_owner,
        review,
        provisioning,
        preparation,
    )
    execution_authorization = execution_authorization_decision_template(handoff)
    return (
        provider,
        review_owner,
        review,
        provisioning,
        preparation,
        execution_authorization,
    )


__all__ = [
    "ALLOWED_DECISIONS",
    "AUTHORIZE_DECISION",
    "HOLD_DECISION",
    "REJECT_DECISION",
    "REQUIRED_EXECUTION_SCOPE_ATTESTATIONS",
    "blank_current_inputs",
    "build_completed_execution_preparation_handoff",
    "build_controlled_execution_scope_manifest",
    "build_current_execution_authorization_state",
    "build_execution_authorization_challenge",
    "build_execution_authorization_decision",
    "build_execution_receipt_contract",
    "build_execution_session_preconditions_manifest",
    "build_execution_window_and_cost_ceiling_manifest",
    "build_inert_controlled_execution_session_plan",
    "execution_authorization_decision_template",
    "freeze_execution_authorization_record",
    "validate_execution_authorization_decision",
    "write_execution_authorization_worksheets",
]
