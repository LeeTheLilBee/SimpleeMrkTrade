
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OWNER_ACTION_ASSIGNMENTS_PATH = DATA_DIR / "owner_action_assignments.json"
OWNER_ACTION_ASSIGNMENT_RECEIPTS_PATH = DATA_DIR / "owner_action_assignment_receipts.json"
OWNER_ACTION_ASSIGNMENTS_STATUS_PATH = DATA_DIR / "owner_action_assignments_status.json"
OWNER_ACTION_ASSIGNMENTS_PANEL_PATH = DATA_DIR / "owner_action_assignments_panel.html"
OWNER_ACTION_ASSIGNMENT_DETAIL_PANEL_PATH = DATA_DIR / "owner_action_assignment_detail_panel.html"

OWNER_ACTION_ALLOWED_ASSIGNMENT_STATUSES = {
    "unassigned",
    "assigned",
    "accepted",
    "in_progress",
    "waiting",
    "completed",
    "reassigned",
    "declined",
}

OWNER_ACTION_CLOSED_ASSIGNMENT_STATUSES = {
    "completed",
    "declined",
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


def _redact_string(value: str) -> str:
    text = str(value or "")
    lowered = text.lower()

    redaction_triggers = [
        "should_not_survive",
        "tower_keycard=",
        "bearer ",
        "ghp_",
        "sk_live_",
        "-----begin private key-----",
        "access_token=",
        "refresh_token=",
        "api_key=",
        "password=",
        "private_key=",
    ]

    if any(trigger in lowered for trigger in redaction_triggers):
        return "[REDACTED_OWNER_ACTION_ASSIGNMENT_VALUE]"

    return text


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

            if isinstance(redacted_item, dict) and "__redacted_owner_action_assignment_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_owner_action_assignment_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_owner_action_assignment_field_count__", None)

            if isinstance(redacted_item, str) and redacted_item == "[REDACTED_OWNER_ACTION_ASSIGNMENT_VALUE]":
                redacted_count += 1

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_owner_action_assignment_field_count__"] = redacted_count

        return clean

    if isinstance(value, list):
        return [_redact(item) for item in value]

    if isinstance(value, str):
        return _redact_string(value)

    return value


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def _num(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        try:
            return int(float(value))
        except Exception:
            return default


def _load_assignments() -> Dict[str, Dict[str, Any]]:
    data = _load_json(OWNER_ACTION_ASSIGNMENTS_PATH, {})
    return data if isinstance(data, dict) else {}


def _save_assignments(assignments: Dict[str, Dict[str, Any]]) -> None:
    _write_json(OWNER_ACTION_ASSIGNMENTS_PATH, assignments)


def _load_assignment_receipts() -> List[Dict[str, Any]]:
    data = _load_json(OWNER_ACTION_ASSIGNMENT_RECEIPTS_PATH, [])
    return [item for item in data if isinstance(item, dict)] if isinstance(data, list) else []


def _save_assignment_receipts(receipts: List[Dict[str, Any]]) -> None:
    _write_json(OWNER_ACTION_ASSIGNMENT_RECEIPTS_PATH, receipts[-1000:])


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


def _sort_assignment_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        [item for item in rows if isinstance(item, dict)],
        key=lambda item: str(item.get("updated_at", item.get("created_at", ""))),
        reverse=True,
    )


