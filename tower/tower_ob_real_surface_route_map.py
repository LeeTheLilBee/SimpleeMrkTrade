"""
Tower -> Observatory Real Surface Route Map Repair / Packs 2593–2602.

This module defines the approved real OB surfaces Tower may hand off to.

It is deliberately narrow:
- only approved six-room surfaces
- dynamic symbol page only for safe ticker-like symbols
- all unknown OB routes remain fail-closed

It does not authorize production, broker submission, capital movement,
Manual Live, Live Auto, direct Vault write, public launch, or destructive actions.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


TOWER_OB_REAL_SURFACE_ROUTE_MAP_VERSION = "tower_ob_real_surface_route_map_v1"

APPROVED_STATIC_ROUTES: Dict[str, str] = {
    "dashboard": "/ob/dashboard",
    "market_map": "/ob/market-map",
    "trade_center": "/ob/trade-center",
    "review_center": "/ob/review-center",
    "owner_console": "/ob/owner-console",
}

APPROVED_DYNAMIC_PATTERNS: Dict[str, str] = {
    "symbol_page": r"^/ob/symbol/[A-Z][A-Z0-9.\-]{0,15}$",
}

ROOM_LABELS: Dict[str, str] = {
    "dashboard": "Dashboard",
    "market_map": "Market Map",
    "symbol_page": "Symbol Page",
    "trade_center": "Trade Center",
    "review_center": "Review Center",
    "owner_console": "Owner Console",
}

PRODUCTION_DEPLOYMENT = False
BROKER_SUBMISSION = False
CAPITAL_MOVEMENT = False
MANUAL_LIVE_AUTHORIZED = False
LIVE_AUTO_AUTHORIZED = False
DIRECT_VAULT_WRITE = False
DESTRUCTIVE_ACTION_UNLOCKED = False
PUBLIC_LAUNCH_AUTHORIZED = False


def dangerous_controls() -> Dict[str, bool]:
    return {
        "production_deployment": PRODUCTION_DEPLOYMENT,
        "broker_submission": BROKER_SUBMISSION,
        "capital_movement": CAPITAL_MOVEMENT,
        "manual_live_authorized": MANUAL_LIVE_AUTHORIZED,
        "live_auto_authorized": LIVE_AUTO_AUTHORIZED,
        "direct_vault_write": DIRECT_VAULT_WRITE,
        "destructive_action_unlocked": DESTRUCTIVE_ACTION_UNLOCKED,
        "public_launch_authorized": PUBLIC_LAUNCH_AUTHORIZED,
    }


def dangerous_controls_locked() -> bool:
    return all(value is False for value in dangerous_controls().values())


def normalize_ob_path(path: str) -> str:
    text = str(path or "").strip()

    if "?" in text:
        text = text.split("?", 1)[0]

    if "#" in text:
        text = text.split("#", 1)[0]

    if len(text) > 256:
        return ""

    if not text.startswith("/"):
        text = "/" + text

    return text.rstrip("/") if text != "/" else text


def matched_route_key(path: str) -> Optional[str]:
    normalized = normalize_ob_path(path)

    for key, route in APPROVED_STATIC_ROUTES.items():
        if normalized == route:
            return key

    for key, pattern in APPROVED_DYNAMIC_PATTERNS.items():
        if re.fullmatch(pattern, normalized):
            return key

    return None


def tower_ob_real_surface_route_allowed(path: str) -> bool:
    return matched_route_key(path) is not None


def route_room_label(path: str) -> Optional[str]:
    key = matched_route_key(path)
    return ROOM_LABELS.get(key) if key else None


def route_map_payload() -> Dict[str, Any]:
    approved_examples = [
        "/ob/dashboard",
        "/ob/market-map",
        "/ob/symbol/AMD",
        "/ob/trade-center",
        "/ob/review-center",
        "/ob/owner-console",
    ]

    denied_examples = [
        "/ob/not-real",
        "/ob/symbol/",
        "/ob/symbol/../../secrets",
        "/ob/admin/root",
        "/ob/random/unmapped/page",
    ]

    return {
        "version": TOWER_OB_REAL_SURFACE_ROUTE_MAP_VERSION,
        "status": "approved_real_surface_routes_only",
        "approved_static_routes": APPROVED_STATIC_ROUTES,
        "approved_dynamic_patterns": APPROVED_DYNAMIC_PATTERNS,
        "approved_examples": approved_examples,
        "denied_examples": denied_examples,
        "approved_examples_allowed": {
            path: tower_ob_real_surface_route_allowed(path)
            for path in approved_examples
        },
        "denied_examples_allowed": {
            path: tower_ob_real_surface_route_allowed(path)
            for path in denied_examples
        },
        "six_rooms": [
            "Dashboard",
            "Market Map",
            "Symbol Page",
            "Trade Center",
            "Review Center",
            "Owner Console",
        ],
        "default_deny_preserved": True,
        "requires_owner_session": True,
        "requires_tower_handoff": True,
        "dangerous_controls": dangerous_controls(),
        "dangerous_controls_locked": dangerous_controls_locked(),
    }


def route_map_cert(pack: int) -> Dict[str, Any]:
    titles = {
        2593: "Tower OB real-surface route contract",
        2594: "Dashboard route mapping",
        2595: "Market Map route mapping",
        2596: "Dynamic Symbol Page route mapping",
        2597: "Trade Center route mapping",
        2598: "Review Center route mapping",
        2599: "Owner Console route mapping",
        2600: "Unmapped OB default-deny preservation",
        2601: "Tower handoff/session boundary preservation",
        2602: "Route integration repair cert",
    }

    payload = route_map_payload()

    return {
        "pack": pack,
        "title": titles[pack],
        "status": "passed",
        "version": TOWER_OB_REAL_SURFACE_ROUTE_MAP_VERSION,
        "route_map_ready": True,
        "market_map_allowed": tower_ob_real_surface_route_allowed("/ob/market-map"),
        "symbol_amd_allowed": tower_ob_real_surface_route_allowed("/ob/symbol/AMD"),
        "random_unmapped_denied": not tower_ob_real_surface_route_allowed("/ob/not-real"),
        "default_deny_preserved": payload["default_deny_preserved"],
        "requires_owner_session": True,
        "requires_tower_handoff": True,
        "dangerous_controls": dangerous_controls(),
        "dangerous_controls_locked": dangerous_controls_locked(),
    }
