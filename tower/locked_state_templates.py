
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _escape_html(value: Any) -> str:
    text = _safe_str(value)
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
    )


def _redact_sensitive_text(value: Any) -> str:
    text = _safe_str(value)
    lowered = text.lower()

    # Redact actual secret-bearing text, not normal policy/action names.
    if "tower_keycard=" in lowered:
        return "[REDACTED]"
    if "raw_token" in lowered:
        return "[REDACTED]"
    if "bearer " in lowered:
        return "[REDACTED]"
    if lowered.startswith("authorization:") or lowered.startswith("authorization="):
        return "[REDACTED]"

    return text


def build_locked_state_payload(
    *,
    lock_type: str = "route",
    title: str = "Restricted Corridor",
    reason_code: str = "clearance_required",
    human_reason: str = "Clearance is required before this area can open.",
    path: str = "",
    object_type: str = "",
    object_id: str = "",
    mode_name: str = "",
    user_id: str = "anonymous",
    risk_state: str = "restricted",
    risk_score: int = 60,
    required_actions: list[str] | None = None,
    status_code: int = 403,
    soulaana_translation: str = "",
) -> Dict[str, Any]:
    required_actions = required_actions if isinstance(required_actions, list) else []

    clean_path = _redact_sensitive_text(path)
    clean_reason = _redact_sensitive_text(human_reason)
    clean_soulaana = _redact_sensitive_text(soulaana_translation)

    if not clean_soulaana:
        clean_soulaana = "Soulaana: No clearance, no corridor. The Tower stayed quiet and kept the protected room closed."

    return {
        "ok": False,
        "status": "locked",
        "status_code": int(status_code or 403),
        "event_type": "tower_locked_state",
        "generated_at": _utc_now(),
        "lock_type": _safe_str(lock_type, "route"),
        "title": _safe_str(title, "Restricted Corridor"),
        "reason_code": _safe_str(reason_code, "clearance_required"),
        "human_reason": clean_reason,
        "path": clean_path,
        "object_type": _safe_str(object_type),
        "object_id": _safe_str(object_id),
        "mode_name": _safe_str(mode_name),
        "user_id": _safe_str(user_id, "anonymous"),
        "risk_state": _safe_str(risk_state, "restricted"),
        "risk_score": int(risk_score or 0),
        "required_actions": [_redact_sensitive_text(item) for item in required_actions],
        "soulaana_translation": clean_soulaana,
        "tower_language": {
            "headline": "CLEARANCE REQUIRED",
            "subhead": "This corridor is protected by The Tower.",
            "signal": "Restricted Zone",
            "control": "Access held at the clearance gate.",
        },
    }


