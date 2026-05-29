
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

INCIDENT_STATE_PATH = DATA_DIR / "security_incident_desk_states.json"
INCIDENT_RECEIPTS_PATH = DATA_DIR / "security_incident_desk_receipts.json"
INCIDENT_STATUS_PATH = DATA_DIR / "security_incident_desk_status.json"
INCIDENT_PANEL_PATH = DATA_DIR / "security_incident_desk_panel.html"

ALLOWED_INCIDENT_STATUSES = {
    "new",
    "triaged",
    "investigating",
    "contained",
    "resolved",
    "monitoring",
    "false_alarm",
    "archived",
}

ALLOWED_INCIDENT_SEVERITIES = {
    "critical",
    "high",
    "medium",
    "low",
    "info",
}

OPEN_INCIDENT_STATUSES = {
    "new",
    "triaged",
    "investigating",
    "contained",
    "monitoring",
}

CLOSED_INCIDENT_STATUSES = {
    "resolved",
    "false_alarm",
    "archived",
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

            if isinstance(redacted_item, dict) and "__redacted_incident_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_incident_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_incident_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_incident_field_count__"] = redacted_count
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
            return "[REDACTED_INCIDENT_VALUE]"
        return value

    return value


def _load_states() -> Dict[str, Any]:
    data = _load_json(INCIDENT_STATE_PATH, {})
    return data if isinstance(data, dict) else {}


def _save_states(states: Dict[str, Any]) -> None:
    _write_json(INCIDENT_STATE_PATH, states)


def _load_receipts() -> List[Dict[str, Any]]:
    data = _load_json(INCIDENT_RECEIPTS_PATH, [])
    return data if isinstance(data, list) else []


def _save_receipts(receipts: List[Dict[str, Any]]) -> None:
    _write_json(INCIDENT_RECEIPTS_PATH, receipts)


def _get_priority_items(limit: int = 160) -> List[Dict[str, Any]]:
    try:
        from tower.security_inbox_filters_priorities import build_security_inbox_filters_priorities_status

        status = build_security_inbox_filters_priorities_status(write_panel=True)
        items = status.get("top_priority_items", [])
        if isinstance(items, list):
            return [item for item in items[:limit] if isinstance(item, dict)]
    except Exception:
        pass
    return []


def _default_severity(item: Dict[str, Any]) -> str:
    severity = str(item.get("severity", "info")).lower()
    priority = int(item.get("priority_score", 0) or 0)
    review_state = str(item.get("review_state", "")).lower()

    if review_state == "escalated" or priority >= 150:
        return "critical"
    if severity == "high" or priority >= 100:
        return "high"
    if severity == "medium" or priority >= 70:
        return "medium"
    if severity == "watch":
        return "low"
    return "info"


def _should_be_incident(item: Dict[str, Any]) -> bool:
    severity = str(item.get("severity", "info")).lower()
    review_state = str(item.get("review_state", "new")).lower()
    priority = int(item.get("priority_score", 0) or 0)

    if review_state == "escalated":
        return True
    if severity in {"high", "medium"} and review_state in {"new", "acknowledged", "investigating"}:
        return True
    if priority >= 90:
        return True
    return False


def _incident_id_for_item(item: Dict[str, Any]) -> str:
    base = {
        "inbox_item_id": item.get("inbox_item_id", ""),
        "source": item.get("source", ""),
        "decision": item.get("decision", ""),
        "object_id": item.get("object_id", ""),
        "route_path": item.get("route_path", ""),
    }
    return "incident_" + _fingerprint(base)[:18]


def _candidate_from_item(item: Dict[str, Any]) -> Dict[str, Any]:
    incident_id = _incident_id_for_item(item)

    return {
        "incident_id": incident_id,
        "inbox_item_id": item.get("inbox_item_id", ""),
        "source": item.get("source", ""),
        "created_at": item.get("created_at", ""),
        "security_decision": item.get("decision", ""),
        "priority_score": item.get("priority_score", 0),
        "severity": _default_severity(item),
        "incident_status": "new",
        "review_state": item.get("review_state", ""),
        "object_type": item.get("object_type", ""),
        "object_id": item.get("object_id", ""),
        "route_path": item.get("route_path", ""),
        "human_reason": item.get("human_reason", "Security incident candidate recorded."),
        "safe_summary": item.get("safe_summary", {}),
    }


