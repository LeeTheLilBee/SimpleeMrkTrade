from __future__ import annotations

import contextlib
import io
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
from web.app import app
import web.app as web_app_module


def _print(title, payload=None):
    print()
    print('=' * 80)
    print(title)
    print('=' * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))


def run_tests():
    assert hasattr(web_app_module, '_pack035_quiet_news_cache_refresh')

    _print('SAFE HELPER WITH MISSING REFRESH FUNCTION')
    original = getattr(web_app_module, 'refresh_news_for_symbols', None)
    if hasattr(web_app_module, 'refresh_news_for_symbols'):
        delattr(web_app_module, 'refresh_news_for_symbols')

    result = web_app_module._pack035_quiet_news_cache_refresh(['AAPL'])
    _print('helper result', result)
    assert result.get('ok') is True
    assert result.get('status') == 'skipped'
    assert result.get('reason_code') == 'news_refresh_function_missing'

    if original is not None:
        setattr(web_app_module, 'refresh_news_for_symbols', original)

    _print('TOWER ROUTES DO NOT PRINT NEWS WARNING')
    packet = build_owner_tower_launch_packet(
        actor_user_id='owner_solice',
        target_user_id='owner_solice',
        session_id='session_pack035',
        device_id='device_pack035',
        ttl_seconds=900,
        include_regenerate=False,
    )
    assert packet.get('ok') is True

    client = app.test_client()
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        locked = client.get('/tower/security-command')
        command = client.get(packet['urls']['command'])
        status = client.get(packet['urls']['status'])

    output = captured.getvalue()
    _print('captured route output', {'output_preview': output[:500], 'contains_warning': '[NEWS_CACHE_AUTO_REFRESH]' in output})

    assert locked.status_code == 403
    assert command.status_code == 200
    assert status.status_code == 200
    assert '[NEWS_CACHE_AUTO_REFRESH]' not in output

    result = {
        'pack': '035',
        'status': 'passed',
        'human_reason': 'Missing news refresh function is now skipped quietly and Tower route tests no longer print the news auto-refresh warning.',
    }
    _print('PACK 035 RESULT', result)
    return result


if __name__ == '__main__':
    run_tests()
