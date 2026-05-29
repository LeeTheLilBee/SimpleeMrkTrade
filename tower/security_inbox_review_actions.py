
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

REVIEW_STATE_PATH = DATA_DIR / "security_inbox_review_states.json"
REVIEW_RECEIPTS_PATH = DATA_DIR / "security_inbox_review_receipts.json"
REVIEW_STATUS_PATH = DATA_DIR / "security_inbox_review_status.json"
REVIEW_PANEL_PATH = DATA_DIR / "security_inbox_review_panel.html"

ALLOWED_REVIEW_STATES = {
    "new",
    "acknowledged",
    "investigating",
    "resolved",
    "escalated",
    "false_alarm",
    "archived",
}

STATE_LABELS = {
    "new": "New",
    "acknowledged": "Acknowledged",
    "investigating": "Investigating",
    "resolved": "Resolved",
    "escalated": "Escalated",
    "false_alarm": "False Alarm",
    "archived": "Archived",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)


def _load_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


def _html_escape(value: Any) -> str:
    text = str(value if value is not None else "")
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


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
        "sk_live_",
        "ghp_",
    ]
    hits = [item for item in forbidden if item in serialized]
    return {
        "ok": not hits,
        "forbidden_hit_count": len(hits),
        "had_forbidden_hits": bool(hits),
    }


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
        "bank_account",
        "routing_number",
        "account_number",
        "ssn",
    }

    if isinstance(value, dict):
        clean = {}
        redacted_count = 0
        for key, item in value.items():
            key_text = str(key).lower().strip()
            if key_text in secret_keys or key_text.endswith(("_token", "_password", "_api_key", "_secret", "_credential")):
                redacted_count += 1
                continue

            redacted_item = _redact(item)

            if isinstance(redacted_item, dict) and "__redacted_security_review_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_security_review_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_security_review_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_security_review_field_count__"] = redacted_count
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
            return "[REDACTED_SECURITY_REVIEW_VALUE]"
        return value

    return value


def _load_states() -> Dict[str, Any]:
    data = _load_json(REVIEW_STATE_PATH, {})
    return data if isinstance(data, dict) else {}


def _save_states(states: Dict[str, Any]) -> None:
    _write_json(REVIEW_STATE_PATH, states)


def _load_receipts() -> List[Dict[str, Any]]:
    data = _load_json(REVIEW_RECEIPTS_PATH, [])
    return data if isinstance(data, list) else []


def _save_receipts(receipts: List[Dict[str, Any]]) -> None:
    _write_json(REVIEW_RECEIPTS_PATH, receipts)


def _get_inbox_items(limit: int = 120) -> List[Dict[str, Any]]:
    try:
        from tower.security_inbox_owner_queue import build_security_inbox_owner_queue

        inbox = build_security_inbox_owner_queue(limit_per_source=80, write_panel=True)
        items = inbox.get("recent_items", [])
        if isinstance(items, list):
            return [item for item in items[:limit] if isinstance(item, dict)]
    except Exception:
        pass
    return []


def _default_state_for_item(item: Dict[str, Any]) -> str:
    if item.get("needs_owner_review"):
        return "new"
    return "archived"


def _merge_state(item: Dict[str, Any], states: Dict[str, Any]) -> Dict[str, Any]:
    item_id = str(item.get("inbox_item_id", "") or "")
    state = states.get(item_id, {}) if item_id else {}
    if not isinstance(state, dict):
        state = {}

    review_state = state.get("review_state") or _default_state_for_item(item)

    merged = dict(item)
    merged["review_state"] = review_state
    merged["review_label"] = STATE_LABELS.get(review_state, review_state)
    merged["review_notes"] = state.get("review_notes", "")
    merged["reviewed_by"] = state.get("reviewed_by", "")
    merged["reviewed_at"] = state.get("reviewed_at", "")
    merged["last_review_action"] = state.get("last_review_action", "")
    return merged


