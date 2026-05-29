from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

TOWER_ROOT = Path(__file__).resolve().parent
DATA_DIR = TOWER_ROOT / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

SECURITY_COMMAND_HTML = DATA_DIR / 'security_command_dashboard.html'
SECURITY_COMMAND_JSON = DATA_DIR / 'security_command_dashboard.json'
SECURITY_COMMAND_VIEW_JSON = DATA_DIR / 'security_command_dashboard_view.json'

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default

def _write_json(path: Path, payload: Any) -> None:
    temp = path.with_suffix(path.suffix + '.tmp')
    with temp.open('w', encoding='utf-8') as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
    temp.replace(path)

def _get_tower_status_safe() -> Dict[str, Any]:
    try:
        from tower.tower_status import get_tower_status
        payload = get_tower_status()
        if isinstance(payload, dict):
            payload.setdefault('ok', True)
            return payload
    except Exception as exc:
        return {'ok': False, 'tower_name': 'The Tower', 'reason_code': 'tower_status_unavailable', 'human_reason': 'Tower status could not be loaded.', 'error': f'{type(exc).__name__}: {exc}'}
    return {'ok': False, 'tower_name': 'The Tower', 'reason_code': 'tower_status_bad_payload', 'human_reason': 'Tower status returned an invalid payload.'}

