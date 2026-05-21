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

from tower.ob_clearance_bridge import evaluate_ob_route_clearance
from tower.ob_clearance_bridge import get_ob_route_clearance_catalog
from tower.ob_clearance_bridge import require_ob_route_clearance


def _print(title, payload=None):
    print()
    print('=' * 80)
    print(title)
    print('=' * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))


def run_tests():
    catalog = get_ob_route_clearance_catalog()
    _print('CATALOG', {'ok': catalog.get('ok'), 'count': catalog.get('count'), 'keys': sorted(catalog.get('catalog', {}).keys())})
    assert catalog.get('ok') is True
    assert catalog.get('count', 0) >= 8
    assert 'live_automated' in catalog.get('catalog', {})
    assert 'export' in catalog.get('catalog', {})

    owner_live = evaluate_ob_route_clearance(
        user_id='owner_solice',
        role='owner',
        route_key='live_automated',
        action='enter',
        current_risk_score=10,
    )
    _print('OWNER LIVE AUTOMATED', owner_live)
    assert owner_live.get('allowed') is True
    assert owner_live.get('decision') == 'allow'

    beta_live = evaluate_ob_route_clearance(
        user_id='beta_001',
        role='user',
        route_key='live_automated',
        action='enter',
        current_risk_score=10,
    )
    _print('BETA LIVE AUTOMATED DENIED', beta_live)
    assert beta_live.get('allowed') is False
    assert beta_live.get('reason_code') == 'ob_clearance_level_too_low'

    beta_dashboard = evaluate_ob_route_clearance(
        user_id='beta_001',
        role='user',
        route_key='dashboard',
        action='view',
        current_risk_score=10,
    )
    _print('BETA DASHBOARD ALLOWED', beta_dashboard)
    assert beta_dashboard.get('allowed') is True

    wrong_action = evaluate_ob_route_clearance(
        user_id='owner_solice',
        role='owner',
        route_key='signals',
        action='export',
        current_risk_score=10,
    )
    _print('WRONG ACTION DENIED', wrong_action)
    assert wrong_action.get('allowed') is False
    assert wrong_action.get('reason_code') == 'ob_action_not_allowed_for_route'

    risky = evaluate_ob_route_clearance(
        user_id='owner_solice',
        role='owner',
        route_key='live_mode',
        action='enter',
        current_risk_score=95,
        max_allowed_risk_score=85,
    )
    _print('RISK STEP UP', risky)
    assert risky.get('allowed') is False
    assert risky.get('decision') == 'step_up'
    assert risky.get('reason_code') == 'ob_route_risk_too_high'

    unknown = evaluate_ob_route_clearance(
        user_id='owner_solice',
        role='owner',
        route_key='not_real_yet',
        action='view',
    )
    _print('UNKNOWN ROUTE DENIED', unknown)
    assert unknown.get('allowed') is False
    assert unknown.get('reason_code') == 'unknown_ob_route_or_action'

    wrapper = require_ob_route_clearance(
        user_id='owner_solice',
        role='owner',
        route_key='export',
        action='export',
        current_risk_score=5,
    )
    _print('WRAPPER EXPORT', wrapper)
    assert wrapper.get('allowed') is True

    serialized = json.dumps([owner_live, beta_live, beta_dashboard, wrong_action, risky, unknown, wrapper], sort_keys=True)
    assert 'tower_keycard=' not in serialized
    assert 'raw_token' not in serialized
    assert 'Soulaana:' in serialized

    final = {
        'pack': '041',
        'status': 'passed',
        'human_reason': 'Tower OB route/action clearance helper can allow, deny, step up, and explain OB access decisions before route wiring.'
    }
    _print('PACK 041 RESULT', final)
    return final


if __name__ == '__main__':
    run_tests()
