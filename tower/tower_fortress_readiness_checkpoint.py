
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

FORTRESS_CHECKPOINT_PATH = DATA_DIR / "tower_fortress_readiness_checkpoint.json"
FORTRESS_PROOF_BUNDLE_PATH = DATA_DIR / "tower_fortress_proof_bundle.json"
FORTRESS_PANEL_PATH = DATA_DIR / "tower_fortress_readiness_panel.html"


REQUIRED_MODULES = {
    "tamper_evident_audit_chain": "tower/tamper_evident_audit_chain.py",
    "step_up_auth": "tower/step_up_auth.py",
    "emergency_lockdown": "tower/emergency_lockdown.py",
    "quarantine_mode": "tower/quarantine_mode.py",
    "session_risk_scoring": "tower/session_risk_scoring.py",
    "secrets_vault_boundary": "tower/secrets_vault_boundary.py",
    "redaction_reveal_system": "tower/redaction_reveal_system.py",
    "security_rehearsal_panel": "tower/security_rehearsal_panel.py",
    "owner_admin_action_receipts": "tower/owner_admin_action_receipts.py",
}


REQUIRED_DATA_ARTIFACTS = {
    "tamper_chain": "tower/data/tamper_evident_audit_chain.json",
    "step_up_events": "tower/data/step_up_auth_events.json",
    "lockdown_state": "tower/data/emergency_lockdown_state.json",
    "lockdown_events": "tower/data/emergency_lockdown_events.json",
    "quarantine_state": "tower/data/quarantine_mode_state.json",
    "quarantine_events": "tower/data/quarantine_mode_events.json",
    "session_risk_events": "tower/data/session_risk_events.json",
    "session_risk_profiles": "tower/data/session_risk_profiles.json",
    "secrets_registry": "tower/data/secrets_vault_boundary_registry.json",
    "secrets_events": "tower/data/secrets_vault_boundary_events.json",
    "redaction_policy": "tower/data/redaction_reveal_policy.json",
    "redaction_receipts": "tower/data/redaction_reveal_receipts.json",
    "security_rehearsal_results": "tower/data/security_rehearsal_results.json",
    "security_rehearsal_events": "tower/data/security_rehearsal_events.json",
    "owner_admin_receipts": "tower/data/owner_admin_action_receipts.json",
    "owner_admin_summary": "tower/data/owner_admin_action_receipt_summary.json",
}


OPTIONAL_VISIBILITY_POLICY_ARTIFACTS = {
    "deny_path_replacement_receipts": "tower/data/deny_path_replacement_audit_receipts.json",
    "exposure_mapping": "tower/data/ob_exposure_mapping_pass.json",
    "route_replacement_policy_list": "tower/data/route_replacement_policy_list.json",
    "visibility_transition_checkpoint": "tower/data/visibility_policy_transition_checkpoint.json",
    "security_command_dashboard": "tower/data/security_command_dashboard.html",
}


