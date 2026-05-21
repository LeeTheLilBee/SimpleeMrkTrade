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

from tower.door_audit_capsules import DOOR_SECURITY_INBOX_PATH
from tower.door_audit_capsules import load_door_swipe_audit_capsules
from tower.door_audit_capsules import load_door_swipe_security_inbox
from tower.door_audit_capsules import summarize_door_swipe_security_inbox
from tower.owner_launch_cell import build_owner_tower_launch_packet
from web.app import app


def _print(title, payload=None):
    print()
    print('=' * 80)
    print(title)
    print('=' * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))


def run_tests():
    before_audit = len(load_door_swipe_audit_capsules())
    before_inbox = len(load_door_swipe_security_inbox())
    _print('BEFORE COUNTS', {'audit': before_audit, 'inbox': before_inbox, 'path': str(DOOR_SECURITY_INBOX_PATH)})

    client = app.test_client()

    _print('NORMAL ALLOWED SWIPE SHOULD STAY QUIET')
    packet = build_owner_tower_launch_packet(
        actor_user_id='owner_solice',
        target_user_id='owner_solice',
        session_id='session_pack033',
        device_id='device_pack033',
        ttl_seconds=900,
        include_regenerate=False,
    )
    assert packet.get('ok') is True
    allowed = client.get(packet['urls']['command'])
    assert allowed.status_code == 200

    _print('MISSING KEYCARD DENY SHOULD CREATE INBOX ITEM')
    missing = client.get('/tower/security-command')
    assert missing.status_code == 403

    _print('WRONG DOOR DENY SHOULD CREATE INBOX ITEM')
    wrong = client.get(packet['urls']['status'].replace('/tower/status.json', '/tower/security-command'))
    assert wrong.status_code == 403

    after_audit = len(load_door_swipe_audit_capsules())
    inbox_items = load_door_swipe_security_inbox()
    after_inbox = len(inbox_items)
    summary = summarize_door_swipe_security_inbox(limit=8)
    _print('AFTER SUMMARY', {
        'audit_before': before_audit,
        'audit_after': after_audit,
        'inbox_before': before_inbox,
        'inbox_after': after_inbox,
        'summary_total': summary.get('total'),
        'summary_open': summary.get('open'),
        'by_severity': summary.get('by_severity'),
        'by_reason': summary.get('by_reason'),
    })

    assert after_audit >= before_audit + 3
    assert after_inbox >= before_inbox + 1
    assert summary.get('open', 0) >= 1
    assert summary.get('by_reason', {}).get('wrong_door', 0) >= 1 or summary.get('by_reason', {}).get('tower_keycard_required', 0) >= 1

    recent = summary.get('last', [])
    serialized = json.dumps(recent, sort_keys=True)
    assert 'tower_keycard=' not in serialized
    assert 'raw_token' not in serialized
    assert 'Soulaana:' in serialized

    review_items = [item for item in inbox_items if item.get('event_type') == 'tower_door_swipe_security_review']
    assert review_items
    for item in review_items[-3:]:
        assert item.get('inbox_item_id')
        assert item.get('source_capsule_id')
        assert item.get('severity') in {'medium', 'high', 'critical', 'watch', 'info'}
        assert item.get('owner_action')
        assert item.get('soulaana_translation')
        assert item.get('routing', {}).get('queue') == 'tower_security_inbox'

    result = {
        'pack': '033',
        'status': 'passed',
        'human_reason': 'Review-worthy Tower door swipes now become actionable security inbox items without storing raw keycard tokens.',
        'inbox_path': str(DOOR_SECURITY_INBOX_PATH),
    }
    _print('PACK 033 RESULT', result)
    return result


if __name__ == '__main__':
    run_tests()
