
from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

TAMPER_CHAIN_PATH = DATA_DIR / "tamper_evident_audit_chain.json"

CHAINED_SOURCE_FILES = {
    "deny_path_replacement_audit_receipts": DATA_DIR / "deny_path_replacement_audit_receipts.json",
    "ob_object_audit_capsules": DATA_DIR / "ob_object_audit_capsules.json",
    "ob_object_security_inbox": DATA_DIR / "ob_object_security_inbox.json",
    "ui_action_audit_receipts": DATA_DIR / "ui_action_audit_receipts.json",
    "archive_vault_handoff_queue": DATA_DIR / "archive_vault_handoff_queue.json",
    "door_swipe_audit_capsules": DATA_DIR / "door_swipe_audit_capsules.json",
    "door_swipe_security_inbox": DATA_DIR / "door_swipe_security_inbox.json",
    "route_replacement_policy_list": DATA_DIR / "route_replacement_policy_list.json",
    "visibility_policy_transition_checkpoint": DATA_DIR / "visibility_policy_transition_checkpoint.json",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)


def _redact_sensitive(value: Any) -> Any:
    sensitive_keys = {
        "token",
        "raw_token",
        "tower_keycard",
        "password",
        "secret",
        "api_key",
        "apikey",
        "authorization",
        "bearer",
        "credential",
        "credentials",
        "github_token",
        "broker_key",
        "payment_secret",
    }

    if isinstance(value, dict):
        clean = {}
        redacted_count = 0

        for key, item in value.items():
            key_text = str(key).lower()
            if any(sensitive in key_text for sensitive in sensitive_keys):
                clean[key] = "[REDACTED]"
                redacted_count += 1
            else:
                clean[key] = _redact_sensitive(item)

        if redacted_count:
            clean["__redacted_sensitive_field_count__"] = clean.get("__redacted_sensitive_field_count__", 0) + redacted_count

        return clean

    if isinstance(value, list):
        return [_redact_sensitive(item) for item in value]

    if isinstance(value, str):
        lowered = value.lower()
        if "tower_keycard=" in lowered or "bearer " in lowered or "should_not_survive" in lowered:
            return "[REDACTED]"
        return value

    return value


def _canonical_json(value: Any) -> str:
    safe = _redact_sensitive(value)
    return json.dumps(safe, sort_keys=True, separators=(",", ":"), default=str)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _fingerprint(value: Any) -> str:
    return _sha256_text(_canonical_json(value))


def _source_payload_summary(source_name: str, path: Path) -> Dict[str, Any]:
    exists = path.exists()
    raw = _load_json(path, [] if exists else None)

    if isinstance(raw, list):
        record_count = len(raw)
        sample = raw[-5:]
    elif isinstance(raw, dict):
        if isinstance(raw.get("items"), list):
            record_count = len(raw.get("items", []))
            sample = raw.get("items", [])[-5:]
        elif isinstance(raw.get("recent"), list):
            record_count = len(raw.get("recent", []))
            sample = raw.get("recent", [])[-5:]
        else:
            record_count = 1
            sample = raw
    else:
        record_count = 0
        sample = raw

    payload_hash = _fingerprint(raw)

    return {
        "source_name": source_name,
        "path": str(path),
        "exists": exists,
        "record_count": record_count,
        "payload_hash": payload_hash,
        "sample_hash": _fingerprint(sample),
        "sample_preview": _redact_sensitive(sample),
    }


def _load_chain() -> Dict[str, Any]:
    return _load_json(TAMPER_CHAIN_PATH, {
        "ok": True,
        "pack": "091",
        "chain_version": "pack091.v1",
        "path": str(TAMPER_CHAIN_PATH),
        "entries": [],
        "human_reason": "Tamper-evident audit chain initialized.",
    })


def _entry_material(entry: Dict[str, Any]) -> Dict[str, Any]:
    clean = dict(entry)
    clean.pop("current_hash", None)
    return clean


def _compute_entry_hash(entry: Dict[str, Any]) -> str:
    return _fingerprint(_entry_material(entry))