def _health_score(status: Dict[str, Any]) -> Dict[str, Any]:
    open_items = _safe_int(status.get('security_inbox_open'), 0)
    critical = _safe_int(status.get('security_inbox_critical'), 0)
    high = _safe_int(status.get('security_inbox_high'), 0)
    urgent_groups = _safe_int(status.get('security_review_urgent_groups'), 0)
    audit_ok = bool(status.get('audit_chain_ok', False))
    score = 100
    score -= min(30, critical * 2)
    score -= min(22, high // 3)
    score -= min(18, urgent_groups * 2)
    score -= min(12, open_items // 12)
    if not audit_ok:
        score -= 35
    score = max(0, min(100, score))
    if score >= 85:
        label = 'Calm'
        posture = 'The Tower is quiet.'
    elif score >= 68:
        label = 'Guarded'
        posture = 'Attention required, but the core is holding.'
    elif score >= 45:
        label = 'Strained'
        posture = 'Security pressure is elevated.'
    else:
        label = 'Critical'
        posture = 'Owner review should happen now.'
    return {
        'score': score,
        'label': label,
        'posture': posture,
        'soulaana': 'Soulaana: Start with access risk, then exports, then admin keys. Leave Live Automated sealed unless every gate is clean.',
        'factors': [
            {'label': 'Audit chain', 'value': 'Clean' if audit_ok else 'Needs review'},
            {'label': 'Urgent groups', 'value': str(urgent_groups)},
            {'label': 'Open inbox', 'value': str(open_items)},
        ],
    }

def build_security_command_view(tower_user_id: str = 'owner_solice') -> Dict[str, Any]:
    status = _get_tower_status_safe()
    health = _health_score(status)
    critical = _safe_int(status.get('security_inbox_critical'), 0)
    high = _safe_int(status.get('security_inbox_high'), 0)
    open_items = _safe_int(status.get('security_inbox_open'), 0)
    urgent_groups = _safe_int(status.get('security_review_urgent_groups'), 0)
    step_up_pending = _safe_int(status.get('step_up_pending'), 0)
    evidence_open = _safe_int(status.get('evidence_open_capsules'), 0)
    exports_step_up = _safe_int(status.get('export_step_up_required'), 0)
    admin_step_up = _safe_int(status.get('admin_action_step_up_required'), 0)
    door_inbox_open = _safe_int(status.get('door_swipe_security_inbox_open'), 0)
    door_inbox_total = _safe_int(status.get('door_swipe_security_inbox_total'), 0)
    door_inbox_by_severity = status.get('door_swipe_security_inbox_by_severity', {})
    door_inbox_recent = status.get('door_swipe_security_inbox_recent', [])
    if not isinstance(door_inbox_by_severity, dict):
        door_inbox_by_severity = {}
    if not isinstance(door_inbox_recent, list):
        door_inbox_recent = []
    return {
        'ok': True,
        'view_name': 'The Tower Security Command View',
        'generated_at': _utc_now(),
        'tower_user_id': tower_user_id,
        'state': 'attention_required' if urgent_groups or critical or high else 'calm',
        'status': status,
        'health': health,
        'command_stats': [
            {'label': 'Owner attention', 'value': str(urgent_groups), 'note': 'urgent groups'},
            {'label': 'Security inbox', 'value': str(open_items), 'note': 'open signals'},
            {'label': 'Access swipes', 'value': str(status.get('door_swipe_audit_denied', 0)), 'note': 'denied receipts'},
            {'label': 'Door inbox', 'value': str(door_inbox_open), 'note': 'review items'},
            {'label': 'Evidence chain', 'value': 'Clean' if status.get('audit_chain_ok') else 'Review', 'note': 'audit integrity'},
            {'label': 'Step-up gate', 'value': str(step_up_pending), 'note': 'pending keys'},
        ],
        'attention_lanes': [
            {'title': 'Access risk', 'signal': f'{critical} critical / {high} high', 'plain': 'Soulaana: Review risky sessions, new devices, failed attempts, and anything that smells like forced entry.', 'next': 'Review access-risk group first.', 'priority': 'Priority 1'},
            {'title': 'Protected exports', 'signal': f'{exports_step_up} waiting', 'plain': 'Soulaana: Exports are how information leaves the building. Approve only what belongs, redact what is too sensitive, and deny anything unclear.', 'next': 'Check export requests after access risk.', 'priority': 'Priority 2'},
            {'title': 'Admin keys', 'signal': f'{admin_step_up} step-up', 'plain': 'Soulaana: Admin changes decide who can touch doors later. Match actor, target, permission, and reason.', 'next': 'Review admin authority changes.', 'priority': 'Priority 3'},
            {'title': 'Door access inbox', 'signal': f'{door_inbox_open} open', 'plain': 'Soulaana: These are the door swipes that rose above quiet receipts and became owner-review items. Start here if the count is not zero.', 'next': 'Review open door access issues before deeper archive work.', 'priority': 'Priority 4'},
            {'title': 'Door-swipe receipts', 'signal': f"{status.get('door_swipe_audit_denied', 0)} denied / {status.get('door_swipe_audit_allowed', 0)} allowed", 'plain': 'Soulaana: Every Tower door swipe leaves a receipt now. Allowed, denied, wrong-door, and missing-key attempts are visible without exposing raw keycards.', 'next': 'Review repeated denies or wrong-door attempts first.', 'priority': 'Priority 5'},
            {'title': 'Evidence capsules', 'signal': f'{evidence_open} open', 'plain': 'Soulaana: Evidence capsules preserve the why. They are the receipts.', 'next': 'Open only when you need the story behind a decision.', 'priority': 'Priority 5'},
        ],
        'system_panels': [
            {'label': 'Identity Root', 'value': str(status.get('total_users', 0)), 'detail': 'known users', 'code': 'ID'},
            {'label': 'Threat Weather', 'value': health['label'], 'detail': health['posture'], 'code': 'TW'},
            {'label': 'Evidence Rings', 'value': str(evidence_open), 'detail': 'open capsules', 'code': 'ER'},
            {'label': 'OB Bridge', 'value': 'Live', 'detail': 'protected route active', 'code': 'OB'},
            {'label': 'Step-up Gate', 'value': str(step_up_pending), 'detail': 'pending approvals', 'code': 'SG'},
            {'label': 'Mode Seal', 'value': 'Closed', 'detail': 'Live automation remains sealed', 'code': 'MS'},
            {'label': 'Door Receipts', 'value': str(status.get('door_swipe_audit_total', 0)), 'detail': 'door-swipe audit capsules', 'code': 'DR'},
            {'label': 'Door Inbox', 'value': str(door_inbox_open), 'detail': 'review-worthy door swipes', 'code': 'DI'},
        ],
        'workflow': [
            {'title': 'Verify the gate', 'priority': 'Priority 1', 'lane': 'Access risk', 'why': 'Unsafe sessions can touch everything else if they get through.', 'action': 'Review devices, failed attempts, rapid denials, and session risk.'},
            {'title': 'Protect the vault', 'priority': 'Priority 2', 'lane': 'Protected exports', 'why': 'Exports can leak sensitive OB records.', 'action': 'Approve, deny, or redact export requests.'},
            {'title': 'Check admin keys', 'priority': 'Priority 3', 'lane': 'Admin authority', 'why': 'Permission changes decide who can touch the system later.', 'action': 'Match actor, target, permission, reason, and risk.'},
            {'title': 'Confirm sealed modes', 'priority': 'Priority 4', 'lane': 'Live Automated lock', 'why': 'This is a final confirmation step.', 'action': 'Make sure Live Automated remains locked unless every gate is clean.'},
        ],
        'door_security_inbox': {
            'open': door_inbox_open,
            'total': door_inbox_total,
            'by_severity': door_inbox_by_severity,
            'recent': door_inbox_recent[-6:],
        },
        'primary_owner_tasks': urgent_groups,
        'open_inbox': open_items,
    }

def _render_stat_cards(view: Dict[str, Any]) -> str:
    cards = []
    for item in view.get('command_stats', []):
        cards.append(f"<article class='card'><p class='tiny'>{item['label']}</p><h3>{item['value']}</h3><p>{item['note']}</p></article>")
    return ''.join(cards)

def _render_lanes(view: Dict[str, Any]) -> str:
    cards = []
    for lane in view.get('attention_lanes', []):
        cards.append(f"<article class='lane'><div><p class='tiny'>{lane['priority']}</p><h3>{lane['title']}</h3></div><span>{lane['signal']}</span><p>{lane['plain']}</p><strong>{lane['next']}</strong></article>")
    return ''.join(cards)

def _render_system_panels(view: Dict[str, Any]) -> str:
    cards = []
    for panel in view.get('system_panels', []):
        cards.append(f"<article class='panel'><p class='tiny'>{panel['code']}</p><h3>{panel['value']}</h3><p>{panel['label']}</p><small>{panel['detail']}</small></article>")
    return ''.join(cards)

def _render_workflow(view: Dict[str, Any]) -> str:
    cards = []
    for step in view.get('workflow', []):
        cards.append(f"<article class='step'><p class='tiny'>{step['priority']} · {step['lane']}</p><h3>{step['title']}</h3><p><b>Why:</b> {step['why']}</p><p><b>Action:</b> {step['action']}</p></article>")
    return ''.join(cards)

def render_security_command_dashboard_html(tower_user_id: str = 'owner_solice') -> str:
    view = build_security_command_view(tower_user_id=tower_user_id)
    health = view['health']
    stats = _render_stat_cards(view)
    lanes = _render_lanes(view)
    panels = _render_system_panels(view)
    workflow = _render_workflow(view)
    generated = view['generated_at']
    score = health['score']
    label = health['label']
    posture = health['posture']
    soulaana = health['soulaana']
    css = '''
    <style>
      body { margin:0; min-height:100vh; background:#030503; color:#f5f5f4; font-family:Arial, sans-serif; }
      body:before { content:''; position:fixed; inset:0; background:radial-gradient(circle at 20% 10%, rgba(132,204,22,.14), transparent 28%), radial-gradient(circle at 70% 80%, rgba(16,185,129,.09), transparent 30%); pointer-events:none; }
      main { position:relative; width:min(1180px, calc(100vw - 32px)); margin:0 auto; padding:38px 0 70px; }
      .masthead,.hero,.section { border:1px solid rgba(245,245,244,.14); background:rgba(5,8,6,.88); border-radius:34px; padding:24px; box-shadow:0 24px 70px rgba(0,0,0,.55); margin-bottom:24px; }
      .masthead { display:flex; justify-content:space-between; gap:20px; align-items:center; flex-wrap:wrap; }
      .brand { display:flex; align-items:center; gap:18px; }
      .mark { width:76px; height:76px; display:grid; place-items:center; border-radius:24px; border:1px solid rgba(217,249,157,.25); background:rgba(217,249,157,.08); color:#d9f99d; font-size:38px; font-weight:900; }
      h1 { margin:0; font-size:clamp(3rem, 7vw, 5.4rem); letter-spacing:-.06em; }
      h2 { margin:.4rem 0 0; font-size:clamp(2rem, 4vw, 3rem); letter-spacing:-.04em; }
      h3 { margin:.35rem 0; font-size:1.45rem; }
      p { color:#a8a29e; line-height:1.65; }
      .tiny { margin:0; color:#78716c; text-transform:uppercase; letter-spacing:.2em; font-size:.7rem; font-weight:900; }
      .hero { display:grid; grid-template-columns:minmax(0,1fr) 340px; gap:20px; }
      .gauge { border:1px solid rgba(217,249,157,.18); background:#071009; border-radius:28px; padding:22px; display:grid; grid-template-columns:150px 1fr; gap:20px; align-items:center; margin:20px 0; }
      .circle { width:140px; height:140px; border-radius:50%; border:12px solid rgba(217,249,157,.8); display:grid; place-items:center; color:#d9f99d; font-size:2.4rem; font-weight:900; }
      .grid { display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; }
      .system { display:grid; grid-template-columns:repeat(6, 1fr); gap:12px; }
      .lanes { display:grid; grid-template-columns:repeat(2, 1fr); gap:14px; }
      .workflow { display:grid; grid-template-columns:repeat(2, 1fr); gap:14px; }
      .card,.panel,.lane,.step,.soulaana { border:1px solid rgba(245,245,244,.12); background:#050806; border-radius:22px; padding:16px; }
      .pill { display:inline-flex; border:1px solid rgba(217,249,157,.25); background:rgba(217,249,157,.08); color:#d9f99d; border-radius:999px; padding:8px 12px; font-weight:800; }
      .soulaana { background:#101510; }
      button { border:1px solid rgba(217,249,157,.25); background:rgba(217,249,157,.08); color:#d9f99d; border-radius:999px; padding:12px 16px; font-weight:800; }
      footer { color:#78716c; text-align:center; margin-top:30px; line-height:1.6; }
      @media(max-width:900px){ .hero,.grid,.system,.lanes,.workflow,.gauge { grid-template-columns:1fr; } }
    </style>
    '''
    return f'''<!doctype html>
<html lang='en'>
<head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>The Tower Security Command View</title>{css}</head>
<body>
<main>
<section class='masthead'>
  <div class='brand'><div class='mark'>T</div><div><p class='tiny'>The Tower behind OB</p><h1>The Tower</h1></div></div>
  <div class='soulaana'><p class='tiny'>Role</p><p>The private security force behind OB, watching gates, roots, keys, and vault paths before anything reaches the Observatory.</p></div>
</section>
<section class='hero'>
  <div>
    <p class='tiny'>Command overview</p><h2>What needs attention</h2><p>This panel is only for the current security picture: status, pressure, and what needs your hand.</p>
    <section class='gauge'><div class='circle'>{score}</div><div><p class='tiny'>Tower health gauge</p><h2>{label}</h2><span class='pill'>{posture}</span><p>{soulaana}</p></div></section>
    <div class='grid'>{stats}</div>
  </div>
  <aside class='soulaana'><p class='tiny'>Soulaana</p><h3>Plain-language guardian</h3><p>I translate The Tower for OB. I do not make the page louder. I make the decision clearer.</p><button>Walk me through it with Soulaana</button></aside>
</section>
<section class='section'><p class='tiny'>System panels</p><h2>Security instruments behind OB</h2><div class='system'>{panels}</div></section>
<section class='section'><p class='tiny'>Attention lanes</p><h2>Priority review</h2><div class='lanes'>{lanes}</div></section>
<section class='section'><p class='tiny'>Soulaana workflow</p><h2>Walk me through it</h2><p>Exit workflow · Skip this · Back · Next priority</p><div class='workflow'>{workflow}</div></section>
<footer>The Tower is the security force behind OB: rooted, quiet, strict, and hard to casually pass.<br>Generated at {generated}.</footer>
</main>
</body>
</html>'''

def save_security_command_dashboard_html(tower_user_id: str = 'owner_solice') -> Dict[str, Any]:
    view = build_security_command_view(tower_user_id=tower_user_id)
    html_text = render_security_command_dashboard_html(tower_user_id=tower_user_id)
    SECURITY_COMMAND_HTML.write_text(html_text, encoding='utf-8')
    _write_json(SECURITY_COMMAND_JSON, view)
    _write_json(SECURITY_COMMAND_VIEW_JSON, {'ok': True, 'view_name': view.get('view_name'), 'generated_at': view.get('generated_at'), 'state': view.get('state'), 'tower_user_id': tower_user_id, 'html_path': str(SECURITY_COMMAND_HTML), 'json_path': str(SECURITY_COMMAND_JSON)})
    return {'ok': True, 'status': 'saved', 'view_name': view.get('view_name'), 'state': view.get('state'), 'open_inbox': view.get('open_inbox'), 'primary_owner_tasks': view.get('primary_owner_tasks'), 'path': str(SECURITY_COMMAND_HTML), 'bytes': len(html_text.encode('utf-8'))}



# ================================================================================
# PACK059_OBJECT_SECURITY_INBOX_UI_HELPERS
# ================================================================================
# Adds object-security-inbox fields to Tower Security Command view payloads.
# ================================================================================

def _pack059_object_security_inbox_panel_html():
    try:
        from tower.ob_object_audit_capsules import summarize_ob_object_security_inbox

        summary = summarize_ob_object_security_inbox(limit=6)
        total = summary.get("total", 0)
        open_count = summary.get("open", 0)
        by_severity = summary.get("by_severity", {})
        by_object_type = summary.get("by_object_type", {})
        recent = summary.get("recent", [])

        recent_cards = []
        for item in recent[-6:]:
            title = str(item.get("title", "Object security review"))
            severity = str(item.get("severity", "unknown"))
            status = str(item.get("status", "open"))
            owner_action = str(item.get("owner_action", "Review object event."))
            soulaana = str(item.get("soulaana_translation", "Soulaana: Object event needs review."))
            recent_cards.append(f"""
              <div class="tower-mini-card">
                <div class="tower-mini-top">
                  <span>{severity.upper()}</span>
                  <span>{status}</span>
                </div>
                <strong>{title}</strong>
                <p>{owner_action}</p>
                <p>{soulaana}</p>
              </div>
            """)

        recent_html = "\n".join(recent_cards) if recent_cards else "<p>No object security inbox items yet.</p>"

        return f"""
        <section class="tower-panel">
          <div class="tower-panel-kicker">OB OBJECT SECURITY INBOX</div>
          <h2>Drawer Review Queue</h2>
          <p>Review-worthy Observatory object attempts are surfaced here.</p>

          <div class="tower-stat-grid">
            <div class="tower-stat-card">
              <span>Total</span>
              <strong>{total}</strong>
            </div>
            <div class="tower-stat-card">
              <span>Open</span>
              <strong>{open_count}</strong>
            </div>
            <div class="tower-stat-card">
              <span>By Severity</span>
              <strong>{by_severity}</strong>
            </div>
            <div class="tower-stat-card">
              <span>By Object</span>
              <strong>{by_object_type}</strong>
            </div>
          </div>

          <div class="tower-mini-list">
            {recent_html}
          </div>
        </section>
        """
    except Exception as exc:
        return f"""
        <section class="tower-panel">
          <div class="tower-panel-kicker">OB OBJECT SECURITY INBOX</div>
          <h2>Drawer Review Queue</h2>
          <p>Object security inbox panel could not load: {type(exc).__name__}: {exc}</p>
        </section>
        """


def _pack059_object_security_inbox_payload_fields():
    try:
        from tower.ob_object_audit_capsules import summarize_ob_object_security_inbox

        summary = summarize_ob_object_security_inbox(limit=8)
        return {
            "ob_object_security_inbox_ok": bool(summary.get("ok")),
            "ob_object_security_inbox_total": int(summary.get("total", 0) or 0),
            "ob_object_security_inbox_open": int(summary.get("open", 0) or 0),
            "ob_object_security_inbox_by_status": summary.get("by_status", {}),
            "ob_object_security_inbox_by_reason": summary.get("by_reason", {}),
            "ob_object_security_inbox_by_severity": summary.get("by_severity", {}),
            "ob_object_security_inbox_by_object_type": summary.get("by_object_type", {}),
            "ob_object_security_inbox_recent": summary.get("recent", []),
        }
    except Exception as exc:
        return {
            "ob_object_security_inbox_ok": False,
            "ob_object_security_inbox_error": f"{type(exc).__name__}: {exc}",
            "ob_object_security_inbox_total": 0,
            "ob_object_security_inbox_open": 0,
        }



# ================================================================================
# PACK059_SECURITY_COMMAND_VIEW_WRAPPER
# ================================================================================
# Wraps generate_security_command_dashboard() if it exists so the saved view/payload
# includes object security inbox fields/panel without needing to rewrite the page.
# ================================================================================

try:
    _pack059_original_generate_security_command_dashboard
except NameError:
    try:
        _pack059_original_generate_security_command_dashboard = generate_security_command_dashboard
    except NameError:
        _pack059_original_generate_security_command_dashboard = None


if _pack059_original_generate_security_command_dashboard is not None:
    def generate_security_command_dashboard(*args, **kwargs):
        result = _pack059_original_generate_security_command_dashboard(*args, **kwargs)

        try:
            fields = _pack059_object_security_inbox_payload_fields()

            # If result is a dict, enrich it directly.
            if isinstance(result, dict):
                result.update(fields)

                path = result.get("path")
                if path:
                    try:
                        from pathlib import Path
                        html_path = Path(path)
                        if html_path.exists():
                            html = html_path.read_text(encoding="utf-8", errors="replace")
                            panel = _pack059_object_security_inbox_panel_html()
                            if "OB OBJECT SECURITY INBOX" not in html:
                                if "</body>" in html:
                                    html = html.replace("</body>", panel + "\n</body>", 1)
                                else:
                                    html = html + "\n" + panel
                                html_path.write_text(html, encoding="utf-8")
                                result["bytes"] = html_path.stat().st_size
                    except Exception as html_error:
                        result["ob_object_security_inbox_html_error"] = str(html_error)

                return result

            return result
        except Exception as exc:
            if isinstance(result, dict):
                result["ob_object_security_inbox_ok"] = False
                result["ob_object_security_inbox_error"] = str(exc)
            return result



# ================================================================================
# PACK059B_COMPAT_GENERATE_SECURITY_COMMAND_DASHBOARD
# ================================================================================
# Current Tower page uses render_security_command_dashboard_html().
# This compatibility function gives tests and later routes a stable generator name.
# ================================================================================

def generate_security_command_dashboard(*args, **kwargs):
    try:
        from pathlib import Path
        import json

        root = Path(__file__).resolve().parents[1]
        data_dir = root / "tower" / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        html_path = data_dir / "security_command_dashboard.html"
        json_path = data_dir / "security_command_dashboard.json"
        view_path = data_dir / "security_command_dashboard_view.json"

        fields = _pack059_object_security_inbox_payload_fields()

        # Use the current renderer if present.
        html = ""
        try:
            html = render_security_command_dashboard_html()
        except TypeError:
            try:
                html = render_security_command_dashboard_html({})
            except Exception:
                html = ""
        except Exception:
            html = ""

        if not isinstance(html, str) or not html.strip():
            html = """
            <!doctype html>
            <html>
            <head><meta charset='utf-8'><title>The Tower Security Command View</title></head>
            <body>
              <h1>The Tower Security Command View</h1>
            </body>
            </html>
            """

        panel = _pack059_object_security_inbox_panel_html()
        if "OB OBJECT SECURITY INBOX" not in html:
            if "</body>" in html:
                html = html.replace("</body>", panel + "\n</body>", 1)
            else:
                html = html + "\n" + panel

        html_path.write_text(html, encoding="utf-8")

        payload = {
            "ok": True,
            "status": "saved",
            "view_name": "The Tower Security Command View",
            "path": str(html_path),
            "json_path": str(json_path),
            "view_path": str(view_path),
            "bytes": html_path.stat().st_size,
            **fields,
        }

        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
        view_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")

        return payload

    except Exception as exc:
        return {
            "ok": False,
            "status": "error",
            "reason_code": "security_command_dashboard_generate_failed",
            "human_reason": f"{type(exc).__name__}: {exc}",
            "path": "",
        }



# ================================================================================
# PACK063_OBJECT_INBOX_UI_ACTION_FORMS
# ================================================================================
# Adds owner action forms to the OB Object Security Inbox panel.
# ================================================================================

def _pack063_escape_html(value):
    text = "" if value is None else str(value)
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
    )


def _pack063_object_inbox_action_forms(item):
    inbox_item_id = _pack063_escape_html(item.get("inbox_item_id", ""))
    status = _pack063_escape_html(item.get("status", "open"))
    object_id = _pack063_escape_html(item.get("object_id", ""))
    object_type = _pack063_escape_html(item.get("object_type", "object"))

    return f"""
      <div class="tower-action-box" data-pack="063" data-inbox-item-id="{inbox_item_id}">
        <div class="tower-action-title">Owner Actions</div>
        <p class="tower-action-hint">Item: {object_type}:{object_id} · Status: {status}</p>

        <form class="tower-action-form" method="post" action="/tower/security-command/object-inbox/action-audited">
          <input type="hidden" name="inbox_item_id" value="{inbox_item_id}">
          <input type="hidden" name="action_type" value="note">
          <label>Add note</label>
          <textarea name="note" placeholder="Owner note for this drawer event"></textarea>
          <button type="submit">Add Note</button>
        </form>

        <div class="tower-action-row">
          <form method="post" action="/tower/security-command/object-inbox/action-audited">
            <input type="hidden" name="inbox_item_id" value="{inbox_item_id}">
            <input type="hidden" name="action_type" value="reviewing">
            <input type="hidden" name="note" value="Owner marked this object inbox item as reviewing from Tower UI.">
            <button type="submit">Mark Reviewing</button>
          </form>

          <form method="post" action="/tower/security-command/object-inbox/action-audited">
            <input type="hidden" name="inbox_item_id" value="{inbox_item_id}">
            <input type="hidden" name="action_type" value="resolve">
            <input type="hidden" name="resolution_reason" value="owner_resolved_from_tower_ui">
            <input type="hidden" name="note" value="Owner resolved this object inbox item from Tower UI.">
            <button type="submit">Resolve</button>
          </form>

          <form method="post" action="/tower/security-command/object-inbox/action-audited">
            <input type="hidden" name="inbox_item_id" value="{inbox_item_id}">
            <input type="hidden" name="action_type" value="ignore">
            <input type="hidden" name="resolution_reason" value="owner_ignored_from_tower_ui">
            <input type="hidden" name="note" value="Owner ignored this object inbox item from Tower UI.">
            <button type="submit">Ignore</button>
          </form>
        </div>
      </div>
    """


def _pack063_object_inbox_panel_styles():
    return """
    <style data-pack="063-object-inbox-actions">
      .tower-action-box {
        margin-top: 14px;
        padding: 14px;
        border: 1px solid rgba(255,255,255,.16);
        border-radius: 18px;
        background: rgba(255,255,255,.045);
      }
      .tower-action-title {
        font-size: 12px;
        letter-spacing: .16em;
        text-transform: uppercase;
        opacity: .72;
        margin-bottom: 6px;
      }
      .tower-action-hint {
        font-size: 13px;
        opacity: .76;
        margin: 0 0 10px 0;
      }
      .tower-action-form textarea {
        width: 100%;
        min-height: 70px;
        resize: vertical;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,.18);
        background: rgba(0,0,0,.22);
        color: inherit;
        padding: 10px;
        margin: 8px 0;
      }
      .tower-action-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 10px;
      }
      .tower-action-row form {
        margin: 0;
      }
      .tower-action-box button {
        border: 1px solid rgba(255,255,255,.2);
        background: rgba(255,255,255,.10);
        color: inherit;
        border-radius: 999px;
        padding: 9px 13px;
        cursor: pointer;
      }
      .tower-action-box button:hover {
        background: rgba(255,255,255,.16);
      }
    </style>
    """


def _pack063_object_security_inbox_panel_html_with_actions():
    try:
        from tower.ob_object_audit_capsules import summarize_ob_object_security_inbox

        summary = summarize_ob_object_security_inbox(limit=6)
        total = summary.get("total", 0)
        open_count = summary.get("open", 0)
        by_severity = summary.get("by_severity", {})
        by_object_type = summary.get("by_object_type", {})
        recent = summary.get("recent", [])

        recent_cards = []
        for item in recent[-6:]:
            title = _pack063_escape_html(item.get("title", "Object security review"))
            severity = _pack063_escape_html(item.get("severity", "unknown"))
            status = _pack063_escape_html(item.get("status", "open"))
            owner_action = _pack063_escape_html(item.get("owner_action", "Review object event."))
            soulaana = _pack063_escape_html(item.get("soulaana_translation", "Soulaana: Object event needs review."))

            actions_html = ""
            if status in {"open", "reviewing"}:
                actions_html = _pack063_object_inbox_action_forms(item)
            else:
                actions_html = "<p class='tower-action-hint'>Archived item. No active owner action needed.</p>"

            recent_cards.append(f"""
              <div class="tower-mini-card">
                <div class="tower-mini-top">
                  <span>{severity.upper()}</span>
                  <span>{status}</span>
                </div>
                <strong>{title}</strong>
                <p>{owner_action}</p>
                <p>{soulaana}</p>
                {actions_html}
              </div>
            """)

        recent_html = "\n".join(recent_cards) if recent_cards else "<p>No object security inbox items yet.</p>"

        return f"""
        {_pack063_object_inbox_panel_styles()}
        <section class="tower-panel" data-pack="063">
          <div class="tower-panel-kicker">OB OBJECT SECURITY INBOX</div>
          <h2>Drawer Review Queue</h2>
          <p>Review-worthy Observatory object attempts are surfaced here with owner action forms.</p>

          <div class="tower-stat-grid">
            <div class="tower-stat-card">
              <span>Total</span>
              <strong>{total}</strong>
            </div>
            <div class="tower-stat-card">
              <span>Open</span>
              <strong>{open_count}</strong>
            </div>
            <div class="tower-stat-card">
              <span>By Severity</span>
              <strong>{_pack063_escape_html(by_severity)}</strong>
            </div>
            <div class="tower-stat-card">
              <span>By Object</span>
              <strong>{_pack063_escape_html(by_object_type)}</strong>
            </div>
          </div>

          <div class="tower-mini-list">
            {recent_html}
          </div>
        </section>
        """
    except Exception as exc:
        return f"""
        <section class="tower-panel" data-pack="063">
          <div class="tower-panel-kicker">OB OBJECT SECURITY INBOX</div>
          <h2>Drawer Review Queue</h2>
          <p>Object security inbox action panel could not load: {type(exc).__name__}: {_pack063_escape_html(exc)}</p>
        </section>
        """


# Override the Pack 059 panel helper with the Pack 063 action-enabled version.
_pack059_object_security_inbox_panel_html = _pack063_object_security_inbox_panel_html_with_actions



# ================================================================================
# PACK074_ARCHIVE_VAULT_HANDOFF_UI_PANEL
# ================================================================================
# Adds Archive Vault handoff queue panel to Security Command dashboard.
# ================================================================================

def _pack074_escape_html(value):
    text = "" if value is None else str(value)
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
    )


