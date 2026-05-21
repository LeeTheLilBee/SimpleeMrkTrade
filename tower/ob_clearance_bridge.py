from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


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


OB_ROUTE_CLEARANCE_CATALOG: Dict[str, Dict[str, Any]] = {
    'dashboard': {
        'route_id': '/dashboard',
        'label': 'OB Dashboard',
        'required_clearance_level': 'internal',
        'allowed_actions': ['view'],
        'plain': 'Basic logged-in OB dashboard access.',
    },
    'signals_spotlight': {
        'route_id': '/signals-spotlight',
        'label': 'Signals Spotlight',
        'required_clearance_level': 'internal',
        'allowed_actions': ['view'],
        'plain': 'Public teaser or low-sensitivity signal overview surface.',
    },
    'signals': {
        'route_id': '/signals',
        'label': 'Signals',
        'required_clearance_level': 'confidential',
        'allowed_actions': ['view'],
        'plain': 'Protected signal intelligence surface.',
    },
    'symbol_detail': {
        'route_id': '/signals/<symbol>',
        'label': 'Symbol Intelligence',
        'required_clearance_level': 'confidential',
        'allowed_actions': ['view'],
        'plain': 'Protected per-symbol intelligence page.',
    },
    'analysis_vault': {
        'route_id': '/analysis-vault',
        'label': 'Analysis Vault',
        'required_clearance_level': 'restricted',
        'allowed_actions': ['view'],
        'plain': 'Higher-sensitivity analysis evidence and reasoning layer.',
    },
    'positions': {
        'route_id': '/my-positions',
        'label': 'Positions',
        'required_clearance_level': 'restricted',
        'allowed_actions': ['view', 'edit'],
        'plain': 'User-owned position information and position actions.',
    },
    'paper_mode': {
        'route_id': 'mode:paper',
        'label': 'Paper Mode',
        'required_clearance_level': 'confidential',
        'allowed_actions': ['enter', 'view'],
        'plain': 'Simulated trading mode access.',
    },
    'live_mode': {
        'route_id': 'mode:live',
        'label': 'Live Mode',
        'required_clearance_level': 'critical',
        'allowed_actions': ['enter', 'view'],
        'plain': 'Live trading mode access. This should stay heavily gated.',
    },
    'live_automated': {
        'route_id': 'mode:live_automated',
        'label': 'Live Automated Mode',
        'required_clearance_level': 'critical',
        'allowed_actions': ['enter', 'execute'],
        'plain': 'Automated live trading access. This must remain owner/approved only.',
    },
    'export': {
        'route_id': 'action:export',
        'label': 'Export / Download',
        'required_clearance_level': 'critical',
        'allowed_actions': ['export', 'download'],
        'plain': 'Anything leaving OB must ask The Tower first.',
    },
}


CLEARANCE_ORDER = {
    'public': 0,
    'internal': 1,
    'confidential': 2,
    'restricted': 3,
    'critical': 4,
}


def get_ob_route_clearance_catalog() -> Dict[str, Any]:
    return {
        'ok': True,
        'tower_name': 'The Tower',
        'catalog': OB_ROUTE_CLEARANCE_CATALOG,
        'count': len(OB_ROUTE_CLEARANCE_CATALOG),
        'human_reason': 'OB route/action clearance catalog loaded.',
    }


def _clearance_allows(user_level: str, required_level: str) -> bool:
    return CLEARANCE_ORDER.get(user_level, 0) >= CLEARANCE_ORDER.get(required_level, 0)


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