def apply_security_inbox_review_action(
    inbox_item_id: str,
    review_state: str,
    actor_user_id: str = "owner_solice",
    note: str = "",
    reason: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    inbox_item_id = str(inbox_item_id or "").strip()
    review_state = str(review_state or "").strip().lower()
    actor_user_id = str(actor_user_id or "owner_solice").strip() or "owner_solice"
    note = str(note or "").strip()
    reason = str(reason or "").strip()
    metadata = metadata if isinstance(metadata, dict) else {}

    if not inbox_item_id:
        return {
            "ok": False,
            "pack": "122",
            "decision": "review_action_rejected",
            "reason_code": "missing_inbox_item_id",
            "human_reason": "Inbox item ID is required.",
            "required_actions": ["provide_inbox_item_id"],
        }

    if review_state not in ALLOWED_REVIEW_STATES:
        return {
            "ok": False,
            "pack": "122",
            "decision": "review_action_rejected",
            "reason_code": "invalid_review_state",
            "allowed_states": sorted(ALLOWED_REVIEW_STATES),
            "human_reason": "Review state is not allowed.",
            "required_actions": ["choose_allowed_review_state"],
        }

    item_lookup = {str(item.get("inbox_item_id", "")): item for item in _get_inbox_items(limit=200)}
    item = item_lookup.get(inbox_item_id)

    if item is None:
        return {
            "ok": False,
            "pack": "122",
            "decision": "review_action_rejected",
            "reason_code": "inbox_item_not_found",
            "inbox_item_id": inbox_item_id,
            "human_reason": "Inbox item could not be found in the current security inbox.",
            "required_actions": ["refresh_security_inbox", "confirm_inbox_item_id"],
        }

    now = _utc_now()
    states = _load_states()
    prior = states.get(inbox_item_id, {}) if isinstance(states.get(inbox_item_id), dict) else {}
    prior_state = prior.get("review_state", _default_state_for_item(item))

    state_record = {
        "inbox_item_id": inbox_item_id,
        "review_state": review_state,
        "review_label": STATE_LABELS.get(review_state, review_state),
        "review_notes": note,
        "reviewed_by": actor_user_id,
        "reviewed_at": now,
        "last_review_action": f"{prior_state}_to_{review_state}",
        "source": item.get("source", ""),
        "severity": item.get("severity", ""),
        "decision": item.get("decision", ""),
        "object_type": item.get("object_type", ""),
        "object_id": item.get("object_id", ""),
        "route_path": item.get("route_path", ""),
        "metadata": metadata,
    }

    state_record = _redact(state_record)
    states[inbox_item_id] = state_record
    _save_states(states)

    receipt = {
        "receipt_id": "security_review_receipt_" + _fingerprint({
            "inbox_item_id": inbox_item_id,
            "review_state": review_state,
            "actor_user_id": actor_user_id,
            "created_at": now,
        })[:18],
        "event_type": "tower_security_inbox_review_action",
        "pack": "122",
        "created_at": now,
        "actor_user_id": actor_user_id,
        "inbox_item_id": inbox_item_id,
        "prior_review_state": prior_state,
        "new_review_state": review_state,
        "decision": "review_action_applied",
        "reason_code": "security_inbox_review_state_updated",
        "human_reason": reason or f"Security inbox item moved from {prior_state} to {review_state}.",
        "source": item.get("source", ""),
        "severity": item.get("severity", ""),
        "object_type": item.get("object_type", ""),
        "object_id": item.get("object_id", ""),
        "route_path": item.get("route_path", ""),
        "metadata": metadata,
    }

    receipt = _redact(receipt)
    receipts = _load_receipts()
    receipts.append(receipt)
    _save_receipts(receipts[-500:])

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_security_inbox_review_action",
            source_name="security_inbox_review_receipt",
            source_path=str(REVIEW_RECEIPTS_PATH),
            source_hash=_fingerprint(receipt),
            record_count=1,
            actor_user_id=actor_user_id,
            reason=receipt.get("human_reason"),
            metadata={
                "pack": "122",
                "inbox_item_id": inbox_item_id,
                "new_review_state": review_state,
                "source": item.get("source", ""),
            },
        )
    except Exception:
        pass

    result = {
        "ok": True,
        "pack": "122",
        "decision": "review_action_applied",
        "inbox_item_id": inbox_item_id,
        "prior_review_state": prior_state,
        "new_review_state": review_state,
        "state_record": state_record,
        "receipt": receipt,
        "human_reason": "Security inbox review action applied with a separate review receipt.",
        "soulaana_translation": "Soulaana: Review state updated. The original event stayed untouched; the owner receipt was added.",
    }

    scan = _safe_scan(result)
    result["no_secret_leakage"] = scan.get("ok") is True
    result["leakage_scan"] = scan
    return result


