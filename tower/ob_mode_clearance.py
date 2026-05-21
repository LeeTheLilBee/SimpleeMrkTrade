from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from tower.ob_clearance_bridge import CLEARANCE_ORDER
from tower.ob_clearance_bridge import evaluate_ob_route_clearance
from tower.ob_object_clearance import evaluate_ob_object_clearance


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _safe_str(value: Any, default: str = '') -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {'1', 'true', 'yes', 'y', 'on'}:
        return True
    if text in {'0', 'false', 'no', 'n', 'off'}:
        return False
    return default


MODE_CLEARANCE_POLICIES: Dict[str, Dict[str, Any]] = {
    'survey': {
        'label': 'Survey Mode',
        'mode_key': 'survey',
        'route_key': 'dashboard',
        'required_clearance_level': 'internal',
        'allowed_actions': ['enter', 'view'],
        'automation_allowed': False,
        'broker_required': False,
        'live_money_allowed': False,
        'max_default_risk_score': 90,
        'plain': 'Research/watch mode. No live money and no automation.',
    },
    'paper': {
        'label': 'Paper Mode',
        'mode_key': 'paper',
        'route_key': 'paper_mode',
        'required_clearance_level': 'confidential',
        'allowed_actions': ['enter', 'view'],
        'automation_allowed': False,
        'broker_required': False,
        'live_money_allowed': False,
        'max_default_risk_score': 85,
        'plain': 'Simulation mode. Can test logic, but should not touch live money.',
    },
    'manual': {
        'label': 'Manual Mode',
        'mode_key': 'manual',
        'route_key': 'live_mode',
        'required_clearance_level': 'restricted',
        'allowed_actions': ['enter', 'view'],
        'automation_allowed': False,
        'broker_required': True,
        'live_money_allowed': True,
        'max_default_risk_score': 75,
        'plain': 'Manual live-control environment. Serious, dark-screen, owner-approved behavior.',
    },
    'live': {
        'label': 'Live Mode',
        'mode_key': 'live',
        'route_key': 'live_mode',
        'required_clearance_level': 'critical',
        'allowed_actions': ['enter', 'view'],
        'automation_allowed': False,
        'broker_required': True,
        'live_money_allowed': True,
        'max_default_risk_score': 65,
        'plain': 'Live trading mode. Live money requires critical clearance and broker readiness.',
    },
    'live_automated': {
        'label': 'Live Automated Mode',
        'mode_key': 'live_automated',
        'route_key': 'live_automated',
        'required_clearance_level': 'critical',
        'allowed_actions': ['enter', 'execute', 'view'],
        'automation_allowed': True,
        'broker_required': True,
        'live_money_allowed': True,
        'max_default_risk_score': 45,
        'plain': 'Automated live trading. This is the most restricted OB mode.',
    },
}

MODE_ALIASES = {
    'survey_mode': 'survey',
    'research': 'survey',
    'watch': 'survey',
    'paper_mode': 'paper',
    'simulation': 'paper',
    'sim': 'paper',
    'manual_mode': 'manual',
    'live_manual': 'manual',
    'live_mode': 'live',
    'automated_live': 'live_automated',
    'auto_live': 'live_automated',
    'live_auto': 'live_automated',
}


def normalize_ob_mode(mode_name: str) -> str:
    raw = _safe_str(mode_name).lower().replace(' ', '_').replace('-', '_')
    return MODE_ALIASES.get(raw, raw)


def get_ob_mode_clearance_catalog() -> Dict[str, Any]:
    return {
        'ok': True,
        'tower_name': 'The Tower',
        'catalog': MODE_CLEARANCE_POLICIES,
        'aliases': MODE_ALIASES,
        'count': len(MODE_CLEARANCE_POLICIES),
        'human_reason': 'OB mode clearance catalog loaded.',
    }


def _default_user_clearance(user_id: str, role: str = '') -> str:
    user_id = _safe_str(user_id)
    role = _safe_str(role).lower()
    if user_id == 'owner_solice' or role == 'owner':
        return 'critical'
    if role in {'admin', 'master'}:
        return 'restricted'
    if role in {'elite', 'pro'}:
        return 'confidential'
    return 'internal'


def _clearance_allows(user_level: str, required_level: str) -> bool:
    return CLEARANCE_ORDER.get(user_level, 0) >= CLEARANCE_ORDER.get(required_level, 0)


