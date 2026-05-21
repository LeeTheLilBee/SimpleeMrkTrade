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
