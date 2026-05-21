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

from tower.tower_security_smoke import run_tower_security_smoke
from tower.door_audit_capsules import summarize_door_swipe_security_inbox


def _print(title, payload=None):
    print()
    print('=' * 80)
    print(title)
    print('=' * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))


def run_tests():
    _print('RUN UPDATED TOWER SECURITY SMOKE TEST')
    result = run_tower_security_smoke()
    _print('smoke result', result)

    assert result.get('ok') is True
    assert not result.get('failures')

    required = [
        'keycard_health_loads',
        'owner_launch_packet_issued',
        'unkeyed_command_locks',
        'keyed_command_opens',
        'status_json_opens',
        'wrong_door_locks',
        'news_warning_quiet',
        'door_audit_capsules_active',
        'door_security_inbox_active',
        'door_inbox_open_items_listable',
        'door_inbox_review_resolve_workflow',
        'tower_status_has_door_audit',
        'tower_status_has_door_security_inbox',
        'tower_ui_regenerates',
        'tower_ui_has_door_security_inbox_data',
        'no_raw_keycard_in_status_or_view',
    ]

    for key in required:
        assert key in result['checks'], key
        assert result['checks'][key]['ok'] is True, key

    workflow_detail = result['checks']['door_inbox_review_resolve_workflow']['detail']
    assert workflow_detail.get('reviewing_ok') is True
    assert workflow_detail.get('resolved_ok') is True
    assert workflow_detail.get('capsule_unchanged') is True

    inbox = summarize_door_swipe_security_inbox(limit=10)
    _print('door inbox after smoke', {
        'total': inbox.get('total'),
        'open': inbox.get('open'),
        'by_status': inbox.get('by_status'),
    })
    assert inbox.get('by_status', {}).get('resolved', 0) >= 1

    serialized = json.dumps(result, sort_keys=True, default=str)
    assert 'tower_keycard=' not in serialized
    assert 'raw_token' not in serialized

    final = {
        'pack': '038',
        'status': 'passed',
        'human_reason': 'Tower smoke test now validates door-swipe inbox review/resolve workflow and original audit capsule preservation.',
    }
    _print('PACK 038 RESULT', final)
    return final


if __name__ == '__main__':
    run_tests()
