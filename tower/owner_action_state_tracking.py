
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OWNER_ACTION_STATE_PATH = DATA_DIR / "owner_action_states.json"
OWNER_ACTION_STATE_RECEIPTS_PATH = DATA_DIR / "owner_action_state_receipts.json"
OWNER_ACTION_STATE_STATUS_PATH = DATA_DIR / "owner_action_state_status.json"
OWNER_ACTION_STATE_PANEL_PATH = DATA_DIR / "owner_action_state_panel.html"

OWNER_ACTION_ALLOWED_STATES = {
    "open",
    "acknowledged",
    "investigating",
    "resolved",
    "archived",
    "false_alarm",
}

OWNER_ACTION_CLOSED_STATES = {
    "resolved",
    "archived",
    "false_alarm",
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
        data = json.loads(path.read_text(encoding="utf-8"))
        return data
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

            if isinstance(redacted_item, dict) and "__redacted_owner_action_state_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_owner_action_state_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_owner_action_state_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_owner_action_state_field_count__"] = redacted_count
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
            return "[REDACTED_OWNER_ACTION_STATE_VALUE]"
        return value

    return value


def _load_states() -> Dict[str, Any]:
    data = _load_json(OWNER_ACTION_STATE_PATH, {})
    return data if isinstance(data, dict) else {}


def _save_states(states: Dict[str, Any]) -> None:
    _write_json(OWNER_ACTION_STATE_PATH, states)


def _load_receipts() -> List[Dict[str, Any]]:
    data = _load_json(OWNER_ACTION_STATE_RECEIPTS_PATH, [])
    return data if isinstance(data, list) else []


def _save_receipts(receipts: List[Dict[str, Any]]) -> None:
    _write_json(OWNER_ACTION_STATE_RECEIPTS_PATH, receipts[-500:])


def _load_owner_actions() -> List[Dict[str, Any]]:
    try:
        from tower.owner_action_center import load_owner_action_center_status
        status = load_owner_action_center_status()
        actions = status.get("actions", []) if isinstance(status.get("actions"), list) else []
        return [action for action in actions if isinstance(action, dict)]
    except Exception:
        return []


def _find_owner_action(action_id: str) -> Dict[str, Any]:
    action_id = str(action_id or "").strip()
    if not action_id:
        return {}

    for action in _load_owner_actions():
        if str(action.get("action_id", "")) == action_id:
            return action

    return {}


def _state_record_for(action_id: str, action: Dict[str, Any] | None = None) -> Dict[str, Any]:
    states = _load_states()
    existing = states.get(action_id)
    if isinstance(existing, dict):
        return existing

    action = action if isinstance(action, dict) else _find_owner_action(action_id)

    return {
        "action_id": action_id,
        "current_state": "open",
        "prior_state": "",
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
        "last_actor_user_id": "tower_system",
        "last_reason": "Initial owner action state.",
        "action_type": action.get("action_type", "") if isinstance(action, dict) else "",
        "title": action.get("title", "") if isinstance(action, dict) else "",
        "href": action.get("href", "") if isinstance(action, dict) else "",
    }