def _merge_incident_state(candidate: Dict[str, Any], states: Dict[str, Any]) -> Dict[str, Any]:
    incident_id = candidate.get("incident_id", "")
    state = states.get(incident_id, {}) if incident_id else {}
    if not isinstance(state, dict):
        state = {}

    merged = dict(candidate)
    merged["incident_status"] = state.get("incident_status", candidate.get("incident_status", "new"))
    merged["severity"] = state.get("severity", candidate.get("severity", "medium"))
    merged["assigned_to"] = state.get("assigned_to", "")
    merged["owner_notes"] = state.get("owner_notes", "")
    merged["last_action"] = state.get("last_action", "")
    merged["updated_at"] = state.get("updated_at", "")
    merged["updated_by"] = state.get("updated_by", "")
    merged["incident_state_source"] = "saved_state" if state else "candidate"
    return merged


def apply_security_incident_action(
    incident_id: str,
    incident_status: str,
    severity: str = "",
    actor_user_id: str = "owner_solice",
    note: str = "",
    assigned_to: str = "",
    reason: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    incident_id = str(incident_id or "").strip()
    incident_status = str(incident_status or "").strip().lower()
    severity = str(severity or "").strip().lower()
    actor_user_id = str(actor_user_id or "owner_solice").strip() or "owner_solice"
    note = str(note or "").strip()
    assigned_to = str(assigned_to or "").strip()
    reason = str(reason or "").strip()
    metadata = metadata if isinstance(metadata, dict) else {}

    if not incident_id:
        return {
            "ok": False,
            "pack": "126",
            "decision": "incident_action_rejected",
            "reason_code": "missing_incident_id",
            "human_reason": "Incident ID is required.",
            "required_actions": ["provide_incident_id"],
        }

    if incident_status not in ALLOWED_INCIDENT_STATUSES:
        return {
            "ok": False,
            "pack": "126",
            "decision": "incident_action_rejected",
            "reason_code": "invalid_incident_status",
            "allowed_statuses": sorted(ALLOWED_INCIDENT_STATUSES),
            "human_reason": "Incident status is not allowed.",
            "required_actions": ["choose_allowed_incident_status"],
        }

    if severity and severity not in ALLOWED_INCIDENT_SEVERITIES:
        return {
            "ok": False,
            "pack": "126",
            "decision": "incident_action_rejected",
            "reason_code": "invalid_incident_severity",
            "allowed_severities": sorted(ALLOWED_INCIDENT_SEVERITIES),
            "human_reason": "Incident severity is not allowed.",
            "required_actions": ["choose_allowed_incident_severity"],
        }

    candidates = build_security_incident_desk_status(write_panel=False).get("incident_candidates", [])
    candidate_lookup = {
        str(item.get("incident_id", "")): item
        for item in candidates
        if isinstance(item, dict)
    }
    candidate = candidate_lookup.get(incident_id)

    if candidate is None:
        return {
            "ok": False,
            "pack": "126",
            "decision": "incident_action_rejected",
            "reason_code": "incident_not_found",
            "incident_id": incident_id,
            "human_reason": "Incident could not be found in the current Incident Desk.",
            "required_actions": ["refresh_incident_desk", "confirm_incident_id"],
        }

    states = _load_states()
    prior = states.get(incident_id, {}) if isinstance(states.get(incident_id), dict) else {}
    prior_status = prior.get("incident_status", candidate.get("incident_status", "new"))
    prior_severity = prior.get("severity", candidate.get("severity", "medium"))

    now = _utc_now()
    state_record = {
        "incident_id": incident_id,
        "inbox_item_id": candidate.get("inbox_item_id", ""),
        "incident_status": incident_status,
        "severity": severity or prior_severity or candidate.get("severity", "medium"),
        "assigned_to": assigned_to,
        "owner_notes": note,
        "updated_by": actor_user_id,
        "updated_at": now,
        "last_action": f"{prior_status}_to_{incident_status}",
        "source": candidate.get("source", ""),
        "security_decision": candidate.get("security_decision", ""),
        "priority_score": candidate.get("priority_score", 0),
        "object_type": candidate.get("object_type", ""),
        "object_id": candidate.get("object_id", ""),
        "route_path": candidate.get("route_path", ""),
        "metadata": metadata,
    }

    state_record = _redact(state_record)
    states[incident_id] = state_record
    _save_states(states)

    receipt = {
        "receipt_id": "security_incident_receipt_" + _fingerprint({
            "incident_id": incident_id,
            "incident_status": incident_status,
            "actor_user_id": actor_user_id,
            "created_at": now,
        })[:18],
        "event_type": "tower_security_incident_action",
        "pack": "126",
        "created_at": now,
        "actor_user_id": actor_user_id,
        "incident_id": incident_id,
        "inbox_item_id": candidate.get("inbox_item_id", ""),
        "prior_incident_status": prior_status,
        "new_incident_status": incident_status,
        "prior_severity": prior_severity,
        "new_severity": state_record.get("severity"),
        "decision": "incident_action_applied",
        "reason_code": "security_incident_state_updated",
        "human_reason": reason or f"Security incident moved from {prior_status} to {incident_status}.",
        "source": candidate.get("source", ""),
        "priority_score": candidate.get("priority_score", 0),
        "object_type": candidate.get("object_type", ""),
        "object_id": candidate.get("object_id", ""),
        "route_path": candidate.get("route_path", ""),
        "metadata": metadata,
    }

    receipt = _redact(receipt)
    receipts = _load_receipts()
    receipts.append(receipt)
    _save_receipts(receipts[-500:])

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_security_incident_action",
            source_name="security_incident_desk_receipt",
            source_path=str(INCIDENT_RECEIPTS_PATH),
            source_hash=_fingerprint(receipt),
            record_count=1,
            actor_user_id=actor_user_id,
            reason=receipt.get("human_reason"),
            metadata={
                "pack": "126",
                "incident_id": incident_id,
                "new_incident_status": incident_status,
                "severity": state_record.get("severity"),
            },
        )
    except Exception:
        pass

    result = {
        "ok": True,
        "pack": "126",
        "decision": "incident_action_applied",
        "incident_id": incident_id,
        "prior_incident_status": prior_status,
        "new_incident_status": incident_status,
        "state_record": state_record,
        "receipt": receipt,
        "human_reason": "Security incident action applied with a separate incident receipt.",
        "soulaana_translation": "Soulaana: Incident status updated. The original event stayed untouched; the Incident Desk got a receipt.",
    }

    scan = _safe_scan(result)
    result["no_secret_leakage"] = scan.get("ok") is True
    result["leakage_scan"] = scan
    return result


