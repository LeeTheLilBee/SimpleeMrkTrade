
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OWNER_ACTION_STATE_RECEIPTS_STATUS_PATH = DATA_DIR / "owner_action_state_receipts_status.json"
OWNER_ACTION_STATE_RECEIPTS_PANEL_PATH = DATA_DIR / "owner_action_state_receipts_panel.html"
OWNER_ACTION_STATE_RECEIPT_DETAIL_PANEL_PATH = DATA_DIR / "owner_action_state_receipt_detail_panel.html"


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

            if isinstance(redacted_item, dict) and "__redacted_owner_action_receipt_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_owner_action_receipt_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_owner_action_receipt_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_owner_action_receipt_field_count__"] = redacted_count
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
            return "[REDACTED_OWNER_ACTION_RECEIPT_VALUE]"
        return value

    return value


def _num(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        try:
            return int(float(value))
        except Exception:
            return default


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def _load_owner_action_state_receipts() -> List[Dict[str, Any]]:
    try:
        from tower.owner_action_state_tracking import OWNER_ACTION_STATE_RECEIPTS_PATH
        data = _load_json(OWNER_ACTION_STATE_RECEIPTS_PATH, [])
        return [item for item in data if isinstance(item, dict)] if isinstance(data, list) else []
    except Exception:
        return []


def _load_owner_action_state_status() -> Dict[str, Any]:
    try:
        from tower.owner_action_state_tracking import build_owner_action_state_status
        status = build_owner_action_state_status(write_panel=True)
        return status if isinstance(status, dict) else {}
    except Exception:
        try:
            from tower.owner_action_state_tracking import OWNER_ACTION_STATE_STATUS_PATH
            data = _load_json(OWNER_ACTION_STATE_STATUS_PATH, {})
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}


def _receipt_matches(
    receipt: Dict[str, Any],
    *,
    receipt_id: str = "",
    action_id: str = "",
    new_state: str = "",
    prior_state: str = "",
    actor_user_id: str = "",
    event_type: str = "",
) -> bool:
    if not isinstance(receipt, dict):
        return False

    if receipt_id and _norm(receipt.get("receipt_id")) != receipt_id:
        return False

    if action_id and _norm(receipt.get("action_id")) != action_id:
        return False

    if new_state and _norm(receipt.get("new_state")) != new_state:
        return False

    if prior_state and _norm(receipt.get("prior_state")) != prior_state:
        return False

    if actor_user_id and _norm(receipt.get("actor_user_id")) != actor_user_id:
        return False

    if event_type and _norm(receipt.get("event_type")) != event_type:
        return False

    return True


def _sort_receipts(receipts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        [item for item in receipts if isinstance(item, dict)],
        key=lambda item: str(item.get("created_at", "")),
        reverse=True,
    )


