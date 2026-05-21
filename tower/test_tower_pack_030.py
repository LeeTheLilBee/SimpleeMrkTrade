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

from tower.owner_launch_cell import build_owner_tower_launch_packet
from tower.owner_launch_cell import print_owner_tower_launch_cell
from web.app import app


def _print(title, payload=None):
    print()
    print('=' * 80)
    print(title)
    print('=' * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))


def run_tests():
    _print('BUILD OWNER TOWER LAUNCH PACKET')
    packet = build_owner_tower_launch_packet(
        actor_user_id='owner_solice',
        target_user_id='owner_solice',
        session_id='session_pack030',
        device_id='device_pack030',
        ttl_seconds=900,
        include_regenerate=False,
    )
    _print('packet summary', {
        'ok': packet.get('ok'),
        'issued_keys': packet.get('issued_keys'),
        'url_keys': sorted(packet.get('urls', {}).keys()),
        'expires_in_seconds': packet.get('expires_in_seconds'),
    })
    assert packet.get('ok') is True
    assert sorted(packet.get('urls', {}).keys()) == ['command', 'entry', 'status']
    assert 'tower_keycard=' in packet['urls']['command']
    assert 'tower_keycard=' in packet['urls']['entry']
    assert 'tower_keycard=' in packet['urls']['status']

    client = app.test_client()

    _print('COMMAND URL OPENS PROTECTED UI')
    response = client.get(packet['urls']['command'])
    text = response.get_data(as_text=True)
    _print('command response', {
        'status': response.status_code,
        'has_tower': 'The Tower' in text,
        'has_health': 'Tower health gauge' in text,
        'has_soulaana': 'Soulaana' in text,
    })
    assert response.status_code == 200
    assert 'Tower health gauge' in text
    assert 'Soulaana' in text

    _print('UNKEYED COMMAND STILL LOCKS')
    locked = client.get('/tower/security-command')
    locked_text = locked.get_data(as_text=True)
    _print('locked response', {
        'status': locked.status_code,
        'has_clearance_required': 'Clearance required' in locked_text,
    })
    assert locked.status_code == 403
    assert 'Clearance required' in locked_text
    assert 'Tower health gauge' not in locked_text

    _print('PRINT HELPER RETURNS PACKET')
    printed = print_owner_tower_launch_cell(
        actor_user_id='owner_solice',
        target_user_id='owner_solice',
        session_id='session_pack030_print',
        device_id='device_pack030_print',
        ttl_seconds=900,
        include_regenerate=False,
    )
    assert printed.get('ok') is True
    assert sorted(printed.get('urls', {}).keys()) == ['command', 'entry', 'status']

    result = {
        'pack': '030',
        'status': 'passed',
        'human_reason': 'Owner Tower launch cell helper creates fresh temporary scoped Tower links and protected routes still enforce keycards.',
    }
    _print('PACK 030 RESULT', result)
    return result


if __name__ == '__main__':
    run_tests()