def _pack074_archive_vault_handoff_panel_html():
    try:
        from tower.archive_vault_handoff import summarize_archive_vault_handoffs

        summary = summarize_archive_vault_handoffs(limit=6)
        total = summary.get("total", 0)
        queued = summary.get("queued", 0)
        by_status = summary.get("by_status", {})
        by_source_type = summary.get("by_source_type", {})
        by_severity = summary.get("by_severity", {})
        recent = summary.get("recent", [])

        cards = []
        for item in recent[-6:]:
            title = _pack074_escape_html(item.get("title", "Archive Vault handoff"))
            status = _pack074_escape_html(item.get("status", "queued"))
            severity = _pack074_escape_html(item.get("severity", "unknown"))
            source_type = _pack074_escape_html(item.get("source_type", "unknown"))
            source_id = _pack074_escape_html(item.get("source_id", ""))
            summary_text = _pack074_escape_html(item.get("summary", "Evidence handoff queued."))
            soulaana = _pack074_escape_html(item.get("soulaana_translation", "Soulaana: Evidence handoff queued safely."))

            cards.append(f"""
              <div class="tower-mini-card">
                <div class="tower-mini-top">
                  <span>{severity.upper()}</span>
                  <span>{status}</span>
                </div>
                <strong>{title}</strong>
                <p>{summary_text}</p>
                <p>{soulaana}</p>
                <div class="tower-action-hint">Source: {source_type} · {source_id}</div>
              </div>
            """)

        recent_html = "\n".join(cards) if cards else "<p>No Archive Vault handoffs queued yet.</p>"

        return f"""
        <section class="tower-panel" data-pack="074">
          <div class="tower-panel-kicker">ARCHIVE VAULT HANDOFFS</div>
          <h2>Evidence Bundle Queue</h2>
          <p>Security events prepared for future Archive Vault evidence bundles appear here.</p>

          <div class="tower-stat-grid">
            <div class="tower-stat-card">
              <span>Total</span>
              <strong>{total}</strong>
            </div>
            <div class="tower-stat-card">
              <span>Queued</span>
              <strong>{queued}</strong>
            </div>
            <div class="tower-stat-card">
              <span>By Status</span>
              <strong>{_pack074_escape_html(by_status)}</strong>
            </div>
            <div class="tower-stat-card">
              <span>By Source</span>
              <strong>{_pack074_escape_html(by_source_type)}</strong>
            </div>
            <div class="tower-stat-card">
              <span>By Severity</span>
              <strong>{_pack074_escape_html(by_severity)}</strong>
            </div>
          </div>

          <div class="tower-mini-list">
            {recent_html}
          </div>
        </section>
        """
    except Exception as exc:
        return f"""
        <section class="tower-panel" data-pack="074">
          <div class="tower-panel-kicker">ARCHIVE VAULT HANDOFFS</div>
          <h2>Evidence Bundle Queue</h2>
          <p>Archive Vault handoff panel could not load: {type(exc).__name__}: {_pack074_escape_html(exc)}</p>
        </section>
        """


