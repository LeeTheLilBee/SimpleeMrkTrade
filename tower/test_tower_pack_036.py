from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path('/content/SimpleeMrkTrade_REAL_CLONE')
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tower.tower_security_smoke import run_tower_security_smoke


def _print(title, payload=None):
    print()
    print('=' * 80)
    print(title)
    print('=' * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))


def run_tests():
    result = run_tower_security_smoke()
    _print('SMOKE RESULT', result)
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
        'tower_status_has_door_audit',
        'tower_status_has_door_security_inbox',
        'tower_ui_regenerates',
        'tower_ui_has_door_security_inbox_data',
        'no_raw_keycard_in_status_or_view',
    ]
    for key in required:
        assert key in result['checks']
        assert result['checks'][key]['ok'] is True
    final = {
        'pack': '036',
        'status': 'passed',
        'human_reason': 'One-command Tower security smoke test runner validates Packs 025 through 035 together.',
    }
    _print('PACK 036 RESULT', final)
    return final


if __name__ == '__main__':
    run_tests()
