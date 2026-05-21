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

from tower.door_audit_capsules import summarize_door_swipe_audit_capsules
from tower.owner_launch_cell import build_owner_tower_launch_packet
from tower.security_command_page import save_security_command_dashboard_html
from tower.tower_status import get_tower_status
from web.app import app


def _print(title, payload=None):
    print()
    print('=' * 80)
    print(title)
    print('=' * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))


def run_tests():
    client = app.test_client()

    _print('CREATE SOME DOOR-SWIPE ACTIVITY')
    client.get('/tower/security-command')
    packet = build_owner_tower_launch_packet(
        actor_user_id='owner_solice',
        target_user_id='owner_solice',
        session_id='session_pack032',
        device_id='device_pack032',
        ttl_seconds=900,
        include_regenerate=False,
    )
    assert packet.get('ok') is True
    client.get(packet['urls']['command'])
    client.get(packet['urls']['status'].replace('/tower/status.json', '/tower/security-command'))

    _print('DIRECT AUDIT SUMMARY')
    audit = summarize_door_swipe_audit_capsules(limit=5)
    _print('audit', {
        'ok': audit.get('ok'),
        'total': audit.get('total'),
        'allowed': audit.get('allowed'),
        'denied': audit.get('denied'),
        'by_reason': audit.get('by_reason'),
    })
    assert audit.get('ok') is True
    assert audit.get('total', 0) >= 3

    _print('TOWER STATUS HAS DOOR AUDIT FIELDS')
    status = get_tower_status()
    _print('status audit fields', {
        'door_swipe_audit_ok': status.get('door_swipe_audit_ok'),
        'door_swipe_audit_total': status.get('door_swipe_audit_total'),
        'door_swipe_audit_allowed': status.get('door_swipe_audit_allowed'),
        'door_swipe_audit_denied': status.get('door_swipe_audit_denied'),
        'recent_count': len(status.get('door_swipe_audit_recent', [])),
    })
    assert status.get('door_swipe_audit_ok') is True
    assert status.get('door_swipe_audit_total', 0) >= 3
    assert status.get('door_swipe_audit_denied', 0) >= 1
    assert isinstance(status.get('door_swipe_audit_recent'), list)

    serialized_status = json.dumps(status, sort_keys=True)
    assert 'tower_keycard=' not in serialized_status

    _print('STATUS JSON ROUTE HAS DOOR AUDIT FIELDS')
    status_response = client.get(packet['urls']['status'])
    status_json = status_response.get_json(silent=True)
    _print('status route', {
        'http': status_response.status_code,
        'ok': status_json.get('ok') if isinstance(status_json, dict) else None,
        'door_swipe_audit_total': status_json.get('door_swipe_audit_total') if isinstance(status_json, dict) else None,
    })
    assert status_response.status_code == 200
    assert isinstance(status_json, dict)
    assert status_json.get('door_swipe_audit_total', 0) >= 3

    _print('TOWER UI SURFACES DOOR RECEIPTS')
    ui_result = save_security_command_dashboard_html(tower_user_id='owner_solice')
    assert ui_result.get('ok') is True
    command_response = client.get(packet['urls']['command'])
    text = command_response.get_data(as_text=True)
    _print('ui route', {
        'http': command_response.status_code,
        'has_door_swipe_receipts': 'Door-swipe receipts' in text,
        'has_door_receipts': 'Door Receipts' in text,
        'has_access_swipes': 'Access swipes' in text,
    })
    assert command_response.status_code == 200
    assert 'Door-swipe receipts' in text
    assert 'Door Receipts' in text
    assert 'Access swipes' in text
    assert 'tower_keycard=' not in text

    result = {
        'pack': '032',
        'status': 'passed',
        'human_reason': 'Door-swipe audit capsules are now surfaced in Tower status, status JSON, and the protected Tower UI.',
    }
    _print('PACK 032 RESULT', result)
    return result


if __name__ == '__main__':
    run_tests()