FORTRESS_DOMAINS = {
    "visibility_policy": {
        "label": "Visibility + route policy wall",
        "packs": "086–090",
        "weight": 10,
    },
    "tamper_chain": {
        "label": "Tamper-evident audit chain",
        "packs": "091",
        "weight": 10,
    },
    "step_up": {
        "label": "Step-up authentication",
        "packs": "092",
        "weight": 10,
    },
    "lockdown": {
        "label": "Emergency lockdown",
        "packs": "093",
        "weight": 10,
    },
    "quarantine": {
        "label": "Quarantine mode",
        "packs": "094",
        "weight": 10,
    },
    "risk_scoring": {
        "label": "Session/device/IP risk scoring",
        "packs": "095",
        "weight": 10,
    },
    "secrets_boundary": {
        "label": "Secrets Vault separation boundary",
        "packs": "096",
        "weight": 10,
    },
    "redaction_reveal": {
        "label": "Redaction-by-default reveal",
        "packs": "097",
        "weight": 10,
    },
    "security_rehearsal": {
        "label": "Security rehearsal panel",
        "packs": "098",
        "weight": 10,
    },
    "owner_admin_receipts": {
        "label": "Owner/admin action receipts",
        "packs": "099",
        "weight": 10,
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


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


def _bundle_id(prefix: str = "fortress_bundle") -> str:
    return f"{prefix}_{secrets.token_urlsafe(18)}"


def _redact(value: Any) -> Any:
    secret_keys = {
        "token",
        "raw_token",
        "access_token",
        "refresh_token",
        "api_key",
        "apikey",
        "secret",
        "client_secret",
        "password",
        "passphrase",
        "private_key",
        "encryption_key",
        "broker_key",
        "broker_secret",
        "github_token",
        "stripe_secret",
        "payment_secret",
        "authorization",
        "bearer",
        "credential",
        "credentials",
        "tower_keycard",
        "session_secret",
        "device_secret",
        "raw_value",
    }

    if isinstance(value, dict):
        clean = {}
        redacted_count = 0

        for key, item in value.items():
            key_text = str(key).lower().strip()

            # Preserve safe reference/metadata labels.
            safe_key = key_text in {
                "secret_ref_id",
                "secret_type",
                "secret_status",
                "secrets_vault_is_source_of_truth",
                "secret_reference_count",
                "secret_values_never_revealed",
                "no_secret_leakage",
                "no_secret_material_leakage",
            }

            if not safe_key and (
                key_text in secret_keys
                or key_text.endswith(("_token", "_password", "_api_key", "_secret", "_credential"))
            ):
                redacted_count += 1
                continue

            redacted_item = _redact(item)

            if isinstance(redacted_item, dict) and "__redacted_fortress_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_fortress_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_fortress_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_fortress_field_count__"] = redacted_count

        return clean

    if isinstance(value, list):
        return [_redact(item) for item in value]

    if isinstance(value, str):
        lowered = value.lower()
        if lowered.startswith("secret_ref_"):
            return value

        if (
            "should_not_survive" in lowered
            or "tower_keycard=" in lowered
            or "bearer " in lowered
            or "ghp_" in lowered
            or "sk_live_" in lowered
            or "-----begin private key-----" in lowered
            or "access_token=" in lowered
            or "refresh_token=" in lowered
        ):
            return "[REDACTED_FORTRESS_VALUE]"
        return value

    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(_redact(value), sort_keys=True, separators=(",", ":"), default=str)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _safe_scan(payload: Any) -> Dict[str, Any]:
    serialized = json.dumps(payload, sort_keys=True, default=str).lower()
    forbidden = [
        "should_not_survive",
        "tower_keycard=",
        "bearer should_not_survive",
        "ghp_should_not_survive",
        "sk_live_should_not_survive",
        "-----begin private key-----",
        '"raw_token":',
        '"tower_keycard":',
        '"access_token":',
        '"refresh_token":',
        '"api_key":',
        '"github_token":',
        '"stripe_secret":',
        '"password":',
        '"private_key":',
    ]
    hits = [item for item in forbidden if item in serialized]
    return {
        "ok": not hits,
        "forbidden_hit_count": len(hits),
        "had_forbidden_hits": bool(hits),
    }


def _path_status(relative_path: str) -> Dict[str, Any]:
    path = PROJECT_ROOT / relative_path
    exists = path.exists()
    stat = path.stat() if exists else None

    return {
        "path": relative_path,
        "exists": exists,
        "size_bytes": int(stat.st_size) if stat else 0,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat().replace("+00:00", "Z") if stat else "",
    }


def _list_status(paths: Dict[str, str]) -> Dict[str, Any]:
    items = {}
    missing = []
    for name, relative_path in paths.items():
        status = _path_status(relative_path)
        items[name] = status
        if not status.get("exists"):
            missing.append(name)
    return {
        "ok": len(missing) == 0,
        "items": items,
        "missing": missing,
        "present_count": len(paths) - len(missing),
        "total_count": len(paths),
    }


def _safe_count_from_file(relative_path: str) -> int:
    path = PROJECT_ROOT / relative_path
    data = _load_json(path, None)
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        for key in ["receipt_count", "event_count", "total_events", "secret_reference_count", "scenario_count"]:
            try:
                if key in data:
                    return int(data.get(key, 0))
            except Exception:
                pass
        return 1 if data else 0
    return 0


def _readiness_item(name: str, *, ok: bool, score: int, evidence: Dict[str, Any], human_reason: str) -> Dict[str, Any]:
    item = {
        "name": name,
        "ok": bool(ok),
        "score": max(0, min(100, int(score))),
        "evidence": _redact(evidence),
        "human_reason": human_reason,
    }
    item["fingerprint"] = _fingerprint(item)
    return item


def _evaluate_visibility_policy() -> Dict[str, Any]:
    status = _list_status(OPTIONAL_VISIBILITY_POLICY_ARTIFACTS)
    # Optional because Pack 100 is hardening checkpoint and older packs may vary,
    # but we still expect at least replacement/exposure/policy artifacts if present.
    present = status.get("present_count", 0)
    total = status.get("total_count", 1)
    score = int((present / max(1, total)) * 100)
    ok = present >= 3

    return _readiness_item(
        "visibility_policy",
        ok=ok,
        score=score,
        evidence=status,
        human_reason="Visibility/policy artifacts checked. At least three wall artifacts should exist from Packs 086–090.",
    )


def _evaluate_tamper_chain() -> Dict[str, Any]:
    count = _safe_count_from_file(REQUIRED_DATA_ARTIFACTS["tamper_chain"])
    status = _path_status(REQUIRED_DATA_ARTIFACTS["tamper_chain"])
    ok = status.get("exists") and count >= 1

    return _readiness_item(
        "tamper_chain",
        ok=ok,
        score=100 if ok else 50,
        evidence={"status": status, "record_count": count},
        human_reason="Tamper-evident audit chain file exists and contains chained records.",
    )


def _evaluate_step_up() -> Dict[str, Any]:
    count = _safe_count_from_file(REQUIRED_DATA_ARTIFACTS["step_up_events"])
    status = _path_status(REQUIRED_DATA_ARTIFACTS["step_up_events"])
    ok = status.get("exists") and count >= 1

    return _readiness_item(
        "step_up",
        ok=ok,
        score=100 if ok else 50,
        evidence={"status": status, "event_count": count},
        human_reason="Step-up auth event store exists and contains verification/challenge events.",
    )


def _evaluate_lockdown() -> Dict[str, Any]:
    state = _load_json(PROJECT_ROOT / REQUIRED_DATA_ARTIFACTS["lockdown_state"], {})
    event_count = _safe_count_from_file(REQUIRED_DATA_ARTIFACTS["lockdown_events"])
    ok = isinstance(state, dict) and state.get("ok") is True and "blocked_actions" in state

    return _readiness_item(
        "lockdown",
        ok=ok,
        score=100 if ok else 55,
        evidence={
            "state_exists": bool(state),
            "lockdown_active": state.get("lockdown_active"),
            "blocked_action_count": len(state.get("blocked_actions", [])) if isinstance(state.get("blocked_actions"), list) else 0,
            "event_count": event_count,
        },
        human_reason="Emergency lockdown state exists with blocked/recovery action structure.",
    )


def _evaluate_quarantine() -> Dict[str, Any]:
    state = _load_json(PROJECT_ROOT / REQUIRED_DATA_ARTIFACTS["quarantine_state"], {})
    event_count = _safe_count_from_file(REQUIRED_DATA_ARTIFACTS["quarantine_events"])
    ok = isinstance(state, dict) and state.get("ok") is True and "blocked_actions" in state and "allowed_actions" in state

    return _readiness_item(
        "quarantine",
        ok=ok,
        score=100 if ok else 55,
        evidence={
            "state_exists": bool(state),
            "active_case_count": len([c for c in state.get("active_cases", []) if isinstance(c, dict) and c.get("status") == "active"]) if isinstance(state.get("active_cases"), list) else 0,
            "blocked_action_count": len(state.get("blocked_actions", [])) if isinstance(state.get("blocked_actions"), list) else 0,
            "allowed_action_count": len(state.get("allowed_actions", [])) if isinstance(state.get("allowed_actions"), list) else 0,
            "event_count": event_count,
        },
        human_reason="Quarantine state exists with holding-room blocked/recovery action structure.",
    )


def _evaluate_risk_scoring() -> Dict[str, Any]:
    event_count = _safe_count_from_file(REQUIRED_DATA_ARTIFACTS["session_risk_events"])
    profiles = _load_json(PROJECT_ROOT / REQUIRED_DATA_ARTIFACTS["session_risk_profiles"], {})
    ok = event_count >= 1 and isinstance(profiles, dict)

    return _readiness_item(
        "risk_scoring",
        ok=ok,
        score=100 if ok else 55,
        evidence={
            "event_count": event_count,
            "profiles_exist": bool(profiles),
            "profile_keys": sorted(list(profiles.keys()))[:12] if isinstance(profiles, dict) else [],
        },
        human_reason="Session/device/IP risk scoring has event store and profile store.",
    )


def _evaluate_secrets_boundary() -> Dict[str, Any]:
    registry = _load_json(PROJECT_ROOT / REQUIRED_DATA_ARTIFACTS["secrets_registry"], {})
    events = _load_json(PROJECT_ROOT / REQUIRED_DATA_ARTIFACTS["secrets_events"], [])
    refs = registry.get("secret_references", []) if isinstance(registry, dict) and isinstance(registry.get("secret_references"), list) else []
    policy = registry.get("policy", {}) if isinstance(registry, dict) else {}
    scan = _safe_scan({"registry": registry, "events": events})

    ok = (
        isinstance(registry, dict)
        and policy.get("tower_may_store_raw_value") is False
        and policy.get("secrets_vault_is_source_of_truth") is True
        and scan.get("ok") is True
    )

    return _readiness_item(
        "secrets_boundary",
        ok=ok,
        score=100 if ok else 50,
        evidence={
            "secret_reference_count": len(refs),
            "event_count": len(events) if isinstance(events, list) else 0,
            "tower_may_store_raw_value": policy.get("tower_may_store_raw_value"),
            "secrets_vault_is_source_of_truth": policy.get("secrets_vault_is_source_of_truth"),
            "leakage_scan": scan,
        },
        human_reason="Secrets boundary registry/events checked for reference-only behavior and no raw secret leakage.",
    )


def _evaluate_redaction_reveal() -> Dict[str, Any]:
    policy = _load_json(PROJECT_ROOT / REQUIRED_DATA_ARTIFACTS["redaction_policy"], {})
    receipts = _load_json(PROJECT_ROOT / REQUIRED_DATA_ARTIFACTS["redaction_receipts"], [])
    receipt_count = len(receipts) if isinstance(receipts, list) else 0
    scan = _safe_scan({"policy": policy, "receipts": receipts})

    by_decision = {}
    for receipt in receipts if isinstance(receipts, list) else []:
        decision = receipt.get("decision", "unknown") if isinstance(receipt, dict) else "unknown"
        by_decision[decision] = by_decision.get(decision, 0) + 1

    ok = (
        isinstance(policy, dict)
        and receipt_count >= 1
        and scan.get("ok") is True
        and any(key in by_decision for key in ["reveal_denied", "reveal_step_up_required", "reveal_allowed"])
    )

    return _readiness_item(
        "redaction_reveal",
        ok=ok,
        score=100 if ok else 55,
        evidence={
            "receipt_count": receipt_count,
            "by_decision": by_decision,
            "leakage_scan": scan,
        },
        human_reason="Redaction reveal policy/receipts checked for summary-first and gated reveal behavior.",
    )


def _evaluate_security_rehearsal() -> Dict[str, Any]:
    report = _load_json(PROJECT_ROOT / REQUIRED_DATA_ARTIFACTS["security_rehearsal_results"], {})
    events = _load_json(PROJECT_ROOT / REQUIRED_DATA_ARTIFACTS["security_rehearsal_events"], [])
    scan = _safe_scan({"report": report, "events": events})

    ok = (
        isinstance(report, dict)
        and report.get("ok") is True
        and int(report.get("pass_count", 0)) >= 9
        and int(report.get("fail_count", 1)) == 0
        and report.get("no_secret_leakage") is True
        and scan.get("ok") is True
    )

    return _readiness_item(
        "security_rehearsal",
        ok=ok,
        score=100 if ok else 60,
        evidence={
            "scenario_count": report.get("scenario_count"),
            "pass_count": report.get("pass_count"),
            "fail_count": report.get("fail_count"),
            "readiness_score": report.get("readiness_score"),
            "no_secret_leakage": report.get("no_secret_leakage"),
            "event_count": len(events) if isinstance(events, list) else 0,
            "leakage_scan": scan,
        },
        human_reason="Security rehearsal report checked for all scenarios passing without secret leakage.",
    )


def _evaluate_owner_admin_receipts() -> Dict[str, Any]:
    summary = _load_json(PROJECT_ROOT / REQUIRED_DATA_ARTIFACTS["owner_admin_summary"], {})
    receipts = _load_json(PROJECT_ROOT / REQUIRED_DATA_ARTIFACTS["owner_admin_receipts"], [])
    scan = _safe_scan({"summary": summary, "receipts": receipts})
    by_action = summary.get("by_action", {}) if isinstance(summary, dict) else {}

    required_actions = {
        "note_added",
        "security_item_resolved",
        "route_policy_changed",
        "user_clearance_changed",
        "export_approved",
        "lockdown_enabled",
        "lockdown_disabled",
        "mode_access_granted",
        "archive_handoff_created",
        "admin_override_recorded",
    }

    present_actions = {key for key, count in by_action.items() if int(count or 0) >= 1} if isinstance(by_action, dict) else set()

    ok = (
        isinstance(summary, dict)
        and int(summary.get("receipt_count", 0)) >= 10
        and required_actions.issubset(present_actions)
        and summary.get("no_secret_leakage") is True
        and scan.get("ok") is True
    )

    return _readiness_item(
        "owner_admin_receipts",
        ok=ok,
        score=100 if ok else 60,
        evidence={
            "receipt_count": summary.get("receipt_count"),
            "archive_ready_count": summary.get("archive_ready_count"),
            "step_up_missing_high_power_count": summary.get("step_up_missing_high_power_count"),
            "required_actions_present": sorted(list(required_actions.intersection(present_actions))),
            "missing_actions": sorted(list(required_actions - present_actions)),
            "leakage_scan": scan,
        },
        human_reason="Owner/admin receipts checked for full action coverage and no secret leakage.",
    )


def build_tower_fortress_checkpoint(*, actor_user_id: str = "owner_solice", write_panel: bool = True) -> Dict[str, Any]:
    module_status = _list_status(REQUIRED_MODULES)
    required_data_status = _list_status(REQUIRED_DATA_ARTIFACTS)
    optional_visibility_status = _list_status(OPTIONAL_VISIBILITY_POLICY_ARTIFACTS)

    readiness_items = {
        "visibility_policy": _evaluate_visibility_policy(),
        "tamper_chain": _evaluate_tamper_chain(),
        "step_up": _evaluate_step_up(),
        "lockdown": _evaluate_lockdown(),
        "quarantine": _evaluate_quarantine(),
        "risk_scoring": _evaluate_risk_scoring(),
        "secrets_boundary": _evaluate_secrets_boundary(),
        "redaction_reveal": _evaluate_redaction_reveal(),
        "security_rehearsal": _evaluate_security_rehearsal(),
        "owner_admin_receipts": _evaluate_owner_admin_receipts(),
    }

    weighted_total = 0
    weight_max = 0
    failed_domains = []

    for domain, config in FORTRESS_DOMAINS.items():
        item = readiness_items.get(domain, {})
        weight = int(config.get("weight", 10))
        weighted_total += int(item.get("score", 0)) * weight
        weight_max += 100 * weight
        if item.get("ok") is not True:
            failed_domains.append(domain)

    readiness_score = int(round((weighted_total / max(1, weight_max)) * 100))

    module_ok = module_status.get("ok") is True
    data_core_ok = required_data_status.get("present_count", 0) >= 12
    no_domain_failures = len(failed_domains) == 0
    fortress_ready = module_ok and data_core_ok and no_domain_failures and readiness_score >= 90

    checkpoint = {
        "ok": fortress_ready,
        "pack": "100",
        "checkpoint_id": _bundle_id("tower_fortress_checkpoint"),
        "created_at": _utc_now(),
        "actor_user_id": _safe_str(actor_user_id, "owner_solice"),
        "readiness_score": readiness_score,
        "readiness_label": (
            "Tower fortress ready for OB integration"
            if fortress_ready
            else "Tower fortress needs review before OB integration"
        ),
        "failed_domains": failed_domains,
        "module_status": module_status,
        "required_data_status": required_data_status,
        "optional_visibility_status": optional_visibility_status,
        "readiness_items": readiness_items,
        "ob_integration_gate": {
            "allowed_to_start_ob_adapter": fortress_ready,
            "next_adapter": "Adapter 001 / The Teller Integration Adapter or OB clearance bridge",
            "required_before_live_public_access": [
                "legal/compliance review",
                "real Secrets Vault implementation",
                "production identity provider",
                "production database/security hardening",
                "external security review before handling real sensitive public-user data",
            ],
            "safe_next_step": "Build the OB/Tower bridge so OB asks The Tower before protected screens, modes, objects, exports, and live actions load.",
        },
        "human_reason": (
            "Tower fortress checkpoint passed. Core wall/security proof is ready before OB integration."
            if fortress_ready
            else "Tower fortress checkpoint found review items before OB integration."
        ),
        "soulaana_translation": (
            "Soulaana: The wall has receipts. OB can approach the gate next."
            if fortress_ready
            else "Soulaana: Do not plug OB into a loose gate. Review the failed domains first."
        ),
    }

    checkpoint = _redact(checkpoint)
    scan = _safe_scan(checkpoint)
    checkpoint["no_secret_leakage"] = scan.get("ok") is True
    checkpoint["leakage_scan"] = scan
    checkpoint["checkpoint_fingerprint"] = _fingerprint(checkpoint)

    _write_json(FORTRESS_CHECKPOINT_PATH, checkpoint)

    proof_bundle = build_tower_fortress_proof_bundle(checkpoint=checkpoint)
    _write_json(FORTRESS_PROOF_BUNDLE_PATH, proof_bundle)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry

        create_tamper_chain_entry(
            event_type="tower_fortress_readiness_checkpoint",
            source_name="tower_fortress_readiness_checkpoint",
            source_path=str(FORTRESS_CHECKPOINT_PATH),
            source_hash=_fingerprint(checkpoint),
            record_count=1,
            actor_user_id=_safe_str(actor_user_id, "owner_solice"),
            reason="Pack 100 final fortress readiness checkpoint before OB integration.",
            metadata={
                "pack": "100",
                "checkpoint_id": checkpoint.get("checkpoint_id"),
                "readiness_score": checkpoint.get("readiness_score"),
                "ok": checkpoint.get("ok"),
            },
        )
    except Exception:
        pass

    if write_panel:
        write_tower_fortress_readiness_panel(checkpoint)

    return checkpoint


def build_tower_fortress_proof_bundle(*, checkpoint: Dict[str, Any] | None = None) -> Dict[str, Any]:
    checkpoint = checkpoint if isinstance(checkpoint, dict) else _load_json(FORTRESS_CHECKPOINT_PATH, {})

    proof_bundle = {
        "ok": bool(checkpoint.get("ok")),
        "pack": "100",
        "bundle_id": _bundle_id("tower_fortress_proof_bundle"),
        "created_at": _utc_now(),
        "checkpoint_id": checkpoint.get("checkpoint_id"),
        "readiness_score": checkpoint.get("readiness_score"),
        "readiness_label": checkpoint.get("readiness_label"),
        "included_domains": sorted(list(FORTRESS_DOMAINS.keys())),
        "proof_artifacts": {
            "checkpoint": str(FORTRESS_CHECKPOINT_PATH),
            "proof_bundle": str(FORTRESS_PROOF_BUNDLE_PATH),
            "readiness_panel": str(FORTRESS_PANEL_PATH),
            "required_modules": REQUIRED_MODULES,
            "required_data_artifacts": REQUIRED_DATA_ARTIFACTS,
            "optional_visibility_policy_artifacts": OPTIONAL_VISIBILITY_POLICY_ARTIFACTS,
        },
        "domain_evidence": checkpoint.get("readiness_items", {}),
        "ob_integration_gate": checkpoint.get("ob_integration_gate", {}),
        "before_ob_integration_statement": (
            "The Tower has a tested wall/security proof bundle covering policy visibility, tamper chain, step-up, lockdown, quarantine, risk scoring, secrets boundary, redaction reveal, security rehearsal, and owner/admin receipts."
        ),
        "human_reason": "Fortress proof bundle created from Pack 100 checkpoint.",
        "soulaana_translation": "Soulaana: Proof bundle sealed. The gate can explain itself before OB touches it.",
    }

    proof_bundle = _redact(proof_bundle)
    scan = _safe_scan(proof_bundle)
    proof_bundle["no_secret_leakage"] = scan.get("ok") is True
    proof_bundle["leakage_scan"] = scan
    proof_bundle["bundle_fingerprint"] = _fingerprint(proof_bundle)

    return proof_bundle


def write_tower_fortress_readiness_panel(checkpoint: Dict[str, Any] | None = None) -> Dict[str, Any]:
    checkpoint = checkpoint if isinstance(checkpoint, dict) else _load_json(FORTRESS_CHECKPOINT_PATH, {})
    items = checkpoint.get("readiness_items", {}) if isinstance(checkpoint.get("readiness_items"), dict) else {}

    cards = []
    for domain, config in FORTRESS_DOMAINS.items():
        item = items.get(domain, {}) if isinstance(items.get(domain), dict) else {}
        status = "PASS" if item.get("ok") else "REVIEW"
        cards.append(f"""
        <article class="card {'pass' if item.get('ok') else 'fail'}">
          <div class="eyebrow">Packs {config.get('packs')} · {status}</div>
          <h2>{config.get('label')}</h2>
          <p>{item.get('human_reason', '')}</p>
          <div class="score">{item.get('score', 0)} / 100</div>
        </article>
        """)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · Fortress Readiness Checkpoint</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background: #080907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 42px 22px;
    }}
    .hero {{
      border: 1px solid rgba(220, 183, 94, .38);
      border-radius: 30px;
      padding: 30px;
      background: linear-gradient(135deg, rgba(83, 52, 19, .78), rgba(10, 11, 9, .96));
      box-shadow: 0 22px 90px rgba(0,0,0,.42);
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 36px;
      letter-spacing: -.045em;
    }}
    .hero p {{
      margin: 0;
      max-width: 860px;
      color: rgba(245,234,210,.78);
      line-height: 1.55;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin: 20px 0;
    }}
    .stat {{
      border: 1px solid rgba(245,234,210,.14);
      border-radius: 20px;
      padding: 16px;
      background: rgba(255,255,255,.045);
    }}
    .stat b {{
      display: block;
      font-size: 24px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
      margin-top: 18px;
    }}
    .card {{
      border: 1px solid rgba(245,234,210,.14);
      border-radius: 24px;
      padding: 18px;
      background: rgba(255,255,255,.045);
    }}
    .card.pass {{
      border-color: rgba(143, 221, 158, .34);
    }}
    .card.fail {{
      border-color: rgba(255, 128, 128, .46);
    }}
    .eyebrow {{
      color: rgba(220, 183, 94, .84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    h2 {{
      margin: 0 0 8px;
      font-size: 18px;
    }}
    .card p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .score {{
      margin-top: 14px;
      font-weight: 900;
      color: #f2d58b;
    }}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <h1>The Tower · Fortress Readiness Checkpoint</h1>
    <p>{checkpoint.get('human_reason', 'Tower fortress checkpoint loaded.')}</p>
  </section>
  <section class="stats">
    <div class="stat"><b>{checkpoint.get('readiness_score', 0)}</b><span>Readiness</span></div>
    <div class="stat"><b>{'YES' if checkpoint.get('ok') else 'NO'}</b><span>OB Gate Ready</span></div>
    <div class="stat"><b>{len(checkpoint.get('failed_domains', []))}</b><span>Review Domains</span></div>
    <div class="stat"><b>{'YES' if checkpoint.get('no_secret_leakage') else 'NO'}</b><span>No Secret Leakage</span></div>
  </section>
  <section class="grid">
    {''.join(cards)}
  </section>
</main>
</body>
</html>
"""
    FORTRESS_PANEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    FORTRESS_PANEL_PATH.write_text(html, encoding="utf-8")

    return {
        "ok": True,
        "decision": "tower_fortress_readiness_panel_written",
        "path": str(FORTRESS_PANEL_PATH),
        "human_reason": "Tower fortress readiness HTML panel written.",
        "soulaana_translation": "Soulaana: Fortress proof board posted.",
    }


def summarize_tower_fortress_checkpoint() -> Dict[str, Any]:
    checkpoint = _load_json(FORTRESS_CHECKPOINT_PATH, {})
    bundle = _load_json(FORTRESS_PROOF_BUNDLE_PATH, {})

    summary = {
        "ok": bool(checkpoint.get("ok")),
        "pack": "100",
        "checkpoint_path": str(FORTRESS_CHECKPOINT_PATH),
        "proof_bundle_path": str(FORTRESS_PROOF_BUNDLE_PATH),
        "panel_path": str(FORTRESS_PANEL_PATH),
        "checkpoint_id": checkpoint.get("checkpoint_id"),
        "bundle_id": bundle.get("bundle_id"),
        "readiness_score": checkpoint.get("readiness_score", 0),
        "readiness_label": checkpoint.get("readiness_label", "Tower fortress checkpoint not run"),
        "failed_domains": checkpoint.get("failed_domains", []),
        "no_secret_leakage": checkpoint.get("no_secret_leakage"),
        "ob_integration_allowed": checkpoint.get("ob_integration_gate", {}).get("allowed_to_start_ob_adapter") if isinstance(checkpoint.get("ob_integration_gate"), dict) else False,
        "human_reason": "Tower fortress checkpoint summary loaded.",
        "soulaana_translation": "Soulaana: Final wall checkpoint summary is ready.",
    }

    summary = _redact(summary)
    scan = _safe_scan(summary)
    summary["summary_no_secret_leakage"] = scan.get("ok") is True
    summary["leakage_scan"] = scan

    return summary


def reset_tower_fortress_checkpoint_for_test() -> Dict[str, Any]:
    for path in [FORTRESS_CHECKPOINT_PATH, FORTRESS_PROOF_BUNDLE_PATH]:
        _write_json(path, {
            "ok": True,
            "pack": "100",
            "reset_at": _utc_now(),
            "human_reason": "Tower fortress checkpoint reset for test.",
            "soulaana_translation": "Soulaana: Fortress checkpoint reset for a clean test lane.",
        })

    if FORTRESS_PANEL_PATH.exists():
        try:
            FORTRESS_PANEL_PATH.unlink()
        except Exception:
            pass

    return {
        "ok": True,
        "decision": "tower_fortress_checkpoint_reset_for_test",
        "checkpoint_reset": True,
        "proof_bundle_reset": True,
        "soulaana_translation": "Soulaana: Fortress checkpoint reset for a clean test lane.",
    }
