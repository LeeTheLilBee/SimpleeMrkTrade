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

from tower.ob_mode_clearance import evaluate_ob_mode_clearance
from tower.ob_mode_clearance import get_ob_mode_clearance_catalog
from tower.ob_mode_clearance import normalize_ob_mode
from tower.ob_mode_clearance import require_ob_mode_clearance


def _print(title, payload=None):
    print()
    print('=' * 80)
    print(title)
    print('=' * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))


def run_tests():
    catalog = get_ob_mode_clearance_catalog()
    _print('MODE CATALOG', {'ok': catalog.get('ok'), 'count': catalog.get('count'), 'keys': sorted(catalog.get('catalog', {}).keys())})
    assert catalog.get('ok') is True
    assert catalog.get('count') == 5
    assert normalize_ob_mode('Paper Mode') == 'paper'
    assert normalize_ob_mode('automated-live') == 'live_automated'

    survey_user = evaluate_ob_mode_clearance(
        user_id='beta_001',
        role='user',
        mode_name='survey',
        action='enter',
        current_risk_score=10,
    )
    _print('SURVEY USER ALLOWED', survey_user)
    assert survey_user.get('allowed') is True

    paper_pro = evaluate_ob_mode_clearance(
        user_id='beta_pro',
        role='pro',
        mode_name='paper',
        action='enter',
        current_risk_score=10,
    )
    _print('PAPER PRO ALLOWED', paper_pro)
    assert paper_pro.get('allowed') is True

    paper_user = evaluate_ob_mode_clearance(
        user_id='beta_001',
        role='user',
        mode_name='paper',
        action='enter',
        current_risk_score=10,
    )
    _print('PAPER USER DENIED', paper_user)
    assert paper_user.get('allowed') is False
    assert paper_user.get('reason_code') == 'ob_mode_clearance_level_too_low'

    manual_no_broker = evaluate_ob_mode_clearance(
        user_id='owner_solice',
        role='owner',
        mode_name='manual',
        action='enter',
        broker_connected=False,
        broker_healthy=False,
        live_authorized=True,
    )
    _print('MANUAL NO BROKER DENIED', manual_no_broker)
    assert manual_no_broker.get('allowed') is False
    assert manual_no_broker.get('reason_code') == 'ob_mode_broker_not_ready'

    live_no_auth = evaluate_ob_mode_clearance(
        user_id='owner_solice',
        role='owner',
        mode_name='live',
        action='enter',
        broker_connected=True,
        broker_healthy=True,
        live_authorized=False,
    )
    _print('LIVE NO AUTH DENIED', live_no_auth)
    assert live_no_auth.get('allowed') is False
    assert live_no_auth.get('reason_code') == 'ob_mode_live_authorization_missing'

    live_owner = evaluate_ob_mode_clearance(
        user_id='owner_solice',
        role='owner',
        mode_name='live',
        action='enter',
        broker_connected=True,
        broker_healthy=True,
        live_authorized=True,
        current_risk_score=10,
    )
    _print('LIVE OWNER ALLOWED', live_owner)
    assert live_owner.get('allowed') is True

    auto_no_automation = evaluate_ob_mode_clearance(
        user_id='owner_solice',
        role='owner',
        mode_name='live_automated',
        action='enter',
        broker_connected=True,
        broker_healthy=True,
        live_authorized=True,
        automation_authorized=False,
        current_risk_score=10,
    )
    _print('AUTO NO AUTOMATION DENIED', auto_no_automation)
    assert auto_no_automation.get('allowed') is False
    assert auto_no_automation.get('reason_code') == 'ob_mode_automation_authorization_missing'

    auto_owner = require_ob_mode_clearance(
        user_id='owner_solice',
        role='owner',
        mode_name='live_automated',
        action='enter',
        broker_connected=True,
        broker_healthy=True,
        live_authorized=True,
        automation_authorized=True,
        current_risk_score=10,
    )
    _print('AUTO OWNER ALLOWED', auto_owner)
    assert auto_owner.get('allowed') is True

    high_risk_live = evaluate_ob_mode_clearance(
        user_id='owner_solice',
        role='owner',
        mode_name='live',
        action='enter',
        broker_connected=True,
        broker_healthy=True,
        live_authorized=True,
        current_risk_score=90,
    )
    _print('HIGH RISK LIVE STEP UP', high_risk_live)
    assert high_risk_live.get('allowed') is False
    assert high_risk_live.get('decision') == 'step_up'

    lockdown = evaluate_ob_mode_clearance(
        user_id='owner_solice',
        role='owner',
        mode_name='survey',
        action='enter',
        emergency_lockdown=True,
    )
    _print('LOCKDOWN DENIED', lockdown)
    assert lockdown.get('allowed') is False
    assert lockdown.get('reason_code') == 'tower_emergency_lockdown_active'

    unknown = evaluate_ob_mode_clearance(
        user_id='owner_solice',
        role='owner',
        mode_name='not_a_mode',
        action='enter',
    )
    _print('UNKNOWN MODE DENIED', unknown)
    assert unknown.get('allowed') is False
    assert unknown.get('reason_code') == 'unknown_ob_mode'

    serialized = json.dumps([survey_user, paper_pro, paper_user, manual_no_broker, live_no_auth, live_owner, auto_no_automation, auto_owner, high_risk_live, lockdown, unknown], sort_keys=True)
    assert 'tower_keycard=' not in serialized
    assert 'raw_token' not in serialized
    assert 'Soulaana:' in serialized

    final = {
        'pack': '043',
        'status': 'passed',
        'human_reason': 'Tower OB mode clearance bridge protects Survey, Paper, Manual, Live, and Live Automated modes with risk, broker, live, automation, and lockdown checks.'
    }
    _print('PACK 043 RESULT', final)
    return final


if __name__ == '__main__':
    run_tests()
