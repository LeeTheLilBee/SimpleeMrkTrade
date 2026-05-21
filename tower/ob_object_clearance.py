from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from tower.ob_clearance_bridge import CLEARANCE_ORDER
from tower.ob_clearance_bridge import evaluate_ob_route_clearance


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


OB_OBJECT_CLEARANCE_POLICIES: Dict[str, Dict[str, Any]] = {
    'symbol': {
        'label': 'Symbol Intelligence Object',
        'required_clearance_level': 'confidential',
        'allowed_actions': ['view'],
        'plain': 'Specific symbol intelligence pages and signal history.',
    },
    'trade': {
        'label': 'Trade Object',
        'required_clearance_level': 'restricted',
        'allowed_actions': ['view', 'edit', 'close', 'annotate'],
        'plain': 'Specific trade, position, or trade lifecycle record.',
    },
    'account': {
        'label': 'Account Object',
        'required_clearance_level': 'restricted',
        'allowed_actions': ['view', 'edit'],
        'plain': 'Specific user, trust, business, or broker-linked account.',
    },
    'export': {
        'label': 'Export Object',
        'required_clearance_level': 'critical',
        'allowed_actions': ['create', 'download', 'share'],
        'plain': 'Specific file/export/download request leaving OB.',
    },
    'analysis_record': {
        'label': 'Analysis Record',
        'required_clearance_level': 'restricted',
        'allowed_actions': ['view', 'annotate'],
        'plain': 'Specific analysis vault record, evidence packet, or reasoning object.',
    },
    'mode': {
        'label': 'Mode Object',
        'required_clearance_level': 'confidential',
        'allowed_actions': ['enter', 'view'],
        'plain': 'Specific OB mode object, such as Survey, Paper, Live, Manual, or Live Automated.',
    },
    'admin_control': {
        'label': 'Admin Control Object',
        'required_clearance_level': 'critical',
        'allowed_actions': ['view', 'change', 'override'],
        'plain': 'Specific admin control, switch, override, or kill-switch object.',
    },
}


SENSITIVE_SYMBOLS = {'SPY', 'QQQ', 'IWM', 'VIX', 'UVXY', 'SQQQ', 'TQQQ'}
LIVE_MODE_NAMES = {'live', 'live_mode', 'live_automated', 'automated_live'}


