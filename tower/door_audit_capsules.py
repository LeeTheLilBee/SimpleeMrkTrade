from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

TOWER_ROOT = Path(__file__).resolve().parent
DATA_DIR = TOWER_ROOT / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

DOOR_AUDIT_PATH = DATA_DIR / 'door_swipe_audit_capsules.json'


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


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        with path.open('r', encoding='utf-8') as handle:
            return json.load(handle)
    except Exception:
        return default


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    with temp.open('w', encoding='utf-8') as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
    temp.replace(path)


def _new_capsule_id() -> str:
    return 'doorcap_' + secrets.token_urlsafe(18).replace('-', '_')


def _fingerprint(payload: Dict[str, Any]) -> str:
    safe = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(safe.encode('utf-8')).hexdigest()[:24]


def _soulaana_translation(decision: Dict[str, Any], door_id: str, action: str) -> str:
    allowed = bool(decision.get('allowed'))
    reason = _safe_str(decision.get('reason_code'), 'unknown')
    if allowed:
        return f'Soulaana: This door swipe was allowed for {door_id}. The pass matched the door and action {action}.'
    if reason == 'tower_keycard_required':
        return f'Soulaana: Someone reached {door_id} without a keycard. The Tower stayed quiet and showed only the locked wall.'
    if reason == 'wrong_door':
        return f'Soulaana: A keycard was presented, but it did not belong to {door_id}. Neighboring doors stayed sealed.'
    if reason == 'action_not_allowed':
        return f'Soulaana: The keycard may belong somewhere nearby, but it does not allow the requested action: {action}.'
    if reason in {'wrong_user', 'wrong_device', 'wrong_session'}:
        return f'Soulaana: The pass failed identity binding. User, device, or session did not match what The Tower expected.'
    if reason in {'pass_expired', 'pass_not_active'}:
        return f'Soulaana: The pass was stale or revoked. The Tower refused it instead of trusting old access.'
    return f'Soulaana: The Tower denied this door swipe for reason {reason}. Review only if the pattern repeats or risk rises.'


def _should_surface_in_inbox(decision: Dict[str, Any]) -> bool:
    allowed = bool(decision.get('allowed'))
    reason = _safe_str(decision.get('reason_code'))
    risk_score = _safe_int(decision.get('risk_score'), 0)
    risk_state = _safe_str(decision.get('risk_state'))
    if allowed:
        return False
    if reason in {'wrong_user', 'wrong_device', 'wrong_session', 'tower_keycard_validation_failed'}:
        return True
    if risk_state in {'restricted', 'locked', 'critical'}:
        return True
    if risk_score >= 70:
        return True
    return False


def _extract_request_context(request_obj: Any) -> Dict[str, Any]:
    context = {
        'method': None,
        'path': None,
        'remote_addr_present': False,
        'has_query_keycard': False,
        'has_header_keycard': False,
        'has_cookie_keycard': False,
        'user_agent_preview': None,
    }
    try:
        context['method'] = request_obj.method
    except Exception:
        pass
    try:
        context['path'] = request_obj.path
    except Exception:
        pass
    try:
        context['remote_addr_present'] = bool(request_obj.remote_addr)
    except Exception:
        pass
    try:
        context['has_query_keycard'] = bool(request_obj.args.get('tower_keycard'))
    except Exception:
        pass
    try:
        context['has_header_keycard'] = bool(request_obj.headers.get('X-Tower-Keycard'))
    except Exception:
        pass
    try:
        context['has_cookie_keycard'] = bool(request_obj.cookies.get('tower_keycard_pass'))
    except Exception:
        pass
    try:
        ua = _safe_str(request_obj.headers.get('User-Agent'))
        context['user_agent_preview'] = ua[:90] if ua else None
    except Exception:
        pass
    return context


def load_door_swipe_audit_capsules() -> List[Dict[str, Any]]:
    payload = _read_json(DOOR_AUDIT_PATH, [])
    return payload if isinstance(payload, list) else []


