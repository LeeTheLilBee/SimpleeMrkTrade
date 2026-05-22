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
from tower.tower_readiness_checkpoint import build_tower_readiness_checkpoint


def _print(title, payload=None):
    print()
    print('=' * 80)
    print(title)
    print('=' * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))


def run_tests():
    smoke = run_tower_security_smoke()
    _print('UPDATED SMOKE RESULT', {
        'ok': smoke.get('ok'),
        'failures': smoke.get('failures'),
        'checks': sorted(smoke.get('checks', {}).keys()),
    })
    assert smoke.get('ok') is True
    assert not smoke.get('failures')

    for key in [
        'ob_route_clearance_bridge_active',
        'ob_object_clearance_bridge_active',
        'ob_mode_clearance_bridge_active',
        'no_raw_keycard_in_ob_clearance_results',
    ]:
        assert key in smoke.get('checks', {}), key
        assert smoke['checks'][key]['ok'] is True, key

    checkpoint = build_tower_readiness_checkpoint()
    _print('UPDATED READINESS RESULT', {
        'ok': checkpoint.get('ok'),
        'readiness_score': checkpoint.get('readiness_score'),
        'readiness_label': checkpoint.get('readiness_label'),
        'ob_clearance_summary': checkpoint.get('ob_clearance_summary'),
        'built_pack_count': len(checkpoint.get('built_packs', [])),
        'next_steps': checkpoint.get('next_before_deeper_ob'),
    })

    assert checkpoint.get('ok') is True
    assert checkpoint.get('readiness_score', 0) >= 100
    ob_summary = checkpoint.get('ob_clearance_summary')
    assert isinstance(ob_summary, dict)
    assert ob_summary.get('route_bridge_ok') is True
    assert ob_summary.get('object_bridge_ok') is True
    assert ob_summary.get('mode_bridge_ok') is True

    built = json.dumps(checkpoint.get('built_packs', []), sort_keys=True)
    assert '041' in built
    assert '042' in built
    assert '043' in built

    next_steps = json.dumps(checkpoint.get('next_before_deeper_ob', []), sort_keys=True)
    assert 'Wire OB pages' in next_steps
    assert 'object clearance' in next_steps
    assert 'mode switcher' in next_steps

    serialized = json.dumps([smoke, checkpoint], sort_keys=True, default=str)
    assert 'tower_keycard=' not in serialized
    assert 'raw_token' not in serialized

    final = {
        'pack': '044',
        'status': 'passed',
        'human_reason': 'Tower smoke and readiness now officially include OB route/action, object-level, and mode clearance bridges.'
    }
    _print('PACK 044 RESULT', final)
    return final


if __name__ == '__main__':
    run_tests()
