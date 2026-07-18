from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

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


# =============================================================================
# OB ROUTE GUARD MAP
# =============================================================================
# Baby version:
# This is the list of OB routes The Tower knows how to guard right now.
# Pack 046 will start connecting real Flask routes to this guard.

OB_ROUTE_GUARD_MAP: Dict[str, Dict[str, Any]] = {
    '/dashboard': {
        'route_key': 'dashboard',
        'action': 'view',
        'sensitivity': 'internal',
        'public_allowed': False,
        'plain': 'Main OB dashboard. Private app surface.',
    },
    # TOWER_OB_HOSTED_WALKTHROUGH_ROUTE_POLICY_REPAIR_V1
    '/market-map': {
        'route_key': 'market_map',
        'action': 'view',
        'sensitivity': 'confidential',
        'public_allowed': False,
        'plain': 'Protected Observatory Market Map room.',
    },
    '/ob/trade-center': {
        'route_key': 'trade_center',
        'action': 'view',
        'sensitivity': 'restricted',
        'public_allowed': False,
        'plain': 'Protected Observatory Trade Center room.',
    },
    '/ob/review-center': {
        'route_key': 'review_center',
        'action': 'view',
        'sensitivity': 'restricted',
        'public_allowed': False,
        'plain': 'Protected Observatory Review Center room.',
    },
    '/ob/owner-console': {
        'route_key': 'owner_console',
        'action': 'view',
        'sensitivity': 'critical',
        'public_allowed': False,
        'plain': 'Protected owner-only Observatory console.',
    },
    '/signals-spotlight': {
        'route_key': 'signals_spotlight',
        'action': 'view',
        'sensitivity': 'internal',
        'public_allowed': False,
        'plain': 'Signal teaser/spotlight. Private for now unless explicitly opened later.',
    },
    '/signals': {
        'route_key': 'signals',
        'action': 'view',
        'sensitivity': 'confidential',
        'public_allowed': False,
        'plain': 'Protected signal intelligence.',
    },
    '/my-positions': {
        'route_key': 'positions',
        'action': 'view',
        'sensitivity': 'restricted',
        'public_allowed': False,
        'plain': 'User position and trade data.',
    },
    '/my-portfolio': {
        'route_key': 'positions',
        'action': 'view',
        'sensitivity': 'restricted',
        'public_allowed': False,
        'plain': 'User portfolio data.',
    },
    '/analysis-vault': {
        'route_key': 'analysis_vault',
        'action': 'view',
        'sensitivity': 'restricted',
        'public_allowed': False,
        'plain': 'Analysis vault and evidence records.',
    },
    '/premium-analysis': {
        'route_key': 'analysis_vault',
        'action': 'view',
        'sensitivity': 'restricted',
        'public_allowed': False,
        'plain': 'Premium analysis surface.',
    },
    '/research': {
        'route_key': 'analysis_vault',
        'action': 'view',
        'sensitivity': 'restricted',
        'public_allowed': False,
        'plain': 'Research overview and deeper intelligence.',
    },
    '/analytics': {
        'route_key': 'analysis_vault',
        'action': 'view',
        'sensitivity': 'restricted',
        'public_allowed': False,
        'plain': 'Analytics and performance intelligence.',
    },

    # PACK052_EXPORT_ROUTE_MAP
    '/export': {
        'route_key': 'export',
        'action': 'download',
        'sensitivity': 'critical',
        'public_allowed': False,
        'plain': 'Export/download action corridor.',
    },
    '/download': {
        'route_key': 'export',
        'action': 'download',
        'sensitivity': 'critical',
        'public_allowed': False,
        'plain': 'Download action corridor.',
    },
}


# These are intentionally harmless/public-ish shell routes.
# The rule is: public routes must be deliberately listed.
OB_PUBLIC_SAFE_ROUTES = {
    '/',
    '/login',
    '/logout',
    '/signup',
    '/register',
    '/forgot-password',
    '/reset-password',
    '/terms',
    '/privacy',
    '/risk-disclosures',
    '/options-risk-disclosure',
    '/paper-performance-disclosure',
    '/billing-terms',
    '/contact',
    '/health',
    '/static',
    '/favicon.ico',
    '/tower',
    '/tower/',
    '/tower/security-command',
    '/tower/security-command/regenerate',
    '/tower/status.json',
    "/no-access",
    "/no-access.json",

    # PACK079B_CONTROLLED_POLISHED_DENY_PUBLIC_SAFE
    # This route is safe to pass through the old shell because it still returns a 403 polished lock.
    "/observatory-private",
}


