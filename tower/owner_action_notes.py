
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OWNER_ACTION_NOTES_PATH = DATA_DIR / "owner_action_notes.json"
OWNER_ACTION_NOTE_RECEIPTS_PATH = DATA_DIR / "owner_action_note_receipts.json"
OWNER_ACTION_NOTES_STATUS_PATH = DATA_DIR / "owner_action_notes_status.json"
OWNER_ACTION_NOTES_PANEL_PATH = DATA_DIR / "owner_action_notes_panel.html"
OWNER_ACTION_NOTE_DETAIL_PANEL_PATH = DATA_DIR / "owner_action_note_detail_panel.html"

OWNER_ACTION_NOTE_ALLOWED_VISIBILITY = {
    "owner_only",
    "admin_visible",
    "system_internal",
}

OWNER_ACTION_NOTE_ALLOWED_TYPES = {
    "general",
    "investigation",
    "resolution",
    "false_alarm",
    "follow_up",
    "risk_context",
    "owner_memory",
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
        return "[REDACTED_OWNER_ACTION_NOTE_VALUE]"

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

            if isinstance(redacted_item, dict) and "__redacted_owner_action_note_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_owner_action_note_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_owner_action_note_field_count__", None)

            if isinstance(redacted_item, str) and redacted_item == "[REDACTED_OWNER_ACTION_NOTE_VALUE]":
                redacted_count += 1

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_owner_action_note_field_count__"] = redacted_count

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


def _load_notes() -> List[Dict[str, Any]]:
    data = _load_json(OWNER_ACTION_NOTES_PATH, [])
    return [item for item in data if isinstance(item, dict)] if isinstance(data, list) else []


def _save_notes(notes: List[Dict[str, Any]]) -> None:
    _write_json(OWNER_ACTION_NOTES_PATH, notes[-1000:])


def _load_note_receipts() -> List[Dict[str, Any]]:
    data = _load_json(OWNER_ACTION_NOTE_RECEIPTS_PATH, [])
    return [item for item in data if isinstance(item, dict)] if isinstance(data, list) else []


def _save_note_receipts(receipts: List[Dict[str, Any]]) -> None:
    _write_json(OWNER_ACTION_NOTE_RECEIPTS_PATH, receipts[-1000:])


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


def _sort_notes(notes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        [item for item in notes if isinstance(item, dict)],
        key=lambda item: str(item.get("created_at", "")),
        reverse=True,
    )


def _sort_receipts(receipts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        [item for item in receipts if isinstance(item, dict)],
        key=lambda item: str(item.get("created_at", "")),
        reverse=True,
    )