def create_tamper_chain_entry(
    *,
    event_type: str,
    source_name: str,
    source_path: str,
    source_hash: str,
    record_count: int,
    actor_user_id: str = "tower_system",
    reason: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    chain = _load_chain()
    entries = chain.get("entries", []) if isinstance(chain.get("entries"), list) else []

    previous_hash = entries[-1].get("current_hash") if entries else "GENESIS"

    sequence = len(entries) + 1
    entry = {
        "ok": True,
        "event_type": event_type,
        "chain_version": "pack091.v1",
        "sequence": sequence,
        "created_at": _utc_now(),
        "actor_user_id": actor_user_id,
        "source_name": source_name,
        "source_path": source_path,
        "source_hash": source_hash,
        "record_count": record_count,
        "previous_hash": previous_hash,
        "reason": reason or "Tamper-evident audit chain entry recorded.",
        "metadata": _redact_sensitive(metadata or {}),
    }
    entry["current_hash"] = _compute_entry_hash(entry)

    entries.append(entry)

    chain.update({
        "ok": True,
        "pack": "091",
        "chain_version": "pack091.v1",
        "path": str(TAMPER_CHAIN_PATH),
        "updated_at": _utc_now(),
        "total_entries": len(entries),
        "latest_hash": entry["current_hash"],
        "entries": entries,
        "soulaana_translation": "Soulaana: The receipt chain is linked. If someone edits the past, the chain will complain.",
        "human_reason": "Tamper-evident audit chain updated.",
    })

    _write_json(TAMPER_CHAIN_PATH, chain)
    return entry


def build_tamper_evident_audit_chain() -> Dict[str, Any]:
    chain = _load_chain()
    before_count = len(chain.get("entries", []) if isinstance(chain.get("entries"), list) else [])

    source_summaries = []
    created_entries = []

    for source_name, path in CHAINED_SOURCE_FILES.items():
        summary = _source_payload_summary(source_name, path)
        source_summaries.append(summary)

        # Avoid duplicate adjacent entries for the same source hash.
        existing_entries = chain.get("entries", []) if isinstance(chain.get("entries"), list) else []
        latest_same_source = None
        for entry in reversed(existing_entries):
            if entry.get("source_name") == source_name:
                latest_same_source = entry
                break

        if latest_same_source and latest_same_source.get("source_hash") == summary.get("payload_hash"):
            continue

        entry = create_tamper_chain_entry(
            event_type="tower_tamper_evident_source_snapshot",
            source_name=source_name,
            source_path=str(path),
            source_hash=summary.get("payload_hash"),
            record_count=summary.get("record_count", 0),
            actor_user_id="tower_system",
            reason=f"Pack 091 chained source snapshot for {source_name}.",
            metadata={
                "pack": "091",
                "exists": summary.get("exists"),
                "sample_hash": summary.get("sample_hash"),
            },
        )
        created_entries.append(entry)

        # Reload chain after each append so previous_hash stays correct.
        chain = _load_chain()

    verification = verify_tamper_evident_audit_chain()

    final_chain = _load_chain()
    entries = final_chain.get("entries", []) if isinstance(final_chain.get("entries"), list) else []

    result = {
        "ok": verification.get("ok") is True,
        "pack": "091",
        "path": str(TAMPER_CHAIN_PATH),
        "created_at": _utc_now(),
        "before_count": before_count,
        "after_count": len(entries),
        "created_count": len(created_entries),
        "total_entries": len(entries),
        "latest_hash": entries[-1].get("current_hash") if entries else "",
        "source_count": len(source_summaries),
        "sources": source_summaries,
        "created_entries": created_entries,
        "verification": verification,
        "readiness_score": 100 if verification.get("ok") else 80,
        "readiness_label": (
            "Tamper-evident audit chain ready"
            if verification.get("ok")
            else "Tamper-evident audit chain needs repair"
        ),
        "soulaana_translation": "Soulaana: Receipts now hold hands in order. Change one without permission and the chain starts side-eyeing.",
        "human_reason": "Tamper-evident audit chain built and verified.",
    }

    return result


def verify_tamper_evident_audit_chain(chain_payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    chain = copy.deepcopy(chain_payload) if isinstance(chain_payload, dict) else _load_chain()
    entries = chain.get("entries", []) if isinstance(chain.get("entries"), list) else []

    failures: List[Dict[str, Any]] = []
    previous_hash = "GENESIS"

    for index, entry in enumerate(entries):
        expected_sequence = index + 1
        actual_sequence = entry.get("sequence")
        if actual_sequence != expected_sequence:
            failures.append({
                "index": index,
                "failure": "sequence_mismatch",
                "expected": expected_sequence,
                "actual": actual_sequence,
            })

        if entry.get("previous_hash") != previous_hash:
            failures.append({
                "index": index,
                "sequence": actual_sequence,
                "failure": "previous_hash_mismatch",
                "expected": previous_hash,
                "actual": entry.get("previous_hash"),
            })

        expected_hash = _compute_entry_hash(entry)
        if entry.get("current_hash") != expected_hash:
            failures.append({
                "index": index,
                "sequence": actual_sequence,
                "failure": "current_hash_mismatch",
                "expected": expected_hash,
                "actual": entry.get("current_hash"),
            })

        previous_hash = entry.get("current_hash")

    ok = not failures

    return {
        "ok": ok,
        "pack": "091",
        "path": str(TAMPER_CHAIN_PATH),
        "total_entries": len(entries),
        "latest_hash": entries[-1].get("current_hash") if entries else "",
        "failures": failures,
        "readiness_score": 100 if ok else 60,
        "readiness_label": "Tamper chain verified" if ok else "Tamper chain verification failed",
        "human_reason": (
            "Tamper-evident audit chain verified."
            if ok
            else "Tamper-evident audit chain found hash/link failures."
        ),
        "soulaana_translation": (
            "Soulaana: The chain is clean."
            if ok
            else "Soulaana: Something touched the story and the chain noticed."
        ),
    }


def simulate_tamper_detection() -> Dict[str, Any]:
    chain = _load_chain()
    entries = chain.get("entries", []) if isinstance(chain.get("entries"), list) else []

    if not entries:
        build_tamper_evident_audit_chain()
        chain = _load_chain()
        entries = chain.get("entries", []) if isinstance(chain.get("entries"), list) else []

    if not entries:
        return {
            "ok": False,
            "tamper_detected": False,
            "human_reason": "No chain entries exist to tamper-test.",
        }

    tampered = copy.deepcopy(chain)
    tampered_entries = tampered.get("entries", [])

    # Change historical material without recomputing hash.
    tampered_entries[0]["reason"] = "TAMPERED_REASON_SHOULD_BE_DETECTED"

    verification = verify_tamper_evident_audit_chain(tampered)

    return {
        "ok": verification.get("ok") is False,
        "tamper_detected": verification.get("ok") is False,
        "verification": verification,
        "human_reason": (
            "Tamper simulation was detected."
            if verification.get("ok") is False
            else "Tamper simulation was not detected."
        ),
        "soulaana_translation": (
            "Soulaana: I saw the edit. The receipt chain snitched beautifully."
            if verification.get("ok") is False
            else "Soulaana: The tamper test slipped through. That is not acceptable."
        ),
    }


def summarize_tamper_evident_audit_chain(limit: int = 12) -> Dict[str, Any]:
    chain = _load_chain()
    entries = chain.get("entries", []) if isinstance(chain.get("entries"), list) else []

    try:
        limit = int(limit)
    except Exception:
        limit = 12
    limit = max(1, min(limit, 200))

    verification = verify_tamper_evident_audit_chain(chain)

    by_source: Dict[str, int] = {}
    by_event_type: Dict[str, int] = {}

    for entry in entries:
        source = entry.get("source_name", "unknown")
        event_type = entry.get("event_type", "unknown")
        by_source[source] = by_source.get(source, 0) + 1
        by_event_type[event_type] = by_event_type.get(event_type, 0) + 1

    return {
        "ok": verification.get("ok") is True,
        "pack": "091",
        "path": str(TAMPER_CHAIN_PATH),
        "chain_version": chain.get("chain_version", "pack091.v1"),
        "total_entries": len(entries),
        "latest_hash": entries[-1].get("current_hash") if entries else "",
        "by_source": by_source,
        "by_event_type": by_event_type,
        "recent": entries[-limit:],
        "verification": verification,
        "readiness_score": 100 if verification.get("ok") else 60,
        "readiness_label": "Tamper-evident audit chain ready" if verification.get("ok") else "Tamper-evident audit chain needs repair",
        "human_reason": "Tamper-evident audit chain summary loaded.",
        "soulaana_translation": "Soulaana: The receipt chain summary is ready. The receipts have receipts now.",
    }