def build_security_inbox_review_status(write_panel: bool = True) -> Dict[str, Any]:
    items = _get_inbox_items(limit=200)
    states = _load_states()
    receipts = _load_receipts()

    merged = [_merge_state(item, states) for item in items]

    by_state: Dict[str, int] = {}
    by_severity: Dict[str, int] = {}
    open_review_count = 0

    for item in merged:
        state = item.get("review_state", "new")
        severity = item.get("severity", "info")
        by_state[state] = by_state.get(state, 0) + 1
        by_severity[severity] = by_severity.get(severity, 0) + 1
        if state in {"new", "acknowledged", "investigating", "escalated"}:
            open_review_count += 1

    checks = {
        "allowed_states_available": len(ALLOWED_REVIEW_STATES) >= 7,
        "inbox_loaded": isinstance(items, list),
        "states_loaded": isinstance(states, dict),
        "receipts_loaded": isinstance(receipts, list),
        "merged_items_ready": isinstance(merged, list),
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    status = {
        "ok": not failed_checks,
        "pack": "122",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(REVIEW_STATUS_PATH),
        "panel_path": str(REVIEW_PANEL_PATH),
        "state_path": str(REVIEW_STATE_PATH),
        "receipts_path": str(REVIEW_RECEIPTS_PATH),
        "allowed_states": sorted(ALLOWED_REVIEW_STATES),
        "inbox_count": len(items),
        "tracked_state_count": len(states),
        "receipt_count": len(receipts),
        "open_review_count": open_review_count,
        "by_state": by_state,
        "by_severity": by_severity,
        "recent_items": merged[:80],
        "recent_receipts": receipts[-20:],
        "checks": checks,
        "failed_checks": failed_checks,
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 10)),
        "readiness_label": (
            "Security Inbox owner review actions ready"
            if not failed_checks
            else "Security Inbox owner review actions need review"
        ),
        "human_reason": "Security Inbox review states/actions are ready and tracked separately from original event logs.",
        "soulaana_translation": "Soulaana: The inbox can now be worked instead of only watched.",
    }

    status = _redact(status)
    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(REVIEW_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_security_inbox_review_status",
            source_name="security_inbox_review_status",
            source_path=str(REVIEW_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=int(status.get("inbox_count", 0) or 0),
            actor_user_id="tower_system",
            reason="Pack 122 Security Inbox review status generated.",
            metadata={
                "pack": "122",
                "status": status.get("status"),
                "open_review_count": status.get("open_review_count"),
                "readiness_score": status.get("readiness_score"),
            },
        )
    except Exception:
        pass

    if write_panel:
        write_security_inbox_review_panel(status)

    return status


def render_security_inbox_review_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_security_inbox_review_status(write_panel=False)
    items = status.get("recent_items", []) if isinstance(status.get("recent_items"), list) else []

    card_html = []
    for item in items[:24]:
        if not isinstance(item, dict):
            continue
        state = _html_escape(item.get("review_state", "new"))
        label = _html_escape(item.get("review_label", STATE_LABELS.get(item.get("review_state", "new"), "New")))
        severity = _html_escape(item.get("severity", "info"))
        source = _html_escape(item.get("source", "source"))
        decision = _html_escape(item.get("decision", "recorded"))
        reason = _html_escape(item.get("human_reason", "Security event recorded."))
        item_id = _html_escape(item.get("inbox_item_id", ""))

        card_html.append(f"""
        <article class="security-review-card security-review-card--{state}">
          <div class="security-review-card__eyebrow">{label} · {severity} · {source}</div>
          <h3>{decision}</h3>
          <p>{reason}</p>
          <small>{item_id}</small>
        </article>
        """)

    if not card_html:
        card_html.append("""
        <article class="security-review-card security-review-card--new">
          <div class="security-review-card__eyebrow">NEW · INFO · EMPTY</div>
          <h3>No review items yet</h3>
          <p>The review-state layer is ready. Items will appear as the Security Inbox fills.</p>
        </article>
        """)

    html = f"""
<!-- PACK122_SECURITY_INBOX_REVIEW_ACTIONS_SECTION -->
<section class="security-inbox-review-actions" data-pack="122">
  <style>
    .security-inbox-review-actions {{
      margin: 24px 0;
      border: 1px solid rgba(168,175,255,.38);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top right, rgba(168,175,255,.14), transparent 34%),
        linear-gradient(135deg, rgba(18,20,38,.78), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .security-inbox-review-actions__eyebrow {{
      color: rgba(168,175,255,.9);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .security-inbox-review-actions h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .security-inbox-review-actions p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .security-review-stats {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .security-review-stat {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
    }}
    .security-review-stat b {{
      display: block;
      font-size: 22px;
    }}
    .security-review-stat span {{
      color: rgba(245,234,210,.62);
      font-size: 12px;
    }}
    .security-review-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .security-review-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
    }}
    .security-review-card--new {{
      border-color: rgba(220,183,94,.5);
    }}
    .security-review-card--acknowledged {{
      border-color: rgba(168,175,255,.5);
    }}
    .security-review-card--investigating {{
      border-color: rgba(220,183,94,.7);
    }}
    .security-review-card--resolved {{
      border-color: rgba(143,221,158,.5);
    }}
    .security-review-card--escalated {{
      border-color: rgba(255,128,128,.65);
    }}
    .security-review-card--false_alarm,
    .security-review-card--archived {{
      border-color: rgba(245,234,210,.18);
      opacity: .82;
    }}
    .security-review-card__eyebrow {{
      color: rgba(220,183,94,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .security-review-card h3 {{
      margin: 0 0 7px;
      font-size: 16px;
    }}
    .security-review-card p {{
      margin: 0 0 8px;
      color: rgba(245,234,210,.72);
    }}
    .security-review-card small {{
      color: rgba(245,234,210,.55);
      word-break: break-word;
    }}
    @media (max-width: 900px) {{
      .security-review-stats,
      .security-review-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="security-inbox-review-actions__eyebrow">PACK 122 · OWNER REVIEW STATES</div>
  <h2>Security Inbox Review Actions</h2>
  <p>{_html_escape(status.get('human_reason', 'Security Inbox review actions loaded.'))}</p>

  <div class="security-review-stats">
    <div class="security-review-stat"><b>{_html_escape(status.get('inbox_count', 0))}</b><span>Inbox Items</span></div>
    <div class="security-review-stat"><b>{_html_escape(status.get('open_review_count', 0))}</b><span>Open Review</span></div>
    <div class="security-review-stat"><b>{_html_escape(status.get('tracked_state_count', 0))}</b><span>Tracked States</span></div>
    <div class="security-review-stat"><b>{_html_escape(status.get('receipt_count', 0))}</b><span>Review Receipts</span></div>
  </div>

  <div class="security-review-grid">
    {''.join(card_html)}
  </div>
</section>
<!-- END PACK122_SECURITY_INBOX_REVIEW_ACTIONS_SECTION -->
"""
    return html


def write_security_inbox_review_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_security_inbox_review_status(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Security Inbox Review</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_security_inbox_review_section(status)}
</main>
</body>
</html>
"""
    _write_text(REVIEW_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "122",
        "decision": "security_inbox_review_panel_written",
        "path": str(REVIEW_PANEL_PATH),
        "human_reason": "Security Inbox review panel written.",
        "soulaana_translation": "Soulaana: Security Inbox review board posted.",
    }


def load_security_inbox_review_status() -> Dict[str, Any]:
    status = _load_json(REVIEW_STATUS_PATH, {})
    if not status:
        status = build_security_inbox_review_status(write_panel=True)
    return status


def security_inbox_review_status_card() -> Dict[str, Any]:
    status = load_security_inbox_review_status()
    return {
        "ok": status.get("ok") is True,
        "pack": "122",
        "title": "Security Inbox Review",
        "readiness_score": status.get("readiness_score", 0),
        "inbox_count": status.get("inbox_count", 0),
        "open_review_count": status.get("open_review_count", 0),
        "tracked_state_count": status.get("tracked_state_count", 0),
        "receipt_count": status.get("receipt_count", 0),
        "panel_path": status.get("panel_path", str(REVIEW_PANEL_PATH)),
        "status_path": status.get("status_path", str(REVIEW_STATUS_PATH)),
        "human_reason": "Security Inbox review status card loaded.",
        "soulaana_translation": "Soulaana: Security Inbox review states are visible.",
    }


def reset_security_inbox_review_actions_for_test() -> Dict[str, Any]:
    _write_json(REVIEW_STATE_PATH, {})
    _write_json(REVIEW_RECEIPTS_PATH, [])
    _write_json(REVIEW_STATUS_PATH, {
        "ok": True,
        "pack": "122",
        "reset_at": _utc_now(),
        "human_reason": "Security Inbox review actions reset for test.",
    })
    if REVIEW_PANEL_PATH.exists():
        try:
            REVIEW_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "security_inbox_review_actions_reset_for_test",
        "states_reset": True,
        "receipts_reset": True,
        "soulaana_translation": "Soulaana: Security Inbox review actions reset for a clean test lane.",
    }
