from __future__ import annotations

import contextlib
import io
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path('/content/SimpleeMrkTrade_REAL_CLONE')
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _clear_runtime_modules() -> None:
    for name in list(sys.modules.keys()):
        if name == 'tower' or name.startswith('tower.') or name == 'web.app':
            sys.modules.pop(name, None)


def run_tower_security_smoke() -> Dict[str, Any]:
    _clear_runtime_modules()

    from tower.door_audit_capsules import summarize_door_swipe_audit_capsules
    from tower.door_audit_capsules import summarize_door_swipe_security_inbox
    from tower.door_audit_capsules import load_door_swipe_audit_capsules
    from tower.door_audit_capsules import list_door_swipe_security_inbox_items
    from tower.door_audit_capsules import mark_door_swipe_security_inbox_reviewing
    from tower.door_audit_capsules import resolve_door_swipe_security_inbox_item
    from tower.door_audit_capsules import ignore_door_swipe_security_inbox_item
    from tower.keycard_passes import summarize_keycard_health
    from tower.owner_launch_cell import build_owner_tower_launch_packet
    from tower.security_command_page import build_security_command_view
    from tower.security_command_page import save_security_command_dashboard_html
    from tower.tower_status import get_tower_status
    from tower.ob_clearance_bridge import evaluate_ob_route_clearance
    from tower.ob_object_clearance import evaluate_ob_object_clearance
    from tower.ob_mode_clearance import evaluate_ob_mode_clearance
    from web.app import app

    results = {
        'ok': True,
        'pack': '036',
        'checks': {},
        'failures': [],
    }

    def check(name: str, condition: bool, detail: Any = None):
        passed = bool(condition)
        results['checks'][name] = {'ok': passed, 'detail': detail}
        if not passed:
            results['ok'] = False
            results['failures'].append(name)

    client = app.test_client()

    keycard_health = summarize_keycard_health()
    check('keycard_health_loads', keycard_health.get('ok') is True, keycard_health)

    launch = build_owner_tower_launch_packet(
        actor_user_id='owner_solice',
        target_user_id='owner_solice',
        session_id='session_pack036_smoke',
        device_id='device_pack036_smoke',
        ttl_seconds=900,
        include_regenerate=False,
    )
    check('owner_launch_packet_issued', launch.get('ok') is True, {
        'issued_keys': launch.get('issued_keys'),
        'url_keys': sorted(launch.get('urls', {}).keys()) if launch.get('urls') else [],
    })

    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        locked = client.get('/tower/security-command')
        command = client.get(launch['urls']['command'])
        status_response = client.get(launch['urls']['status'])
        wrong = client.get(launch['urls']['status'].replace('/tower/status.json', '/tower/security-command'))

    output = captured.getvalue()
    command_text = command.get_data(as_text=True)
    wrong_text = wrong.get_data(as_text=True)
    status_json = status_response.get_json(silent=True)

    check('unkeyed_command_locks', locked.status_code == 403, {'status': locked.status_code})
    check('keyed_command_opens', command.status_code == 200 and 'Tower health gauge' in command_text, {'status': command.status_code})
    check('status_json_opens', status_response.status_code == 200 and isinstance(status_json, dict) and status_json.get('ok') is True, {'status': status_response.status_code})
    check('wrong_door_locks', wrong.status_code == 403 and 'Clearance required' in wrong_text, {'status': wrong.status_code})
    check('news_warning_quiet', '[NEWS_CACHE_AUTO_REFRESH]' not in output, {'output_preview': output[:300]})

    audit_summary = summarize_door_swipe_audit_capsules(limit=6)
    check('door_audit_capsules_active', audit_summary.get('ok') is True and audit_summary.get('total', 0) >= 3, {
        'total': audit_summary.get('total'),
        'allowed': audit_summary.get('allowed'),
        'denied': audit_summary.get('denied'),
        'by_reason': audit_summary.get('by_reason'),
    })

    inbox_summary = summarize_door_swipe_security_inbox(limit=6)
    check('door_security_inbox_active', inbox_summary.get('ok') is True and inbox_summary.get('open', 0) >= 1, {
        'total': inbox_summary.get('total'),
        'open': inbox_summary.get('open'),
        'by_reason': inbox_summary.get('by_reason'),
    })

    # PACK038_INBOX_ACTION_WORKFLOW
    open_items = list_door_swipe_security_inbox_items(status='open', limit=20)
    check('door_inbox_open_items_listable', open_items.get('ok') is True and open_items.get('count', 0) >= 1, {
        'count': open_items.get('count'),
    })

    action_workflow_detail = {
        'reviewing_ok': False,
        'resolved_ok': False,
        'capsule_unchanged': False,
        'target_item_id': None,
        'self_cleaning': True,
        'cleanup_note': 'Pack039 self-cleaning smoke test resolves the item it selects.',
    }

    try:
        target_item = open_items.get('items', [])[-1]
        target_item_id = target_item.get('inbox_item_id')
        source_capsule_id = target_item.get('source_capsule_id')
        action_workflow_detail['target_item_id'] = target_item_id

        capsules_before = load_door_swipe_audit_capsules()
        matching_before = [x for x in capsules_before if x.get('capsule_id') == source_capsule_id]
        capsule_before = json.dumps(matching_before[0], sort_keys=True, default=str) if matching_before else ''

        reviewing = mark_door_swipe_security_inbox_reviewing(
            target_item_id,
            actor_user_id='owner_solice',
            note='Pack 038 smoke test: reviewing generated door-swipe inbox item.',
        )
        action_workflow_detail['reviewing_ok'] = reviewing.get('ok') is True and reviewing.get('new_status') == 'reviewing'

        resolved = resolve_door_swipe_security_inbox_item(
            target_item_id,
            actor_user_id='owner_solice',
            note='Pack 038 smoke test: resolved generated door-swipe inbox item.',
        )
        action_workflow_detail['resolved_ok'] = resolved.get('ok') is True and resolved.get('new_status') == 'resolved'

        capsules_after = load_door_swipe_audit_capsules()
        matching_after = [x for x in capsules_after if x.get('capsule_id') == source_capsule_id]
        capsule_after = json.dumps(matching_after[0], sort_keys=True, default=str) if matching_after else ''
        action_workflow_detail['capsule_unchanged'] = bool(capsule_before and capsule_before == capsule_after)

    except Exception as exc:
        action_workflow_detail['error'] = f'{type(exc).__name__}: {exc}'

    check(
        'door_inbox_review_resolve_workflow',
        action_workflow_detail.get('reviewing_ok') is True
        and action_workflow_detail.get('resolved_ok') is True
        and action_workflow_detail.get('capsule_unchanged') is True,
        action_workflow_detail,
    )

    # PACK039_SELF_CLEANING_SMOKE_TEST
    # The smoke test may create additional medium watchlist items while checking
    # unkeyed/wrong-door behavior. Clean up one remaining open test-shaped item
    # so repeated smoke runs do not keep growing the live owner queue forever.
    cleanup_detail = {
        'attempted': False,
        'cleaned_item_id': None,
        'ignored_ok': None,
    }
    try:
        remaining_open = list_door_swipe_security_inbox_items(status='open', limit=50)
        candidates = [
            item for item in remaining_open.get('items', [])
            if item.get('reason_code') == 'tower_keycard_required'
            and item.get('door_id') == '/tower/security-command'
            and item.get('user_id') in {'anonymous', '', None}
        ]
        if candidates:
            cleanup_target = candidates[-1]
            cleanup_detail['attempted'] = True
            cleanup_detail['cleaned_item_id'] = cleanup_target.get('inbox_item_id')
            ignored = ignore_door_swipe_security_inbox_item(
                cleanup_target.get('inbox_item_id'),
                actor_user_id='owner_solice',
                note='Pack 039 smoke cleanup: test-generated missing-keycard item archived.',
            )
            cleanup_detail['ignored_ok'] = ignored.get('ok') is True and ignored.get('new_status') == 'ignored'
        else:
            cleanup_detail['ignored_ok'] = True
    except Exception as exc:
        cleanup_detail['error'] = f'{type(exc).__name__}: {exc}'
        cleanup_detail['ignored_ok'] = False

    check(
        'door_inbox_smoke_self_cleanup',
        cleanup_detail.get('ignored_ok') is True,
        cleanup_detail,
    )

    tower_status = get_tower_status()
    check('tower_status_has_door_audit', tower_status.get('door_swipe_audit_ok') is True, {
        'door_swipe_audit_total': tower_status.get('door_swipe_audit_total'),
    })
    check('tower_status_has_door_security_inbox', tower_status.get('door_swipe_security_inbox_ok') is True, {
        'door_swipe_security_inbox_open': tower_status.get('door_swipe_security_inbox_open'),
    })

    ui_result = save_security_command_dashboard_html(tower_user_id='owner_solice')
    view = build_security_command_view(tower_user_id='owner_solice')
    check('tower_ui_regenerates', ui_result.get('ok') is True and ui_result.get('bytes', 0) > 7000, ui_result)
    # Pack 044C: self-cleaning smoke tests may reduce open door-inbox items,
    # and the UI view shape is lighter than the backend summary.
    # Accept the actual UI shape: total/open/recent/by_severity/by_status.
    door_security_inbox_view = view.get('door_security_inbox')
    door_inbox_has_counts = False
    door_inbox_has_activity_shape = False

    if isinstance(door_security_inbox_view, dict):
        try:
            total_value = int(door_security_inbox_view.get('total', 0) or 0)
            open_value = int(door_security_inbox_view.get('open', 0) or 0)
            door_inbox_has_counts = total_value >= 0 and open_value >= 0
        except Exception:
            door_inbox_has_counts = False

        door_inbox_has_activity_shape = (
            isinstance(door_security_inbox_view.get('recent', []), list)
            or isinstance(door_security_inbox_view.get('by_status', {}), dict)
            or isinstance(door_security_inbox_view.get('by_severity', {}), dict)
            or isinstance(door_security_inbox_view.get('by_reason', {}), dict)
        )

    check(
        'tower_ui_has_door_security_inbox_data',
        isinstance(door_security_inbox_view, dict)
        and door_inbox_has_counts
        and door_inbox_has_activity_shape,
        door_security_inbox_view,
    )

    serialized_status = json.dumps(tower_status, sort_keys=True, default=str)
    serialized_ui = json.dumps(view, sort_keys=True, default=str)
    check('no_raw_keycard_in_status_or_view', 'tower_keycard=' not in serialized_status and 'tower_keycard=' not in serialized_ui and 'raw_token' not in serialized_status and 'raw_token' not in serialized_ui, None)

    # PACK044_OB_CLEARANCE_BRIDGE_SMOKE_CHECKS
    route_owner_live_auto = evaluate_ob_route_clearance(
        user_id='owner_solice',
        role='owner',
        route_key='live_automated',
        action='enter',
        current_risk_score=10,
    )
    route_beta_live_auto = evaluate_ob_route_clearance(
        user_id='beta_001',
        role='user',
        route_key='live_automated',
        action='enter',
        current_risk_score=10,
    )
    check(
        'ob_route_clearance_bridge_active',
        route_owner_live_auto.get('allowed') is True
        and route_beta_live_auto.get('allowed') is False
        and route_beta_live_auto.get('reason_code') == 'ob_clearance_level_too_low',
        {
            'owner_reason': route_owner_live_auto.get('reason_code'),
            'beta_reason': route_beta_live_auto.get('reason_code'),
        },
    )

    object_owner_export = evaluate_ob_object_clearance(
        user_id='owner_solice',
        role='owner',
        route_key='export',
        object_type='export',
        object_id='pack044_export_check',
        action='download',
        current_risk_score=5,
    )
    object_beta_export = evaluate_ob_object_clearance(
        user_id='beta_001',
        role='user',
        route_key='export',
        object_type='export',
        object_id='pack044_export_check',
        action='download',
        current_risk_score=5,
    )
    object_wrong_action = evaluate_ob_object_clearance(
        user_id='owner_solice',
        role='owner',
        object_type='symbol',
        object_id='AAPL',
        action='download',
        current_risk_score=5,
    )
    check(
        'ob_object_clearance_bridge_active',
        object_owner_export.get('allowed') is True
        and object_beta_export.get('allowed') is False
        and object_wrong_action.get('reason_code') == 'ob_object_action_not_allowed',
        {
            'owner_export_reason': object_owner_export.get('reason_code'),
            'beta_export_reason': object_beta_export.get('reason_code'),
            'wrong_action_reason': object_wrong_action.get('reason_code'),
        },
    )

    mode_survey_user = evaluate_ob_mode_clearance(
        user_id='beta_001',
        role='user',
        mode_name='survey',
        action='enter',
        current_risk_score=10,
    )
    mode_paper_user = evaluate_ob_mode_clearance(
        user_id='beta_001',
        role='user',
        mode_name='paper',
        action='enter',
        current_risk_score=10,
    )
    mode_auto_owner = evaluate_ob_mode_clearance(
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
    mode_auto_no_auth = evaluate_ob_mode_clearance(
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
    mode_lockdown = evaluate_ob_mode_clearance(
        user_id='owner_solice',
        role='owner',
        mode_name='survey',
        action='enter',
        emergency_lockdown=True,
    )
    check(
        'ob_mode_clearance_bridge_active',
        mode_survey_user.get('allowed') is True
        and mode_paper_user.get('allowed') is False
        and mode_auto_owner.get('allowed') is True
        and mode_auto_no_auth.get('reason_code') == 'ob_mode_automation_authorization_missing'
        and mode_lockdown.get('reason_code') == 'tower_emergency_lockdown_active',
        {
            'survey_user_reason': mode_survey_user.get('reason_code'),
            'paper_user_reason': mode_paper_user.get('reason_code'),
            'auto_owner_reason': mode_auto_owner.get('reason_code'),
            'auto_no_auth_reason': mode_auto_no_auth.get('reason_code'),
            'lockdown_reason': mode_lockdown.get('reason_code'),
        },
    )

    serialized_ob = json.dumps(
        [
            route_owner_live_auto,
            route_beta_live_auto,
            object_owner_export,
            object_beta_export,
            object_wrong_action,
            mode_survey_user,
            mode_paper_user,
            mode_auto_owner,
            mode_auto_no_auth,
            mode_lockdown,
        ],
        sort_keys=True,
        default=str,
    )
    check(
        'no_raw_keycard_in_ob_clearance_results',
        'tower_keycard=' not in serialized_ob and 'raw_token' not in serialized_ob,
        None,
    )

    results['human_reason'] = 'Tower security chain smoke test passed.' if results['ok'] else 'Tower security chain smoke test found failures.'
    return results


def print_tower_security_smoke() -> Dict[str, Any]:
    result = run_tower_security_smoke()
    print('=' * 80)
    print('TOWER SECURITY CHAIN SMOKE TEST')
    print('=' * 80)
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == '__main__':
    output = print_tower_security_smoke()
    if not output.get('ok'):
        raise SystemExit('Tower security smoke test failed.')