try:
    _pack074_original_render_security_command_dashboard_html
except NameError:
    _pack074_original_render_security_command_dashboard_html = render_security_command_dashboard_html


def render_security_command_dashboard_html(*args, **kwargs):
    html = _pack074_original_render_security_command_dashboard_html(*args, **kwargs)
    panel = _pack074_archive_vault_handoff_panel_html()

    if "</body>" in html:
        return html.replace("</body>", panel + "\n</body>")
    return html + panel


try:
    _pack074_original_generate_security_command_dashboard
except NameError:
    _pack074_original_generate_security_command_dashboard = generate_security_command_dashboard


def generate_security_command_dashboard(*args, **kwargs):
    result = _pack074_original_generate_security_command_dashboard(*args, **kwargs)
    if not isinstance(result, dict):
        result = {"ok": False, "status": "invalid_dashboard_result"}

    try:
        from tower.archive_vault_handoff import summarize_archive_vault_handoffs

        summary = summarize_archive_vault_handoffs(limit=6)
        result["archive_vault_handoff_ok"] = summary.get("ok") is True
        result["archive_vault_handoff_total"] = summary.get("total", 0)
        result["archive_vault_handoff_queued"] = summary.get("queued", 0)
        result["archive_vault_handoff_by_status"] = summary.get("by_status", {})
        result["archive_vault_handoff_by_source_type"] = summary.get("by_source_type", {})
        result["archive_vault_handoff_by_severity"] = summary.get("by_severity", {})

        path = result.get("path", "")
        if path:
            from pathlib import Path
            html_path = Path(path)
            if html_path.exists():
                html = html_path.read_text(encoding="utf-8", errors="replace")
                if "ARCHIVE VAULT HANDOFFS" not in html:
                    html = html.replace("</body>", _pack074_archive_vault_handoff_panel_html() + "\n</body>") if "</body>" in html else html + _pack074_archive_vault_handoff_panel_html()
                    html_path.write_text(html, encoding="utf-8")
                    result["bytes"] = html_path.stat().st_size

    except Exception as exc:
        result["archive_vault_handoff_ok"] = False
        result["archive_vault_handoff_error"] = f"{type(exc).__name__}: {exc}"

    return result