def build_owner_action_state_receipts_status(
    *,
    receipt_id: str = "",
    action_id: str = "",
    new_state: str = "",
    prior_state: str = "",
    actor_user_id: str = "",
    event_type: str = "",
    top_only: bool = False,
    limit: int = 80,
    write_panel: bool = True,
) -> Dict[str, Any]:
    receipts = _load_owner_action_state_receipts()
    state_status = _load_owner_action_state_status()

    receipt_id_norm = _norm(receipt_id)
    action_id_norm = _norm(action_id)
    new_state_norm = _norm(new_state)
    prior_state_norm = _norm(prior_state)
    actor_norm = _norm(actor_user_id)
    event_type_norm = _norm(event_type)

    try:
        limit_int = int(limit)
    except Exception:
        limit_int = 80
    limit_int = max(1, min(limit_int, 500))

    filtered = [
        receipt for receipt in receipts
        if _receipt_matches(
            receipt,
            receipt_id=receipt_id_norm,
            action_id=action_id_norm,
            new_state=new_state_norm,
            prior_state=prior_state_norm,
            actor_user_id=actor_norm,
            event_type=event_type_norm,
        )
    ]

    filtered = _sort_receipts(filtered)

    if top_only:
        filtered = filtered[:1]

    filtered = filtered[:limit_int]

    by_new_state: Dict[str, int] = {}
    by_prior_state: Dict[str, int] = {}
    by_actor: Dict[str, int] = {}
    by_event_type: Dict[str, int] = {}
    by_action_type: Dict[str, int] = {}

    for receipt in receipts:
        if not isinstance(receipt, dict):
            continue

        ns = _norm(receipt.get("new_state")) or "unknown"
        ps = _norm(receipt.get("prior_state")) or "unknown"
        actor = str(receipt.get("actor_user_id", "") or "unknown")
        et = str(receipt.get("event_type", "") or "unknown")
        at = str(receipt.get("action_type", "") or "unknown")

        by_new_state[ns] = by_new_state.get(ns, 0) + 1
        by_prior_state[ps] = by_prior_state.get(ps, 0) + 1
        by_actor[actor] = by_actor.get(actor, 0) + 1
        by_event_type[et] = by_event_type.get(et, 0) + 1
        by_action_type[at] = by_action_type.get(at, 0) + 1

    top_receipt = filtered[0] if filtered else {}

    status = {
        "ok": True,
        "pack": "142",
        "status": "passed",
        "created_at": _utc_now(),
        "status_path": str(OWNER_ACTION_STATE_RECEIPTS_STATUS_PATH),
        "panel_path": str(OWNER_ACTION_STATE_RECEIPTS_PANEL_PATH),
        "base_receipt_count": len(receipts),
        "filtered_receipt_count": len(filtered),
        "top_receipt": top_receipt,
        "receipts": filtered,
        "active_filters": {
            "receipt_id": receipt_id_norm,
            "action_id": action_id_norm,
            "new_state": new_state_norm,
            "prior_state": prior_state_norm,
            "actor_user_id": actor_norm,
            "event_type": event_type_norm,
            "top_only": bool(top_only),
            "limit": limit_int,
        },
        "filter_options": {
            "new_state": by_new_state,
            "prior_state": by_prior_state,
            "actor_user_id": by_actor,
            "event_type": by_event_type,
            "action_type": by_action_type,
        },
        "state_summary": {
            "action_count": state_status.get("action_count", 0),
            "tracked_action_count": state_status.get("tracked_action_count", 0),
            "open_action_count": state_status.get("open_action_count", 0),
            "closed_action_count": state_status.get("closed_action_count", 0),
            "receipt_count": state_status.get("receipt_count", len(receipts)),
            "by_state": state_status.get("by_state", {}),
        },
        "readiness_score": 100,
        "human_reason": "Owner Action state receipt layer is ready.",
        "soulaana_translation": "Soulaana: Owner command state changes now have a receipt review layer.",
    }

    status = _redact(status)
    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(OWNER_ACTION_STATE_RECEIPTS_STATUS_PATH, status)

    if write_panel:
        write_owner_action_state_receipts_panel(status)

    return status


