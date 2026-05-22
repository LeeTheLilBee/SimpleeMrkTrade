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
    if name == 'tower' or name.startswith('tower.'):
        sys.modules.pop(name, None)

from tower.ob_route_guard import build_locked_ob_response
from tower.ob_route_guard import evaluate_ob_request_guard
from tower.ob_route_guard import get_ob_route_guard_report
from tower.ob_route_guard import match_ob_guard_policy
from tower.ob_route_guard import should_block_ob_request


def _print(title, payload=None):
    print()
    print('=' * 80)
    print(title)
    print('=' * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))


def run_tests():
    report = get_ob_route_guard_report()
    _print('GUARD REPORT', {
        'ok': report.get('ok'),
        'guarded_count': report.get('guarded_count'),
        'public_safe_count': report.get('public_safe_count'),
        'default_deny_unmapped': report.get('default_deny_unmapped'),
    })
    assert report.get('ok') is True
    assert report.get('guarded_count', 0) >= 8
    assert report.get('default_deny_unmapped') is True

    public_match = match_ob_guard_policy('/login')
    _print('PUBLIC MATCH', public_match)
    assert public_match.get('match_type') == 'public_safe'

    signals_match = match_ob_guard_policy('/signals')
    _print('SIGNALS MATCH', signals_match)
    assert signals_match.get('matched') is True
    assert signals_match.get('policy', {}).get('route_key') == 'signals'

    symbol_match = match_ob_guard_policy('/signals/AAPL')
    _print('SYMBOL MATCH', symbol_match)
    assert symbol_match.get('match_type') == 'dynamic_symbol'
    assert symbol_match.get('object_id') == 'AAPL'

    unmapped_match = match_ob_guard_policy('/secret-new-page')
    _print('UNMAPPED MATCH', unmapped_match)
    assert unmapped_match.get('match_type') == 'unmapped_default_deny'

    public_decision = evaluate_ob_request_guard(
        path='/login',
        user_id='anonymous',
        role='',
    )
    _print('PUBLIC DECISION', public_decision)
    assert public_decision.get('allowed') is True
    assert public_decision.get('reason_code') == 'ob_public_safe_route'

    owner_signals = evaluate_ob_request_guard(
        path='/signals',
        user_id='owner_solice',
        role='owner',
        current_risk_score=10,
    )
    _print('OWNER SIGNALS DECISION', owner_signals)
    assert owner_signals.get('allowed') is True

    user_signals = evaluate_ob_request_guard(
        path='/signals',
        user_id='beta_001',
        role='user',
        current_risk_score=10,
    )
    _print('USER SIGNALS DENIED', user_signals)
    assert user_signals.get('allowed') is False
    assert user_signals.get('reason_code') == 'ob_clearance_level_too_low'

    owner_symbol = evaluate_ob_request_guard(
        path='/signals/AAPL',
        user_id='owner_solice',
        role='owner',
        current_risk_score=10,
    )
    _print('OWNER SYMBOL DECISION', owner_symbol)
    assert owner_symbol.get('allowed') is True

    unmapped_decision = evaluate_ob_request_guard(
        path='/brand-new-unmapped-page',
        user_id='owner_solice',
        role='owner',
        current_risk_score=10,
    )
    _print('UNMAPPED DEFAULT DENY DECISION', unmapped_decision)
    assert unmapped_decision.get('allowed') is False
    assert unmapped_decision.get('reason_code') == 'ob_route_unmapped_default_deny'

    block_decision = should_block_ob_request(
        path='/signals',
        user_id='beta_001',
        role='user',
    )
    _print('BLOCK DECISION', block_decision)
    assert block_decision.get('block') is True

    html, status = build_locked_ob_response(
        reason_code='test_locked',
        human_reason='Testing locked page.',
        path='/signals',
        decision=block_decision,
    )
    _print('LOCKED RESPONSE', {'status': status, 'has_private': 'Private corridor locked' in html, 'has_soulaana': 'Soulaana:' in html})
    assert status == 403
    assert 'Private corridor locked' in html
    assert 'Soulaana:' in html

    serialized = json.dumps([report, public_decision, owner_signals, user_signals, owner_symbol, unmapped_decision, block_decision], sort_keys=True, default=str)
    assert 'tower_keycard=' not in serialized
    assert 'raw_token' not in serialized
    assert 'Soulaana:' in serialized

    final = {
        'pack': '045',
        'status': 'passed',
        'human_reason': 'OB route guard foundation can classify public-safe routes, protected routes, dynamic symbol routes, and unmapped default-deny routes before real Flask wiring.'
    }
    _print('PACK 045 RESULT', final)
    return final


if __name__ == '__main__':
    run_tests()