# ================================================================================
# PACK076_AUDITED_OBJECT_INBOX_FORM_ENDPOINT
# ================================================================================
# Security Command object inbox forms now submit to /action-audited by default.
# This means visible owner button clicks create UI action audit receipts.
# ================================================================================
PACK076_OBJECT_INBOX_FORMS_USE_AUDITED_ENDPOINT = True
PACK076_OBJECT_INBOX_AUDITED_ENDPOINT = "/tower/security-command/object-inbox/action-audited"



# ================================================================================
# PACK077_UI_ACTION_AUDIT_RECEIPT_PANEL
# ================================================================================
# Adds owner button-click receipt summary panel to Security Command dashboard.
# ================================================================================

def _pack077_escape_html(value):
    text = "" if value is None else str(value)
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
    )


def _pack077_ui_action_audit_panel_html():
    try:
        from tower.ui_action_audit import summarize_ui_action_audit_receipts

        summary = summarize_ui_action_audit_receipts(limit=8)
        total = summary.get("total", 0)
        action_ok = summary.get("action_ok", 0)
        action_failed = summary.get("action_failed", 0)
        by_action = summary.get("by_action", {})
        by_reason = summary.get("by_reason", {})
        by_severity = summary.get("by_severity", {})
        by_status_code = summary.get("by_status_code", {})
        recent = summary.get("recent", [])

        cards = []
        for item in recent[-8:]:
            action_type = _pack077_escape_html(item.get("action_type", "unknown"))
            status_code = _pack077_escape_html(item.get("status_code", ""))
            severity = _pack077_escape_html(item.get("severity", "unknown"))
            reason_code = _pack077_escape_html(item.get("reason_code", "unknown"))
            actor_user_id = _pack077_escape_html(item.get("actor_user_id", "unknown"))
            inbox_item_id = _pack077_escape_html(item.get("inbox_item_id", ""))
            human_reason = _pack077_escape_html(item.get("human_reason", "UI action receipt recorded."))
            soulaana = _pack077_escape_html(item.get("soulaana_translation", "Soulaana: UI action receipt recorded."))
            receipt_id = _pack077_escape_html(item.get("receipt_id", ""))

            cards.append(f"""
              <div class="tower-mini-card">
                <div class="tower-mini-top">
                  <span>{severity.upper()}</span>
                  <span>{status_code}</span>
                </div>
                <strong>{action_type} · {reason_code}</strong>
                <p>{human_reason}</p>
                <p>{soulaana}</p>
                <div class="tower-action-hint">Actor: {actor_user_id} · Inbox item: {inbox_item_id}</div>
                <div class="tower-action-hint">Receipt: {receipt_id}</div>
              </div>
            """)

        recent_html = "\n".join(cards) if cards else "<p>No UI action receipts yet.</p>"

        return f"""
        <section class="tower-panel" data-pack="077">
          <div class="tower-panel-kicker">UI ACTION AUDIT RECEIPTS</div>
          <h2>Owner Button-Click Receipts</h2>
          <p>Every audited Security Command action creates a receipt here, including successful and failed attempts.</p>

          <div class="tower-stat-grid">
            <div class="tower-stat-card">
              <span>Total</span>
              <strong>{total}</strong>
            </div>
            <div class="tower-stat-card">
              <span>Successful</span>
              <strong>{action_ok}</strong>
            </div>
            <div class="tower-stat-card">
              <span>Failed / Blocked</span>
              <strong>{action_failed}</strong>
            </div>
            <div class="tower-stat-card">
              <span>By Action</span>
              <strong>{_pack077_escape_html(by_action)}</strong>
            </div>
            <div class="tower-stat-card">
              <span>By Reason</span>
              <strong>{_pack077_escape_html(by_reason)}</strong>
            </div>
            <div class="tower-stat-card">
              <span>By Severity</span>
              <strong>{_pack077_escape_html(by_severity)}</strong>
            </div>
            <div class="tower-stat-card">
              <span>By Status Code</span>
              <strong>{_pack077_escape_html(by_status_code)}</strong>
            </div>
          </div>

          <div class="tower-mini-list">
            {recent_html}
          </div>
        </section>
        """
    except Exception as exc:
        return f"""
        <section class="tower-panel" data-pack="077">
          <div class="tower-panel-kicker">UI ACTION AUDIT RECEIPTS</div>
          <h2>Owner Button-Click Receipts</h2>
          <p>UI action audit panel could not load: {type(exc).__name__}: {_pack077_escape_html(exc)}</p>
        </section>
        """


try:
    _pack077_original_render_security_command_dashboard_html
except NameError:
    _pack077_original_render_security_command_dashboard_html = render_security_command_dashboard_html


def render_security_command_dashboard_html(*args, **kwargs):
    html = _pack077_original_render_security_command_dashboard_html(*args, **kwargs)
    panel = _pack077_ui_action_audit_panel_html()

    if "UI ACTION AUDIT RECEIPTS" in html:
        return html

    if "</body>" in html:
        return html.replace("</body>", panel + "\n</body>")
    return html + panel


try:
    _pack077_original_generate_security_command_dashboard
except NameError:
    _pack077_original_generate_security_command_dashboard = generate_security_command_dashboard


def generate_security_command_dashboard(*args, **kwargs):
    result = _pack077_original_generate_security_command_dashboard(*args, **kwargs)
    if not isinstance(result, dict):
        result = {"ok": False, "status": "invalid_dashboard_result"}

    try:
        from tower.ui_action_audit import summarize_ui_action_audit_receipts

        summary = summarize_ui_action_audit_receipts(limit=8)
        result["ui_action_audit_ok"] = summary.get("ok") is True
        result["ui_action_audit_total"] = summary.get("total", 0)
        result["ui_action_audit_action_ok"] = summary.get("action_ok", 0)
        result["ui_action_audit_action_failed"] = summary.get("action_failed", 0)
        result["ui_action_audit_by_action"] = summary.get("by_action", {})
        result["ui_action_audit_by_reason"] = summary.get("by_reason", {})
        result["ui_action_audit_by_severity"] = summary.get("by_severity", {})
        result["ui_action_audit_by_status_code"] = summary.get("by_status_code", {})

        path = result.get("path", "")
        if path:
            from pathlib import Path
            html_path = Path(path)
            if html_path.exists():
                html = html_path.read_text(encoding="utf-8", errors="replace")
                if "UI ACTION AUDIT RECEIPTS" not in html:
                    html = html.replace("</body>", _pack077_ui_action_audit_panel_html() + "\n</body>") if "</body>" in html else html + _pack077_ui_action_audit_panel_html()
                    html_path.write_text(html, encoding="utf-8")
                    result["bytes"] = html_path.stat().st_size

    except Exception as exc:
        result["ui_action_audit_ok"] = False
        result["ui_action_audit_error"] = f"{type(exc).__name__}: {exc}"

    return result



# ================================================================================
# PACK087_EXPOSURE_MAPPING_UI_PANEL
# ================================================================================
# Adds OB exposure mapping pass panel to Security Command dashboard.
# ================================================================================

def _pack087_escape_html(value):
    text = "" if value is None else str(value)
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
    )


