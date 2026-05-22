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

        <form class="tower-action-form" method="post" action="/tower/security-command/object-inbox/action">
          <input type="hidden" name="inbox_item_id" value="{inbox_item_id}">
          <input type="hidden" name="action_type" value="note">
          <label>Add note</label>
          <textarea name="note" placeholder="Owner note for this drawer event"></textarea>
          <button type="submit">Add Note</button>
        </form>

        <div class="tower-action-row">
          <form method="post" action="/tower/security-command/object-inbox/action">
            <input type="hidden" name="inbox_item_id" value="{inbox_item_id}">
            <input type="hidden" name="action_type" value="reviewing">
            <input type="hidden" name="note" value="Owner marked this object inbox item as reviewing from Tower UI.">
            <button type="submit">Mark Reviewing</button>
          </form>

          <form method="post" action="/tower/security-command/object-inbox/action">
            <input type="hidden" name="inbox_item_id" value="{inbox_item_id}">
            <input type="hidden" name="action_type" value="resolve">
            <input type="hidden" name="resolution_reason" value="owner_resolved_from_tower_ui">
            <input type="hidden" name="note" value="Owner resolved this object inbox item from Tower UI.">
            <button type="submit">Resolve</button>
          </form>

          <form method="post" action="/tower/security-command/object-inbox/action">
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

