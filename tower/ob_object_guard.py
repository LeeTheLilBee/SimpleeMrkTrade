
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from tower.ob_object_clearance import evaluate_ob_object_clearance


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


# =============================================================================
# OB OBJECT GUARD MAP
# =============================================================================
# Baby version:
# This map teaches The Tower how to classify "the thing inside the page."
# Page route = room.
# Object = drawer/file/item inside the room.

OB_OBJECT_GUARD_MAP: Dict[str, Dict[str, Any]] = {
    "symbol": {
        "object_type": "symbol",
        "default_action": "view",
        "route_key": "symbol_detail",
        "sensitivity": "confidential",
        "plain": "Per-symbol intelligence, signal history, symbol notes, and chart intelligence.",
    },
    "trade": {
        "object_type": "trade",
        "default_action": "view",
        "route_key": "positions",
        "sensitivity": "restricted",
        "plain": "Specific trade, position, or lifecycle record.",
    },
    "position": {
        "object_type": "trade",
        "default_action": "view",
        "route_key": "positions",
        "sensitivity": "restricted",
        "plain": "Specific open/closed position record.",
    },
    "account": {
        "object_type": "account",
        "default_action": "view",
        "route_key": "positions",
        "sensitivity": "restricted",
        "plain": "Specific account, business account, trust account, or broker-linked account.",
    },
    "export": {
        "object_type": "export",
        "default_action": "download",
        "route_key": "export",
        "sensitivity": "critical",
        "plain": "Specific export/download/share request leaving OB.",
    },
    "analysis_record": {
        "object_type": "analysis_record",
        "default_action": "view",
        "route_key": "analysis_vault",
        "sensitivity": "restricted",
        "plain": "Specific analysis vault record, evidence note, or reasoning object.",
    },
    "mode": {
        "object_type": "mode",
        "default_action": "enter",
        "route_key": "",
        "sensitivity": "mode_specific",
        "plain": "Specific Observatory mode object.",
    },
    "admin_control": {
        "object_type": "admin_control",
        "default_action": "change",
        "route_key": "analysis_vault",
        "sensitivity": "critical",
        "plain": "Specific admin switch, override, kill switch, or sensitive control.",
    },
}


def normalize_object_kind(kind: str) -> str:
    raw = _safe_str(kind).lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "ticker": "symbol",
        "stock": "symbol",
        "option_symbol": "symbol",
        "signal": "symbol",
        "signals": "symbol",
        "my_trade": "trade",
        "my_position": "position",
        "positions": "position",
        "portfolio": "account",
        "broker_account": "account",
        "download": "export",
        "file_export": "export",
        "analysis": "analysis_record",
        "record": "analysis_record",
        "evidence": "analysis_record",
        "control": "admin_control",
        "switch": "admin_control",
        "kill_switch": "admin_control",
    }
    return aliases.get(raw, raw)


def get_ob_object_guard_report() -> Dict[str, Any]:
    return {
        "ok": True,
        "tower_name": "The Tower",
        "object_guard_map": OB_OBJECT_GUARD_MAP,
        "object_guard_count": len(OB_OBJECT_GUARD_MAP),
        "default_object_policy": "deny if unmapped",
        "human_reason": "OB object guard foundation is loaded. Specific objects must be cleared before reveal/action.",
        "soulaana_translation": "Soulaana: The hallway is not enough. Every drawer gets its own key.",
    }


def match_ob_object_guard_policy(
    *,
    object_kind: str,
    object_id: str,
    route_key: str = "",
    action: str = "",
) -> Dict[str, Any]:
    normalized_kind = normalize_object_kind(object_kind)
    object_id = _safe_str(object_id)

    policy = OB_OBJECT_GUARD_MAP.get(normalized_kind)
    if not policy:
        return {
            "ok": True,
            "matched": False,
            "match_type": "unmapped_object_default_deny",
            "object_kind": normalized_kind,
            "object_id": object_id,
            "policy": {
                "object_type": normalized_kind or "unknown",
                "default_action": _safe_str(action, "view"),
                "route_key": _safe_str(route_key, ""),
                "sensitivity": "unknown",
                "plain": "This object kind is not mapped yet. Default deny for private build.",
            },
        }

    merged_policy = dict(policy)
    if route_key:
        merged_policy["route_key"] = route_key
    if action:
        merged_policy["default_action"] = action

    return {
        "ok": True,
        "matched": True,
        "match_type": "object_policy",
        "object_kind": normalized_kind,
        "object_id": object_id,
        "policy": merged_policy,
    }