def build_owner_action_state_receipt_detail(
    *,
    receipt_id: str = "",
    write_panel: bool = True,
) -> Dict[str, Any]:
    receipt_id_norm = _norm(receipt_id)
    receipts = _load_owner_action_state_receipts()
    sorted_receipts = _sort_receipts(receipts)

    receipt = {}

    if receipt_id_norm:
        for item in sorted_receipts:
            if _norm(item.get("receipt_id")) == receipt_id_norm:
                receipt = item
                break
    elif sorted_receipts:
        receipt = sorted_receipts[0]

    found = bool(receipt)

    detail = {
        "ok": found,
        "pack": "142",
        "status": "passed" if found else "not_found",
        "requested_receipt_id": str(receipt_id or ""),
        "found_receipt_id": receipt.get("receipt_id", "") if found else "",
        "receipt": receipt if found else {},
        "detail": {
            "receipt_id": receipt.get("receipt_id", "") if found else "",
            "event_type": receipt.get("event_type", "") if found else "",
            "action_id": receipt.get("action_id", "") if found else "",
            "action_type": receipt.get("action_type", "") if found else "",
            "title": receipt.get("title", "") if found else "",
            "prior_state": receipt.get("prior_state", "") if found else "",
            "new_state": receipt.get("new_state", "") if found else "",
            "actor_user_id": receipt.get("actor_user_id", "") if found else "",
            "reason": receipt.get("reason", "") if found else "",
            "note": receipt.get("note", "") if found else "",
            "created_at": receipt.get("created_at", "") if found else "",
            "receipt_fingerprint": receipt.get("receipt_fingerprint", "") if found else "",
            "no_secret_leakage": receipt.get("no_secret_leakage") is True if found else False,
        },
        "readiness_score": 100 if found else 80,
        "human_reason": (
            "Owner Action state receipt detail loaded."
            if found
            else "Owner Action state receipt was not found."
        ),
        "soulaana_translation": (
            "Soulaana: This receipt shows how the owner command changed state."
            if found
            else "Soulaana: I could not find that state receipt."
        ),
    }

    detail = _redact(detail)
    scan = _safe_scan(detail)
    detail["no_secret_leakage"] = scan.get("ok") is True
    detail["leakage_scan"] = scan
    detail["status_fingerprint"] = _fingerprint(detail)

    if write_panel:
        write_owner_action_state_receipt_detail_panel(detail)

    return detail


def render_owner_action_state_receipts_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_owner_action_state_receipts_status(write_panel=False)
    receipts = status.get("receipts", []) if isinstance(status.get("receipts"), list) else []
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
        <article class="owner-action-receipt-option">
          <h3>{_html_escape(label)}</h3>
          <div>{''.join(chips)}</div>
        </article>
        """)

    receipt_cards = []
    for receipt in receipts[:24]:
        if not isinstance(receipt, dict):
            continue

        receipt_cards.append(f"""
        <article class="owner-action-receipt-card">
          <div class="owner-action-receipt-card__eyebrow">{_html_escape(receipt.get('event_type', 'receipt'))}</div>
          <h3>{_html_escape(receipt.get('new_state', 'state'))}</h3>
          <p>{_html_escape(receipt.get('title', 'Owner Action'))}</p>
          <small>{_html_escape(receipt.get('prior_state', ''))} → {_html_escape(receipt.get('new_state', ''))}</small>
          <code>{_html_escape(receipt.get('receipt_id', ''))}</code>
        </article>
        """)

    if not receipt_cards:
        receipt_cards.append("""
        <article class="owner-action-receipt-card">
          <div class="owner-action-receipt-card__eyebrow">empty</div>
          <h3>No receipts</h3>
          <p>State receipts will appear after owner actions move through review states.</p>
          <small>open → acknowledged → investigating → resolved</small>
        </article>
        """)

    html = f"""