def assign_owner_action(
    *,
    action_id: str,
    assigned_to: str,
    assigned_role: str = "owner",
    assignment_status: str = "assigned",
    actor_user_id: str = "owner_solice",
    assignment_reason: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    action_id = str(action_id or "").strip()
    assigned_to = str(assigned_to or "").strip()
    assigned_role = str(assigned_role or "owner").strip() or "owner"
    assignment_status = _norm(assignment_status) or "assigned"
    actor_user_id = str(actor_user_id or "owner_solice").strip() or "owner_solice"
    assignment_reason = str(assignment_reason or "").strip()
    metadata = metadata if isinstance(metadata, dict) else {}

    if not action_id:
        return {
            "ok": False,
            "pack": "144",
            "decision": "owner_action_assignment_rejected",
            "reason_code": "missing_action_id",
            "human_reason": "Owner action ID is required before assigning an action.",
            "required_actions": ["provide_action_id"],
        }

    if not assigned_to:
        return {
            "ok": False,
            "pack": "144",
            "decision": "owner_action_assignment_rejected",
            "reason_code": "missing_assigned_to",
            "human_reason": "Assigned-to value is required.",
            "required_actions": ["provide_assigned_to"],
        }

    if assignment_status not in OWNER_ACTION_ALLOWED_ASSIGNMENT_STATUSES:
        return {
            "ok": False,
            "pack": "144",
            "decision": "owner_action_assignment_rejected",
            "reason_code": "invalid_assignment_status",
            "allowed_assignment_statuses": sorted(OWNER_ACTION_ALLOWED_ASSIGNMENT_STATUSES),
            "human_reason": "Owner action assignment status is not allowed.",
            "required_actions": ["choose_allowed_assignment_status"],
        }

    action = _find_owner_action(action_id)
    if not action:
        return {
            "ok": False,
            "pack": "144",
            "decision": "owner_action_assignment_rejected",
            "reason_code": "owner_action_not_found",
            "action_id": action_id,
            "human_reason": "Owner action was not found in the current command queue.",
            "required_actions": ["refresh_owner_action_center_or_choose_existing_action"],
        }

    now = _utc_now()
    assignments = _load_assignments()
    prior = assignments.get(action_id) if isinstance(assignments.get(action_id), dict) else {}

    prior_assigned_to = prior.get("assigned_to", "")
    prior_assigned_role = prior.get("assigned_role", "")
    prior_assignment_status = prior.get("assignment_status", "unassigned") if prior else "unassigned"

    assignment = {
        "assignment_id": prior.get("assignment_id") or "owner_action_assignment_" + _fingerprint({
            "action_id": action_id,
            "created_at": now,
        })[:18],
        "pack": "144",
        "action_id": action_id,
        "action_type": action.get("action_type", ""),
        "title": action.get("title", ""),
        "href": action.get("href", ""),
        "assigned_to": assigned_to,
        "assigned_role": assigned_role,
        "assignment_status": assignment_status,
        "assignment_reason": assignment_reason,
        "created_at": prior.get("created_at") or now,
        "updated_at": now,
        "updated_by": actor_user_id,
        "is_closed": assignment_status in OWNER_ACTION_CLOSED_ASSIGNMENT_STATUSES,
        "metadata": metadata,
    }

    assignment = _redact(assignment)
    scan = _safe_scan(assignment)
    assignment["no_secret_leakage"] = scan.get("ok") is True
    assignment["assignment_fingerprint"] = _fingerprint(assignment)

    assignments[action_id] = assignment
    _save_assignments(assignments)

    receipt = {
        "receipt_id": "owner_action_assignment_receipt_" + _fingerprint({
            "action_id": action_id,
            "assigned_to": assigned_to,
            "assigned_role": assigned_role,
            "assignment_status": assignment_status,
            "actor_user_id": actor_user_id,
            "created_at": now,
        })[:18],
        "pack": "144",
        "event_type": "owner_action_assignment_updated",
        "assignment_id": assignment.get("assignment_id"),
        "action_id": action_id,
        "action_type": action.get("action_type", ""),
        "title": action.get("title", ""),
        "prior_assigned_to": prior_assigned_to,
        "assigned_to": assigned_to,
        "prior_assigned_role": prior_assigned_role,
        "assigned_role": assigned_role,
        "prior_assignment_status": prior_assignment_status,
        "assignment_status": assignment_status,
        "actor_user_id": actor_user_id,
        "assignment_reason": assignment_reason,
        "assignment_fingerprint": assignment.get("assignment_fingerprint"),
        "metadata": metadata,
        "created_at": now,
    }

    receipt = _redact(receipt)
    receipt_scan = _safe_scan(receipt)
    receipt["no_secret_leakage"] = receipt_scan.get("ok") is True
    receipt["receipt_fingerprint"] = _fingerprint(receipt)

    receipts = _load_assignment_receipts()
    receipts.append(receipt)
    _save_assignment_receipts(receipts)

    result = {
        "ok": True,
        "pack": "144",
        "decision": "owner_action_assignment_updated",
        "assignment_id": assignment.get("assignment_id"),
        "receipt_id": receipt.get("receipt_id"),
        "action_id": action_id,
        "assignment": assignment,
        "receipt": receipt,
        "no_secret_leakage": assignment.get("no_secret_leakage") is True and receipt.get("no_secret_leakage") is True,
        "human_reason": "Owner action assignment updated and receipt saved.",
        "soulaana_translation": "Soulaana: Owner command assignment updated and receipt sealed.",
    }

    result = _redact(result)
    result_scan = _safe_scan(result)
    result["no_secret_leakage"] = result.get("no_secret_leakage") is True and result_scan.get("ok") is True
    return result


def _assignment_matches(
    assignment: Dict[str, Any],
    *,
    action_id: str = "",
    assigned_to: str = "",
    assigned_role: str = "",
    assignment_status: str = "",
) -> bool:
    if not isinstance(assignment, dict):
        return False

    if action_id and _norm(assignment.get("action_id")) != action_id:
        return False

    if assigned_to and _norm(assignment.get("assigned_to")) != assigned_to:
        return False

    if assigned_role and _norm(assignment.get("assigned_role")) != assigned_role:
        return False

    if assignment_status and _norm(assignment.get("assignment_status")) != assignment_status:
        return False

    return True


def build_owner_action_assignments_status(
    *,
    action_id: str = "",
    assigned_to: str = "",
    assigned_role: str = "",
    assignment_status: str = "",
    top_only: bool = False,
    limit: int = 80,
    write_panel: bool = True,
) -> Dict[str, Any]:
    assignments_map = _load_assignments()
    receipts = _load_assignment_receipts()
    actions = _load_owner_actions()

    rows = [value for value in assignments_map.values() if isinstance(value, dict)]

    action_id_norm = _norm(action_id)
    assigned_to_norm = _norm(assigned_to)
    assigned_role_norm = _norm(assigned_role)
    assignment_status_norm = _norm(assignment_status)

    try:
        limit_int = int(limit)
    except Exception:
        limit_int = 80
    limit_int = max(1, min(limit_int, 500))

    filtered = [
        row for row in rows
        if _assignment_matches(
            row,
            action_id=action_id_norm,
            assigned_to=assigned_to_norm,
            assigned_role=assigned_role_norm,
            assignment_status=assignment_status_norm,
        )
    ]

    filtered = _sort_assignment_rows(filtered)

    if top_only:
        filtered = filtered[:1]

    filtered = filtered[:limit_int]

    by_assigned_to: Dict[str, int] = {}
    by_assigned_role: Dict[str, int] = {}
    by_assignment_status: Dict[str, int] = {}
    by_action_type: Dict[str, int] = {}

    for row in rows:
        if not isinstance(row, dict):
            continue

        at = str(row.get("assigned_to", "") or "unknown")
        role = str(row.get("assigned_role", "") or "unknown")
        status = _norm(row.get("assignment_status")) or "unknown"
        action_type_value = str(row.get("action_type", "") or "unknown")

        by_assigned_to[at] = by_assigned_to.get(at, 0) + 1
        by_assigned_role[role] = by_assigned_role.get(role, 0) + 1
        by_assignment_status[status] = by_assignment_status.get(status, 0) + 1
        by_action_type[action_type_value] = by_action_type.get(action_type_value, 0) + 1

    assigned_action_ids = {str(row.get("action_id", "")) for row in rows if isinstance(row, dict)}
    unassigned_count = len([
        action for action in actions
        if isinstance(action, dict) and str(action.get("action_id", "")) not in assigned_action_ids
    ])

    top_assignment = filtered[0] if filtered else {}

    status_payload = {
        "ok": True,
        "pack": "144",
        "status": "passed",
        "created_at": _utc_now(),
        "status_path": str(OWNER_ACTION_ASSIGNMENTS_STATUS_PATH),
        "panel_path": str(OWNER_ACTION_ASSIGNMENTS_PANEL_PATH),
        "action_count": len(actions),
        "base_assignment_count": len(rows),
        "filtered_assignment_count": len(filtered),
        "unassigned_action_count": unassigned_count,
        "receipt_count": len(receipts),
        "top_assignment": top_assignment,
        "assignments": filtered,
        "active_filters": {
            "action_id": action_id_norm,
            "assigned_to": assigned_to_norm,
            "assigned_role": assigned_role_norm,
            "assignment_status": assignment_status_norm,
            "top_only": bool(top_only),
            "limit": limit_int,
        },
        "filter_options": {
            "assigned_to": by_assigned_to,
            "assigned_role": by_assigned_role,
            "assignment_status": by_assignment_status,
            "action_type": by_action_type,
        },
        "allowed_assignment_statuses": sorted(OWNER_ACTION_ALLOWED_ASSIGNMENT_STATUSES),
        "closed_assignment_statuses": sorted(OWNER_ACTION_CLOSED_ASSIGNMENT_STATUSES),
        "readiness_score": 100,
        "human_reason": "Owner Action assignment layer is ready.",
        "soulaana_translation": "Soulaana: Owner commands can now be assigned and tracked by responsible person or role.",
    }

    status_payload = _redact(status_payload)
    scan = _safe_scan(status_payload)
    status_payload["no_secret_leakage"] = scan.get("ok") is True
    status_payload["leakage_scan"] = scan
    status_payload["status_fingerprint"] = _fingerprint(status_payload)

    _write_json(OWNER_ACTION_ASSIGNMENTS_STATUS_PATH, status_payload)

    if write_panel:
        write_owner_action_assignments_panel(status_payload)

    return status_payload


def build_owner_action_assignment_detail(
    *,
    action_id: str = "",
    assignment_id: str = "",
    write_panel: bool = True,
) -> Dict[str, Any]:
    action_id_norm = _norm(action_id)
    assignment_id_norm = _norm(assignment_id)
    assignments_map = _load_assignments()
    receipts = _load_assignment_receipts()

    assignment = {}

    if action_id_norm:
        for row in assignments_map.values():
            if isinstance(row, dict) and _norm(row.get("action_id")) == action_id_norm:
                assignment = row
                break
    elif assignment_id_norm:
        for row in assignments_map.values():
            if isinstance(row, dict) and _norm(row.get("assignment_id")) == assignment_id_norm:
                assignment = row
                break
    else:
        rows = _sort_assignment_rows([row for row in assignments_map.values() if isinstance(row, dict)])
        if rows:
            assignment = rows[0]

    found = bool(assignment)
    assignment_receipts = []

    if found:
        for receipt in receipts:
            if (
                _norm(receipt.get("assignment_id")) == _norm(assignment.get("assignment_id"))
                or _norm(receipt.get("action_id")) == _norm(assignment.get("action_id"))
            ):
                assignment_receipts.append(receipt)

    detail = {
        "ok": found,
        "pack": "144",
        "status": "passed" if found else "not_found",
        "requested_action_id": str(action_id or ""),
        "requested_assignment_id": str(assignment_id or ""),
        "found_action_id": assignment.get("action_id", "") if found else "",
        "found_assignment_id": assignment.get("assignment_id", "") if found else "",
        "assignment": assignment if found else {},
        "receipts": _sort_assignment_rows(assignment_receipts),
        "detail": {
            "assignment_id": assignment.get("assignment_id", "") if found else "",
            "action_id": assignment.get("action_id", "") if found else "",
            "action_type": assignment.get("action_type", "") if found else "",
            "title": assignment.get("title", "") if found else "",
            "assigned_to": assignment.get("assigned_to", "") if found else "",
            "assigned_role": assignment.get("assigned_role", "") if found else "",
            "assignment_status": assignment.get("assignment_status", "") if found else "",
            "assignment_reason": assignment.get("assignment_reason", "") if found else "",
            "updated_by": assignment.get("updated_by", "") if found else "",
            "created_at": assignment.get("created_at", "") if found else "",
            "updated_at": assignment.get("updated_at", "") if found else "",
            "is_closed": assignment.get("is_closed") is True if found else False,
            "receipt_count": len(assignment_receipts),
            "assignment_fingerprint": assignment.get("assignment_fingerprint", "") if found else "",
            "no_secret_leakage": assignment.get("no_secret_leakage") is True if found else False,
        },
        "readiness_score": 100 if found else 80,
        "human_reason": (
            "Owner Action assignment detail loaded."
            if found
            else "Owner Action assignment was not found."
        ),
        "soulaana_translation": (
            "Soulaana: This assignment shows who owns the command."
            if found
            else "Soulaana: I could not find that assignment."
        ),
    }

    detail = _redact(detail)
    scan = _safe_scan(detail)
    detail["no_secret_leakage"] = scan.get("ok") is True
    detail["leakage_scan"] = scan
    detail["status_fingerprint"] = _fingerprint(detail)

    if write_panel:
        write_owner_action_assignment_detail_panel(detail)

    return detail


def render_owner_action_assignments_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_owner_action_assignments_status(write_panel=False)
    assignments = status.get("assignments", []) if isinstance(status.get("assignments"), list) else []
    options = status.get("filter_options", {}) if isinstance(status.get("filter_options"), dict) else {}
    active = status.get("active_filters", {}) if isinstance(status.get("active_filters"), dict) else {}

    option_cards = []
    for label, mapping in options.items():
        if not isinstance(mapping, dict):
            continue

        chips = []
        for key, count in sorted(mapping.items(), key=lambda item: str(item[0])):
            chips.append(f"<span>{_html_escape(key)} · {_html_escape(count)}</span>")

        option_cards.append(f"""
        <article class="owner-action-assignment-option">
          <h3>{_html_escape(label)}</h3>
          <div>{''.join(chips)}</div>
        </article>
        """)

    assignment_cards = []
    for assignment in assignments[:24]:
        if not isinstance(assignment, dict):
            continue

        assignment_cards.append(f"""
        <article class="owner-action-assignment-card">
          <div class="owner-action-assignment-card__eyebrow">{_html_escape(assignment.get('assignment_status', 'assigned'))}</div>
          <h3>{_html_escape(assignment.get('title', 'Owner Action'))}</h3>
          <p>{_html_escape(assignment.get('assigned_to', ''))} · {_html_escape(assignment.get('assigned_role', ''))}</p>
          <small>{_html_escape(assignment.get('assignment_reason', ''))}</small>
          <code>{_html_escape(assignment.get('assignment_id', ''))}</code>
        </article>
        """)

    if not assignment_cards:
        assignment_cards.append("""
        <article class="owner-action-assignment-card">
          <div class="owner-action-assignment-card__eyebrow">empty</div>
          <h3>No assignments</h3>
          <p>Assignments will appear after an owner action is assigned.</p>
          <small>Receipts are generated on assignment.</small>
        </article>
        """)

    html = f"""
<!-- PACK144_OWNER_ACTION_ASSIGNMENTS_SECTION -->
<section class="owner-action-assignments" data-pack="144">
  <style>
    .owner-action-assignments {{
      margin: 24px 0;
      border: 1px solid rgba(168,175,255,.42);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top right, rgba(168,175,255,.14), transparent 34%),
        linear-gradient(135deg, rgba(22,20,48,.86), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .owner-action-assignments__eyebrow {{
      color: rgba(168,175,255,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-action-assignments h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .owner-action-assignments p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .owner-action-assignments-active {{
      margin-top: 12px;
      border: 1px solid rgba(245,234,210,.14);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
      color: rgba(245,234,210,.72);
      font-size: 12px;
    }}
    .owner-action-assignment-options,
    .owner-action-assignment-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-assignment-option,
    .owner-action-assignment-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
    }}
    .owner-action-assignment-option h3,
    .owner-action-assignment-card h3 {{
      margin: 0 0 8px;
      font-size: 16px;
    }}
    .owner-action-assignment-option span {{
      display: inline-flex;
      margin: 3px;
      border: 1px solid rgba(168,175,255,.22);
      border-radius: 999px;
      padding: 5px 8px;
      color: rgba(245,234,210,.70);
      font-size: 11px;
    }}
    .owner-action-assignment-card__eyebrow {{
      color: rgba(168,175,255,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .owner-action-assignment-card small,
    .owner-action-assignment-card code {{
      display: block;
      color: rgba(245,234,210,.55);
      margin-top: 8px;
      word-break: break-word;
    }}
    .owner-action-assignment-card code {{
      font-size: 11px;
      color: rgba(168,175,255,.88);
    }}
    @media (max-width: 1000px) {{
      .owner-action-assignment-options,
      .owner-action-assignment-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="owner-action-assignments__eyebrow">PACK 144 · OWNER ACTION ASSIGNMENTS</div>
  <h2>Owner Action Assignments</h2>
  <p>{_html_escape(status.get('human_reason', 'Owner Action assignments loaded.'))}</p>

  <div class="owner-action-assignments-active">
    <strong>Actions:</strong> {_html_escape(status.get('action_count', 0))}<br>
    <strong>Assignments:</strong> {_html_escape(status.get('base_assignment_count', 0))}<br>
    <strong>Filtered assignments:</strong> {_html_escape(status.get('filtered_assignment_count', 0))}<br>
    <strong>Unassigned actions:</strong> {_html_escape(status.get('unassigned_action_count', 0))}<br>
    <strong>Receipts:</strong> {_html_escape(status.get('receipt_count', 0))}<br>
    <strong>Active filters:</strong> {_html_escape(active)}
  </div>

  <div class="owner-action-assignment-options">
    {''.join(option_cards)}
  </div>

  <div class="owner-action-assignment-grid">
    {''.join(assignment_cards)}
  </div>
</section>
<!-- END PACK144_OWNER_ACTION_ASSIGNMENTS_SECTION -->
"""
    return html


def render_owner_action_assignment_detail_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_owner_action_assignment_detail(write_panel=False)
    detail = status.get("detail", {}) if isinstance(status.get("detail"), dict) else {}

    html = f"""
<!-- PACK144_OWNER_ACTION_ASSIGNMENT_DETAIL_SECTION -->
<section class="owner-action-assignment-detail" data-pack="144-detail">
  <style>
    .owner-action-assignment-detail {{
      margin: 24px 0;
      border: 1px solid rgba(143,221,158,.42);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top right, rgba(143,221,158,.14), transparent 34%),
        linear-gradient(135deg, rgba(10,34,25,.86), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .owner-action-assignment-detail__eyebrow {{
      color: rgba(143,221,158,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-action-assignment-detail h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .owner-action-assignment-detail p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .owner-action-assignment-detail-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-assignment-detail-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
    }}
    .owner-action-assignment-detail-card span {{
      display: block;
      color: rgba(143,221,158,.72);
      text-transform: uppercase;
      letter-spacing: .11em;
      font-size: 10px;
      margin-bottom: 6px;
    }}
    .owner-action-assignment-detail-card b {{
      display: block;
      color: #f5ead2;
      font-size: 14px;
      word-break: break-word;
    }}
    .owner-action-assignment-detail-reason {{
      margin-top: 14px;
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 14px;
      background: rgba(255,255,255,.04);
      color: rgba(245,234,210,.78);
      line-height: 1.5;
    }}
    @media (max-width: 1000px) {{
      .owner-action-assignment-detail-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="owner-action-assignment-detail__eyebrow">PACK 144 · ASSIGNMENT DETAIL</div>
  <h2>{_html_escape(detail.get('assignment_status', 'Assignment Detail'))}</h2>
  <p>{_html_escape(status.get('human_reason', 'Owner Action assignment detail loaded.'))}</p>

  <div class="owner-action-assignment-detail-grid">
    <article class="owner-action-assignment-detail-card"><span>Assignment</span><b>{_html_escape(detail.get('assignment_id', ''))}</b></article>
    <article class="owner-action-assignment-detail-card"><span>Action</span><b>{_html_escape(detail.get('action_type', ''))}</b></article>
    <article class="owner-action-assignment-detail-card"><span>Assigned To</span><b>{_html_escape(detail.get('assigned_to', ''))}</b></article>
    <article class="owner-action-assignment-detail-card"><span>Role</span><b>{_html_escape(detail.get('assigned_role', ''))}</b></article>
    <article class="owner-action-assignment-detail-card"><span>Status</span><b>{_html_escape(detail.get('assignment_status', ''))}</b></article>
    <article class="owner-action-assignment-detail-card"><span>Updated By</span><b>{_html_escape(detail.get('updated_by', ''))}</b></article>
    <article class="owner-action-assignment-detail-card"><span>Receipts</span><b>{_html_escape(detail.get('receipt_count', 0))}</b></article>
    <article class="owner-action-assignment-detail-card"><span>No Secrets</span><b>{_html_escape(detail.get('no_secret_leakage', False))}</b></article>
  </div>

  <div class="owner-action-assignment-detail-reason">
    {_html_escape(detail.get('assignment_reason', ''))}
  </div>
</section>
<!-- END PACK144_OWNER_ACTION_ASSIGNMENT_DETAIL_SECTION -->
"""
    return html


def write_owner_action_assignments_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_owner_action_assignments_status(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Owner Action Assignments</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_owner_action_assignments_section(status)}
</main>
</body>
</html>
"""
    _write_text(OWNER_ACTION_ASSIGNMENTS_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "144",
        "decision": "owner_action_assignments_panel_written",
        "path": str(OWNER_ACTION_ASSIGNMENTS_PANEL_PATH),
        "human_reason": "Owner Action Assignments panel written.",
        "soulaana_translation": "Soulaana: Owner action assignments board posted.",
    }


def write_owner_action_assignment_detail_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_owner_action_assignment_detail(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Owner Action Assignment Detail</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_owner_action_assignment_detail_section(status)}
</main>
</body>
</html>
"""
    _write_text(OWNER_ACTION_ASSIGNMENT_DETAIL_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "144",
        "decision": "owner_action_assignment_detail_panel_written",
        "path": str(OWNER_ACTION_ASSIGNMENT_DETAIL_PANEL_PATH),
        "human_reason": "Owner Action Assignment detail panel written.",
        "soulaana_translation": "Soulaana: Owner action assignment detail card posted.",
    }


def load_owner_action_assignments_status() -> Dict[str, Any]:
    data = _load_json(OWNER_ACTION_ASSIGNMENTS_STATUS_PATH, {})
    if not data:
        data = build_owner_action_assignments_status(write_panel=True)
    return data if isinstance(data, dict) else {}


def owner_action_assignments_status_card() -> Dict[str, Any]:
    status = load_owner_action_assignments_status()
    top = status.get("top_assignment", {}) if isinstance(status.get("top_assignment"), dict) else {}

    return {
        "ok": status.get("ok") is True,
        "pack": "144",
        "title": "Owner Action Assignments",
        "readiness_score": status.get("readiness_score", 0),
        "action_count": status.get("action_count", 0),
        "base_assignment_count": status.get("base_assignment_count", 0),
        "filtered_assignment_count": status.get("filtered_assignment_count", 0),
        "unassigned_action_count": status.get("unassigned_action_count", 0),
        "receipt_count": status.get("receipt_count", 0),
        "top_assignment_id": top.get("assignment_id"),
        "top_assigned_to": top.get("assigned_to"),
        "top_assigned_role": top.get("assigned_role"),
        "top_assignment_status": top.get("assignment_status"),
        "panel_path": status.get("panel_path", str(OWNER_ACTION_ASSIGNMENTS_PANEL_PATH)),
        "status_path": status.get("status_path", str(OWNER_ACTION_ASSIGNMENTS_STATUS_PATH)),
        "human_reason": "Owner Action Assignments status card loaded.",
        "soulaana_translation": "Soulaana: Owner action assignments are visible.",
    }


def reset_owner_action_assignments_for_test() -> Dict[str, Any]:
    _write_json(OWNER_ACTION_ASSIGNMENTS_PATH, {})
    _write_json(OWNER_ACTION_ASSIGNMENT_RECEIPTS_PATH, [])
    _write_json(OWNER_ACTION_ASSIGNMENTS_STATUS_PATH, {
        "ok": True,
        "pack": "144",
        "reset_at": _utc_now(),
        "human_reason": "Owner Action Assignments reset for test.",
    })

    if OWNER_ACTION_ASSIGNMENTS_PANEL_PATH.exists():
        try:
            OWNER_ACTION_ASSIGNMENTS_PANEL_PATH.unlink()
        except Exception:
            pass

    if OWNER_ACTION_ASSIGNMENT_DETAIL_PANEL_PATH.exists():
        try:
            OWNER_ACTION_ASSIGNMENT_DETAIL_PANEL_PATH.unlink()
        except Exception:
            pass

    return {
        "ok": True,
        "decision": "owner_action_assignments_reset_for_test",
        "soulaana_translation": "Soulaana: Owner action assignments reset for a clean test lane.",
    }