def render_locked_state_html(payload: Dict[str, Any]) -> str:
    payload = payload if isinstance(payload, dict) else build_locked_state_payload()

    title = _escape_html(payload.get("title", "Restricted Corridor"))
    reason = _escape_html(payload.get("human_reason", "Clearance is required."))
    reason_code = _escape_html(payload.get("reason_code", "clearance_required"))
    lock_type = _escape_html(payload.get("lock_type", "route"))
    path = _escape_html(payload.get("path", ""))
    object_type = _escape_html(payload.get("object_type", ""))
    object_id = _escape_html(payload.get("object_id", ""))
    mode_name = _escape_html(payload.get("mode_name", ""))
    risk_state = _escape_html(payload.get("risk_state", "restricted"))
    risk_score = _escape_html(payload.get("risk_score", 0))
    soulaana = _escape_html(payload.get("soulaana_translation", "Soulaana: Clearance required."))
    generated_at = _escape_html(payload.get("generated_at", ""))

    required_actions = payload.get("required_actions", [])
    if not isinstance(required_actions, list):
        required_actions = []

    actions_html = ""
    if required_actions:
        actions_html = "".join(f"<li>{_escape_html(action)}</li>" for action in required_actions)
    else:
        actions_html = "<li>Return to the authorized Tower entry point.</li><li>Request owner clearance if this access should exist.</li>"

    object_line = ""
    if object_type or object_id:
        object_line = f"""
          <div class="locked-data-row">
            <span>Object</span>
            <strong>{object_type}:{object_id}</strong>
          </div>
        """

    mode_line = ""
    if mode_name:
        mode_line = f"""
          <div class="locked-data-row">
            <span>Mode</span>
            <strong>{mode_name}</strong>
          </div>
        """

    path_line = ""
    if path:
        path_line = f"""
          <div class="locked-data-row">
            <span>Requested corridor</span>
            <strong>{path}</strong>
          </div>
        """

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>The Tower · Clearance Required</title>
  <style>
    :root {{
      --bg0: #050706;
      --bg1: #0b1110;
      --panel: rgba(255,255,255,.065);
      --panel2: rgba(255,255,255,.035);
      --line: rgba(255,255,255,.16);
      --text: #f4f7f5;
      --muted: rgba(244,247,245,.68);
      --gold: #d8b875;
      --danger: #ff6b7a;
      --blue: #9bbcff;
      --green: #8ef0c1;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 16% 12%, rgba(216,184,117,.14), transparent 32%),
        radial-gradient(circle at 84% 16%, rgba(155,188,255,.12), transparent 30%),
        radial-gradient(circle at 45% 88%, rgba(142,240,193,.10), transparent 35%),
        linear-gradient(135deg, var(--bg0), var(--bg1));
      display: grid;
      place-items: center;
      padding: 28px;
    }}
    .tower-shell {{
      width: min(1040px, 100%);
      border: 1px solid var(--line);
      border-radius: 34px;
      background: linear-gradient(145deg, rgba(255,255,255,.08), rgba(255,255,255,.032));
      box-shadow: 0 28px 90px rgba(0,0,0,.45);
      overflow: hidden;
      position: relative;
    }}
    .tower-shell:before {{
      content: "";
      position: absolute;
      inset: -1px;
      background:
        linear-gradient(90deg, transparent, rgba(216,184,117,.16), transparent),
        repeating-linear-gradient(90deg, rgba(255,255,255,.028) 0 1px, transparent 1px 82px);
      pointer-events: none;
      opacity: .55;
    }}
    .tower-topbar {{
      display: flex;
      justify-content: space-between;
      gap: 18px;
      padding: 22px 26px;
      border-bottom: 1px solid var(--line);
      background: rgba(0,0,0,.18);
      position: relative;
      z-index: 2;
    }}
    .tower-brand {{
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}
    .tower-brand span {{
      font-size: 12px;
      letter-spacing: .22em;
      text-transform: uppercase;
      color: var(--gold);
    }}
    .tower-brand strong {{
      font-size: 20px;
      letter-spacing: .02em;
    }}
    .tower-badge {{
      align-self: flex-start;
      border: 1px solid rgba(255,107,122,.34);
      color: #ffd0d5;
      background: rgba(255,107,122,.10);
      padding: 9px 13px;
      border-radius: 999px;
      font-size: 12px;
      letter-spacing: .14em;
      text-transform: uppercase;
    }}
    .tower-body {{
      display: grid;
      grid-template-columns: 1.15fr .85fr;
      gap: 0;
      position: relative;
      z-index: 2;
    }}
    .tower-main {{
      padding: 38px;
      border-right: 1px solid var(--line);
    }}
    .kicker {{
      color: var(--gold);
      font-size: 12px;
      letter-spacing: .22em;
      text-transform: uppercase;
      margin-bottom: 14px;
    }}
    h1 {{
      margin: 0 0 14px 0;
      font-size: clamp(34px, 5vw, 62px);
      line-height: .95;
      letter-spacing: -.055em;
    }}
    .reason {{
      color: var(--muted);
      font-size: 17px;
      line-height: 1.65;
      max-width: 620px;
      margin: 0 0 24px 0;
    }}
    .soulaana {{
      border: 1px solid rgba(216,184,117,.22);
      background: rgba(216,184,117,.08);
      padding: 16px;
      border-radius: 22px;
      line-height: 1.55;
      color: #fff3d2;
    }}
    .tower-side {{
      padding: 30px;
      background: rgba(0,0,0,.12);
    }}
    .locked-data {{
      display: grid;
      gap: 12px;
    }}
    .locked-data-row {{
      padding: 14px;
      border-radius: 18px;
      border: 1px solid var(--line);
      background: var(--panel2);
    }}
    .locked-data-row span {{
      display: block;
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .16em;
      margin-bottom: 6px;
    }}
    .locked-data-row strong {{
      word-break: break-word;
      font-size: 14px;
    }}
    .actions {{
      margin-top: 18px;
      border: 1px solid rgba(155,188,255,.22);
      background: rgba(155,188,255,.07);
      border-radius: 22px;
      padding: 16px;
    }}
    .actions h2 {{
      margin: 0 0 10px 0;
      font-size: 15px;
      letter-spacing: .08em;
      text-transform: uppercase;
    }}
    .actions ul {{
      margin: 0;
      padding-left: 20px;
      color: var(--muted);
      line-height: 1.7;
    }}
    .footer {{
      padding: 18px 26px;
      border-top: 1px solid var(--line);
      display: flex;
      justify-content: space-between;
      gap: 16px;
      color: var(--muted);
      font-size: 12px;
      position: relative;
      z-index: 2;
      background: rgba(0,0,0,.16);
    }}
    @media (max-width: 820px) {{
      .tower-body {{ grid-template-columns: 1fr; }}
      .tower-main {{ border-right: 0; border-bottom: 1px solid var(--line); }}
      .tower-topbar, .footer {{ flex-direction: column; }}
    }}
  </style>
</head>
<body>
  <main class="tower-shell" data-lock-type="{lock_type}">
    <section class="tower-topbar">
      <div class="tower-brand">
        <span>The Tower</span>
        <strong>Clearance Gate</strong>
      </div>
      <div class="tower-badge">Restricted Zone</div>
    </section>

    <section class="tower-body">
      <div class="tower-main">
        <div class="kicker">CLEARANCE REQUIRED · {reason_code}</div>
        <h1>{title}</h1>
        <p class="reason">{reason}</p>
        <div class="soulaana">{soulaana}</div>
      </div>

      <aside class="tower-side">
        <div class="locked-data">
          <div class="locked-data-row">
            <span>Lock type</span>
            <strong>{lock_type}</strong>
          </div>
          {path_line}
          {object_line}
          {mode_line}
          <div class="locked-data-row">
            <span>Risk state</span>
            <strong>{risk_state} · {risk_score}</strong>
          </div>
        </div>

        <div class="actions">
          <h2>Next allowed moves</h2>
          <ul>{actions_html}</ul>
        </div>
      </aside>
    </section>

    <section class="footer">
      <span>Access held at the clearance gate.</span>
      <span>{generated_at}</span>
    </section>
  </main>
</body>
</html>"""


def render_locked_state_response(
    *,
    lock_type: str = "route",
    title: str = "Restricted Corridor",
    reason_code: str = "clearance_required",
    human_reason: str = "Clearance is required before this area can open.",
    path: str = "",
    object_type: str = "",
    object_id: str = "",
    mode_name: str = "",
    user_id: str = "anonymous",
    risk_state: str = "restricted",
    risk_score: int = 60,
    required_actions: list[str] | None = None,
    status_code: int = 403,
    soulaana_translation: str = "",
) -> tuple[str, int, Dict[str, Any]]:
    payload = build_locked_state_payload(
        lock_type=lock_type,
        title=title,
        reason_code=reason_code,
        human_reason=human_reason,
        path=path,
        object_type=object_type,
        object_id=object_id,
        mode_name=mode_name,
        user_id=user_id,
        risk_state=risk_state,
        risk_score=risk_score,
        required_actions=required_actions,
        status_code=status_code,
        soulaana_translation=soulaana_translation,
    )
    html = render_locked_state_html(payload)
    return html, payload["status_code"], payload



# ================================================================================
# PACK067_LOCKED_STATE_VARIANTS
# ================================================================================
# Variant helpers for route/object/mode/export/unmapped locked states.
# ================================================================================

def render_route_locked_response(
    *,
    path: str = "",
    reason_code: str = "ob_route_clearance_required",
    human_reason: str = "This Observatory corridor requires Tower clearance.",
    user_id: str = "anonymous",
    risk_state: str = "restricted",
    risk_score: int = 60,
    required_actions: list[str] | None = None,
    soulaana_translation: str = "",
) -> tuple[str, int, Dict[str, Any]]:
    if required_actions is None:
        required_actions = ["return_to_tower_entry", "request_route_clearance"]

    if not soulaana_translation:
        soulaana_translation = "Soulaana: This corridor is not public. The Tower held the line."

    return render_locked_state_response(
        lock_type="route",
        title="Observatory Corridor Locked",
        reason_code=reason_code,
        human_reason=human_reason,
        path=path,
        user_id=user_id,
        risk_state=risk_state,
        risk_score=risk_score,
        required_actions=required_actions,
        soulaana_translation=soulaana_translation,
    )


def render_object_locked_response(
    *,
    object_type: str = "object",
    object_id: str = "",
    path: str = "",
    reason_code: str = "ob_object_clearance_required",
    human_reason: str = "This Observatory object requires exact object clearance.",
    user_id: str = "anonymous",
    risk_state: str = "restricted",
    risk_score: int = 70,
    required_actions: list[str] | None = None,
    soulaana_translation: str = "",
) -> tuple[str, int, Dict[str, Any]]:
    if required_actions is None:
        required_actions = ["request_object_clearance", "owner_review"]

    if not soulaana_translation:
        soulaana_translation = "Soulaana: I did not open that drawer. Exact object clearance is required."

    pretty = f"{object_type.title()} Locked" if object_type else "Object Locked"

    return render_locked_state_response(
        lock_type="object",
        title=pretty,
        reason_code=reason_code,
        human_reason=human_reason,
        path=path,
        object_type=object_type,
        object_id=object_id,
        user_id=user_id,
        risk_state=risk_state,
        risk_score=risk_score,
        required_actions=required_actions,
        soulaana_translation=soulaana_translation,
    )


def render_mode_locked_response(
    *,
    mode_name: str = "",
    path: str = "",
    reason_code: str = "ob_mode_clearance_required",
    human_reason: str = "This Observatory mode requires Tower mode clearance.",
    user_id: str = "anonymous",
    risk_state: str = "restricted",
    risk_score: int = 80,
    required_actions: list[str] | None = None,
    soulaana_translation: str = "",
) -> tuple[str, int, Dict[str, Any]]:
    if required_actions is None:
        required_actions = ["request_mode_clearance", "complete_required_authorization"]

    label = _safe_str(mode_name, "Mode").replace("_", " ").title()

    if not soulaana_translation:
        soulaana_translation = "Soulaana: Mode access is not a vibe. The Tower needs the right clearance first."

    return render_locked_state_response(
        lock_type="mode",
        title=f"{label} Locked",
        reason_code=reason_code,
        human_reason=human_reason,
        path=path,
        mode_name=mode_name,
        user_id=user_id,
        risk_state=risk_state,
        risk_score=risk_score,
        required_actions=required_actions,
        soulaana_translation=soulaana_translation,
    )


def render_export_locked_response(
    *,
    export_id: str = "",
    path: str = "",
    reason_code: str = "ob_export_clearance_required",
    human_reason: str = "Exports and downloads require critical Tower clearance.",
    user_id: str = "anonymous",
    risk_state: str = "restricted",
    risk_score: int = 85,
    required_actions: list[str] | None = None,
    soulaana_translation: str = "",
) -> tuple[str, int, Dict[str, Any]]:
    if required_actions is None:
        required_actions = ["request_export_clearance", "owner_review", "log_export_reason"]

    if not soulaana_translation:
        soulaana_translation = "Soulaana: Nothing leaves the Observatory without export clearance."

    return render_locked_state_response(
        lock_type="export",
        title="Export Locked",
        reason_code=reason_code,
        human_reason=human_reason,
        path=path,
        object_type="export",
        object_id=export_id,
        user_id=user_id,
        risk_state=risk_state,
        risk_score=risk_score,
        required_actions=required_actions,
        soulaana_translation=soulaana_translation,
    )


def render_unmapped_locked_response(
    *,
    path: str = "",
    object_type: str = "",
    object_id: str = "",
    user_id: str = "anonymous",
    reason_code: str = "unmapped_default_deny",
    human_reason: str = "This protected surface is not mapped yet, so The Tower blocks it by default.",
    soulaana_translation: str = "",
) -> tuple[str, int, Dict[str, Any]]:
    if not soulaana_translation:
        soulaana_translation = "Soulaana: I do not open doors that are not on the map. Default deny."

    return render_locked_state_response(
        lock_type="unmapped",
        title="Unmapped Corridor Locked",
        reason_code=reason_code,
        human_reason=human_reason,
        path=path,
        object_type=object_type,
        object_id=object_id,
        user_id=user_id,
        risk_state="restricted",
        risk_score=75,
        required_actions=["map_policy", "owner_review", "keep_default_deny_until_mapped"],
        soulaana_translation=soulaana_translation,
    )


def render_decision_locked_response(
    *,
    decision: Dict[str, Any],
    path: str = "",
    object_type: str = "",
    object_id: str = "",
    mode_name: str = "",
    user_id: str = "anonymous",
) -> tuple[str, int, Dict[str, Any]]:
    decision = decision if isinstance(decision, dict) else {}

    reason_code = _safe_str(decision.get("reason_code"), "clearance_required")
    human_reason = _safe_str(decision.get("human_reason"), "Clearance is required.")
    risk_state = _safe_str(decision.get("risk_state"), "restricted")
    risk_score = int(decision.get("risk_score", 60) or 60)
    required_actions = decision.get("required_actions") if isinstance(decision.get("required_actions"), list) else []
    soulaana = _safe_str(decision.get("soulaana_translation"), "")

    metadata = decision.get("metadata") if isinstance(decision.get("metadata"), dict) else {}
    final_user_id = _safe_str(user_id, _safe_str(metadata.get("user_id"), "anonymous"))
    final_path = _safe_str(path, _safe_str(metadata.get("guard_path"), ""))
    final_object_type = _safe_str(object_type, _safe_str(metadata.get("object_type"), ""))
    final_object_id = _safe_str(object_id, _safe_str(metadata.get("object_id"), ""))
    final_mode_name = _safe_str(mode_name, _safe_str(metadata.get("mode_name"), ""))

    if "unmapped" in reason_code:
        return render_unmapped_locked_response(
            path=final_path,
            object_type=final_object_type,
            object_id=final_object_id,
            user_id=final_user_id,
            reason_code=reason_code,
            human_reason=human_reason,
            soulaana_translation=soulaana,
        )

    if final_mode_name or reason_code.startswith("ob_mode"):
        return render_mode_locked_response(
            mode_name=final_mode_name,
            path=final_path,
            reason_code=reason_code,
            human_reason=human_reason,
            user_id=final_user_id,
            risk_state=risk_state,
            risk_score=risk_score,
            required_actions=required_actions,
            soulaana_translation=soulaana,
        )

    if final_object_type == "export" or "export" in reason_code:
        return render_export_locked_response(
            export_id=final_object_id,
            path=final_path,
            reason_code=reason_code,
            human_reason=human_reason,
            user_id=final_user_id,
            risk_state=risk_state,
            risk_score=risk_score,
            required_actions=required_actions,
            soulaana_translation=soulaana,
        )

    if final_object_type or final_object_id or reason_code.startswith("ob_object") or reason_code == "parent_route_clearance_failed":
        return render_object_locked_response(
            object_type=final_object_type or "object",
            object_id=final_object_id,
            path=final_path,
            reason_code=reason_code,
            human_reason=human_reason,
            user_id=final_user_id,
            risk_state=risk_state,
            risk_score=risk_score,
            required_actions=required_actions,
            soulaana_translation=soulaana,
        )

    return render_route_locked_response(
        path=final_path,
        reason_code=reason_code,
        human_reason=human_reason,
        user_id=final_user_id,
        risk_state=risk_state,
        risk_score=risk_score,
        required_actions=required_actions,
        soulaana_translation=soulaana,
    )