def evaluate_ob_object_guard(
    *,
    user_id: str,
    object_kind: str,
    object_id: str,
    action: str = "",
    role: str = "",
    user_clearance_level: str = "",
    route_key: str = "",
    owner_user_id: str = "",
    account_id: str = "",
    current_risk_score: int = 0,
    max_allowed_risk_score: int = 85,
    default_deny_unmapped: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    metadata = metadata if isinstance(metadata, dict) else {}

    match = match_ob_object_guard_policy(
        object_kind=object_kind,
        object_id=object_id,
        route_key=route_key,
        action=action,
    )
    policy = match.get("policy", {}) if isinstance(match.get("policy"), dict) else {}

    if match.get("match_type") == "unmapped_object_default_deny" and default_deny_unmapped:
        return {
            "ok": True,
            "allowed": False,
            "decision": "deny",
            "reason_code": "ob_object_unmapped_default_deny",
            "risk_state": "restricted",
            "risk_score": max(_safe_int(current_risk_score, 0), 65),
            "required_actions": ["map_object_policy", "owner_review"],
            "human_reason": "This OB object kind is not mapped yet, so the private build blocks it by default.",
            "soulaana_translation": "Soulaana: Unmapped drawer. I do not open objects that are not on the Tower map.",
            "metadata": {
                "user_id": _safe_str(user_id, "anonymous"),
                "object_kind": normalize_object_kind(object_kind),
                "object_id": _safe_str(object_id),
                "match": match,
                "evaluated_at": _utc_now(),
            },
        }

    object_type = _safe_str(policy.get("object_type"), normalize_object_kind(object_kind))
    final_action = _safe_str(action, _safe_str(policy.get("default_action"), "view"))
    final_route_key = _safe_str(route_key, _safe_str(policy.get("route_key"), ""))

    decision = evaluate_ob_object_clearance(
        user_id=_safe_str(user_id, "anonymous"),
        role=_safe_str(role, ""),
        user_clearance_level=_safe_str(user_clearance_level, ""),
        object_type=object_type,
        object_id=_safe_str(object_id),
        action=final_action,
        route_key=final_route_key,
        owner_user_id=_safe_str(owner_user_id, ""),
        account_id=_safe_str(account_id, ""),
        current_risk_score=_safe_int(current_risk_score, 0),
        max_allowed_risk_score=_safe_int(max_allowed_risk_score, 85),
        metadata={
            "guard_object_kind": normalize_object_kind(object_kind),
            "guard_policy": policy,
            **metadata,
        },
    )

    decision.setdefault("metadata", {})
    if isinstance(decision["metadata"], dict):
        decision["metadata"]["object_guard_match"] = match
        decision["metadata"]["object_guard_policy"] = policy

    return decision


def should_block_ob_object(**kwargs) -> Dict[str, Any]:
    decision = evaluate_ob_object_guard(**kwargs)
    decision["block"] = not bool(decision.get("allowed"))
    return decision


def build_locked_ob_object_response(
    *,
    reason_code: str,
    human_reason: str,
    object_kind: str,
    object_id: str,
    decision: Optional[Dict[str, Any]] = None,
) -> Tuple[str, int]:
    decision = decision if isinstance(decision, dict) else {}
    safe_reason = _safe_str(reason_code, "ob_object_access_denied")
    safe_human = _safe_str(human_reason, "This Observatory object is private.")
    safe_kind = _safe_str(object_kind, "object")
    safe_id = _safe_str(object_id, "unknown")
    soulaana = _safe_str(
        decision.get("soulaana_translation"),
        "Soulaana: This drawer is private. No clearance, no reveal.",
    )

    html = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset='utf-8'>
      <meta name='viewport' content='width=device-width, initial-scale=1'>
      <title>Object Locked</title>
      <style>
        body {{
          margin:0;
          min-height:100vh;
          display:grid;
          place-items:center;
          background:#040615;
          color:#f8fafc;
          font-family:Arial, sans-serif;
        }}
        .card {{
          width:min(720px, calc(100vw - 32px));
          border:1px solid rgba(255,255,255,.16);
          border-radius:24px;
          padding:28px;
          background:linear-gradient(145deg, rgba(15,23,42,.96), rgba(49,46,129,.80));
          box-shadow:0 24px 80px rgba(0,0,0,.42);
        }}
        .kicker {{
          color:#facc15;
          letter-spacing:.18em;
          text-transform:uppercase;
          font-weight:900;
          font-size:.75rem;
        }}
        h1 {{ margin:.5rem 0 1rem; font-size:2rem; }}
        p {{ line-height:1.55; color:#dbeafe; }}
        .reason {{
          margin-top:18px;
          padding:14px;
          border-radius:16px;
          background:rgba(255,255,255,.07);
          color:#fef3c7;
        }}
        code {{ color:#bae6fd; }}
      </style>
    </head>
    <body>
      <section class='card'>
        <div class='kicker'>THE OBSERVATORY OBJECT GUARD</div>
        <h1>Private drawer locked.</h1>
        <p>{soulaana}</p>
        <div class='reason'>
          <strong>{safe_reason}</strong><br>
          {safe_human}<br>
          <code>{safe_kind}:{safe_id}</code>
        </div>
      </section>
    </body>
    </html>
    """
    return html, 403