def save_door_swipe_audit_capsules(items: List[Dict[str, Any]]) -> None:
    _write_json(DOOR_AUDIT_PATH, items)


def record_tower_door_swipe(
    *,
    decision: Dict[str, Any],
    door_id: str,
    action: str,
    request_obj: Any = None,
    source: str = 'tower_web_bridge',
) -> Dict[str, Any]:
    decision = decision if isinstance(decision, dict) else {}
    metadata = decision.get('metadata') if isinstance(decision.get('metadata'), dict) else {}
    requested = metadata.get('requested') if isinstance(metadata.get('requested'), dict) else {}

    user_id = _safe_str(requested.get('user_id') or metadata.get('user_id'), 'unknown')
    session_id = _safe_str(requested.get('session_id') or metadata.get('session_id'), '')
    device_id = _safe_str(requested.get('device_id') or metadata.get('device_id'), '')

    capsule = {
        'ok': True,
        'capsule_id': _new_capsule_id(),
        'event_type': 'tower_door_swipe',
        'timestamp': _utc_now(),
        'source': source,
        'app_name': 'tower',
        'door_type': 'route',
        'door_id': door_id,
        'action': action,
        'allowed': bool(decision.get('allowed')),
        'decision': _safe_str(decision.get('decision'), 'unknown'),
        'reason_code': _safe_str(decision.get('reason_code'), 'unknown'),
        'human_reason': _safe_str(decision.get('human_reason'), 'No reason provided.'),
        'risk_state': _safe_str(decision.get('risk_state'), 'unknown'),
        'risk_score': _safe_int(decision.get('risk_score'), 0),
        'required_actions': decision.get('required_actions') if isinstance(decision.get('required_actions'), list) else [],
        'user_id': user_id,
        'session_id': session_id,
        'device_id': device_id,
        'should_surface_in_inbox': _should_surface_in_inbox(decision),
        'soulaana_translation': _soulaana_translation(decision, door_id, action),
        'request_context': _extract_request_context(request_obj) if request_obj is not None else {},
    }

    capsule['fingerprint'] = _fingerprint({
        'door_id': capsule['door_id'],
        'action': capsule['action'],
        'allowed': capsule['allowed'],
        'reason_code': capsule['reason_code'],
        'user_id': capsule['user_id'],
        'session_id': capsule['session_id'],
        'device_id': capsule['device_id'],
    })

    # Never store raw tokens.
    serialized = json.dumps(capsule, sort_keys=True)
    if 'tower_keycard=' in serialized:
        capsule['token_leak_guard'] = 'redacted_before_write'

    items = load_door_swipe_audit_capsules()
    items.append(capsule)
    if len(items) > 1000:
        items = items[-1000:]
    save_door_swipe_audit_capsules(items)

    return {
        'ok': True,
        'status': 'recorded',
        'capsule_id': capsule['capsule_id'],
        'allowed': capsule['allowed'],
        'reason_code': capsule['reason_code'],
        'should_surface_in_inbox': capsule['should_surface_in_inbox'],
    }


def summarize_door_swipe_audit_capsules(limit: int = 10) -> Dict[str, Any]:
    items = load_door_swipe_audit_capsules()
    allowed = sum(1 for item in items if item.get('allowed') is True)
    denied = sum(1 for item in items if item.get('allowed') is False)
    surfaced = sum(1 for item in items if item.get('should_surface_in_inbox') is True)
    by_reason: Dict[str, int] = {}
    by_door: Dict[str, int] = {}
    for item in items:
        reason = _safe_str(item.get('reason_code'), 'unknown')
        door = _safe_str(item.get('door_id'), 'unknown')
        by_reason[reason] = by_reason.get(reason, 0) + 1
        by_door[door] = by_door.get(door, 0) + 1
    return {
        'ok': True,
        'total': len(items),
        'allowed': allowed,
        'denied': denied,
        'surfaced': surfaced,
        'by_reason': by_reason,
        'by_door': by_door,
        'last': items[-int(limit or 10):],
        'path': str(DOOR_AUDIT_PATH),
    }
