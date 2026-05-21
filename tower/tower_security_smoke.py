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
    from tower.keycard_passes import summarize_keycard_health
    from tower.owner_launch_cell import build_owner_tower_launch_packet
    from tower.security_command_page import build_security_command_view
    from tower.security_command_page import save_security_command_dashboard_html
    from tower.tower_status import get_tower_status
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
    check('tower_ui_has_door_security_inbox_data', isinstance(view.get('door_security_inbox'), dict) and view['door_security_inbox'].get('open', 0) >= 1, view.get('door_security_inbox'))

    serialized_status = json.dumps(tower_status, sort_keys=True, default=str)
    serialized_ui = json.dumps(view, sort_keys=True, default=str)
    check('no_raw_keycard_in_status_or_view', 'tower_keycard=' not in serialized_status and 'tower_keycard=' not in serialized_ui and 'raw_token' not in serialized_status and 'raw_token' not in serialized_ui, None)

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
