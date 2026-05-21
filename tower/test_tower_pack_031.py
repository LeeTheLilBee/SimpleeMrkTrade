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

from tower.door_audit_capsules import DOOR_AUDIT_PATH
from tower.door_audit_capsules import load_door_swipe_audit_capsules
from tower.door_audit_capsules import summarize_door_swipe_audit_capsules
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
    before = load_door_swipe_audit_capsules()
    before_count = len(before)
    _print('BEFORE AUDIT COUNT', {'count': before_count, 'path': str(DOOR_AUDIT_PATH)})

    client = app.test_client()

    _print('UNKEYED COMMAND DENY CREATES CAPSULE')
    locked = client.get('/tower/security-command')
    locked_text = locked.get_data(as_text=True)
    _print('locked', {'status': locked.status_code, 'has_clearance_required': 'Clearance required' in locked_text})
    assert locked.status_code == 403

    _print('KEYED COMMAND ALLOW CREATES CAPSULE')
    packet = build_owner_tower_launch_packet(
        actor_user_id='owner_solice',
        target_user_id='owner_solice',
        session_id='session_pack031',
        device_id='device_pack031',
        ttl_seconds=900,
        include_regenerate=False,
    )
    assert packet.get('ok') is True
    command = client.get(packet['urls']['command'])
    command_text = command.get_data(as_text=True)
    _print('command', {'status': command.status_code, 'has_health': 'Tower health gauge' in command_text})
    assert command.status_code == 200

    _print('WRONG DOOR CREATES DENY CAPSULE')
    wrong = client.get(packet['urls']['status'].replace('/tower/status.json', '/tower/security-command'))
    wrong_text = wrong.get_data(as_text=True)
    _print('wrong door', {'status': wrong.status_code, 'has_clearance_required': 'Clearance required' in wrong_text})
    assert wrong.status_code == 403

    after = load_door_swipe_audit_capsules()
    after_count = len(after)
    summary = summarize_door_swipe_audit_capsules(limit=8)
    _print('AUDIT SUMMARY', {
        'before': before_count,
        'after': after_count,
        'total': summary.get('total'),
        'allowed': summary.get('allowed'),
        'denied': summary.get('denied'),
        'surfaced': summary.get('surfaced'),
        'by_reason': summary.get('by_reason'),
    })

    assert after_count >= before_count + 3
    recent = after[-3:]
    reasons = [item.get('reason_code') for item in recent]
    assert 'tower_keycard_required' in reasons
    assert 'keycard_pass_allowed' in reasons
    assert 'wrong_door' in reasons

    serialized_recent = json.dumps(recent, sort_keys=True)
    assert 'tower_keycard=' not in serialized_recent
    assert 'Soulaana:' in serialized_recent

    for item in recent:
        assert item.get('capsule_id')
        assert item.get('timestamp')
        assert item.get('door_id')
        assert item.get('action')
        assert item.get('reason_code')
        assert item.get('soulaana_translation')
        assert 'raw_token' not in item
        assert 'token' not in item

    result = {
        'pack': '031',
        'status': 'passed',
        'human_reason': 'Tower door-swipe audit capsules record allow/deny receipts with Soulaana translations and no raw keycard tokens.',
        'audit_path': str(DOOR_AUDIT_PATH),
    }
    _print('PACK 031 RESULT', result)
    return result


if __name__ == '__main__':
    run_tests()
