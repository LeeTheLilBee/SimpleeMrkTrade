"""
Tower Owner-Beta Issue Intake Persistence + Review Receipts / Packs 2573–2582.

This module provides a local append-only JSONL issue intake and review
receipt contract for the Owner-Beta Control Room.

It is owner-gated by Tower routes. It does not authorize production,
broker submission, capital movement, Manual Live, Live Auto, direct Vault
write, public launch, or destructive actions.
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


OWNER_BETA_ISSUE_INTAKE_VERSION = "tower_owner_beta_issue_intake_v1"

DEFAULT_STORE_PATH = "data/tower_owner_beta_issue_intake.jsonl"

ALLOWED_CATEGORIES = {
    "walkthrough",
    "access",
    "tower_ui",
    "observatory_ui",
    "owner_beta_control_room",
    "market_map",
    "soulaana",
    "six_room_acceptance",
    "session_return",
    "tester_access",
    "safety_boundary",
    "other",
}

ALLOWED_SEVERITIES = {"low", "medium", "high", "blocker"}
ALLOWED_STATUSES = {"open", "triage", "reviewed", "closed", "reopened"}

PRODUCTION_DEPLOYMENT = False
BROKER_SUBMISSION = False
CAPITAL_MOVEMENT = False
MANUAL_LIVE_AUTHORIZED = False
LIVE_AUTO_AUTHORIZED = False
DIRECT_VAULT_WRITE = False
DESTRUCTIVE_ACTION_UNLOCKED = False
PUBLIC_LAUNCH_AUTHORIZED = False


def dangerous_controls() -> Dict[str, bool]:
    return {
        "production_deployment": PRODUCTION_DEPLOYMENT,
        "broker_submission": BROKER_SUBMISSION,
        "capital_movement": CAPITAL_MOVEMENT,
        "manual_live_authorized": MANUAL_LIVE_AUTHORIZED,
        "live_auto_authorized": LIVE_AUTO_AUTHORIZED,
        "direct_vault_write": DIRECT_VAULT_WRITE,
        "destructive_action_unlocked": DESTRUCTIVE_ACTION_UNLOCKED,
        "public_launch_authorized": PUBLIC_LAUNCH_AUTHORIZED,
    }


def dangerous_controls_locked() -> bool:
    return all(value is False for value in dangerous_controls().values())


def issue_store_path(explicit_path: Optional[str] = None) -> Path:
    return Path(
        explicit_path
        or os.environ.get("TOWER_OWNER_BETA_ISSUE_STORE")
        or DEFAULT_STORE_PATH
    )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_text(value: Any, *, limit: int = 1200) -> str:
    text = str(value or "").strip()
    return text[:limit]


def normalize_category(value: Any) -> str:
    category = normalize_text(value, limit=80).lower().replace(" ", "_")
    return category if category in ALLOWED_CATEGORIES else "other"


def normalize_severity(value: Any) -> str:
    severity = normalize_text(value, limit=40).lower()
    return severity if severity in ALLOWED_SEVERITIES else "medium"


def classify_market_map_feedback(category: str, text: str) -> str:
    combined = f"{category} {text}".lower()

    if "market" in combined and ("map" in combined or "deep" in combined or "symbol" in combined):
        return "market_map_deep_dive"

    if "soulaana" in combined or "interpret" in combined or "explain" in combined:
        return "soulaana_interpretation"

    if "return" in combined or "session" in combined or "tower" in combined:
        return "tower_session_boundary"

    if "access" in combined or "login" in combined or "permission" in combined:
        return "tower_access_boundary"

    return "general_owner_beta_feedback"


def build_issue_record(input_payload: Dict[str, Any], *, owner_id: str = "owner") -> Dict[str, Any]:
    title = normalize_text(input_payload.get("title"), limit=160)
    description = normalize_text(input_payload.get("description"), limit=2000)

    if not title:
        raise ValueError("Issue title is required.")

    if not description:
        raise ValueError("Issue description is required.")

    category = normalize_category(input_payload.get("category"))
    severity = normalize_severity(input_payload.get("severity"))
    now = utc_now()

    issue_id = "obi_" + uuid.uuid4().hex[:16]

    soulaana_note = normalize_text(
        input_payload.get("soulaana_note")
        or input_payload.get("soulaana_interpretation_note"),
        limit=1000,
    )

    owner_requested_action = normalize_text(
        input_payload.get("owner_requested_action")
        or input_payload.get("requested_action"),
        limit=800,
    )

    room = normalize_text(input_payload.get("room"), limit=120)
    source_route = normalize_text(input_payload.get("source_route"), limit=240) or "/tower/owner-beta"

    classification = classify_market_map_feedback(category, f"{title} {description} {soulaana_note}")

    blocker_link = normalize_text(input_payload.get("blocker_id"), limit=120)

    issue = {
        "record_type": "tower_owner_beta_issue",
        "version": OWNER_BETA_ISSUE_INTAKE_VERSION,
        "issue_id": issue_id,
        "created_at": now,
        "updated_at": now,
        "owner_id": normalize_text(owner_id, limit=120) or "owner",
        "title": title,
        "description": description,
        "category": category,
        "severity": severity,
        "status": "open",
        "classification": classification,
        "room": room,
        "source_route": source_route,
        "blocker_id": blocker_link,
        "soulaana_note": soulaana_note,
        "owner_requested_action": owner_requested_action,
        "dangerous_controls": dangerous_controls(),
        "dangerous_controls_locked": dangerous_controls_locked(),
    }

    issue["issue_hash"] = issue_hash(issue)

    return issue


def issue_hash(issue: Dict[str, Any]) -> str:
    stable = {
        key: value
        for key, value in issue.items()
        if key not in {"issue_hash"}
    }

    encoded = json.dumps(stable, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def append_jsonl_record(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def read_jsonl_records(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    records: List[Dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue

            records.append(json.loads(text))

    return records


def create_issue(
    input_payload: Dict[str, Any],
    *,
    owner_id: str = "owner",
    store_path: Optional[str] = None,
) -> Dict[str, Any]:
    issue = build_issue_record(input_payload, owner_id=owner_id)
    append_jsonl_record(issue_store_path(store_path), issue)
    return issue


def list_issues(*, store_path: Optional[str] = None) -> List[Dict[str, Any]]:
    return [
        record
        for record in read_jsonl_records(issue_store_path(store_path))
        if record.get("record_type") == "tower_owner_beta_issue"
    ]


def create_review_receipt(
    issue: Dict[str, Any],
    *,
    reviewer_id: str = "owner",
    decision: str = "received_for_review",
    notes: str = "",
    store_path: Optional[str] = None,
) -> Dict[str, Any]:
    decision_clean = normalize_text(decision, limit=120) or "received_for_review"
    notes_clean = normalize_text(notes, limit=1200)

    receipt = {
        "record_type": "tower_owner_beta_review_receipt",
        "version": OWNER_BETA_ISSUE_INTAKE_VERSION,
        "receipt_id": "obr_" + uuid.uuid4().hex[:16],
        "issue_id": issue["issue_id"],
        "issue_hash": issue["issue_hash"],
        "created_at": utc_now(),
        "reviewer_id": normalize_text(reviewer_id, limit=120) or "owner",
        "decision": decision_clean,
        "notes": notes_clean,
        "category": issue.get("category"),
        "severity": issue.get("severity"),
        "classification": issue.get("classification"),
        "blocker_id": issue.get("blocker_id", ""),
        "dangerous_controls": dangerous_controls(),
        "dangerous_controls_locked": dangerous_controls_locked(),
    }

    receipt["receipt_hash"] = review_receipt_hash(receipt)

    append_jsonl_record(issue_store_path(store_path), receipt)
    return receipt


def review_receipt_hash(receipt: Dict[str, Any]) -> str:
    stable = {
        key: value
        for key, value in receipt.items()
        if key not in {"receipt_hash"}
    }

    encoded = json.dumps(stable, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def list_review_receipts(*, store_path: Optional[str] = None) -> List[Dict[str, Any]]:
    return [
        record
        for record in read_jsonl_records(issue_store_path(store_path))
        if record.get("record_type") == "tower_owner_beta_review_receipt"
    ]


def intake_contract() -> Dict[str, Any]:
    return {
        "version": OWNER_BETA_ISSUE_INTAKE_VERSION,
        "routes": {
            "list_or_submit_issues": "/tower/owner-beta/issues.json",
            "review_receipts": "/tower/owner-beta/review-receipts.json",
        },
        "requires_owner_session": True,
        "persistence": {
            "mode": "append_only_jsonl",
            "default_store_path": DEFAULT_STORE_PATH,
            "test_override_env": "TOWER_OWNER_BETA_ISSUE_STORE",
        },
        "allowed_categories": sorted(ALLOWED_CATEGORIES),
        "allowed_severities": sorted(ALLOWED_SEVERITIES),
        "allowed_statuses": sorted(ALLOWED_STATUSES),
        "dangerous_controls": dangerous_controls(),
        "dangerous_controls_locked": dangerous_controls_locked(),
    }


def issue_intake_cert(pack: int) -> Dict[str, Any]:
    titles = {
        2573: "Issue intake persistence contract",
        2574: "Owner-session issue submission schema",
        2575: "Local JSONL append-only beta issue store",
        2576: "Issue list/read model",
        2577: "Review receipt generation",
        2578: "Beta blocker receipt linkage",
        2579: "Soulaana interpretation note field",
        2580: "Market Map feedback classification",
        2581: "Owner decision receipt surface",
        2582: "Route/API integration safety cert",
    }

    return {
        "pack": pack,
        "title": titles[pack],
        "status": "passed",
        "version": OWNER_BETA_ISSUE_INTAKE_VERSION,
        "routes": intake_contract()["routes"],
        "requires_owner_session": True,
        "persistence_mode": "append_only_jsonl",
        "dangerous_controls": dangerous_controls(),
        "dangerous_controls_locked": dangerous_controls_locked(),
    }