def normalize_request_path(path: str) -> str:
    path = _safe_str(path, '/')
    if not path.startswith('/'):
        path = '/' + path
    if len(path) > 1 and path.endswith('/'):
        path = path.rstrip('/')
    return path


def match_ob_guard_policy(path: str) -> Dict[str, Any]:
    normalized = normalize_request_path(path)

    if normalized in OB_ROUTE_GUARD_MAP:
        return {
            'ok': True,
            'matched': True,
            'match_type': 'exact',
            'path': normalized,
            'policy': OB_ROUTE_GUARD_MAP[normalized],
        }

    # TOWER_OB_HOSTED_WALKTHROUGH_SYMBOL_ROUTE_POLICY_REPAIR_V1
    # Canonical hosted Symbol Page corridors.
    if (
        normalized.startswith('/ob/symbol/')
        or normalized.startswith('/symbol/')
    ):
        parts = normalized.split('/')
        symbol = parts[-1].upper() if parts else ''
        if symbol:
            return {
                'ok': True,
                'matched': True,
                'match_type': 'dynamic_ob_symbol',
                'path': normalized,
                'object_id': symbol,
                'policy': {
                    'route_key': 'symbol_detail',
                    'action': 'view',
                    'sensitivity': 'confidential',
                    'public_allowed': False,
                    'plain': 'Protected Observatory symbol intelligence page.',
                },
            }

    # Dynamic symbol detail pages: /signals/AAPL, /signals/AMD, etc.
    if normalized.startswith('/signals/') and len(normalized.split('/')) >= 3:
        symbol = normalized.split('/')[2].upper()
        return {
            'ok': True,
            'matched': True,
            'match_type': 'dynamic_symbol',
            'path': normalized,
            'object_id': symbol,
            'policy': {
                'route_key': 'symbol_detail',
                'action': 'view',
                'sensitivity': 'confidential',
                'public_allowed': False,
                'plain': 'Protected per-symbol intelligence page.',
            },
        }

    # PACK051_DYNAMIC_POSITION_ROUTE_MATCH
    # Nested position/trade pages still belong to the protected positions corridor.
    if (
        normalized.startswith('/my-positions/')
        or normalized.startswith('/positions/')
        or normalized.startswith('/trade/')
        or normalized.startswith('/trades/')
    ):
        object_id = normalized.split('/')[-1]
        return {
            'ok': True,
            'matched': True,
            'match_type': 'dynamic_position_or_trade',
            'path': normalized,
            'object_id': object_id,
            'policy': {
                'route_key': 'positions',
                'action': 'view',
                'sensitivity': 'restricted',
                'public_allowed': False,
                'plain': 'Protected position/trade detail corridor.',
            },
        }

    for public_path in OB_PUBLIC_SAFE_ROUTES:
        if normalized == public_path or normalized.startswith(public_path + '/'):
            return {
                'ok': True,
                'matched': False,
                'match_type': 'public_safe',
                'path': normalized,
                'policy': {
                    'public_allowed': True,
                    'route_key': 'public_safe',
                    'action': 'view',
                    'sensitivity': 'public_shell',
                    'plain': 'Deliberately public or harmless shell route.',
                },
            }

    return {
        'ok': True,
        'matched': False,
        'match_type': 'unmapped_default_deny',
        'path': normalized,
        'policy': {
            'public_allowed': False,
            'route_key': 'unmapped',
            'action': 'view',
            'sensitivity': 'unknown',
            'plain': 'This route is not mapped yet. Default deny for private build.',
        },
    }


