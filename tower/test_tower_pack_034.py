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

from tower.door_audit_capsules import summarize_door_swipe_security_inbox
from tower.owner_launch_cell import build_owner_tower_launch_packet
from tower.security_command_page import build_security_command_view
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

    _print('CREATE REVIEW-WORTHY DOOR SWIPES')
    client.get('/tower/security-command')
    packet = build_owner_tower_launch_packet(
        actor_user_id='owner_solice',
        target_user_id='owner_solice',
        session_id='session_pack034',
        device_id='device_pack034',
        ttl_seconds=900,
        include_regenerate=False,
    )
    assert packet.get('ok') is True
    client.get(packet['urls']['status'].replace('/tower/status.json', '/tower/security-command'))

    inbox = summarize_door_swipe_security_inbox(limit=6)
    _print('DIRECT DOOR SECURITY INBOX', {
        'ok': inbox.get('ok'),
        'total': inbox.get('total'),
        'open': inbox.get('open'),
        'by_severity': inbox.get('by_severity'),
        'by_reason': inbox.get('by_reason'),
    })
    assert inbox.get('ok') is True
    assert inbox.get('open', 0) >= 1

    _print('TOWER STATUS HAS DOOR SECURITY INBOX FIELDS')
    status = get_tower_status()
    _print('status fields', {
        'door_swipe_security_inbox_ok': status.get('door_swipe_security_inbox_ok'),
        'door_swipe_security_inbox_total': status.get('door_swipe_security_inbox_total'),
        'door_swipe_security_inbox_open': status.get('door_swipe_security_inbox_open'),
        'recent_count': len(status.get('door_swipe_security_inbox_recent', [])),
    })
    assert status.get('door_swipe_security_inbox_ok') is True
    assert status.get('door_swipe_security_inbox_open', 0) >= 1
    assert isinstance(status.get('door_swipe_security_inbox_recent'), list)

    serialized_status = json.dumps(status, sort_keys=True)
    assert 'tower_keycard=' not in serialized_status
    assert 'raw_token' not in serialized_status

    _print('STATUS JSON ROUTE HAS DOOR SECURITY INBOX FIELDS')
    status_response = client.get(packet['urls']['status'])
    status_json = status_response.get_json(silent=True)
    _print('status route', {
        'http': status_response.status_code,
        'door_swipe_security_inbox_open': status_json.get('door_swipe_security_inbox_open') if isinstance(status_json, dict) else None,
    })
    assert status_response.status_code == 200
    assert isinstance(status_json, dict)
    assert status_json.get('door_swipe_security_inbox_open', 0) >= 1

    _print('SECURITY COMMAND VIEW HAS DOOR INBOX DATA')
    view = build_security_command_view(tower_user_id='owner_solice')
    _print('view door inbox', view.get('door_security_inbox'))
    assert isinstance(view.get('door_security_inbox'), dict)
    assert view['door_security_inbox'].get('open', 0) >= 1

    ui_result = save_security_command_dashboard_html(tower_user_id='owner_solice')
    assert ui_result.get('ok') is True
    command_response = client.get(packet['urls']['command'])
    text = command_response.get_data(as_text=True)
    _print('ui route', {
        'http': command_response.status_code,
        'has_door_access_inbox': 'Door access inbox' in text,
        'has_door_inbox': 'Door Inbox' in text,
        'has_review_items': 'review items' in text,
    })
    assert command_response.status_code == 200
    assert 'Door access inbox' in text
    assert 'Door Inbox' in text
    assert 'review items' in text
    assert 'tower_keycard=' not in text

    result = {
        'pack': '034',
        'status': 'passed',
        'human_reason': 'Door-swipe security inbox items are surfaced in Tower status, status JSON, and the protected Tower UI.',
    }
    _print('PACK 034 RESULT', result)
    return result


if __name__ == '__main__':
    run_tests()
