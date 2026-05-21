from __future__ import annotations
import json
import os
import sys
from pathlib import Path
PROJECT_ROOT = Path('/content/SimpleeMrkTrade_REAL_CLONE')
os.chdir(PROJECT_ROOT)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
for name in list(sys.modules.keys()):
    if name == 'tower' or name.startswith('tower.') or name == 'web.app':
        sys.modules.pop(name, None)
from tower.keycard_issuer import issue_owner_tower_access_urls
from tower.security_command_page import SECURITY_COMMAND_HTML, build_security_command_view, render_security_command_dashboard_html, save_security_command_dashboard_html
from web.app import app

def _print(title, payload=None):
    print('\n' + '=' * 80)
    print(title)
    print('=' * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))

def run_tests():
    view = build_security_command_view(tower_user_id='owner_solice')
    _print('VIEW SUMMARY', {'ok': view.get('ok'), 'state': view.get('state'), 'health': view.get('health', {}).get('score'), 'stats': len(view.get('command_stats', [])), 'lanes': len(view.get('attention_lanes', [])), 'workflow': len(view.get('workflow', [])), 'system_panels': len(view.get('system_panels', []))})
    assert view['ok'] is True
    assert view['view_name'] == 'The Tower Security Command View'
    assert len(view['command_stats']) == 4
    assert len(view['attention_lanes']) >= 4
    assert len(view['workflow']) >= 4
    assert len(view['system_panels']) >= 6
    assert 0 <= int(view['health']['score']) <= 100
    html = render_security_command_dashboard_html(tower_user_id='owner_solice')
    checks = {'has_doctype': '<!doctype html>' in html.lower(), 'has_tower': 'The Tower' in html, 'has_health_gauge': 'Tower health gauge' in html, 'has_soulaana': 'Soulaana' in html, 'has_workflow': 'Walk me through it' in html, 'has_exit': 'Exit workflow' in html, 'has_skip': 'Skip this' in html, 'has_system_panels': 'System panels' in html, 'has_security_canopy_name': 'Security Canopy' in html}
    _print('HTML CHECKS', checks)
    assert checks['has_doctype']
    assert checks['has_tower']
    assert checks['has_health_gauge']
    assert checks['has_soulaana']
    assert checks['has_workflow']
    assert checks['has_exit']
    assert checks['has_skip']
    assert checks['has_system_panels']
    assert checks['has_security_canopy_name'] is False
    result = save_security_command_dashboard_html(tower_user_id='owner_solice')
    _print('SAVE RESULT', result)
    assert result['ok'] is True
    assert Path(result['path']).exists()
    assert result['bytes'] > 7000
    saved = SECURITY_COMMAND_HTML.read_text(encoding='utf-8')
    assert 'Plain-language guardian' in saved
    assert 'Security instruments behind OB' in saved
    assert 'The private security force behind OB' in saved
    access = issue_owner_tower_access_urls(actor_user_id='owner_solice', target_user_id='owner_solice', reason='Pack 028 protected UI route test.', session_id='session_pack028', device_id='device_pack028', include_regenerate=False)
    assert access['ok'] is True
    client = app.test_client()
    response = client.get(access['urls']['command'])
    text = response.get_data(as_text=True)
    _print('PROTECTED ROUTE', {'status': response.status_code, 'has_tower': 'The Tower' in text, 'has_health': 'Tower health gauge' in text, 'has_soulaana': 'Soulaana' in text, 'preview': text[:260]})
    assert response.status_code == 200
    assert 'Tower health gauge' in text
    assert 'Soulaana' in text
    assert 'Security Canopy' not in text
    locked = client.get('/tower/security-command')
    locked_text = locked.get_data(as_text=True)
    _print('LOCKED ROUTE', {'status': locked.status_code, 'preview': locked_text[:240]})
    assert locked.status_code == 403
    assert 'Clearance required' in locked_text
    assert 'Tower health gauge' not in locked_text
    assert 'security_inbox_total' not in locked_text
    final = {'pack': '028', 'status': 'passed', 'human_reason': 'Approved Tower UI renders behind the protected keycard route and unauthorized users still see only the locked page.', 'html_path': str(SECURITY_COMMAND_HTML)}
    _print('PACK 028 RESULT', final)
    return final

if __name__ == '__main__':
    run_tests()