def _pack087_render_mapping_cards(items, empty_text):
    if not items:
        return f"<p>{_pack087_escape_html(empty_text)}</p>"

    cards = []
    for item in items[:12]:
        path = _pack087_escape_html(item.get("path", "unknown"))
        category = _pack087_escape_html(item.get("category", "unknown"))
        priority = _pack087_escape_html(item.get("priority", ""))
        reason_code = _pack087_escape_html(item.get("reason_code", "unknown"))
        plain = _pack087_escape_html(item.get("plain", "Needs review."))
        classification = _pack087_escape_html(item.get("classification", "unknown"))

        cards.append(f"""
          <div class="tower-mini-card">
            <div class="tower-mini-top">
              <span>PRIORITY {priority}</span>
              <span>{category}</span>
            </div>
            <strong>{path}</strong>
            <p>{plain}</p>
            <div class="tower-action-hint">Reason: {reason_code}</div>
            <div class="tower-action-hint">Classification: {classification}</div>
          </div>
        """)

    return "\n".join(cards)


def _pack087_exposure_mapping_panel_html():
    try:
        from tower.ob_exposure_mapping import (
            build_ob_exposure_mapping_pass,
            summarize_ob_exposure_mapping_pass,
        )

        build_ob_exposure_mapping_pass()
        summary = summarize_ob_exposure_mapping_pass(limit=12)

        total = summary.get("total", 0)
        counts = summary.get("counts", {})
        reason_counts = summary.get("reason_counts", {})
        priority_counts = summary.get("priority_counts", {})
        top_next = summary.get("top_next", [])
        retire_or_redirect = summary.get("retire_or_redirect", [])
        later_review = summary.get("later_review", [])
        readiness_label = _pack087_escape_html(summary.get("readiness_label", "Exposure mapping pass"))
        readiness_score = _pack087_escape_html(summary.get("readiness_score", ""))

        map_next_html = _pack087_render_mapping_cards(top_next, "No map-next routes found.")
        retire_html = _pack087_render_mapping_cards(retire_or_redirect, "No retire/redirect routes found.")
        review_html = _pack087_render_mapping_cards(later_review, "No later-review routes found.")

        return f"""
        <section class="tower-panel" data-pack="087">
          <div class="tower-panel-kicker">OB EXPOSURE MAPPING PASS</div>
          <h2>Route Exposure Door Map</h2>
          <p>Routes are categorized as protected, public-safe, map-next, retire/redirect, or later-review before future changes.</p>

          <div class="tower-stat-grid">
            <div class="tower-stat-card">
              <span>Total Routes</span>
              <strong>{total}</strong>
            </div>
            <div class="tower-stat-card">
              <span>Readiness</span>
              <strong>{readiness_score}</strong>
            </div>
            <div class="tower-stat-card">
              <span>Status</span>
              <strong>{readiness_label}</strong>
            </div>
            <div class="tower-stat-card">
              <span>By Category</span>
              <strong>{_pack087_escape_html(counts)}</strong>
            </div>
            <div class="tower-stat-card">
              <span>By Reason</span>
              <strong>{_pack087_escape_html(reason_counts)}</strong>
            </div>
            <div class="tower-stat-card">
              <span>By Priority</span>
              <strong>{_pack087_escape_html(priority_counts)}</strong>
            </div>
          </div>

          <div class="tower-subpanel">
            <h3>Map Next</h3>
            <div class="tower-mini-list">
              {map_next_html}
            </div>
          </div>

          <div class="tower-subpanel">
            <h3>Retire or Redirect</h3>
            <div class="tower-mini-list">
              {retire_html}
            </div>
          </div>

          <div class="tower-subpanel">
            <h3>Later Review</h3>
            <div class="tower-mini-list">
              {review_html}
            </div>
          </div>
        </section>
        """
    except Exception as exc:
        return f"""
        <section class="tower-panel" data-pack="087">
          <div class="tower-panel-kicker">OB EXPOSURE MAPPING PASS</div>
          <h2>Route Exposure Door Map</h2>
          <p>Exposure mapping panel could not load: {type(exc).__name__}: {_pack087_escape_html(exc)}</p>
        </section>
        """


try:
    _pack087_original_render_security_command_dashboard_html
except NameError:
    _pack087_original_render_security_command_dashboard_html = render_security_command_dashboard_html


def render_security_command_dashboard_html(*args, **kwargs):
    html = _pack087_original_render_security_command_dashboard_html(*args, **kwargs)
    panel = _pack087_exposure_mapping_panel_html()

    if "OB EXPOSURE MAPPING PASS" in html:
        return html

    if "</body>" in html:
        return html.replace("</body>", panel + "\n</body>")
    return html + panel


try:
    _pack087_original_generate_security_command_dashboard
except NameError:
    _pack087_original_generate_security_command_dashboard = generate_security_command_dashboard


def generate_security_command_dashboard(*args, **kwargs):
    result = _pack087_original_generate_security_command_dashboard(*args, **kwargs)
    if not isinstance(result, dict):
        result = {"ok": False, "status": "invalid_dashboard_result"}

    try:
        from tower.ob_exposure_mapping import (
            build_ob_exposure_mapping_pass,
            summarize_ob_exposure_mapping_pass,
        )

        mapping = build_ob_exposure_mapping_pass()
        summary = summarize_ob_exposure_mapping_pass(limit=12)

        result["ob_exposure_mapping_ok"] = summary.get("ok") is True
        result["ob_exposure_mapping_total"] = summary.get("total", 0)
        result["ob_exposure_mapping_counts"] = summary.get("counts", {})
        result["ob_exposure_mapping_reason_counts"] = summary.get("reason_counts", {})
        result["ob_exposure_mapping_priority_counts"] = summary.get("priority_counts", {})
        result["ob_exposure_mapping_top_next_count"] = len(summary.get("top_next", []))
        result["ob_exposure_mapping_retire_or_redirect_count"] = len(summary.get("retire_or_redirect", []))
        result["ob_exposure_mapping_later_review_count"] = len(summary.get("later_review", []))
        result["ob_exposure_mapping_readiness_label"] = summary.get("readiness_label")
        result["ob_exposure_mapping_readiness_score"] = summary.get("readiness_score")
        result["ob_exposure_mapping_file_path"] = mapping.get("path")

        path = result.get("path", "")
        if path:
            from pathlib import Path
            html_path = Path(path)
            if html_path.exists():
                html = html_path.read_text(encoding="utf-8", errors="replace")
                if "OB EXPOSURE MAPPING PASS" not in html:
                    panel = _pack087_exposure_mapping_panel_html()
                    html = html.replace("</body>", panel + "\n</body>") if "</body>" in html else html + panel
                    html_path.write_text(html, encoding="utf-8")
                    result["bytes"] = html_path.stat().st_size

    except Exception as exc:
        result["ob_exposure_mapping_ok"] = False
        result["ob_exposure_mapping_error"] = f"{type(exc).__name__}: {exc}"

    return result



# ================================================================================
# PACK088B_FINAL_REPLACEMENT_EXPOSURE_DASHBOARD_WRAPPER
# ================================================================================
# Guarantees final Security Command dashboard includes BOTH:
# - DENY-PATH REPLACEMENT RECEIPTS panel
# - OB EXPOSURE MAPPING PASS panel
# regardless of earlier wrapper order.
# ================================================================================

def _pack088b_escape_html(value):
    text = "" if value is None else str(value)
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
    )


