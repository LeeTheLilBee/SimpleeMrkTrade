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
    before = summarize_door_swipe_security_inbox(limit=10)
    before_open = int(before.get('open', 0) or 0)
    _print('BEFORE DOOR INBOX', {
        'total': before.get('total'),
        'open': before_open,
        'by_status': before.get('by_status'),
    })

    result = run_tower_security_smoke()
    _print('SMOKE RESULT', result)

    assert result.get('ok') is True
    assert not result.get('failures')
    assert 'door_inbox_smoke_self_cleanup' in result.get('checks', {})
    assert result['checks']['door_inbox_smoke_self_cleanup']['ok'] is True

    workflow_detail = result['checks']['door_inbox_review_resolve_workflow']['detail']
    assert workflow_detail.get('reviewing_ok') is True
    assert workflow_detail.get('resolved_ok') is True
    assert workflow_detail.get('capsule_unchanged') is True
    assert workflow_detail.get('self_cleaning') is True

    after = summarize_door_swipe_security_inbox(limit=10)
    after_open = int(after.get('open', 0) or 0)
    _print('AFTER DOOR INBOX', {
        'total': after.get('total'),
        'open': after_open,
        'by_status': after.get('by_status'),
    })

    # The smoke test may create and resolve/archive items, but it should not
    # balloon the open queue by more than one across a full run.
    assert after_open <= before_open + 1
    assert after.get('by_status', {}).get('ignored', 0) >= 1 or after.get('by_status', {}).get('resolved', 0) >= 1

    serialized = json.dumps(result, sort_keys=True, default=str)
    assert 'tower_keycard=' not in serialized
    assert 'raw_token' not in serialized

    final = {
        'pack': '039',
        'status': 'passed',
        'human_reason': 'Tower smoke test now self-cleans test-generated door inbox noise while still validating security behavior.',
    }
    _print('PACK 039 RESULT', final)
    return final


if __name__ == '__main__':
    run_tests()