def apply_owner_action_state(
    *,
    action_id: str,
    new_state: str,
    actor_user_id: str = "owner_solice",
    reason: str = "",
    note: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    action_id = str(action_id or "").strip()
    new_state = str(new_state or "").strip().lower()
    actor_user_id = str(actor_user_id or "owner_solice").strip() or "owner_solice"
    reason = str(reason or "").strip()
    note = str(note or "").strip()
    metadata = metadata if isinstance(metadata, dict) else {}

    if not action_id:
        return {
            "ok": False,
            "pack": "141",
            "decision": "owner_action_state_rejected",
            "reason_code": "missing_action_id",
            "human_reason": "Owner action ID is required.",
            "required_actions": ["provide_action_id"],
        }

    if new_state not in OWNER_ACTION_ALLOWED_STATES:
        return {
            "ok": False,
            "pack": "141",
            "decision": "owner_action_state_rejected",
            "reason_code": "invalid_owner_action_state",
            "allowed_states": sorted(OWNER_ACTION_ALLOWED_STATES),
            "human_reason": "Owner action state is not allowed.",
            "required_actions": ["choose_allowed_owner_action_state"],
        }

    action = _find_owner_action(action_id)
    if not action:
        return {
            "ok": False,
            "pack": "141",
            "decision": "owner_action_state_rejected",
            "reason_code": "owner_action_not_found",
            "action_id": action_id,
            "human_reason": "Owner action was not found in the current command queue.",
            "required_actions": ["refresh_owner_action_center_or_choose_existing_action"],
        }

    states = _load_states()
    record = _state_record_for(action_id, action)
    prior_state = str(record.get("current_state", "open") or "open")

    record.update({
        "action_id": action_id,
        "prior_state": prior_state,
        "current_state": new_state,
        "updated_at": _utc_now(),
        "last_actor_user_id": actor_user_id,
        "last_reason": reason,
        "last_note": note,
        "is_closed": new_state in OWNER_ACTION_CLOSED_STATES,
        "action_type": action.get("action_type", record.get("action_type", "")),
        "title": action.get("title", record.get("title", "")),
        "href": action.get("href", record.get("href", "")),
    })

    record = _redact(record)
    states[action_id] = record
    _save_states(states)

    receipt = {
        "receipt_id": "owner_action_state_" + _fingerprint({
            "action_id": action_id,
            "new_state": new_state,
            "actor_user_id": actor_user_id,
            "timestamp": record.get("updated_at"),
            "reason": reason,
        })[:18],
        "pack": "141",
        "event_type": "owner_action_state_change",
        "action_id": action_id,
        "action_type": action.get("action_type", ""),
        "title": action.get("title", ""),
        "prior_state": prior_state,
        "new_state": new_state,
        "actor_user_id": actor_user_id,
        "reason": reason,
        "note": note,
        "metadata": metadata,
        "created_at": record.get("updated_at"),
    }

    receipt = _redact(receipt)
    receipt_scan = _safe_scan(receipt)
    receipt["no_secret_leakage"] = receipt_scan.get("ok") is True
    receipt["receipt_fingerprint"] = _fingerprint(receipt)

    receipts = _load_receipts()
    receipts.append(receipt)
    _save_receipts(receipts)

    result = {
        "ok": True,
        "pack": "141",
        "decision": "owner_action_state_updated",
        "action_id": action_id,
        "prior_state": prior_state,
        "new_state": new_state,
        "receipt_id": receipt.get("receipt_id"),
        "record": record,
        "no_secret_leakage": receipt.get("no_secret_leakage") is True,
        "human_reason": "Owner action state updated.",
        "soulaana_translation": "Soulaana: Owner command state updated and receipt saved.",
    }

    scan = _safe_scan(result)
    result["no_secret_leakage"] = result.get("no_secret_leakage") is True and scan.get("ok") is True
    return result


def build_owner_action_state_status(write_panel: bool = True) -> Dict[str, Any]:
    actions = _load_owner_actions()
    states = _load_states()
    receipts = _load_receipts()

    by_state: Dict[str, int] = {state: 0 for state in sorted(OWNER_ACTION_ALLOWED_STATES)}
    tracked_action_count = 0

    action_rows: List[Dict[str, Any]] = []

    for action in actions:
        action_id = str(action.get("action_id", "") or "")
        if not action_id:
            continue

        state_record = states.get(action_id)
        state = "open"

        if isinstance(state_record, dict):
            state = str(state_record.get("current_state", "open") or "open")
            tracked_action_count += 1

        if state not in by_state:
            by_state[state] = 0

        by_state[state] += 1

        action_rows.append({
            "action_id": action_id,
            "title": action.get("title", ""),
            "action_type": action.get("action_type", ""),
            "href": action.get("href", ""),
            "state": state,
            "is_closed": state in OWNER_ACTION_CLOSED_STATES,
            "priority_score": action.get("priority_score", 0),
            "severity": action.get("severity", ""),
        })

    open_action_count = len([row for row in action_rows if not row.get("is_closed")])
    closed_action_count = len([row for row in action_rows if row.get("is_closed")])

    status = {
        "ok": True,
        "pack": "141",
        "status": "passed",
        "created_at": _utc_now(),
        "status_path": str(OWNER_ACTION_STATE_STATUS_PATH),
        "panel_path": str(OWNER_ACTION_STATE_PANEL_PATH),
        "action_count": len(action_rows),
        "tracked_action_count": tracked_action_count,
        "open_action_count": open_action_count,
        "closed_action_count": closed_action_count,
        "receipt_count": len(receipts),
        "allowed_states": sorted(OWNER_ACTION_ALLOWED_STATES),
        "closed_states": sorted(OWNER_ACTION_CLOSED_STATES),
        "by_state": by_state,
        "actions": action_rows[:120],
        "recent_receipts": receipts[-20:],
        "readiness_score": 100,
        "human_reason": "Owner Action Center state tracking is ready.",
        "soulaana_translation": "Soulaana: Owner commands can now move through review states.",
    }

    status = _redact(status)
    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(OWNER_ACTION_STATE_STATUS_PATH, status)

    if write_panel:
        write_owner_action_state_panel(status)

    return status


def render_owner_action_state_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_owner_action_state_status(write_panel=False)
    by_state = status.get("by_state", {}) if isinstance(status.get("by_state"), dict) else {}
    actions = status.get("actions", []) if isinstance(status.get("actions"), list) else []

    state_cards = []
    for state, count in sorted(by_state.items(), key=lambda item: str(item[0])):
        state_cards.append(f"""
        <article class="owner-action-state-card">
          <div class="owner-action-state-card__eyebrow">{_html_escape(state)}</div>
          <h3>{_html_escape(count)}</h3>
          <p>Actions</p>
        </article>
        """)

    action_cards = []
    for action in actions[:16]:
        if not isinstance(action, dict):
            continue
        action_cards.append(f"""
        <article class="owner-action-state-row">
          <span>{_html_escape(action.get('state', 'open'))}</span>
          <b>{_html_escape(action.get('title', 'Owner Action'))}</b>
          <small>{_html_escape(action.get('action_type', ''))}</small>
        </article>
        """)

    if not action_cards:
        action_cards.append("""
        <article class="owner-action-state-row">
          <span>empty</span>
          <b>No owner actions found</b>
          <small>Refresh Owner Action Center first.</small>
        </article>
        """)

    html = f"""
<!-- PACK141_OWNER_ACTION_STATE_SECTION -->
<section class="owner-action-state" data-pack="141">
  <style>
    .owner-action-state {{
      margin: 24px 0;
      border: 1px solid rgba(220,183,94,.42);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top right, rgba(220,183,94,.14), transparent 34%),
        linear-gradient(135deg, rgba(54,35,11,.88), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .owner-action-state__eyebrow {{
      color: rgba(220,183,94,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-action-state h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .owner-action-state p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .owner-action-state-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-state-card,
    .owner-action-state-row {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
    }}
    .owner-action-state-card__eyebrow {{
      color: rgba(220,183,94,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .owner-action-state-card h3 {{
      margin: 0 0 6px;
      font-size: 18px;
      word-break: break-word;
    }}
    .owner-action-state-card p {{
      margin: 0;
      color: rgba(245,234,210,.62);
      font-size: 12px;
    }}
    .owner-action-state-list {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-state-row span {{
      display: inline-flex;
      border: 1px solid rgba(220,183,94,.28);
      border-radius: 999px;
      padding: 4px 8px;
      color: rgba(220,183,94,.88);
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-action-state-row b,
    .owner-action-state-row small {{
      display: block;
      word-break: break-word;
    }}
    .owner-action-state-row small {{
      color: rgba(245,234,210,.58);
      margin-top: 4px;
    }}
    @media (max-width: 1000px) {{
      .owner-action-state-grid,
      .owner-action-state-list {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="owner-action-state__eyebrow">PACK 141 · OWNER ACTION STATE TRACKING</div>
  <h2>Owner Action State Tracking</h2>
  <p>{_html_escape(status.get('human_reason', 'Owner Action state tracking loaded.'))}</p>

  <div class="owner-action-state-grid">
    {''.join(state_cards)}
  </div>

  <div class="owner-action-state-list">
    {''.join(action_cards)}
  </div>
</section>
<!-- END PACK141_OWNER_ACTION_STATE_SECTION -->
"""
    return html


def write_owner_action_state_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_owner_action_state_status(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Owner Action State Tracking</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_owner_action_state_section(status)}
</main>
</body>
</html>
"""
    _write_text(OWNER_ACTION_STATE_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "141",
        "decision": "owner_action_state_panel_written",
        "path": str(OWNER_ACTION_STATE_PANEL_PATH),
        "human_reason": "Owner Action State panel written.",
        "soulaana_translation": "Soulaana: Owner action state board posted.",
    }


def owner_action_state_status_card() -> Dict[str, Any]:
    status = build_owner_action_state_status(write_panel=True)
    return {
        "ok": status.get("ok") is True,
        "pack": "141",
        "title": "Owner Action State Tracking",
        "readiness_score": status.get("readiness_score", 0),
        "action_count": status.get("action_count", 0),
        "tracked_action_count": status.get("tracked_action_count", 0),
        "open_action_count": status.get("open_action_count", 0),
        "closed_action_count": status.get("closed_action_count", 0),
        "receipt_count": status.get("receipt_count", 0),
        "status_path": status.get("status_path", str(OWNER_ACTION_STATE_STATUS_PATH)),
        "panel_path": status.get("panel_path", str(OWNER_ACTION_STATE_PANEL_PATH)),
        "human_reason": "Owner Action State status card loaded.",
        "soulaana_translation": "Soulaana: Owner action states are visible.",
    }


def reset_owner_action_state_tracking_for_test() -> Dict[str, Any]:
    _write_json(OWNER_ACTION_STATE_PATH, {})
    _write_json(OWNER_ACTION_STATE_RECEIPTS_PATH, [])
    _write_json(OWNER_ACTION_STATE_STATUS_PATH, {
        "ok": True,
        "pack": "141",
        "reset_at": _utc_now(),
        "human_reason": "Owner Action State tracking reset for test.",
    })
    if OWNER_ACTION_STATE_PANEL_PATH.exists():
        try:
            OWNER_ACTION_STATE_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "owner_action_state_tracking_reset_for_test",
        "soulaana_translation": "Soulaana: Owner action state tracking reset for a clean test lane.",
    }