<!-- PACK142_OWNER_ACTION_STATE_RECEIPTS_SECTION -->
<section class="owner-action-receipts" data-pack="142">
  <style>
    .owner-action-receipts {{
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
    .owner-action-receipts__eyebrow {{
      color: rgba(168,175,255,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-action-receipts h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .owner-action-receipts p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .owner-action-receipts-active {{
      margin-top: 12px;
      border: 1px solid rgba(245,234,210,.14);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
      color: rgba(245,234,210,.72);
      font-size: 12px;
    }}
    .owner-action-receipt-options,
    .owner-action-receipt-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-receipt-option,
    .owner-action-receipt-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
    }}
    .owner-action-receipt-option h3,
    .owner-action-receipt-card h3 {{
      margin: 0 0 8px;
      font-size: 16px;
    }}
    .owner-action-receipt-option span {{
      display: inline-flex;
      margin: 3px;
      border: 1px solid rgba(168,175,255,.22);
      border-radius: 999px;
      padding: 5px 8px;
      color: rgba(245,234,210,.70);
      font-size: 11px;
    }}
    .owner-action-receipt-card__eyebrow {{
      color: rgba(168,175,255,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .owner-action-receipt-card small,
    .owner-action-receipt-card code {{
      display: block;
      color: rgba(245,234,210,.55);
      margin-top: 8px;
      word-break: break-word;
    }}
    .owner-action-receipt-card code {{
      font-size: 11px;
      color: rgba(168,175,255,.88);
    }}
    @media (max-width: 1000px) {{
      .owner-action-receipt-options,
      .owner-action-receipt-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="owner-action-receipts__eyebrow">PACK 142 · OWNER ACTION STATE RECEIPTS</div>
  <h2>Owner Action State Receipts</h2>
  <p>{_html_escape(status.get('human_reason', 'Owner Action state receipts loaded.'))}</p>

  <div class="owner-action-receipts-active">
    <strong>Base receipts:</strong> {_html_escape(status.get('base_receipt_count', 0))}<br>
    <strong>Filtered receipts:</strong> {_html_escape(status.get('filtered_receipt_count', 0))}<br>
    <strong>Active filters:</strong> {_html_escape(active)}
  </div>

  <div class="owner-action-receipt-options">
    {''.join(option_cards)}
  </div>

  <div class="owner-action-receipt-grid">
    {''.join(receipt_cards)}
  </div>
</section>
<!-- END PACK142_OWNER_ACTION_STATE_RECEIPTS_SECTION -->
"""
    return html


def render_owner_action_state_receipt_detail_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_owner_action_state_receipt_detail(write_panel=False)
    detail = status.get("detail", {}) if isinstance(status.get("detail"), dict) else {}

    html = f"""
<!-- PACK142_OWNER_ACTION_STATE_RECEIPT_DETAIL_SECTION -->
<section class="owner-action-receipt-detail" data-pack="142-detail">
  <style>
    .owner-action-receipt-detail {{
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
    .owner-action-receipt-detail__eyebrow {{
      color: rgba(220,183,94,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-action-receipt-detail h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .owner-action-receipt-detail p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .owner-action-receipt-detail-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-receipt-detail-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
    }}
    .owner-action-receipt-detail-card span {{
      display: block;
      color: rgba(220,183,94,.72);
      text-transform: uppercase;
      letter-spacing: .11em;
      font-size: 10px;
      margin-bottom: 6px;
    }}
    .owner-action-receipt-detail-card b {{
      display: block;
      color: #f5ead2;
      font-size: 14px;
      word-break: break-word;
    }}
    @media (max-width: 1000px) {{
      .owner-action-receipt-detail-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="owner-action-receipt-detail__eyebrow">PACK 142 · RECEIPT DETAIL</div>
  <h2>{_html_escape(detail.get('new_state', 'Receipt Detail'))}</h2>
  <p>{_html_escape(status.get('human_reason', 'Owner Action state receipt detail loaded.'))}</p>

  <div class="owner-action-receipt-detail-grid">
    <article class="owner-action-receipt-detail-card"><span>Receipt</span><b>{_html_escape(detail.get('receipt_id', ''))}</b></article>
    <article class="owner-action-receipt-detail-card"><span>Action</span><b>{_html_escape(detail.get('action_type', ''))}</b></article>
    <article class="owner-action-receipt-detail-card"><span>Prior</span><b>{_html_escape(detail.get('prior_state', ''))}</b></article>
    <article class="owner-action-receipt-detail-card"><span>New</span><b>{_html_escape(detail.get('new_state', ''))}</b></article>
    <article class="owner-action-receipt-detail-card"><span>Actor</span><b>{_html_escape(detail.get('actor_user_id', ''))}</b></article>
    <article class="owner-action-receipt-detail-card"><span>Reason</span><b>{_html_escape(detail.get('reason', ''))}</b></article>
    <article class="owner-action-receipt-detail-card"><span>No Secrets</span><b>{_html_escape(detail.get('no_secret_leakage', False))}</b></article>
    <article class="owner-action-receipt-detail-card"><span>Fingerprint</span><b>{_html_escape(detail.get('receipt_fingerprint', ''))}</b></article>
  </div>
</section>
<!-- END PACK142_OWNER_ACTION_STATE_RECEIPT_DETAIL_SECTION -->
"""
    return html


def write_owner_action_state_receipts_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_owner_action_state_receipts_status(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Owner Action State Receipts</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_owner_action_state_receipts_section(status)}
</main>
</body>
</html>
"""
    _write_text(OWNER_ACTION_STATE_RECEIPTS_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "142",
        "decision": "owner_action_state_receipts_panel_written",
        "path": str(OWNER_ACTION_STATE_RECEIPTS_PANEL_PATH),
        "human_reason": "Owner Action State Receipts panel written.",
        "soulaana_translation": "Soulaana: Owner action state receipts board posted.",
    }


def write_owner_action_state_receipt_detail_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_owner_action_state_receipt_detail(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Owner Action Receipt Detail</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_owner_action_state_receipt_detail_section(status)}
</main>
</body>
</html>
"""
    _write_text(OWNER_ACTION_STATE_RECEIPT_DETAIL_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "142",
        "decision": "owner_action_state_receipt_detail_panel_written",
        "path": str(OWNER_ACTION_STATE_RECEIPT_DETAIL_PANEL_PATH),
        "human_reason": "Owner Action State Receipt detail panel written.",
        "soulaana_translation": "Soulaana: Owner action state receipt detail card posted.",
    }


def load_owner_action_state_receipts_status() -> Dict[str, Any]:
    data = _load_json(OWNER_ACTION_STATE_RECEIPTS_STATUS_PATH, {})
    if not data:
        data = build_owner_action_state_receipts_status(write_panel=True)
    return data if isinstance(data, dict) else {}


def owner_action_state_receipts_status_card() -> Dict[str, Any]:
    status = load_owner_action_state_receipts_status()
    state = status.get("state_summary", {}) if isinstance(status.get("state_summary"), dict) else {}
    top = status.get("top_receipt", {}) if isinstance(status.get("top_receipt"), dict) else {}

    return {
        "ok": status.get("ok") is True,
        "pack": "142",
        "title": "Owner Action State Receipts",
        "readiness_score": status.get("readiness_score", 0),
        "base_receipt_count": status.get("base_receipt_count", 0),
        "filtered_receipt_count": status.get("filtered_receipt_count", 0),
        "top_receipt_id": top.get("receipt_id"),
        "top_new_state": top.get("new_state"),
        "state_action_count": state.get("action_count", 0),
        "state_tracked_action_count": state.get("tracked_action_count", 0),
        "panel_path": status.get("panel_path", str(OWNER_ACTION_STATE_RECEIPTS_PANEL_PATH)),
        "status_path": status.get("status_path", str(OWNER_ACTION_STATE_RECEIPTS_STATUS_PATH)),
        "human_reason": "Owner Action State Receipts status card loaded.",
        "soulaana_translation": "Soulaana: Owner action state receipts are visible.",
    }


def reset_owner_action_state_receipts_for_test() -> Dict[str, Any]:
    _write_json(OWNER_ACTION_STATE_RECEIPTS_STATUS_PATH, {
        "ok": True,
        "pack": "142",
        "reset_at": _utc_now(),
        "human_reason": "Owner Action State Receipts reset for test.",
    })
    if OWNER_ACTION_STATE_RECEIPTS_PANEL_PATH.exists():
        try:
            OWNER_ACTION_STATE_RECEIPTS_PANEL_PATH.unlink()
        except Exception:
            pass
    if OWNER_ACTION_STATE_RECEIPT_DETAIL_PANEL_PATH.exists():
        try:
            OWNER_ACTION_STATE_RECEIPT_DETAIL_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "owner_action_state_receipts_reset_for_test",
        "soulaana_translation": "Soulaana: Owner action state receipts view reset for a clean test lane.",
    }