def get_ob_object_clearance_policy_catalog() -> Dict[str, Any]:
    return {
        'ok': True,
        'tower_name': 'The Tower',
        'catalog': OB_OBJECT_CLEARANCE_POLICIES,
        'count': len(OB_OBJECT_CLEARANCE_POLICIES),
        'human_reason': 'OB object-level clearance policy catalog loaded.',
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


def _object_required_level(
    *,
    object_type: str,
    object_id: str,
    base_required_level: str,
    metadata: Dict[str, Any],
) -> str:
    object_type = _safe_str(object_type).lower()
    object_id = _safe_str(object_id).upper()

    # Live/Automated objects are always critical.
    mode_name = _safe_str(metadata.get('mode_name')).lower()
    if object_type == 'mode' and (mode_name in LIVE_MODE_NAMES or object_id.lower() in LIVE_MODE_NAMES):
        return 'critical'

    # Exports are always critical.
    if object_type == 'export':
        return 'critical'

    # Sensitive broad-market or volatility instruments require restricted clearance.
    if object_type == 'symbol' and object_id in SENSITIVE_SYMBOLS:
        if CLEARANCE_ORDER.get(base_required_level, 0) < CLEARANCE_ORDER['restricted']:
            return 'restricted'

    # User-owned financial/account objects stay restricted unless already higher.
    if object_type in {'trade', 'account', 'analysis_record'}:
        if CLEARANCE_ORDER.get(base_required_level, 0) < CLEARANCE_ORDER['restricted']:
            return 'restricted'

    return base_required_level


def evaluate_ob_object_clearance(
    *,
    user_id: str,
    object_type: str,
    object_id: str,
    action: str = 'view',
    role: str = '',
    user_clearance_level: str = '',
    route_key: str = '',
    owner_user_id: str = '',
    account_id: str = '',
    current_risk_score: int = 0,
    max_allowed_risk_score: int = 85,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    metadata = metadata if isinstance(metadata, dict) else {}
    user_id = _safe_str(user_id, 'anonymous')
    object_type = _safe_str(object_type).lower()
    object_id = _safe_str(object_id)
    action = _safe_str(action, 'view')
    role = _safe_str(role)
    owner_user_id = _safe_str(owner_user_id)
    account_id = _safe_str(account_id)
    route_key = _safe_str(route_key)
    user_clearance_level = _safe_str(user_clearance_level) or _default_user_clearance(user_id, role)
    current_risk_score = _safe_int(current_risk_score, 0)
    max_allowed_risk_score = _safe_int(max_allowed_risk_score, 85)

    policy = OB_OBJECT_CLEARANCE_POLICIES.get(object_type)
    if not policy:
        return {
            'ok': False,
            'allowed': False,
            'decision': 'deny',
            'reason_code': 'unknown_ob_object_type',
            'risk_state': 'restricted',
            'risk_score': max(current_risk_score, 65),
            'required_actions': ['define_object_clearance_policy'],
            'human_reason': 'The Tower does not have an object-level clearance policy for this OB object type yet.',
            'soulaana_translation': 'Soulaana: This object type is not in the Tower map. I will not reveal unmapped objects.',
            'metadata': {
                'user_id': user_id,
                'object_type': object_type,
                'object_id': object_id,
                'action': action,
            },
        }

    allowed_actions = policy.get('allowed_actions') if isinstance(policy.get('allowed_actions'), list) else []
    base_required_level = _safe_str(policy.get('required_clearance_level'), 'internal')
    required_level = _object_required_level(
        object_type=object_type,
        object_id=object_id,
        base_required_level=base_required_level,
        metadata=metadata,
    )

    if action not in allowed_actions:
        return {
            'ok': True,
            'allowed': False,
            'decision': 'deny',
            'reason_code': 'ob_object_action_not_allowed',
            'risk_state': 'watch',
            'risk_score': max(current_risk_score, 45),
            'required_actions': ['request_object_action_clearance'],
            'human_reason': 'This OB object does not allow that action.',
            'soulaana_translation': f'Soulaana: The object exists, but action {action} is not cleared for this object type.',
            'metadata': {
                'user_id': user_id,
                'object_type': object_type,
                'object_id': object_id,
                'action': action,
                'allowed_actions': allowed_actions,
            },
        }

    if route_key:
        route_decision = evaluate_ob_route_clearance(
            user_id=user_id,
            route_key=route_key,
            action='view' if action not in {'enter', 'export', 'download'} else action,
            role=role,
            user_clearance_level=user_clearance_level,
            current_risk_score=current_risk_score,
            max_allowed_risk_score=max_allowed_risk_score,
            object_id=object_id,
            metadata={'object_type': object_type, **metadata},
        )
        if not route_decision.get('allowed'):
            return {
                'ok': True,
                'allowed': False,
                'decision': route_decision.get('decision', 'deny'),
                'reason_code': 'parent_route_clearance_failed',
                'risk_state': route_decision.get('risk_state', 'restricted'),
                'risk_score': route_decision.get('risk_score', current_risk_score),
                'required_actions': route_decision.get('required_actions', []),
                'human_reason': 'The parent OB route was not cleared, so the object cannot be revealed.',
                'soulaana_translation': 'Soulaana: I cannot open the drawer if the hallway itself is not cleared first.',
                'metadata': {
                    'user_id': user_id,
                    'route_key': route_key,
                    'object_type': object_type,
                    'object_id': object_id,
                    'parent_route_decision': route_decision,
                },
            }

    # Owner binding: if a record belongs to another user, require owner/admin-level control.
    if owner_user_id and owner_user_id != user_id and role not in {'owner', 'admin', 'master'}:
        return {
            'ok': True,
            'allowed': False,
            'decision': 'deny',
            'reason_code': 'ob_object_owner_mismatch',
            'risk_state': 'restricted',
            'risk_score': max(current_risk_score, 80),
            'required_actions': ['owner_review', 'object_owner_verification'],
            'human_reason': 'This object belongs to another user or account.',
            'soulaana_translation': 'Soulaana: This is not their drawer. Object ownership does not match the requesting user.',
            'metadata': {
                'user_id': user_id,
                'owner_user_id': owner_user_id,
                'account_id': account_id,
                'object_type': object_type,
                'object_id': object_id,
            },
        }

    if current_risk_score > max_allowed_risk_score:
        return {
            'ok': True,
            'allowed': False,
            'decision': 'step_up',
            'reason_code': 'ob_object_risk_too_high',
            'risk_state': 'step_up_required',
            'risk_score': current_risk_score,
            'required_actions': ['step_up_authentication', 'security_review'],
            'human_reason': 'Risk is too high for this OB object right now.',
            'soulaana_translation': 'Soulaana: The object may normally be allowed, but the risk score is too high. Step up first.',
            'metadata': {
                'user_id': user_id,
                'object_type': object_type,
                'object_id': object_id,
                'current_risk_score': current_risk_score,
                'max_allowed_risk_score': max_allowed_risk_score,
            },
        }

    if not _clearance_allows(user_clearance_level, required_level):
        return {
            'ok': True,
            'allowed': False,
            'decision': 'deny',
            'reason_code': 'ob_object_clearance_level_too_low',
            'risk_state': 'restricted',
            'risk_score': max(current_risk_score, 70),
            'required_actions': ['upgrade_clearance', 'owner_review'],
            'human_reason': 'User clearance is not high enough for this OB object.',
            'soulaana_translation': f'Soulaana: {policy.get('label')} needs {required_level} clearance. This user only has {user_clearance_level}.',
            'metadata': {
                'user_id': user_id,
                'object_type': object_type,
                'object_id': object_id,
                'action': action,
                'user_clearance_level': user_clearance_level,
                'required_clearance_level': required_level,
            },
        }

    return {
        'ok': True,
        'allowed': True,
        'decision': 'allow',
        'reason_code': 'ob_object_clearance_allowed',
        'risk_state': 'clear' if current_risk_score < 40 else 'watch',
        'risk_score': current_risk_score,
        'required_actions': [],
        'human_reason': 'The Tower allowed this OB object action.',
        'soulaana_translation': f'Soulaana: {policy.get('label')} {object_id} is cleared for {action}. This opens only this object, not the whole room.',
        'metadata': {
            'user_id': user_id,
            'role': role,
            'route_key': route_key,
            'object_type': object_type,
            'object_id': object_id,
            'action': action,
            'owner_user_id': owner_user_id,
            'account_id': account_id,
            'user_clearance_level': user_clearance_level,
            'required_clearance_level': required_level,
            'evaluated_at': _utc_now(),
            'metadata': metadata,
        },
    }


def require_ob_object_clearance(**kwargs) -> Dict[str, Any]:
    return evaluate_ob_object_clearance(**kwargs)
