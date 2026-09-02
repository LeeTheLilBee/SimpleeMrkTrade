
"""Honest hosted-release configuration and owner walkthrough readiness / TWR111-TWR115."""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from flask import current_app, has_app_context

from tower.hosted_owner_release_candidate_state import (
    CANDIDATE_CHANGED,
    CANDIDATE_INVALID,
    DECISION_STATE_UNAVAILABLE,
    NO_CANDIDATE,
    OWNER_APPROVED,
    OWNER_HELD,
    OWNER_REJECTED,
    READY_FOR_OWNER_REVIEW,
    STALE_CANDIDATE,
    project_owner_release_candidate_state,
)
from tower.hosted_owner_release_review import (
    SAFETY_FALSE_FIELDS,
    owner_release_session_context,
    validate_owner_release_context,
)
from tower.hosted_release_candidate_publication import (
    PACKET_STORE_DURABLE_CONFIG,
    configured_release_base_url,
)
from tower.hosted_release_packet_provider import _config, _expected_candidate_revision
from tower.hosted_runtime_parity import normalize_base_url


OWNER_VERIFICATION_REQUIRED = "OWNER_VERIFICATION_REQUIRED"
HOSTED_READINESS_BLOCKED = "HOSTED_READINESS_BLOCKED"
HOSTED_AWAITING_CANDIDATE = "HOSTED_AWAITING_CANDIDATE"
HOSTED_AWAITING_OWNER_DECISION = "HOSTED_AWAITING_OWNER_DECISION"
HOSTED_OWNER_APPROVED_CERTIFIED = "HOSTED_OWNER_APPROVED_CERTIFIED"
HOSTED_OWNER_HOLD_RECORDED = "HOSTED_OWNER_HOLD_RECORDED"
HOSTED_OWNER_REJECTION_RECORDED = "HOSTED_OWNER_REJECTION_RECORDED"

REQUIRED_HOSTED_ROUTES = (
    "/tower/healthz",
    "/tower/runtime-manifest.json",
    "/tower/login",
    "/tower/owner/release-review",
    "/tower/owner/release-review/publish",
    "/tower/owner/release-review/state.json",
    "/tower/owner/release-review/decision",
    "/tower/owner/release-review/receipt/<receipt_id>",
    "/tower/owner/release-review/walkthrough",
    "/tower/owner/release-review/readiness.json",
    "/tower/owner/release-review/walkthrough/certification.json",
)


def _safety() -> dict[str, bool]:
    return {field: False for field in SAFETY_FALSE_FIELDS}


def _owner_required() -> dict[str, Any]:
    return {
        "status": "tower_hosted_owner_release_readiness_denied",
        "readiness_state": OWNER_VERIFICATION_REQUIRED,
        "hosted_configuration_ready": False,
        "owner_walkthrough_complete": False,
        "staging_prerequisites_certified": False,
        "owner_next_action": "Verify your Tower owner session before viewing hosted release readiness.",
        "owner_review_required": True,
        "separate_release_execution_gate_required": True,
        "staging_ready": False,
        **_safety(),
    }


def _store_usable(value: str) -> bool:
    if not value:
        return False
    try:
        path = Path(value).expanduser()
        if not path.is_absolute() or path.is_symlink() or path.parent.is_symlink():
            return False
        if not path.parent.is_dir() or not os.access(path.parent, os.W_OK | os.X_OK):
            return False
        if path.exists():
            return path.is_file() and os.access(path, os.R_OK | os.W_OK)
        return True
    except (OSError, TypeError, ValueError):
        return False


def _critical_routes_ready() -> bool:
    if not has_app_context():
        return False
    try:
        available = {rule.rule for rule in current_app.url_map.iter_rules()}
    except Exception:
        return False
    return all(route in available for route in REQUIRED_HOSTED_ROUTES)


def _managed_safety_closed() -> bool:
    managed = sys.modules.get("web.managed_staging")
    if managed is None:
        return True
    for name in (
        "PRODUCTION_DEPLOYMENT",
        "BROKER_SUBMISSION",
        "CAPITAL_MOVEMENT",
        "MANUAL_LIVE_AUTHORIZED",
        "LIVE_AUTO_AUTHORIZED",
        "STAGING_READY",
    ):
        if getattr(managed, name, False) is not False:
            return False
    return True