def _pack088b_deny_path_replacement_panel_html():
    try:
        from tower.deny_path_replacement_audit import summarize_deny_path_replacement_receipts

        summary = summarize_deny_path_replacement_receipts(limit=8)
        total = summary.get("total", 0)
        verified = summary.get("verified", 0)
        needs_review = summary.get("needs_review", 0)
        by_status = summary.get("by_status", {})
        by_route = summary.get("by_route", {})
        by_type = summary.get("by_replacement_type", {})
        by_severity = summary.get("by_severity", {})
        recent = summary.get("recent", [])

        cards = []
        for item in recent[-8:]:
            route_path = _pack088b_escape_html(item.get("route_path", "unknown"))
            status = _pack088b_escape_html(item.get("status", "unknown"))
            severity = _pack088b_escape_html(item.get("severity", "unknown"))
            replacement_type = _pack088b_escape_html(item.get("replacement_type", "unknown"))
            old_behavior = _pack088b_escape_html(item.get("old_behavior", "unknown"))
            new_behavior = _pack088b_escape_html(item.get("new_behavior", "unknown"))
            reason = _pack088b_escape_html(item.get("reason", "Deny-path replacement receipt recorded."))
            soulaana = _pack088b_escape_html(item.get("soulaana_translation", "Soulaana: Replacement receipt filed."))
            receipt_id = _pack088b_escape_html(item.get("receipt_id", ""))

            cards.append(f"""
              <div class="tower-mini-card">
                <div class="tower-mini-top">
                  <span>{severity.upper()}</span>
                  <span>{status}</span>
                </div>
                <strong>{route_path}</strong>
                <p>{reason}</p>
                <p>{soulaana}</p>
                <div class="tower-action-hint">Type: {replacement_type}</div>
                <div class="tower-action-hint">Old: {old_behavior} → New: {new_behavior}</div>
                <div class="tower-action-hint">Receipt: {receipt_id}</div>
              </div>
            """)

        recent_html = "\n".join(cards) if cards else "<p>No deny-path replacement receipts yet.</p>"

        return f"""
        <section class="tower-panel" data-pack="086">
          <div class="tower-panel-kicker">DENY-PATH REPLACEMENT RECEIPTS</div>
          <h2>Locked Door Replacement Log</h2>
          <p>Tracks old locked surfaces that were replaced with polished Tower clearance walls.</p>

          <div class="tower-stat-grid">
            <div class="tower-stat-card"><span>Total</span><strong>{total}</strong></div>
            <div class="tower-stat-card"><span>Verified</span><strong>{verified}</strong></div>
            <div class="tower-stat-card"><span>Needs Review</span><strong>{needs_review}</strong></div>
            <div class="tower-stat-card"><span>By Status</span><strong>{_pack088b_escape_html(by_status)}</strong></div>
            <div class="tower-stat-card"><span>By Route</span><strong>{_pack088b_escape_html(by_route)}</strong></div>
            <div class="tower-stat-card"><span>By Type</span><strong>{_pack088b_escape_html(by_type)}</strong></div>
            <div class="tower-stat-card"><span>By Severity</span><strong>{_pack088b_escape_html(by_severity)}</strong></div>
          </div>

          <div class="tower-mini-list">
            {recent_html}
          </div>
        </section>
        """
    except Exception as exc:
        return f"""
        <section class="tower-panel" data-pack="086">
          <div class="tower-panel-kicker">DENY-PATH REPLACEMENT RECEIPTS</div>
          <h2>Locked Door Replacement Log</h2>
          <p>Deny-path replacement panel could not load: {type(exc).__name__}: {_pack088b_escape_html(exc)}</p>
        </section>
        """


def _pack088b_render_mapping_cards(items, empty_text):
    if not items:
        return f"<p>{_pack088b_escape_html(empty_text)}</p>"

    cards = []
    for item in items[:12]:
        path = _pack088b_escape_html(item.get("path", "unknown"))
        category = _pack088b_escape_html(item.get("category", "unknown"))
        priority = _pack088b_escape_html(item.get("priority", ""))
        reason_code = _pack088b_escape_html(item.get("reason_code", "unknown"))
        plain = _pack088b_escape_html(item.get("plain", "Needs review."))
        classification = _pack088b_escape_html(item.get("classification", "unknown"))

        cards.append(f"""
          <div class="tower-mini-card">
            <div class="tower-mini-top">
              <span>PRIORITY {priority}</span>
              <span>{category}</span>
            </div>
            <strong>{path}</strong>
            <p>{plain}</p>
            <div class="tower-action-hint">Reason: {reason_code}</div>
            <div class="tower-action-hint">Classification: {classification}</div>
          </div>
        """)
    return "\n".join(cards)


def _pack088b_exposure_mapping_panel_html():
    try:
        from tower.ob_exposure_mapping import (
            build_ob_exposure_mapping_pass,
            summarize_ob_exposure_mapping_pass,
        )

        build_ob_exposure_mapping_pass()
        summary = summarize_ob_exposure_mapping_pass(limit=12)

        total = summary.get("total", 0)
        counts = summary.get("counts", {})
        reason_counts = summary.get("reason_counts", {})
        priority_counts = summary.get("priority_counts", {})
        top_next = summary.get("top_next", [])
        retire_or_redirect = summary.get("retire_or_redirect", [])
        later_review = summary.get("later_review", [])
        readiness_label = _pack088b_escape_html(summary.get("readiness_label", "Exposure mapping pass"))
        readiness_score = _pack088b_escape_html(summary.get("readiness_score", ""))

        return f"""
        <section class="tower-panel" data-pack="087">
          <div class="tower-panel-kicker">OB EXPOSURE MAPPING PASS</div>
          <h2>Route Exposure Door Map</h2>
          <p>Routes are categorized as protected, public-safe, map-next, retire/redirect, or later-review before future changes.</p>

          <div class="tower-stat-grid">
            <div class="tower-stat-card"><span>Total Routes</span><strong>{total}</strong></div>
            <div class="tower-stat-card"><span>Readiness</span><strong>{readiness_score}</strong></div>
            <div class="tower-stat-card"><span>Status</span><strong>{readiness_label}</strong></div>
            <div class="tower-stat-card"><span>By Category</span><strong>{_pack088b_escape_html(counts)}</strong></div>
            <div class="tower-stat-card"><span>By Reason</span><strong>{_pack088b_escape_html(reason_counts)}</strong></div>
            <div class="tower-stat-card"><span>By Priority</span><strong>{_pack088b_escape_html(priority_counts)}</strong></div>
          </div>

          <div class="tower-subpanel">
            <h3>Map Next</h3>
            <div class="tower-mini-list">{_pack088b_render_mapping_cards(top_next, "No map-next routes found.")}</div>
          </div>

          <div class="tower-subpanel">
            <h3>Retire or Redirect</h3>
            <div class="tower-mini-list">{_pack088b_render_mapping_cards(retire_or_redirect, "No retire/redirect routes found.")}</div>
          </div>

          <div class="tower-subpanel">
            <h3>Later Review</h3>
            <div class="tower-mini-list">{_pack088b_render_mapping_cards(later_review, "No later-review routes found.")}</div>
          </div>
        </section>
        """
    except Exception as exc:
        return f"""
        <section class="tower-panel" data-pack="087">
          <div class="tower-panel-kicker">OB EXPOSURE MAPPING PASS</div>
          <h2>Route Exposure Door Map</h2>
          <p>Exposure mapping panel could not load: {type(exc).__name__}: {_pack088b_escape_html(exc)}</p>
        </section>
        """


def _pack088b_ensure_panel_before_body(html, marker, panel_html):
    if marker in html:
        return html
    if "</body>" in html:
        return html.replace("</body>", panel_html + "\n</body>")
    return html + panel_html


try:
    _pack088b_original_render_security_command_dashboard_html
except NameError:
    _pack088b_original_render_security_command_dashboard_html = render_security_command_dashboard_html


def render_security_command_dashboard_html(*args, **kwargs):
    html = _pack088b_original_render_security_command_dashboard_html(*args, **kwargs)
    html = _pack088b_ensure_panel_before_body(
        html,
        "DENY-PATH REPLACEMENT RECEIPTS",
        _pack088b_deny_path_replacement_panel_html(),
    )
    html = _pack088b_ensure_panel_before_body(
        html,
        "OB EXPOSURE MAPPING PASS",
        _pack088b_exposure_mapping_panel_html(),
    )
    return html


try:
    _pack088b_original_generate_security_command_dashboard
except NameError:
    _pack088b_original_generate_security_command_dashboard = generate_security_command_dashboard


def generate_security_command_dashboard(*args, **kwargs):
    result = _pack088b_original_generate_security_command_dashboard(*args, **kwargs)
    if not isinstance(result, dict):
        result = {"ok": False, "status": "invalid_dashboard_result"}

    try:
        from tower.deny_path_replacement_audit import summarize_deny_path_replacement_receipts
        from tower.ob_exposure_mapping import (
            build_ob_exposure_mapping_pass,
            summarize_ob_exposure_mapping_pass,
        )

        deny_summary = summarize_deny_path_replacement_receipts(limit=8)
        mapping = build_ob_exposure_mapping_pass()
        exposure_summary = summarize_ob_exposure_mapping_pass(limit=12)

        result["deny_path_replacement_ok"] = deny_summary.get("ok") is True
        result["deny_path_replacement_total"] = deny_summary.get("total", 0)
        result["deny_path_replacement_verified"] = deny_summary.get("verified", 0)
        result["deny_path_replacement_needs_review"] = deny_summary.get("needs_review", 0)
        result["deny_path_replacement_by_status"] = deny_summary.get("by_status", {})
        result["deny_path_replacement_by_route"] = deny_summary.get("by_route", {})
        result["deny_path_replacement_by_type"] = deny_summary.get("by_replacement_type", {})
        result["deny_path_replacement_by_severity"] = deny_summary.get("by_severity", {})

        result["ob_exposure_mapping_ok"] = exposure_summary.get("ok") is True
        result["ob_exposure_mapping_total"] = exposure_summary.get("total", 0)
        result["ob_exposure_mapping_counts"] = exposure_summary.get("counts", {})
        result["ob_exposure_mapping_reason_counts"] = exposure_summary.get("reason_counts", {})
        result["ob_exposure_mapping_priority_counts"] = exposure_summary.get("priority_counts", {})
        result["ob_exposure_mapping_top_next_count"] = len(exposure_summary.get("top_next", []))
        result["ob_exposure_mapping_retire_or_redirect_count"] = len(exposure_summary.get("retire_or_redirect", []))
        result["ob_exposure_mapping_later_review_count"] = len(exposure_summary.get("later_review", []))
        result["ob_exposure_mapping_readiness_label"] = exposure_summary.get("readiness_label")
        result["ob_exposure_mapping_readiness_score"] = exposure_summary.get("readiness_score")
        result["ob_exposure_mapping_file_path"] = mapping.get("path")

        path = result.get("path", "")
        if path:
            from pathlib import Path
            html_path = Path(path)
            if html_path.exists():
                html = html_path.read_text(encoding="utf-8", errors="replace")
                html = _pack088b_ensure_panel_before_body(
                    html,
                    "DENY-PATH REPLACEMENT RECEIPTS",
                    _pack088b_deny_path_replacement_panel_html(),
                )
                html = _pack088b_ensure_panel_before_body(
                    html,
                    "OB EXPOSURE MAPPING PASS",
                    _pack088b_exposure_mapping_panel_html(),
                )
                html_path.write_text(html, encoding="utf-8")
                result["bytes"] = html_path.stat().st_size

    except Exception as exc:
        result["replacement_exposure_panel_ok"] = False
        result["replacement_exposure_panel_error"] = f"{type(exc).__name__}: {exc}"

    return result