def evaluate_ob_mode_clearance(
    *,
    user_id: str,
    mode_name: str,
    action: str = 'enter',
    role: str = '',
    user_clearance_level: str = '',
    current_risk_score: int = 0,
    broker_connected: bool = False,
    broker_healthy: bool = False,
    live_authorized: bool = False,
    automation_authorized: bool = False,
    emergency_lockdown: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    metadata = metadata if isinstance(metadata, dict) else {}
    user_id = _safe_str(user_id, 'anonymous')
    mode_key = normalize_ob_mode(mode_name)
    action = _safe_str(action, 'enter')
    role = _safe_str(role)
    user_clearance_level = _safe_str(user_clearance_level) or _default_user_clearance(user_id, role)
    current_risk_score = _safe_int(current_risk_score, 0)
    broker_connected = _safe_bool(broker_connected)
    broker_healthy = _safe_bool(broker_healthy)
    live_authorized = _safe_bool(live_authorized)
    automation_authorized = _safe_bool(automation_authorized)
    emergency_lockdown = _safe_bool(emergency_lockdown)

    policy = MODE_CLEARANCE_POLICIES.get(mode_key)
    if not policy:
        return {
            'ok': False,
            'allowed': False,
            'decision': 'deny',
            'reason_code': 'unknown_ob_mode',
            'risk_state': 'restricted',
            'risk_score': max(current_risk_score, 70),
            'required_actions': ['define_mode_clearance_policy'],
            'human_reason': 'The Tower does not have a policy for this OB mode yet.',
            'soulaana_translation': 'Soulaana: I do not open unknown modes. Name the mode and map the clearance first.',
            'metadata': {'user_id': user_id, 'mode_name': mode_name, 'mode_key': mode_key, 'action': action},
        }

    if emergency_lockdown:
        return {
            'ok': True,
            'allowed': False,
            'decision': 'deny',
            'reason_code': 'tower_emergency_lockdown_active',
            'risk_state': 'locked',
            'risk_score': 100,
            'required_actions': ['owner_unlock_required', 'incident_review_required'],
            'human_reason': 'The Tower is in emergency lockdown. OB mode access is blocked.',
            'soulaana_translation': 'Soulaana: Lockdown is active. The doors are not debating today.',
            'metadata': {'user_id': user_id, 'mode_key': mode_key, 'action': action},
        }

    allowed_actions = policy.get('allowed_actions') if isinstance(policy.get('allowed_actions'), list) else []
    if action not in allowed_actions:
        return {
            'ok': True,
            'allowed': False,
            'decision': 'deny',
            'reason_code': 'ob_mode_action_not_allowed',
            'risk_state': 'watch',
            'risk_score': max(current_risk_score, 45),
            'required_actions': ['request_mode_action_clearance'],
            'human_reason': 'This OB mode does not allow that action.',
            'soulaana_translation': f'Soulaana: {policy.get('label')} exists, but action {action} is not allowed in this mode.',
            'metadata': {'user_id': user_id, 'mode_key': mode_key, 'action': action, 'allowed_actions': allowed_actions},
        }

    required_level = _safe_str(policy.get('required_clearance_level'), 'internal')
    if not _clearance_allows(user_clearance_level, required_level):
        return {
            'ok': True,
            'allowed': False,
            'decision': 'deny',
            'reason_code': 'ob_mode_clearance_level_too_low',
            'risk_state': 'restricted',
            'risk_score': max(current_risk_score, 70),
            'required_actions': ['upgrade_clearance', 'owner_review'],
            'human_reason': 'User clearance is not high enough for this OB mode.',
            'soulaana_translation': f'Soulaana: {policy.get('label')} needs {required_level} clearance. This user only has {user_clearance_level}.',
            'metadata': {'user_id': user_id, 'mode_key': mode_key, 'required_clearance_level': required_level, 'user_clearance_level': user_clearance_level},
        }

    max_allowed_risk_score = _safe_int(policy.get('max_default_risk_score'), 85)
    if current_risk_score > max_allowed_risk_score:
        return {
            'ok': True,
            'allowed': False,
            'decision': 'step_up',
            'reason_code': 'ob_mode_risk_too_high',
            'risk_state': 'step_up_required',
            'risk_score': current_risk_score,
            'required_actions': ['step_up_authentication', 'security_review'],
            'human_reason': 'Risk is too high for this OB mode right now.',
            'soulaana_translation': 'Soulaana: This mode might be allowed normally, but the risk weather is too loud. Step up first.',
            'metadata': {'user_id': user_id, 'mode_key': mode_key, 'current_risk_score': current_risk_score, 'max_allowed_risk_score': max_allowed_risk_score},
        }

    if policy.get('broker_required') and (not broker_connected or not broker_healthy):
        return {
            'ok': True,
            'allowed': False,
            'decision': 'deny',
            'reason_code': 'ob_mode_broker_not_ready',
            'risk_state': 'restricted',
            'risk_score': max(current_risk_score, 75),
            'required_actions': ['connect_broker', 'verify_broker_health'],
            'human_reason': 'This OB mode requires a connected and healthy broker boundary.',
            'soulaana_translation': 'Soulaana: No clean broker bridge, no live corridor. The Tower is not guessing with money.',
            'metadata': {'user_id': user_id, 'mode_key': mode_key, 'broker_connected': broker_connected, 'broker_healthy': broker_healthy},
        }

    if policy.get('live_money_allowed') and not live_authorized:
        return {
            'ok': True,
            'allowed': False,
            'decision': 'deny',
            'reason_code': 'ob_mode_live_authorization_missing',
            'risk_state': 'restricted',
            'risk_score': max(current_risk_score, 80),
            'required_actions': ['owner_live_authorization', 'risk_disclosure_confirmation'],
            'human_reason': 'Live-money OB mode needs explicit live authorization.',
            'soulaana_translation': 'Soulaana: Live money needs a signed yes. A vibe is not authorization.',
            'metadata': {'user_id': user_id, 'mode_key': mode_key, 'live_authorized': live_authorized},
        }

    if policy.get('automation_allowed') and not automation_authorized:
        return {
            'ok': True,
            'allowed': False,
            'decision': 'deny',
            'reason_code': 'ob_mode_automation_authorization_missing',
            'risk_state': 'restricted',
            'risk_score': max(current_risk_score, 90),
            'required_actions': ['owner_automation_authorization', 'kill_switch_check', 'broker_plugin_check'],
            'human_reason': 'Automated live mode needs explicit automation authorization.',
            'soulaana_translation': 'Soulaana: Automated live trading is the locked vault, not the lobby. Bring the right authorization.',
            'metadata': {'user_id': user_id, 'mode_key': mode_key, 'automation_authorized': automation_authorized},
        }

    # Parent route clearance checks whether the user can load the mode corridor.
    # Most mode pages use "view"; Live Automated's route is stricter and only allows
    # enter/execute, so it must ask for "enter" when entering that corridor.
    parent_route_action = 'view'
    if mode_key == 'live_automated' and action in {'enter', 'execute'}:
        parent_route_action = 'enter'

    route_decision = evaluate_ob_route_clearance(
        user_id=user_id,
        route_key=policy.get('route_key'),
        action=parent_route_action,
        role=role,
        user_clearance_level=user_clearance_level,
        current_risk_score=current_risk_score,
        max_allowed_risk_score=max_allowed_risk_score,
        mode_name=mode_key,
        metadata={'mode_policy': policy, **metadata},
    )
    if not route_decision.get('allowed'):
        return {
            'ok': True,
            'allowed': False,
            'decision': route_decision.get('decision', 'deny'),
            'reason_code': 'ob_mode_parent_route_failed',
            'risk_state': route_decision.get('risk_state', 'restricted'),
            'risk_score': route_decision.get('risk_score', current_risk_score),
            'required_actions': route_decision.get('required_actions', []),
            'human_reason': 'The parent mode route clearance failed.',
            'soulaana_translation': 'Soulaana: The mode key fits, but the hallway to that mode is still blocked.',
            'metadata': {'user_id': user_id, 'mode_key': mode_key, 'parent_route_decision': route_decision},
        }

    object_decision = evaluate_ob_object_clearance(
        user_id=user_id,
        object_type='mode',
        object_id=mode_key,
        action='enter' if action == 'enter' else 'view',
        role=role,
        user_clearance_level=user_clearance_level,
        current_risk_score=current_risk_score,
        max_allowed_risk_score=max_allowed_risk_score,
        metadata={'mode_name': mode_key, 'mode_required_clearance_level': required_level, **metadata},
    )
    if not object_decision.get('allowed'):
        return {
            'ok': True,
            'allowed': False,
            'decision': object_decision.get('decision', 'deny'),
            'reason_code': 'ob_mode_object_clearance_failed',
            'risk_state': object_decision.get('risk_state', 'restricted'),
            'risk_score': object_decision.get('risk_score', current_risk_score),
            'required_actions': object_decision.get('required_actions', []),
            'human_reason': 'The mode object clearance failed.',
            'soulaana_translation': 'Soulaana: The mode route may be clear, but this exact mode object is not cleared.',
            'metadata': {'user_id': user_id, 'mode_key': mode_key, 'object_decision': object_decision},
        }

    return {
        'ok': True,
        'allowed': True,
        'decision': 'allow',
        'reason_code': 'ob_mode_clearance_allowed',
        'risk_state': 'clear' if current_risk_score < 40 else 'watch',
        'risk_score': current_risk_score,
        'required_actions': [],
        'human_reason': 'The Tower allowed this OB mode.',
        'soulaana_translation': f'Soulaana: {policy.get('label')} is cleared. You are inside this mode only, not every neighboring room.',
        'metadata': {
            'user_id': user_id,
            'role': role,
            'mode_name': mode_name,
            'mode_key': mode_key,
            'action': action,
            'required_clearance_level': required_level,
            'user_clearance_level': user_clearance_level,
            'broker_connected': broker_connected,
            'broker_healthy': broker_healthy,
            'live_authorized': live_authorized,
            'automation_authorized': automation_authorized,
            'evaluated_at': _utc_now(),
            'mode_policy': policy,
            'metadata': metadata,
        },
    }


def require_ob_mode_clearance(**kwargs) -> Dict[str, Any]:
    return evaluate_ob_mode_clearance(**kwargs)
