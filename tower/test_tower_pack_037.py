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

from tower.door_audit_capsules import load_door_swipe_audit_capsules
from tower.door_audit_capsules import list_door_swipe_security_inbox_items
from tower.door_audit_capsules import mark_door_swipe_security_inbox_reviewing
from tower.door_audit_capsules import resolve_door_swipe_security_inbox_item
from tower.door_audit_capsules import summarize_door_swipe_security_inbox
from tower.owner_launch_cell import build_owner_tower_launch_packet
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

    _print('ENSURE AT LEAST ONE OPEN DOOR INBOX ITEM EXISTS')
    client.get('/tower/security-command')

    open_items = list_door_swipe_security_inbox_items(status='open', limit=10)
    _print('open items', {
        'ok': open_items.get('ok'),
        'count': open_items.get('count'),
    })
    assert open_items.get('ok') is True
    assert open_items.get('count', 0) >= 1

    target = open_items['items'][-1]
    inbox_item_id = target['inbox_item_id']
    source_capsule_id = target.get('source_capsule_id')

    before_capsules = load_door_swipe_audit_capsules()
    matching_capsules_before = [x for x in before_capsules if x.get('capsule_id') == source_capsule_id]
    assert matching_capsules_before
    original_capsule_before = json.dumps(matching_capsules_before[0], sort_keys=True)

    _print('MARK ITEM REVIEWING')
    reviewing = mark_door_swipe_security_inbox_reviewing(
        inbox_item_id,
        actor_user_id='owner_solice',
        note='Pack 037 test: reviewing this door swipe item.',
    )
    _print('reviewing result', reviewing)
    assert reviewing.get('ok') is True
    assert reviewing.get('new_status') == 'reviewing'

    reviewing_items = list_door_swipe_security_inbox_items(status='reviewing', limit=20)
    reviewed_match = [x for x in reviewing_items.get('items', []) if x.get('inbox_item_id') == inbox_item_id]
    assert reviewed_match
    assert reviewed_match[0].get('review_started_at')
    assert reviewed_match[0].get('owner_notes')
    assert reviewed_match[0].get('history')

    _print('RESOLVE ITEM')
    resolved = resolve_door_swipe_security_inbox_item(
        inbox_item_id,
        actor_user_id='owner_solice',
        note='Pack 037 test: resolved as expected protected-route check.',
    )
    _print('resolved result', resolved)
    assert resolved.get('ok') is True
    assert resolved.get('new_status') == 'resolved'

    resolved_items = list_door_swipe_security_inbox_items(status='resolved', limit=30)
    resolved_match = [x for x in resolved_items.get('items', []) if x.get('inbox_item_id') == inbox_item_id]
    assert resolved_match
    resolved_item = resolved_match[0]
    assert resolved_item.get('resolved_at')
    assert resolved_item.get('resolved_by') == 'owner_solice'
    assert resolved_item.get('routing', {}).get('surface') == 'resolved_archive'
    assert resolved_item.get('routing', {}).get('requires_step_up_review') is False

    _print('ORIGINAL CAPSULE UNCHANGED')
    after_capsules = load_door_swipe_audit_capsules()
    matching_capsules_after = [x for x in after_capsules if x.get('capsule_id') == source_capsule_id]
    assert matching_capsules_after
    original_capsule_after = json.dumps(matching_capsules_after[0], sort_keys=True)
    assert original_capsule_before == original_capsule_after

    _print('SUMMARY REFLECTS RESOLUTION')
    summary = summarize_door_swipe_security_inbox(limit=8)
    _print('summary', {
        'total': summary.get('total'),
        'open': summary.get('open'),
        'by_status': summary.get('by_status'),
    })
    assert summary.get('by_status', {}).get('resolved', 0) >= 1

    status = get_tower_status()
    _print('tower status door inbox', {
        'open': status.get('door_swipe_security_inbox_open'),
        'total': status.get('door_swipe_security_inbox_total'),
        'by_status': status.get('door_swipe_security_inbox_by_status'),
    })
    assert status.get('door_swipe_security_inbox_by_status', {}).get('resolved', 0) >= 1

    serialized = json.dumps(summary, sort_keys=True)
    assert 'tower_keycard=' not in serialized
    assert 'raw_token' not in serialized

    result = {
        'pack': '037',
        'status': 'passed',
        'human_reason': 'Door-swipe security inbox items can be listed, marked reviewing, resolved, and annotated without mutating original audit capsules.',
    }
    _print('PACK 037 RESULT', result)
    return result


if __name__ == '__main__':
    run_tests()
