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

from tower.tower_readiness_checkpoint import build_tower_readiness_checkpoint


def _print(title, payload=None):
    print()
    print('=' * 80)
    print(title)
    print('=' * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))


def run_tests():
    checkpoint = build_tower_readiness_checkpoint()
    _print('READINESS CHECKPOINT', checkpoint)

    assert checkpoint.get('pack') == '040'
    assert checkpoint.get('ok') is True
    assert checkpoint.get('smoke_ok') is True
    assert checkpoint.get('readiness_score', 0) >= 90
    assert 'Soulaana:' in checkpoint.get('soulaana_translation', '')
    assert len(checkpoint.get('built_packs', [])) >= 15
    assert len(checkpoint.get('protected_surfaces', [])) >= 7
    assert len(checkpoint.get('next_before_deeper_ob', [])) >= 5

    protected = json.dumps(checkpoint.get('protected_surfaces', []), sort_keys=True)
    assert '/tower/security-command' in protected
    assert '/tower/status.json' in protected

    next_steps = json.dumps(checkpoint.get('next_before_deeper_ob', []), sort_keys=True)
    assert 'OB' in next_steps
    assert 'object-level' in next_steps or 'object' in next_steps

    serialized = json.dumps(checkpoint, sort_keys=True, default=str)
    assert 'tower_keycard=' not in serialized
    assert 'raw_token' not in serialized

    final = {
        'pack': '040',
        'status': 'passed',
        'human_reason': 'Tower readiness checkpoint summarizes built packs, protected surfaces, readiness score, and next integration steps.'
    }
    _print('PACK 040 RESULT', final)
    return final


if __name__ == '__main__':
    run_tests()