# ================================================================================
# PACK112_OBJECT_PERMISSION_VISIBILITY_COMMAND_BRIDGE
# ================================================================================

def pack112_object_permission_visibility_command_panel():
    try:
        from tower.ob_object_permission_visibility import build_object_permission_visibility_status
        status = build_object_permission_visibility_status(write_panel=True)
        return {
            "ok": True,
            "pack": "112",
            "panel_title": "OB Object Permission Visibility",
            "event_count": status.get("event_count", 0),
            "deny_count": status.get("deny_count", 0),
            "step_up_required_count": status.get("step_up_required_count", 0),
            "export_event_count": status.get("export_event_count", 0),
            "summary_only_count": status.get("summary_only_count", 0),
            "panel_path": status.get("panel_path"),
            "human_reason": "OB object permission visibility command panel loaded.",
        }
    except Exception as exc:
        return {
            "ok": False,
            "pack": "112",
            "reason_code": "object_permission_command_panel_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "OB object permission visibility command panel could not be loaded.",
        }

# ================================================================================
# END PACK112_OBJECT_PERMISSION_VISIBILITY_COMMAND_BRIDGE
# ================================================================================



# ================================================================================
# PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_HTML_BRIDGE
# ================================================================================

def pack113_security_command_object_visibility_html_section():
    try:
        from tower.security_command_object_visibility_integration import (
            build_security_command_object_visibility_status,
            render_security_command_object_visibility_section,
        )
        status = build_security_command_object_visibility_status(write_fragment=True)
        return render_security_command_object_visibility_section(status)
    except Exception as exc:
        return f"""
        <section class="tower-object-visibility-panel" data-pack="113-error">
          <h2>Object Permission Visibility Unavailable</h2>
          <p>Security Command could not load object visibility.</p>
          <p>{type(exc).__name__}</p>
        </section>
        """

# ================================================================================
# END PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_HTML_BRIDGE
# ================================================================================



# ================================================================================
# PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_HTML_BRIDGE
# ================================================================================

def pack115_security_command_navigation_links_html_section():
    try:
        from tower.security_command_navigation_links import (
            build_security_command_navigation_links_status,
            render_security_command_navigation_links_section,
        )
        status = build_security_command_navigation_links_status(write_panel=True)
        return render_security_command_navigation_links_section(status)
    except Exception as exc:
        return f"""
        <section class="tower-security-command-links" data-pack="115-error">
          <h2>Security Command Links Unavailable</h2>
          <p>{type(exc).__name__}</p>
        </section>
        """

# ================================================================================
# END PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_HTML_BRIDGE
# ================================================================================



# ================================================================================
# PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_HTML_BRIDGE
# ================================================================================

def pack117_security_command_preferred_destination_html_section():
    try:
        from tower.security_command_preferred_destination import (
            build_security_command_preferred_destination_status,
            render_security_command_preferred_destination_section,
        )
        status = build_security_command_preferred_destination_status(write_panel=True)
        return render_security_command_preferred_destination_section(status)
    except Exception as exc:
        return f"""
        <section class="preferred-command-destination" data-pack="117-error">
          <h2>Preferred Security Command Destination Unavailable</h2>
          <p>{type(exc).__name__}</p>
        </section>
        """

# ================================================================================
# END PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_HTML_BRIDGE
# ================================================================================



# ================================================================================
# PACK119_OWNER_QUICK_ACTIONS_HTML_BRIDGE
# ================================================================================

def pack119_owner_quick_actions_html_section():
    try:
        from tower.security_command_owner_quick_actions import (
            build_owner_quick_actions_status,
            render_owner_quick_actions_section,
        )
        status = build_owner_quick_actions_status(write_panel=True)
        return render_owner_quick_actions_section(status)
    except Exception as exc:
        return f"""
        <section class="owner-quick-action-rail" data-pack="119-error">
          <h2>Owner Quick Actions Unavailable</h2>
          <p>{type(exc).__name__}</p>
        </section>
        """

# ================================================================================
# END PACK119_OWNER_QUICK_ACTIONS_HTML_BRIDGE
# ================================================================================



# ================================================================================
# PACK123_SECURITY_INBOX_UI_HTML_BRIDGES
# ================================================================================

def pack123_security_inbox_owner_queue_html_section():
    try:
        from tower.security_inbox_owner_queue import (
            build_security_inbox_owner_queue,
            render_security_inbox_owner_queue_section,
        )
        status = build_security_inbox_owner_queue(write_panel=True)
        return render_security_inbox_owner_queue_section(status)
    except Exception as exc:
        return f"""
        <section class="security-inbox-owner-queue" data-pack="123-inbox-error">
          <h2>Tower Security Inbox Unavailable</h2>
          <p>{type(exc).__name__}</p>
        </section>
        """


def pack123_security_inbox_review_html_section():
    try:
        from tower.security_inbox_review_actions import (
            build_security_inbox_review_status,
            render_security_inbox_review_section,
        )
        status = build_security_inbox_review_status(write_panel=True)
        return render_security_inbox_review_section(status)
    except Exception as exc:
        return f"""
        <section class="security-inbox-review-actions" data-pack="123-review-error">
          <h2>Security Inbox Review Unavailable</h2>
          <p>{type(exc).__name__}</p>
        </section>
        """

# ================================================================================
# END PACK123_SECURITY_INBOX_UI_HTML_BRIDGES
# ================================================================================



# ================================================================================
# PACK125_SECURITY_INBOX_FILTERS_HTML_BRIDGE
# ================================================================================

def pack125_security_inbox_filters_priorities_html_section():
    try:
        from tower.security_inbox_filters_priorities import (
            build_security_inbox_filters_priorities_status,
            render_security_inbox_filters_priorities_section,
        )
        status = build_security_inbox_filters_priorities_status(write_panel=True)
        return render_security_inbox_filters_priorities_section(status)
    except Exception as exc:
        return f"""
        <section class="security-inbox-filters-priorities" data-pack="125-filters-error">
          <h2>Security Inbox Filters Unavailable</h2>
          <p>{type(exc).__name__}</p>
        </section>
        """

# ================================================================================
# END PACK125_SECURITY_INBOX_FILTERS_HTML_BRIDGE
# ================================================================================



# ================================================================================
# PACK127_SECURITY_INCIDENT_DESK_HTML_BRIDGE
# ================================================================================

def pack127_security_incident_desk_html_section():
    try:
        from tower.security_incident_desk import (
            build_security_incident_desk_status,
            render_security_incident_desk_section,
        )
        status = build_security_incident_desk_status(write_panel=True)
        return render_security_incident_desk_section(status)
    except Exception as exc:
        return f"""
        <section class="security-incident-desk" data-pack="127-incident-error">
          <h2>Tower Incident Desk Unavailable</h2>
          <p>{type(exc).__name__}</p>
        </section>
        """

# ================================================================================
# END PACK127_SECURITY_INCIDENT_DESK_HTML_BRIDGE
# ================================================================================



# ================================================================================
# PACK129_SECURITY_INCIDENT_FILTERS_HTML_BRIDGE
# ================================================================================

def pack129_security_incident_filters_escalation_html_section():
    try:
        from tower.security_incident_filters_escalation import (
            build_security_incident_filters_escalation_status,
            render_security_incident_filters_escalation_section,
        )
        status = build_security_incident_filters_escalation_status(write_panel=True)
        return render_security_incident_filters_escalation_section(status)
    except Exception as exc:
        return f"""
        <section class="security-incident-filters-escalation" data-pack="129-incident-filters-error">
          <h2>Incident Filters & Escalation Unavailable</h2>
          <p>{type(exc).__name__}</p>
        </section>
        """

# ================================================================================
# END PACK129_SECURITY_INCIDENT_FILTERS_HTML_BRIDGE
# ================================================================================

