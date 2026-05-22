from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path('/content/SimpleeMrkTrade_REAL_CLONE')
if PROJECT_ROOT.exists():
    os.chdir(PROJECT_ROOT)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def build_tower_readiness_checkpoint() -> Dict[str, Any]:
    from tower.door_audit_capsules import summarize_door_swipe_audit_capsules
    from tower.door_audit_capsules import summarize_door_swipe_security_inbox
    from tower.keycard_passes import summarize_keycard_health
    from tower.tower_security_smoke import run_tower_security_smoke
    from tower.tower_status import get_tower_status
    from tower.ob_clearance_bridge import evaluate_ob_route_clearance
    from tower.ob_object_clearance import evaluate_ob_object_clearance
    from tower.ob_mode_clearance import evaluate_ob_mode_clearance

    smoke = run_tower_security_smoke()
    status = get_tower_status()
    keycards = summarize_keycard_health()
    door_audit = summarize_door_swipe_audit_capsules(limit=6)
    door_inbox = summarize_door_swipe_security_inbox(limit=6)

    # PACK044_OB_CLEARANCE_READINESS_SUMMARY
    route_owner = evaluate_ob_route_clearance(
        user_id='owner_solice',
        role='owner',
        route_key='live_automated',
        action='enter',
        current_risk_score=10,
    )
    object_owner = evaluate_ob_object_clearance(
        user_id='owner_solice',
        role='owner',
        route_key='export',
        object_type='export',
        object_id='readiness_export_check',
        action='download',
        current_risk_score=5,
    )
    mode_owner = evaluate_ob_mode_clearance(
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
    mode_beta_paper = evaluate_ob_mode_clearance(
        user_id='beta_001',
        role='user',
        mode_name='paper',
        action='enter',
        current_risk_score=10,
    )

    ob_clearance_summary = {
        'route_bridge_ok': route_owner.get('allowed') is True,
        'object_bridge_ok': object_owner.get('allowed') is True,
        'mode_bridge_ok': mode_owner.get('allowed') is True and mode_beta_paper.get('allowed') is False,
        'route_reason': route_owner.get('reason_code'),
        'object_reason': object_owner.get('reason_code'),
        'mode_reason': mode_owner.get('reason_code'),
        'paper_user_denial_reason': mode_beta_paper.get('reason_code'),
    }

    built_packs = [
        {'pack': '025', 'name': 'Scoped keycard passes', 'plain': 'Every protected door can require a scoped pass.'},
        {'pack': '026', 'name': 'Private front door gate', 'plain': 'Unkeyed Tower routes lock instead of showing protected data.'},
        {'pack': '027', 'name': 'Owner keycard issuer', 'plain': 'Owner can issue short-lived scoped passes.'},
        {'pack': '028', 'name': 'Protected Tower UI', 'plain': 'The Tower Security Command page renders behind the gate.'},
        {'pack': '029', 'name': 'Owner access launcher', 'plain': 'Owner can generate temporary Tower access URLs.'},
        {'pack': '030', 'name': 'Owner launch cell helper', 'plain': 'Notebook helper prints fresh scoped links.'},
        {'pack': '031', 'name': 'Door-swipe audit capsules', 'plain': 'Every allow/deny gets a receipt.'},
        {'pack': '032', 'name': 'Door-swipe audit surfaced', 'plain': 'Door receipts appear in status and UI.'},
        {'pack': '033', 'name': 'Door-swipe security inbox bridge', 'plain': 'Review-worthy swipes become actionable inbox items.'},
        {'pack': '034', 'name': 'Door-swipe inbox surfaced', 'plain': 'Door inbox appears in status and UI.'},
        {'pack': '035', 'name': 'Quiet news refresh warning', 'plain': 'Tower tests are no longer cluttered by unrelated OB news noise.'},
        {'pack': '036', 'name': 'Tower security smoke runner', 'plain': 'One command checks the Tower chain.'},
        {'pack': '037', 'name': 'Door inbox actions', 'plain': 'Door inbox items can be reviewed, resolved, ignored, and annotated.'},
        {'pack': '038', 'name': 'Smoke test validates inbox actions', 'plain': 'The smoke test checks review/resolve safety.'},
        {'pack': '039', 'name': 'Self-cleaning smoke test', 'plain': 'Smoke tests clean up test-generated inbox noise.'},
        {'pack': '041', 'name': 'OB route/action clearance bridge', 'plain': 'OB can ask The Tower before opening a protected route or action.'},
        {'pack': '042', 'name': 'OB object-level clearance bridge', 'plain': 'OB can ask The Tower before revealing a specific symbol, trade, account, export, mode, or record.'},
        {'pack': '043', 'name': 'OB mode clearance bridge', 'plain': 'Survey, Paper, Manual, Live, and Live Automated modes have explicit Tower clearance.'},
    ]

    protected_surfaces = [
        {'surface': '/tower', 'status': 'protected', 'plain': 'Private Tower entry requires keycard.'},
        {'surface': '/tower/security-command', 'status': 'protected', 'plain': 'Security Command UI requires keycard.'},
        {'surface': '/tower/status.json', 'status': 'protected', 'plain': 'Tower status JSON requires keycard.'},
        {'surface': '/tower/security-command/regenerate', 'status': 'protected-critical', 'plain': 'Dashboard regeneration requires critical scoped pass.'},
        {'surface': 'Tower keycard registry', 'status': 'protected-data', 'plain': 'Raw tokens are not stored.'},
        {'surface': 'Door-swipe audit capsules', 'status': 'audit-ready', 'plain': 'Allow/deny receipts are preserved.'},
        {'surface': 'Door-swipe security inbox', 'status': 'actionable', 'plain': 'Review-worthy access attempts become owner tasks.'},
    ]

    next_before_deeper_ob = [
        {'priority': 1, 'item': 'Wire OB pages to call Tower route clearance', 'plain': 'The helpers exist; next OB routes need to actually ask The Tower before showing protected screens.'},
        {'priority': 2, 'item': 'Wire OB symbol/trade/account/export views to object clearance', 'plain': 'Specific objects should stay locked unless the exact object is cleared.'},
        {'priority': 3, 'item': 'Wire OB mode switcher to Tower mode clearance', 'plain': 'Survey, Paper, Manual, Live, and Live Automated should ask the mode bridge before entering.'},
        {'priority': 4, 'item': 'Add export/download lock UI and backend enforcement', 'plain': 'Anything leaving the app should ask The Tower first and leave an audit receipt.'},
        {'priority': 5, 'item': 'Add owner/admin UI actions for resolving Tower inbox items', 'plain': 'The backend can resolve items now; the UI needs buttons later.'},
        {'priority': 6, 'item': 'Add Archive Vault handoff', 'plain': 'Important security events should be able to become evidence bundles.'},
    ]

    readiness_score = 0
    if smoke.get('ok') is True:
        readiness_score += 35
    if status.get('audit_chain_ok') is True:
        readiness_score += 15
    if keycards.get('ok') is True:
        readiness_score += 15
    if door_audit.get('ok') is True and door_audit.get('total', 0) >= 1:
        readiness_score += 15
    if door_inbox.get('ok') is True:
        readiness_score += 10
    if status.get('door_swipe_security_inbox_ok') is True:
        readiness_score += 10
    if ob_clearance_summary.get('route_bridge_ok'):
        readiness_score += 5
    if ob_clearance_summary.get('object_bridge_ok'):
        readiness_score += 5
    if ob_clearance_summary.get('mode_bridge_ok'):
        readiness_score += 5
    readiness_score = min(100, readiness_score)

    if readiness_score >= 90 and smoke.get('ok') is True:
        readiness_label = 'Ready for next integration layer'
        soulaana = 'Soulaana: The Tower gate is holding. Next we connect OB carefully, one protected corridor at a time.'
    elif readiness_score >= 70:
        readiness_label = 'Mostly ready, review before wiring OB'
        soulaana = 'Soulaana: The Tower is awake, but check the failing or incomplete items before deeper integration.'
    else:
        readiness_label = 'Not ready for deeper OB integration'
        soulaana = 'Soulaana: Do not connect more OB surfaces until the smoke test and audit chain are clean.'

    return {
        'ok': bool(smoke.get('ok')) and readiness_score >= 90,
        'pack': '040',
        'generated_at': _utc_now(),
        'tower_name': 'The Tower',
        'readiness_score': readiness_score,
        'readiness_label': readiness_label,
        'soulaana_translation': soulaana,
        'smoke_ok': smoke.get('ok'),
        'smoke_failures': smoke.get('failures', []),
        'keycard_summary': {
            'ok': keycards.get('ok'),
            'total': keycards.get('keycard_total'),
            'active': keycards.get('keycard_active'),
            'expired': keycards.get('keycard_expired'),
            'revoked': keycards.get('keycard_revoked'),
            'allows_logged': keycards.get('door_allows_logged'),
            'denies_logged': keycards.get('door_denies_logged'),
        },
        'tower_status_summary': {
            'audit_chain_ok': status.get('audit_chain_ok'),
            'security_inbox_open': status.get('security_inbox_open'),
            'security_review_urgent_groups': status.get('security_review_urgent_groups'),
            'door_swipe_audit_total': status.get('door_swipe_audit_total'),
            'door_swipe_security_inbox_open': status.get('door_swipe_security_inbox_open'),
            'door_swipe_security_inbox_by_status': status.get('door_swipe_security_inbox_by_status'),
        },
        'door_audit_summary': {
            'total': door_audit.get('total'),
            'allowed': door_audit.get('allowed'),
            'denied': door_audit.get('denied'),
            'by_reason': door_audit.get('by_reason'),
        },
        'door_inbox_summary': {
            'total': door_inbox.get('total'),
            'open': door_inbox.get('open'),
            'by_status': door_inbox.get('by_status'),
            'by_severity': door_inbox.get('by_severity'),
            'by_reason': door_inbox.get('by_reason'),
        },
        'ob_clearance_summary': ob_clearance_summary,
        'built_packs': built_packs,
        'protected_surfaces': protected_surfaces,
        'next_before_deeper_ob': next_before_deeper_ob,
    }


def print_tower_readiness_checkpoint() -> Dict[str, Any]:
    checkpoint = build_tower_readiness_checkpoint()
    print('=' * 80)
    print('THE TOWER READINESS CHECKPOINT')
    print('=' * 80)
    print(json.dumps(checkpoint, indent=2, sort_keys=True))
    return checkpoint


if __name__ == '__main__':
    result = print_tower_readiness_checkpoint()
    if not result.get('ok'):
        raise SystemExit('Tower readiness checkpoint is not clean.')