def create_owner_action_note(
    *,
    action_id: str,
    note_body: str,
    actor_user_id: str = "owner_solice",
    note_type: str = "general",
    visibility: str = "owner_only",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    action_id = str(action_id or "").strip()
    actor_user_id = str(actor_user_id or "owner_solice").strip() or "owner_solice"
    note_body = str(note_body or "").strip()
    note_type = _norm(note_type) or "general"
    visibility = _norm(visibility) or "owner_only"
    metadata = metadata if isinstance(metadata, dict) else {}

    if not action_id:
        return {
            "ok": False,
            "pack": "143",
            "decision": "owner_action_note_rejected",
            "reason_code": "missing_action_id",
            "human_reason": "Owner action ID is required before saving a note.",
            "required_actions": ["provide_action_id"],
        }

    if not note_body:
        return {
            "ok": False,
            "pack": "143",
            "decision": "owner_action_note_rejected",
            "reason_code": "missing_note_body",
            "human_reason": "Note body is required.",
            "required_actions": ["provide_note_body"],
        }

    if note_type not in OWNER_ACTION_NOTE_ALLOWED_TYPES:
        return {
            "ok": False,
            "pack": "143",
            "decision": "owner_action_note_rejected",
            "reason_code": "invalid_note_type",
            "allowed_note_types": sorted(OWNER_ACTION_NOTE_ALLOWED_TYPES),
            "human_reason": "Owner action note type is not allowed.",
            "required_actions": ["choose_allowed_note_type"],
        }

    if visibility not in OWNER_ACTION_NOTE_ALLOWED_VISIBILITY:
        return {
            "ok": False,
            "pack": "143",
            "decision": "owner_action_note_rejected",
            "reason_code": "invalid_visibility",
            "allowed_visibility": sorted(OWNER_ACTION_NOTE_ALLOWED_VISIBILITY),
            "human_reason": "Owner action note visibility is not allowed.",
            "required_actions": ["choose_allowed_visibility"],
        }

    action = _find_owner_action(action_id)
    if not action:
        return {
            "ok": False,
            "pack": "143",
            "decision": "owner_action_note_rejected",
            "reason_code": "owner_action_not_found",
            "action_id": action_id,
            "human_reason": "Owner action was not found in the current command queue.",
            "required_actions": ["refresh_owner_action_center_or_choose_existing_action"],
        }

    created_at = _utc_now()

    raw_note = {
        "note_id": "owner_action_note_" + _fingerprint({
            "action_id": action_id,
            "note_body": note_body,
            "actor_user_id": actor_user_id,
            "created_at": created_at,
        })[:18],
        "pack": "143",
        "action_id": action_id,
        "action_type": action.get("action_type", ""),
        "title": action.get("title", ""),
        "href": action.get("href", ""),
        "actor_user_id": actor_user_id,
        "note_type": note_type,
        "visibility": visibility,
        "note_body": note_body,
        "metadata": metadata,
        "created_at": created_at,
        "updated_at": created_at,
        "is_deleted": False,
    }

    note = _redact(raw_note)
    note_scan = _safe_scan(note)
    note["no_secret_leakage"] = note_scan.get("ok") is True
    note["note_fingerprint"] = _fingerprint(note)

    notes = _load_notes()
    notes.append(note)
    _save_notes(notes)

    receipt = {
        "receipt_id": "owner_action_note_receipt_" + _fingerprint({
            "note_id": note.get("note_id"),
            "action_id": action_id,
            "actor_user_id": actor_user_id,
            "created_at": created_at,
        })[:18],
        "pack": "143",
        "event_type": "owner_action_note_created",
        "note_id": note.get("note_id"),
        "action_id": action_id,
        "action_type": action.get("action_type", ""),
        "title": action.get("title", ""),
        "actor_user_id": actor_user_id,
        "note_type": note_type,
        "visibility": visibility,
        "created_at": created_at,
        "note_fingerprint": note.get("note_fingerprint"),
        "metadata": metadata,
    }

    receipt = _redact(receipt)
    receipt_scan = _safe_scan(receipt)
    receipt["no_secret_leakage"] = receipt_scan.get("ok") is True
    receipt["receipt_fingerprint"] = _fingerprint(receipt)

    receipts = _load_note_receipts()
    receipts.append(receipt)
    _save_note_receipts(receipts)

    result = {
        "ok": True,
        "pack": "143",
        "decision": "owner_action_note_created",
        "note_id": note.get("note_id"),
        "receipt_id": receipt.get("receipt_id"),
        "action_id": action_id,
        "note": note,
        "receipt": receipt,
        "no_secret_leakage": note.get("no_secret_leakage") is True and receipt.get("no_secret_leakage") is True,
        "human_reason": "Owner action note saved with redaction and receipt.",
        "soulaana_translation": "Soulaana: Owner command note saved and receipt sealed.",
    }

    result = _redact(result)
    scan = _safe_scan(result)
    result["no_secret_leakage"] = result.get("no_secret_leakage") is True and scan.get("ok") is True
    return result


def _note_matches(
    note: Dict[str, Any],
    *,
    note_id: str = "",
    action_id: str = "",
    actor_user_id: str = "",
    note_type: str = "",
    visibility: str = "",
) -> bool:
    if not isinstance(note, dict):
        return False

    if note_id and _norm(note.get("note_id")) != note_id:
        return False

    if action_id and _norm(note.get("action_id")) != action_id:
        return False

    if actor_user_id and _norm(note.get("actor_user_id")) != actor_user_id:
        return False

    if note_type and _norm(note.get("note_type")) != note_type:
        return False

    if visibility and _norm(note.get("visibility")) != visibility:
        return False

    return True


def build_owner_action_notes_status(
    *,
    note_id: str = "",
    action_id: str = "",
    actor_user_id: str = "",
    note_type: str = "",
    visibility: str = "",
    top_only: bool = False,
    limit: int = 80,
    write_panel: bool = True,
) -> Dict[str, Any]:
    notes = _load_notes()
    receipts = _load_note_receipts()

    note_id_norm = _norm(note_id)
    action_id_norm = _norm(action_id)
    actor_norm = _norm(actor_user_id)
    note_type_norm = _norm(note_type)
    visibility_norm = _norm(visibility)

    try:
        limit_int = int(limit)
    except Exception:
        limit_int = 80
    limit_int = max(1, min(limit_int, 500))

    filtered = [
        note for note in notes
        if _note_matches(
            note,
            note_id=note_id_norm,
            action_id=action_id_norm,
            actor_user_id=actor_norm,
            note_type=note_type_norm,
            visibility=visibility_norm,
        )
    ]

    filtered = _sort_notes(filtered)

    if top_only:
        filtered = filtered[:1]

    filtered = filtered[:limit_int]

    by_note_type: Dict[str, int] = {}
    by_visibility: Dict[str, int] = {}
    by_actor: Dict[str, int] = {}
    by_action_type: Dict[str, int] = {}

    for note in notes:
        if not isinstance(note, dict):
            continue

        nt = _norm(note.get("note_type")) or "unknown"
        vis = _norm(note.get("visibility")) or "unknown"
        actor = str(note.get("actor_user_id", "") or "unknown")
        action_type_value = str(note.get("action_type", "") or "unknown")

        by_note_type[nt] = by_note_type.get(nt, 0) + 1
        by_visibility[vis] = by_visibility.get(vis, 0) + 1
        by_actor[actor] = by_actor.get(actor, 0) + 1
        by_action_type[action_type_value] = by_action_type.get(action_type_value, 0) + 1

    top_note = filtered[0] if filtered else {}

    status = {
        "ok": True,
        "pack": "143",
        "status": "passed",
        "created_at": _utc_now(),
        "status_path": str(OWNER_ACTION_NOTES_STATUS_PATH),
        "panel_path": str(OWNER_ACTION_NOTES_PANEL_PATH),
        "base_note_count": len(notes),
        "filtered_note_count": len(filtered),
        "receipt_count": len(receipts),
        "top_note": top_note,
        "notes": filtered,
        "active_filters": {
            "note_id": note_id_norm,
            "action_id": action_id_norm,
            "actor_user_id": actor_norm,
            "note_type": note_type_norm,
            "visibility": visibility_norm,
            "top_only": bool(top_only),
            "limit": limit_int,
        },
        "filter_options": {
            "note_type": by_note_type,
            "visibility": by_visibility,
            "actor_user_id": by_actor,
            "action_type": by_action_type,
        },
        "allowed_note_types": sorted(OWNER_ACTION_NOTE_ALLOWED_TYPES),
        "allowed_visibility": sorted(OWNER_ACTION_NOTE_ALLOWED_VISIBILITY),
        "readiness_score": 100,
        "human_reason": "Owner Action note system is ready.",
        "soulaana_translation": "Soulaana: Owner command notes are saved with redaction and receipts.",
    }

    status = _redact(status)
    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(OWNER_ACTION_NOTES_STATUS_PATH, status)

    if write_panel:
        write_owner_action_notes_panel(status)

    return status


def build_owner_action_note_detail(
    *,
    note_id: str = "",
    write_panel: bool = True,
) -> Dict[str, Any]:
    note_id_norm = _norm(note_id)
    notes = _sort_notes(_load_notes())
    receipts = _sort_receipts(_load_note_receipts())

    note = {}

    if note_id_norm:
        for item in notes:
            if _norm(item.get("note_id")) == note_id_norm:
                note = item
                break
    elif notes:
        note = notes[0]

    found = bool(note)
    note_receipts = []

    if found:
        for receipt in receipts:
            if _norm(receipt.get("note_id")) == _norm(note.get("note_id")):
                note_receipts.append(receipt)

    detail = {
        "ok": found,
        "pack": "143",
        "status": "passed" if found else "not_found",
        "requested_note_id": str(note_id or ""),
        "found_note_id": note.get("note_id", "") if found else "",
        "note": note if found else {},
        "receipts": note_receipts,
        "detail": {
            "note_id": note.get("note_id", "") if found else "",
            "action_id": note.get("action_id", "") if found else "",
            "action_type": note.get("action_type", "") if found else "",
            "title": note.get("title", "") if found else "",
            "actor_user_id": note.get("actor_user_id", "") if found else "",
            "note_type": note.get("note_type", "") if found else "",
            "visibility": note.get("visibility", "") if found else "",
            "note_body": note.get("note_body", "") if found else "",
            "created_at": note.get("created_at", "") if found else "",
            "note_fingerprint": note.get("note_fingerprint", "") if found else "",
            "no_secret_leakage": note.get("no_secret_leakage") is True if found else False,
            "receipt_count": len(note_receipts),
        },
        "readiness_score": 100 if found else 80,
        "human_reason": (
            "Owner Action note detail loaded."
            if found
            else "Owner Action note was not found."
        ),
        "soulaana_translation": (
            "Soulaana: This note is attached to an owner command with a receipt."
            if found
            else "Soulaana: I could not find that owner command note."
        ),
    }

    detail = _redact(detail)
    scan = _safe_scan(detail)
    detail["no_secret_leakage"] = scan.get("ok") is True
    detail["leakage_scan"] = scan
    detail["status_fingerprint"] = _fingerprint(detail)

    if write_panel:
        write_owner_action_note_detail_panel(detail)

    return detail


def render_owner_action_notes_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_owner_action_notes_status(write_panel=False)
    notes = status.get("notes", []) if isinstance(status.get("notes"), list) else []
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
        <article class="owner-action-note-option">
          <h3>{_html_escape(label)}</h3>
          <div>{''.join(chips)}</div>
        </article>
        """)

    note_cards = []
    for note in notes[:24]:
        if not isinstance(note, dict):
            continue

        note_cards.append(f"""
        <article class="owner-action-note-card">
          <div class="owner-action-note-card__eyebrow">{_html_escape(note.get('note_type', 'note'))} · {_html_escape(note.get('visibility', 'owner_only'))}</div>
          <h3>{_html_escape(note.get('title', 'Owner Action'))}</h3>
          <p>{_html_escape(note.get('note_body', ''))}</p>
          <small>{_html_escape(note.get('created_at', ''))}</small>
          <code>{_html_escape(note.get('note_id', ''))}</code>
        </article>
        """)

    if not note_cards:
        note_cards.append("""
        <article class="owner-action-note-card">
          <div class="owner-action-note-card__eyebrow">empty</div>
          <h3>No owner action notes</h3>
          <p>Notes will appear after an owner/admin adds context to an action.</p>
          <small>Redaction runs before save.</small>
        </article>
        """)

    html = f"""
<!-- PACK143_OWNER_ACTION_NOTES_SECTION -->
<section class="owner-action-notes" data-pack="143">
  <style>
    .owner-action-notes {{
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
    .owner-action-notes__eyebrow {{
      color: rgba(220,183,94,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-action-notes h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .owner-action-notes p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .owner-action-notes-active {{
      margin-top: 12px;
      border: 1px solid rgba(245,234,210,.14);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
      color: rgba(245,234,210,.72);
      font-size: 12px;
    }}
    .owner-action-note-options,
    .owner-action-note-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-note-option,
    .owner-action-note-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
    }}
    .owner-action-note-option h3,
    .owner-action-note-card h3 {{
      margin: 0 0 8px;
      font-size: 16px;
    }}
    .owner-action-note-option span {{
      display: inline-flex;
      margin: 3px;
      border: 1px solid rgba(220,183,94,.22);
      border-radius: 999px;
      padding: 5px 8px;
      color: rgba(245,234,210,.70);
      font-size: 11px;
    }}
    .owner-action-note-card__eyebrow {{
      color: rgba(220,183,94,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .owner-action-note-card small,
    .owner-action-note-card code {{
      display: block;
      color: rgba(245,234,210,.55);
      margin-top: 8px;
      word-break: break-word;
    }}
    .owner-action-note-card code {{
      font-size: 11px;
      color: rgba(220,183,94,.88);
    }}
    @media (max-width: 1000px) {{
      .owner-action-note-options,
      .owner-action-note-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="owner-action-notes__eyebrow">PACK 143 · OWNER ACTION NOTES</div>
  <h2>Owner Action Notes</h2>
  <p>{_html_escape(status.get('human_reason', 'Owner Action notes loaded.'))}</p>

  <div class="owner-action-notes-active">
    <strong>Base notes:</strong> {_html_escape(status.get('base_note_count', 0))}<br>
    <strong>Filtered notes:</strong> {_html_escape(status.get('filtered_note_count', 0))}<br>
    <strong>Note receipts:</strong> {_html_escape(status.get('receipt_count', 0))}<br>
    <strong>Active filters:</strong> {_html_escape(active)}
  </div>

  <div class="owner-action-note-options">
    {''.join(option_cards)}
  </div>

  <div class="owner-action-note-grid">
    {''.join(note_cards)}
  </div>
</section>
<!-- END PACK143_OWNER_ACTION_NOTES_SECTION -->
"""
    return html


def render_owner_action_note_detail_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_owner_action_note_detail(write_panel=False)
    detail = status.get("detail", {}) if isinstance(status.get("detail"), dict) else {}

    html = f"""
<!-- PACK143_OWNER_ACTION_NOTE_DETAIL_SECTION -->
<section class="owner-action-note-detail" data-pack="143-detail">
  <style>
    .owner-action-note-detail {{
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
    .owner-action-note-detail__eyebrow {{
      color: rgba(143,221,158,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-action-note-detail h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .owner-action-note-detail p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .owner-action-note-detail-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-note-detail-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
    }}
    .owner-action-note-detail-card span {{
      display: block;
      color: rgba(143,221,158,.72);
      text-transform: uppercase;
      letter-spacing: .11em;
      font-size: 10px;
      margin-bottom: 6px;
    }}
    .owner-action-note-detail-card b {{
      display: block;
      color: #f5ead2;
      font-size: 14px;
      word-break: break-word;
    }}
    .owner-action-note-detail-body {{
      margin-top: 14px;
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 14px;
      background: rgba(255,255,255,.04);
      color: rgba(245,234,210,.78);
      line-height: 1.5;
    }}
    @media (max-width: 1000px) {{
      .owner-action-note-detail-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="owner-action-note-detail__eyebrow">PACK 143 · NOTE DETAIL</div>
  <h2>{_html_escape(detail.get('note_type', 'Note Detail'))}</h2>
  <p>{_html_escape(status.get('human_reason', 'Owner Action note detail loaded.'))}</p>

  <div class="owner-action-note-detail-grid">
    <article class="owner-action-note-detail-card"><span>Note</span><b>{_html_escape(detail.get('note_id', ''))}</b></article>
    <article class="owner-action-note-detail-card"><span>Action</span><b>{_html_escape(detail.get('action_type', ''))}</b></article>
    <article class="owner-action-note-detail-card"><span>Visibility</span><b>{_html_escape(detail.get('visibility', ''))}</b></article>
    <article class="owner-action-note-detail-card"><span>Actor</span><b>{_html_escape(detail.get('actor_user_id', ''))}</b></article>
    <article class="owner-action-note-detail-card"><span>No Secrets</span><b>{_html_escape(detail.get('no_secret_leakage', False))}</b></article>
    <article class="owner-action-note-detail-card"><span>Receipts</span><b>{_html_escape(detail.get('receipt_count', 0))}</b></article>
    <article class="owner-action-note-detail-card"><span>Created</span><b>{_html_escape(detail.get('created_at', ''))}</b></article>
    <article class="owner-action-note-detail-card"><span>Fingerprint</span><b>{_html_escape(detail.get('note_fingerprint', ''))}</b></article>
  </div>

  <div class="owner-action-note-detail-body">
    {_html_escape(detail.get('note_body', ''))}
  </div>
</section>
<!-- END PACK143_OWNER_ACTION_NOTE_DETAIL_SECTION -->
"""
    return html


def write_owner_action_notes_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_owner_action_notes_status(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Owner Action Notes</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_owner_action_notes_section(status)}
</main>
</body>
</html>
"""
    _write_text(OWNER_ACTION_NOTES_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "143",
        "decision": "owner_action_notes_panel_written",
        "path": str(OWNER_ACTION_NOTES_PANEL_PATH),
        "human_reason": "Owner Action Notes panel written.",
        "soulaana_translation": "Soulaana: Owner action notes board posted.",
    }


def write_owner_action_note_detail_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_owner_action_note_detail(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Owner Action Note Detail</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_owner_action_note_detail_section(status)}
</main>
</body>
</html>
"""
    _write_text(OWNER_ACTION_NOTE_DETAIL_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "143",
        "decision": "owner_action_note_detail_panel_written",
        "path": str(OWNER_ACTION_NOTE_DETAIL_PANEL_PATH),
        "human_reason": "Owner Action Note detail panel written.",
        "soulaana_translation": "Soulaana: Owner action note detail card posted.",
    }


def load_owner_action_notes_status() -> Dict[str, Any]:
    data = _load_json(OWNER_ACTION_NOTES_STATUS_PATH, {})
    if not data:
        data = build_owner_action_notes_status(write_panel=True)
    return data if isinstance(data, dict) else {}


def owner_action_notes_status_card() -> Dict[str, Any]:
    status = load_owner_action_notes_status()
    top = status.get("top_note", {}) if isinstance(status.get("top_note"), dict) else {}

    return {
        "ok": status.get("ok") is True,
        "pack": "143",
        "title": "Owner Action Notes",
        "readiness_score": status.get("readiness_score", 0),
        "base_note_count": status.get("base_note_count", 0),
        "filtered_note_count": status.get("filtered_note_count", 0),
        "receipt_count": status.get("receipt_count", 0),
        "top_note_id": top.get("note_id"),
        "top_note_type": top.get("note_type"),
        "top_visibility": top.get("visibility"),
        "panel_path": status.get("panel_path", str(OWNER_ACTION_NOTES_PANEL_PATH)),
        "status_path": status.get("status_path", str(OWNER_ACTION_NOTES_STATUS_PATH)),
        "human_reason": "Owner Action Notes status card loaded.",
        "soulaana_translation": "Soulaana: Owner action notes are visible.",
    }


def reset_owner_action_notes_for_test() -> Dict[str, Any]:
    _write_json(OWNER_ACTION_NOTES_PATH, [])
    _write_json(OWNER_ACTION_NOTE_RECEIPTS_PATH, [])
    _write_json(OWNER_ACTION_NOTES_STATUS_PATH, {
        "ok": True,
        "pack": "143",
        "reset_at": _utc_now(),
        "human_reason": "Owner Action Notes reset for test.",
    })
    if OWNER_ACTION_NOTES_PANEL_PATH.exists():
        try:
            OWNER_ACTION_NOTES_PANEL_PATH.unlink()
        except Exception:
            pass
    if OWNER_ACTION_NOTE_DETAIL_PANEL_PATH.exists():
        try:
            OWNER_ACTION_NOTE_DETAIL_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "owner_action_notes_reset_for_test",
        "soulaana_translation": "Soulaana: Owner action notes reset for a clean test lane.",
    }