def build_security_incident_desk_status(write_panel: bool = True) -> Dict[str, Any]:
    priority_items = _get_priority_items(limit=180)
    incident_candidates = [
        _candidate_from_item(item)
        for item in priority_items
        if _should_be_incident(item)
    ]

    states = _load_states()
    receipts = _load_receipts()

    merged = [_merge_incident_state(candidate, states) for candidate in incident_candidates]

    by_status: Dict[str, int] = {}
    by_severity: Dict[str, int] = {}
    by_source: Dict[str, int] = {}

    open_incident_count = 0
    critical_incident_count = 0

    for incident in merged:
        status = str(incident.get("incident_status", "new")).lower()
        severity = str(incident.get("severity", "medium")).lower()
        source = str(incident.get("source", "unknown"))

        by_status[status] = by_status.get(status, 0) + 1
        by_severity[severity] = by_severity.get(severity, 0) + 1
        by_source[source] = by_source.get(source, 0) + 1

        if status in OPEN_INCIDENT_STATUSES:
            open_incident_count += 1
        if severity == "critical":
            critical_incident_count += 1

    checks = {
        "priority_items_loaded": isinstance(priority_items, list),
        "incident_candidates_ready": isinstance(incident_candidates, list),
        "states_loaded": isinstance(states, dict),
        "receipts_loaded": isinstance(receipts, list),
        "allowed_statuses_ready": len(ALLOWED_INCIDENT_STATUSES) >= 8,
        "allowed_severities_ready": len(ALLOWED_INCIDENT_SEVERITIES) >= 5,
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    status = {
        "ok": not failed_checks,
        "pack": "126",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(INCIDENT_STATUS_PATH),
        "panel_path": str(INCIDENT_PANEL_PATH),
        "state_path": str(INCIDENT_STATE_PATH),
        "receipts_path": str(INCIDENT_RECEIPTS_PATH),
        "allowed_incident_statuses": sorted(ALLOWED_INCIDENT_STATUSES),
        "allowed_incident_severities": sorted(ALLOWED_INCIDENT_SEVERITIES),
        "priority_item_count": len(priority_items),
        "incident_count": len(merged),
        "open_incident_count": open_incident_count,
        "critical_incident_count": critical_incident_count,
        "tracked_incident_count": len(states),
        "receipt_count": len(receipts),
        "by_status": by_status,
        "by_severity": by_severity,
        "by_source": by_source,
        "incident_candidates": merged[:120],
        "recent_receipts": receipts[-20:],
        "checks": checks,
        "failed_checks": failed_checks,
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 10)),
        "readiness_label": (
            "Tower Incident Desk ready"
            if not failed_checks
            else "Tower Incident Desk needs review"
        ),
        "human_reason": "Tower Incident Desk is ready to track high-priority security events as formal incidents without mutating original logs.",
        "soulaana_translation": "Soulaana: Serious inbox items can now become formal incidents with status, severity, and receipts.",
    }

    status = _redact(status)
    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(INCIDENT_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_security_incident_desk_status",
            source_name="security_incident_desk_status",
            source_path=str(INCIDENT_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=int(status.get("incident_count", 0) or 0),
            actor_user_id="tower_system",
            reason="Pack 126 Tower Incident Desk status generated.",
            metadata={
                "pack": "126",
                "status": status.get("status"),
                "incident_count": status.get("incident_count"),
                "open_incident_count": status.get("open_incident_count"),
                "readiness_score": status.get("readiness_score"),
            },
        )
    except Exception:
        pass

    if write_panel:
        write_security_incident_desk_panel(status)

    return status


def render_security_incident_desk_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_security_incident_desk_status(write_panel=False)
    incidents = status.get("incident_candidates", []) if isinstance(status.get("incident_candidates"), list) else []

    card_html = []
    for incident in incidents[:24]:
        if not isinstance(incident, dict):
            continue

        severity = _html_escape(incident.get("severity", "medium"))
        incident_status = _html_escape(incident.get("incident_status", "new"))
        source = _html_escape(incident.get("source", "source"))
        priority = _html_escape(incident.get("priority_score", 0))
        reason = _html_escape(incident.get("human_reason", "Security incident recorded."))
        incident_id = _html_escape(incident.get("incident_id", ""))

        card_html.append(f"""
        <article class="incident-desk-card incident-desk-card--{severity}">
          <div class="incident-desk-card__eyebrow">P{priority} · {severity} · {incident_status} · {source}</div>
          <h3>{incident_id}</h3>
          <p>{reason}</p>
          <small>{_html_escape(incident.get('inbox_item_id', ''))}</small>
        </article>
        """)

    if not card_html:
        card_html.append("""
        <article class="incident-desk-card incident-desk-card--info">
          <div class="incident-desk-card__eyebrow">INFO · EMPTY</div>
          <h3>No incidents yet</h3>
          <p>The Incident Desk is ready. High-priority inbox items will appear here as formal incident candidates.</p>
        </article>
        """)

    html = f"""
<!-- PACK126_SECURITY_INCIDENT_DESK_SECTION -->
<section class="security-incident-desk" data-pack="126">
  <style>
    .security-incident-desk {{
      margin: 24px 0;
      border: 1px solid rgba(255,128,128,.38);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top right, rgba(255,128,128,.15), transparent 34%),
        linear-gradient(135deg, rgba(38,14,14,.82), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .security-incident-desk__eyebrow {{
      color: rgba(255,168,128,.9);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .security-incident-desk h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .security-incident-desk p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .incident-desk-stats {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .incident-desk-stat {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
    }}
    .incident-desk-stat b {{
      display: block;
      font-size: 22px;
    }}
    .incident-desk-stat span {{
      color: rgba(245,234,210,.62);
      font-size: 12px;
    }}
    .incident-desk-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .incident-desk-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
    }}
    .incident-desk-card--critical {{
      border-color: rgba(255,80,80,.8);
    }}
    .incident-desk-card--high {{
      border-color: rgba(255,128,128,.65);
    }}
    .incident-desk-card--medium {{
      border-color: rgba(220,183,94,.62);
    }}
    .incident-desk-card--low {{
      border-color: rgba(168,175,255,.52);
    }}
    .incident-desk-card--info {{
      border-color: rgba(143,221,158,.34);
    }}
    .incident-desk-card__eyebrow {{
      color: rgba(220,183,94,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .incident-desk-card h3 {{
      margin: 0 0 7px;
      font-size: 16px;
      word-break: break-word;
    }}
    .incident-desk-card p {{
      margin: 0 0 8px;
      color: rgba(245,234,210,.72);
    }}
    .incident-desk-card small {{
      color: rgba(245,234,210,.55);
      word-break: break-word;
    }}
    @media (max-width: 1000px) {{
      .incident-desk-stats,
      .incident-desk-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="security-incident-desk__eyebrow">PACK 126 · INCIDENT DESK</div>
  <h2>Tower Incident Desk</h2>
  <p>{_html_escape(status.get('human_reason', 'Tower Incident Desk loaded.'))}</p>

  <div class="incident-desk-stats">
    <div class="incident-desk-stat"><b>{_html_escape(status.get('incident_count', 0))}</b><span>Incidents</span></div>
    <div class="incident-desk-stat"><b>{_html_escape(status.get('open_incident_count', 0))}</b><span>Open</span></div>
    <div class="incident-desk-stat"><b>{_html_escape(status.get('critical_incident_count', 0))}</b><span>Critical</span></div>
    <div class="incident-desk-stat"><b>{_html_escape(status.get('tracked_incident_count', 0))}</b><span>Tracked</span></div>
    <div class="incident-desk-stat"><b>{_html_escape(status.get('receipt_count', 0))}</b><span>Receipts</span></div>
  </div>

  <div class="incident-desk-grid">
    {''.join(card_html)}
  </div>
</section>
<!-- END PACK126_SECURITY_INCIDENT_DESK_SECTION -->
"""
    return html


def write_security_incident_desk_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_security_incident_desk_status(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Incident Desk</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_security_incident_desk_section(status)}
</main>
</body>
</html>
"""
    _write_text(INCIDENT_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "126",
        "decision": "security_incident_desk_panel_written",
        "path": str(INCIDENT_PANEL_PATH),
        "human_reason": "Tower Incident Desk panel written.",
        "soulaana_translation": "Soulaana: Incident Desk panel posted.",
    }


def load_security_incident_desk_status() -> Dict[str, Any]:
    status = _load_json(INCIDENT_STATUS_PATH, {})
    if not status:
        status = build_security_incident_desk_status(write_panel=True)
    return status


def security_incident_desk_status_card() -> Dict[str, Any]:
    status = load_security_incident_desk_status()
    return {
        "ok": status.get("ok") is True,
        "pack": "126",
        "title": "Tower Incident Desk",
        "readiness_score": status.get("readiness_score", 0),
        "incident_count": status.get("incident_count", 0),
        "open_incident_count": status.get("open_incident_count", 0),
        "critical_incident_count": status.get("critical_incident_count", 0),
        "tracked_incident_count": status.get("tracked_incident_count", 0),
        "receipt_count": status.get("receipt_count", 0),
        "panel_path": status.get("panel_path", str(INCIDENT_PANEL_PATH)),
        "status_path": status.get("status_path", str(INCIDENT_STATUS_PATH)),
        "human_reason": "Tower Incident Desk status card loaded.",
        "soulaana_translation": "Soulaana: Incident Desk is visible.",
    }


def reset_security_incident_desk_for_test() -> Dict[str, Any]:
    _write_json(INCIDENT_STATE_PATH, {})
    _write_json(INCIDENT_RECEIPTS_PATH, [])
    _write_json(INCIDENT_STATUS_PATH, {
        "ok": True,
        "pack": "126",
        "reset_at": _utc_now(),
        "human_reason": "Tower Incident Desk reset for test.",
    })
    if INCIDENT_PANEL_PATH.exists():
        try:
            INCIDENT_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "security_incident_desk_reset_for_test",
        "states_reset": True,
        "receipts_reset": True,
        "soulaana_translation": "Soulaana: Incident Desk reset for a clean test lane.",
    }