def _check_definitions() -> tuple[dict[str, bool], dict[str, str], str, str]:
    hosted = bool(_config("RENDER", "") or _config("RENDER_GIT_COMMIT", ""))
    configured_url = configured_release_base_url()
    safe_host = ""
    try:
        normalized = normalize_base_url(configured_url, allow_http=False)
        safe_host = urlsplit(normalized).netloc
        https_ready = True
    except (TypeError, ValueError):
        https_ready = False

    expected_revision = str(_expected_candidate_revision() or "").strip().lower()
    deployed_revision = str(_config("RENDER_GIT_COMMIT", "") or "").strip().lower()
    revision_ready = bool(
        expected_revision
        and expected_revision not in {"unknown", "unavailable", "none", "null"}
        and deployed_revision
        and deployed_revision == expected_revision
    )

    packet_path = str(_config("TOWER_HOSTED_RELEASE_PACKET_PATH", "") or "").strip()
    packet_confirmed = str(_config(PACKET_STORE_DURABLE_CONFIG, "") or "").strip().lower() == "true"
    receipt_path = str(os.environ.get("TOWER_RELEASE_RECEIPT_LEDGER_PATH", "") or "").strip()
    receipt_confirmed = (
        str(os.environ.get("TOWER_RELEASE_RECEIPT_STORE_DURABLE", "") or "").strip().lower() == "true"
    )
    distinct = False
    if packet_path and receipt_path:
        try:
            distinct = Path(packet_path).expanduser().resolve() != Path(receipt_path).expanduser().resolve()
        except (OSError, ValueError):
            distinct = False

    owner_username = bool(str(os.environ.get("TOWER_OWNER_USERNAME", "") or "").strip())
    owner_hash = bool(str(os.environ.get("TOWER_OWNER_PASSWORD_HASH", "") or "").strip())
    local_mode = str(os.environ.get("TOWER_LOCAL_WALKTHROUGH_MODE", "") or "").strip().lower()
    local_mode_disabled = local_mode not in {"1", "true", "yes", "on"}
    try:
        session_secret = bool(os.environ.get("TOWER_SESSION_SECRET") or current_app.secret_key)
    except Exception:
        session_secret = False

    checks = {
        "hosted_runtime_detected": hosted,
        "hosted_https_endpoint_configured": https_ready,
        "exact_deployed_revision_confirmed": revision_ready,
        "durable_packet_store_configured": bool(packet_path and packet_confirmed),
        "durable_packet_store_usable": _store_usable(packet_path),
        "durable_receipt_store_configured": bool(receipt_path and receipt_confirmed),
        "durable_receipt_store_usable": _store_usable(receipt_path),
        "packet_and_receipt_stores_distinct": distinct,
        "owner_username_configured": owner_username,
        "owner_password_hash_configured": owner_hash,
        "local_walkthrough_mode_disabled": local_mode_disabled,
        "owner_session_secret_configured": session_secret,
        "critical_owner_routes_present": _critical_routes_ready(),
        "execution_boundaries_closed": _managed_safety_closed(),
    }
    owner_actions = {
        "hosted_runtime_detected": "Run the owner workflow on the actual hosted Tower runtime.",
        "hosted_https_endpoint_configured": "Configure the real Tower HTTPS host without credentials or path prefixes.",
        "exact_deployed_revision_confirmed": "Align the expected owner-review revision with the actual deployed Git commit.",
        "durable_packet_store_configured": "Configure and explicitly confirm durable hosted candidate-packet storage.",
        "durable_packet_store_usable": "Make the configured candidate-packet storage directory safe and writable.",
        "durable_receipt_store_configured": "Configure and explicitly confirm durable owner decision-receipt storage.",
        "durable_receipt_store_usable": "Make the configured owner-receipt storage directory safe and writable.",
        "packet_and_receipt_stores_distinct": "Use separate durable files for release candidates and owner receipts.",
        "owner_username_configured": "Configure the real hosted Tower owner username.",
        "owner_password_hash_configured": "Configure a hashed owner password; hosted plaintext walkthrough credentials are not sufficient.",
        "local_walkthrough_mode_disabled": "Disable local walkthrough mode on the hosted Tower runtime.",
        "owner_session_secret_configured": "Configure the hosted Tower owner-session signing secret.",
        "critical_owner_routes_present": "Restore every required hosted identity, release-review, and walkthrough route.",
        "execution_boundaries_closed": "Close every staging, deployment, broker, capital, and live-trading boundary.",
    }
    return checks, owner_actions, safe_host, expected_revision