def build_locked_ob_response(
    *,
    reason_code: str,
    human_reason: str,
    path: str,
    decision: Optional[Dict[str, Any]] = None,
) -> Tuple[str, int]:
    decision = decision if isinstance(decision, dict) else {}
    safe_reason = _safe_str(reason_code, 'ob_access_denied')
    safe_human = _safe_str(human_reason, 'The Observatory is private.')
    safe_path = _safe_str(path, '/')
    soulaana = _safe_str(
        decision.get('soulaana_translation'),
        'Soulaana: This corridor is private. No clearance, no view.'
    )

    html = f'''
    <!doctype html>
    <html>
    <head>
      <meta charset='utf-8'>
      <meta name='viewport' content='width=device-width, initial-scale=1'>
      <title>Observatory Locked</title>
      <style>
        body {{ margin:0; min-height:100vh; display:grid; place-items:center; background:#050713; color:#f8fafc; font-family:Arial, sans-serif; }}
        .card {{ width:min(720px, calc(100vw - 32px)); border:1px solid rgba(255,255,255,.16); border-radius:24px; padding:28px; background:linear-gradient(145deg, rgba(15,23,42,.96), rgba(30,27,75,.92)); box-shadow:0 24px 80px rgba(0,0,0,.42); }}
        .kicker {{ color:#facc15; letter-spacing:.18em; text-transform:uppercase; font-weight:800; font-size:.75rem; }}
        h1 {{ margin:.5rem 0 1rem; font-size:2rem; }}
        p {{ line-height:1.55; color:#dbeafe; }}
        .reason {{ margin-top:18px; padding:14px; border-radius:16px; background:rgba(255,255,255,.07); color:#fef3c7; }}
        code {{ color:#bae6fd; }}
      </style>
    </head>
    <body>
      <section class='card'>
        <div class='kicker'>THE OBSERVATORY</div>
        <h1>Private corridor locked.</h1>
        <p>{soulaana}</p>
        <div class='reason'>
          <strong>{safe_reason}</strong><br>
          {safe_human}<br>
          <code>{safe_path}</code>
        </div>
      </section>
    </body>
    </html>
    '''
    return html, 403


def evaluate_ob_request_guard(
    *,
    path: str,
    user_id: str = 'anonymous',
    role: str = '',
    user_clearance_level: str = '',
    current_risk_score: int = 0,
    default_deny_unmapped: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    metadata = metadata if isinstance(metadata, dict) else {}
    path = normalize_request_path(path)
    match = match_ob_guard_policy(path)
    policy = match.get('policy', {}) if isinstance(match.get('policy'), dict) else {}

    if policy.get('public_allowed') is True:
        return {
            'ok': True,
            'allowed': True,
            'decision': 'allow',
            'reason_code': 'ob_public_safe_route',
            'risk_state': 'clear',
            'risk_score': _safe_int(current_risk_score, 0),
            'required_actions': [],
            'human_reason': 'This route is deliberately public-safe.',
            'soulaana_translation': 'Soulaana: This is an outer shell route. No protected Observatory data is exposed here.',
            'metadata': {
                'path': path,
                'match': match,
                'evaluated_at': _utc_now(),
            },
        }

    if match.get('match_type') == 'unmapped_default_deny' and default_deny_unmapped:
        return {
            'ok': True,
            'allowed': False,
            'decision': 'deny',
            'reason_code': 'ob_route_unmapped_default_deny',
            'risk_state': 'restricted',
            'risk_score': max(_safe_int(current_risk_score, 0), 65),
            'required_actions': ['map_route_policy', 'owner_review'],
            'human_reason': 'This OB route is not mapped yet, so the private build blocks it by default.',
            'soulaana_translation': 'Soulaana: Unmapped corridor. I do not open doors that are not on the Tower map.',
            'metadata': {
                'path': path,
                'match': match,
                'evaluated_at': _utc_now(),
            },
        }

    route_key = _safe_str(policy.get('route_key'), 'unmapped')
    action = _safe_str(policy.get('action'), 'view')

    decision = evaluate_ob_route_clearance(
        user_id=user_id,
        role=role,
        user_clearance_level=user_clearance_level,
        route_key=route_key,
        action=action,
        current_risk_score=_safe_int(current_risk_score, 0),
        metadata={
            'guard_path': path,
            'guard_policy': policy,
            **metadata,
        },
    )

    decision.setdefault('metadata', {})
    if isinstance(decision['metadata'], dict):
        decision['metadata']['guard_path'] = path
        decision['metadata']['guard_match'] = match

    return decision


def should_block_ob_request(**kwargs) -> Dict[str, Any]:
    decision = evaluate_ob_request_guard(**kwargs)
    decision['block'] = not bool(decision.get('allowed'))
    return decision


def get_ob_route_guard_report() -> Dict[str, Any]:
    return {
        'ok': True,
        'tower_name': 'The Tower',
        'guarded_routes': OB_ROUTE_GUARD_MAP,
        'public_safe_routes': sorted(OB_PUBLIC_SAFE_ROUTES),
        'guarded_count': len(OB_ROUTE_GUARD_MAP),
        'public_safe_count': len(OB_PUBLIC_SAFE_ROUTES),
        'default_deny_unmapped': True,
        'human_reason': 'OB route guard foundation is loaded. Public routes must be deliberate; unmapped private routes default deny.',
    }
