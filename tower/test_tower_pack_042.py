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

from tower.ob_object_clearance import evaluate_ob_object_clearance
from tower.ob_object_clearance import get_ob_object_clearance_policy_catalog
from tower.ob_object_clearance import require_ob_object_clearance


def _print(title, payload=None):
    print()
    print('=' * 80)
    print(title)
    print('=' * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))


def run_tests():
    catalog = get_ob_object_clearance_policy_catalog()
    _print('OBJECT CATALOG', {'ok': catalog.get('ok'), 'count': catalog.get('count'), 'keys': sorted(catalog.get('catalog', {}).keys())})
    assert catalog.get('ok') is True
    assert catalog.get('count', 0) >= 7

    pro_symbol = evaluate_ob_object_clearance(
        user_id='beta_pro',
        role='pro',
        route_key='symbol_detail',
        object_type='symbol',
        object_id='AAPL',
        action='view',
        current_risk_score=12,
    )
    _print('PRO SYMBOL ALLOWED', pro_symbol)
    assert pro_symbol.get('allowed') is True

    user_sensitive_symbol = evaluate_ob_object_clearance(
        user_id='beta_001',
        role='user',
        route_key='symbol_detail',
        object_type='symbol',
        object_id='SPY',
        action='view',
        current_risk_score=12,
    )
    _print('USER SENSITIVE SYMBOL DENIED', user_sensitive_symbol)
    assert user_sensitive_symbol.get('allowed') is False
    assert user_sensitive_symbol.get('reason_code') in {'ob_object_clearance_level_too_low', 'parent_route_clearance_failed'}

    owner_trade = evaluate_ob_object_clearance(
        user_id='owner_solice',
        role='owner',
        route_key='positions',
        object_type='trade',
        object_id='trade_INTL_001',
        owner_user_id='owner_solice',
        action='view',
        current_risk_score=8,
    )
    _print('OWNER TRADE ALLOWED', owner_trade)
    assert owner_trade.get('allowed') is True

    other_user_trade = evaluate_ob_object_clearance(
        user_id='beta_001',
        role='user',
        route_key='positions',
        object_type='trade',
        object_id='trade_owner_only_001',
        owner_user_id='owner_solice',
        action='view',
        current_risk_score=8,
    )
    _print('OTHER USER TRADE DENIED', other_user_trade)
    assert other_user_trade.get('allowed') is False
    assert other_user_trade.get('reason_code') in {'ob_object_owner_mismatch', 'ob_object_clearance_level_too_low', 'parent_route_clearance_failed'}

    export_user = evaluate_ob_object_clearance(
        user_id='beta_001',
        role='user',
        route_key='export',
        object_type='export',
        object_id='export_packet_001',
        action='download',
        current_risk_score=5,
    )
    _print('USER EXPORT DENIED', export_user)
    assert export_user.get('allowed') is False

    owner_export = evaluate_ob_object_clearance(
        user_id='owner_solice',
        role='owner',
        route_key='export',
        object_type='export',
        object_id='export_packet_001',
        action='download',
        current_risk_score=5,
    )
    _print('OWNER EXPORT ALLOWED', owner_export)
    assert owner_export.get('allowed') is True

    risky_object = evaluate_ob_object_clearance(
        user_id='owner_solice',
        role='owner',
        object_type='account',
        object_id='acct_live_001',
        action='view',
        current_risk_score=95,
        max_allowed_risk_score=85,
    )
    _print('RISKY OBJECT STEP UP', risky_object)
    assert risky_object.get('allowed') is False
    assert risky_object.get('decision') == 'step_up'

    wrong_action = evaluate_ob_object_clearance(
        user_id='owner_solice',
        role='owner',
        object_type='symbol',
        object_id='AAPL',
        action='download',
    )
    _print('WRONG OBJECT ACTION DENIED', wrong_action)
    assert wrong_action.get('allowed') is False
    assert wrong_action.get('reason_code') == 'ob_object_action_not_allowed'

    wrapper = require_ob_object_clearance(
        user_id='owner_solice',
        role='owner',
        object_type='mode',
        object_id='live_automated',
        action='enter',
        metadata={'mode_name': 'live_automated'},
    )
    _print('WRAPPER MODE', wrapper)
    assert wrapper.get('allowed') is True
    assert wrapper.get('metadata', {}).get('required_clearance_level') == 'critical'

    serialized = json.dumps([pro_symbol, user_sensitive_symbol, owner_trade, other_user_trade, export_user, owner_export, risky_object, wrong_action, wrapper], sort_keys=True)
    assert 'tower_keycard=' not in serialized
    assert 'raw_token' not in serialized
    assert 'Soulaana:' in serialized

    final = {
        'pack': '042',
        'status': 'passed',
        'human_reason': 'Tower object-level clearance helper can allow, deny, step up, enforce ownership, and protect specific OB objects.'
    }
    _print('PACK 042 RESULT', final)
    return final


if __name__ == '__main__':
    run_tests()