def evaluate_ob_route_clearance(
    *,
    user_id: str,
    route_key: str,
    action: str = 'view',
    role: str = '',
    user_clearance_level: str = '',
    current_risk_score: int = 0,
    max_allowed_risk_score: int = 85,
    mode_name: str = '',
    object_id: str = '',
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    metadata = metadata if isinstance(metadata, dict) else {}
    user_id = _safe_str(user_id, 'anonymous')
    route_key = _safe_str(route_key)
    action = _safe_str(action, 'view')
    role = _safe_str(role)
    user_clearance_level = _safe_str(user_clearance_level) or _default_user_clearance(user_id, role)
    current_risk_score = _safe_int(current_risk_score, 0)
    max_allowed_risk_score = _safe_int(max_allowed_risk_score, 85)

    route = OB_ROUTE_CLEARANCE_CATALOG.get(route_key)
    if not route:
        return {
            'ok': False,
            'allowed': False,
            'decision': 'deny',
            'reason_code': 'unknown_ob_route_or_action',
            'risk_state': 'restricted',
            'risk_score': max(current_risk_score, 65),
            'required_actions': ['define_route_clearance_policy'],
            'human_reason': 'The Tower does not have a clearance policy for this OB route/action yet.',
            'soulaana_translation': 'Soulaana: I do not open doors that are not in the map. Define the OB route policy first.',
            'metadata': {
                'user_id': user_id,
                'route_key': route_key,
                'action': action,
                'mode_name': mode_name,
                'object_id': object_id,
            },
        }

    allowed_actions = route.get('allowed_actions') if isinstance(route.get('allowed_actions'), list) else []
    required_level = _safe_str(route.get('required_clearance_level'), 'internal')

    if action not in allowed_actions:
        return {
            'ok': True,
            'allowed': False,
            'decision': 'deny',
            'reason_code': 'ob_action_not_allowed_for_route',
            'risk_state': 'watch',
            'risk_score': max(current_risk_score, 45),
            'required_actions': ['request_action_clearance'],
            'human_reason': 'This OB route does not allow that action.',
            'soulaana_translation': f'Soulaana: This door exists, but it does not allow {action}. Use the correct action clearance.',
            'metadata': {
                'user_id': user_id,
                'route_key': route_key,
                'route_id': route.get('route_id'),
                'action': action,
                'allowed_actions': allowed_actions,
            },
        }

    if current_risk_score > max_allowed_risk_score:
        return {
            'ok': True,
            'allowed': False,
            'decision': 'step_up',
            'reason_code': 'ob_route_risk_too_high',
            'risk_state': 'step_up_required',
            'risk_score': current_risk_score,
            'required_actions': ['step_up_authentication', 'security_review'],
            'human_reason': 'Risk is too high for this OB route/action right now.',
            'soulaana_translation': 'Soulaana: The route may be allowed normally, but today the risk weather is too loud. Step up first.',
            'metadata': {
                'user_id': user_id,
                'route_key': route_key,
                'route_id': route.get('route_id'),
                'action': action,
                'current_risk_score': current_risk_score,
                'max_allowed_risk_score': max_allowed_risk_score,
            },
        }

    if not _clearance_allows(user_clearance_level, required_level):
        return {
            'ok': True,
            'allowed': False,
            'decision': 'deny',
            'reason_code': 'ob_clearance_level_too_low',
            'risk_state': 'restricted',
            'risk_score': max(current_risk_score, 70),
            'required_actions': ['upgrade_clearance', 'owner_review'],
            'human_reason': 'User clearance is not high enough for this OB route/action.',
            'soulaana_translation': f'Soulaana: {route.get('label')} needs {required_level} clearance. This user only has {user_clearance_level}.',
            'metadata': {
                'user_id': user_id,
                'route_key': route_key,
                'route_id': route.get('route_id'),
                'action': action,
                'user_clearance_level': user_clearance_level,
                'required_clearance_level': required_level,
            },
        }

    return {
        'ok': True,
        'allowed': True,
        'decision': 'allow',
        'reason_code': 'ob_route_clearance_allowed',
        'risk_state': 'clear' if current_risk_score < 40 else 'watch',
        'risk_score': current_risk_score,
        'required_actions': [],
        'human_reason': 'The Tower allowed this OB route/action.',
        'soulaana_translation': f'Soulaana: {route.get('label')} is cleared for {action}. Keep moving, but stay inside the mapped corridor.',
        'metadata': {
            'user_id': user_id,
            'role': role,
            'route_key': route_key,
            'route_id': route.get('route_id'),
            'route_label': route.get('label'),
            'action': action,
            'mode_name': mode_name,
            'object_id': object_id,
            'user_clearance_level': user_clearance_level,
            'required_clearance_level': required_level,
            'evaluated_at': _utc_now(),
            'metadata': metadata,
        },
    }


def require_ob_route_clearance(**kwargs) -> Dict[str, Any]:
    return evaluate_ob_route_clearance(**kwargs)