def project_hosted_owner_release_readiness(
    *,
    owner_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    context = owner_context if owner_context is not None else owner_release_session_context()
    validation = validate_owner_release_context(context)
    if not validation.get("valid"):
        return _owner_required()

    checks, actions, safe_host, expected_revision = _check_definitions()
    blockers = [
        {"code": name, "owner_action": actions[name]}
        for name, passing in checks.items()
        if passing is not True
    ]
    configuration_ready = not blockers
    state = HOSTED_READINESS_BLOCKED
    next_action = blockers[0]["owner_action"] if blockers else "Publish a genuine hosted release candidate."
    candidate_state = None
    receipt_id = None
    walkthrough_complete = False
    staging_certified = False

    if configuration_ready:
        candidate = project_owner_release_candidate_state(owner_context=context)
        candidate_state = candidate.get("candidate_state")
        if candidate_state in {NO_CANDIDATE, CANDIDATE_CHANGED}:
            state = HOSTED_AWAITING_CANDIDATE
            next_action = "Run the genuine hosted candidate check from the owner walkthrough."
        elif candidate_state == STALE_CANDIDATE:
            state = HOSTED_READINESS_BLOCKED
            blockers.append({
                "code": "candidate_expired_same_revision_replay_blocked",
                "owner_action": (
                    "The previously published candidate expired. A distinct deployed revision "
                    "is required; same-revision replay cannot bypass the owner decision boundary."
                ),
            })
            configuration_ready = False
            next_action = blockers[0]["owner_action"]
        elif candidate_state in {CANDIDATE_INVALID, DECISION_STATE_UNAVAILABLE}:
            state = HOSTED_READINESS_BLOCKED
            blockers.append({
                "code": "candidate_or_receipt_integrity_unavailable",
                "owner_action": "Repair the sealed candidate or durable owner-receipt chain before continuing.",
            })
            configuration_ready = False
            next_action = blockers[0]["owner_action"]
        elif candidate_state == READY_FOR_OWNER_REVIEW:
            state = HOSTED_AWAITING_OWNER_DECISION
            next_action = "Review the exact hosted candidate and explicitly approve, hold, or reject it."
        elif candidate_state == OWNER_APPROVED and candidate.get("receipt_integrity_verified") is True:
            state = HOSTED_OWNER_APPROVED_CERTIFIED
            next_action = "Your verified approval is recorded. A separate release-execution gate is still required."
            walkthrough_complete = True
            staging_certified = True
            receipt_id = candidate.get("receipt_id")
        elif candidate_state == OWNER_HELD and candidate.get("receipt_integrity_verified") is True:
            state = HOSTED_OWNER_HOLD_RECORDED
            next_action = "Your hold is recorded; no staging, deployment, or trading action is authorized."
            walkthrough_complete = True
            receipt_id = candidate.get("receipt_id")
        elif candidate_state == OWNER_REJECTED and candidate.get("receipt_integrity_verified") is True:
            state = HOSTED_OWNER_REJECTION_RECORDED
            next_action = "Your rejection is recorded; no staging, deployment, or trading action is authorized."
            walkthrough_complete = True
            receipt_id = candidate.get("receipt_id")
        else:
            state = HOSTED_READINESS_BLOCKED
            blockers.append({
                "code": "owner_candidate_state_unverified",
                "owner_action": "Verify the exact owner candidate and decision receipt before continuing.",
            })
            configuration_ready = False
            next_action = blockers[0]["owner_action"]

    return {
        "status": "tower_hosted_owner_release_readiness_ready",
        "readiness_state": state,
        "hosted_configuration_ready": configuration_ready,
        "owner_walkthrough_complete": walkthrough_complete,
        "staging_prerequisites_certified": staging_certified,
        "hosted_host": safe_host,
        "expected_revision": expected_revision,
        "candidate_state": candidate_state,
        "receipt_id": receipt_id,
        "checks": checks,
        "blockers": blockers,
        "blocker_count": len(blockers),
        "owner_next_action": next_action,
        "owner_review_required": True,
        "separate_release_execution_gate_required": True,
        "staging_ready": False,
        **_safety(),
    }


def certify_hosted_owner_release_walkthrough(
    *,
    owner_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    readiness = project_hosted_owner_release_readiness(owner_context=owner_context)
    certified = bool(
        readiness.get("readiness_state") == HOSTED_OWNER_APPROVED_CERTIFIED
        and readiness.get("hosted_configuration_ready") is True
        and readiness.get("owner_walkthrough_complete") is True
        and readiness.get("staging_prerequisites_certified") is True
        and readiness.get("receipt_id")
        and readiness.get("staging_ready") is False
        and all(readiness.get(field) is False for field in SAFETY_FALSE_FIELDS)
    )
    return {
        "status": (
            "tower_hosted_owner_release_walkthrough_certified"
            if certified
            else "tower_hosted_owner_release_walkthrough_not_certified"
        ),
        "certified": certified,
        "readiness_state": readiness.get("readiness_state"),
        "owner_walkthrough_complete": readiness.get("owner_walkthrough_complete", False),
        "staging_prerequisites_certified": certified,
        "receipt_id": readiness.get("receipt_id") if certified else None,
        "owner_next_action": readiness.get("owner_next_action"),
        "owner_review_required": True,
        "separate_release_execution_gate_required": True,
        "staging_ready": False,
        **_safety(),
    }


def owner_hosted_readiness_dashboard_snapshot() -> dict[str, str]:
    readiness = project_hosted_owner_release_readiness()
    state = readiness["readiness_state"]
    labels = {
        OWNER_VERIFICATION_REQUIRED: "Owner verification needed",
        HOSTED_READINESS_BLOCKED: "Hosted setup needs attention",
        HOSTED_AWAITING_CANDIDATE: "Hosted setup ready · candidate needed",
        HOSTED_AWAITING_OWNER_DECISION: "Hosted candidate ready for your decision",
        HOSTED_OWNER_APPROVED_CERTIFIED: "Owner walkthrough verified · execution locked",
        HOSTED_OWNER_HOLD_RECORDED: "Owner hold recorded · execution locked",
        HOSTED_OWNER_REJECTION_RECORDED: "Owner rejection recorded · execution locked",
    }
    return {
        "state": state,
        "label": labels.get(state, "Hosted readiness unavailable"),
        "detail": str(readiness.get("owner_next_action") or "Review hosted Tower readiness."),
    }
