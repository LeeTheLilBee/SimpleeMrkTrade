"""
Pack 2433 — Real Observatory Room Route
Inventory Contract.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict, List


PACK_ID = "2433"
ENDPOINT = "/tower/ir-cert-v2433.json"

REAL_ROOM_REGISTRY: List[
    Dict[str, Any]
] = [
    {
        "position": 1,
        "room_id": "ob_room_dashboard",
        "display_name": "Dashboard",
        "real_route": "/dashboard",
        "route_pattern": "/dashboard",
        "template": (
            "web/templates/"
            "dashboard.html"
        ),
        "symbol_required": False,
    },
    {
        "position": 2,
        "room_id": "ob_room_market_map",
        "display_name": "Market Map",
        "real_route": "/market-map",
        "route_pattern": "/market-map",
        "template": (
            "web/templates/"
            "market_map.html"
        ),
        "symbol_required": False,
    },
    {
        "position": 3,
        "room_id": "ob_room_symbol_page",
        "display_name": "Symbol Page",
        "real_route": "/ob/symbol/AMD",
        "route_pattern": (
            "/ob/symbol/<symbol>"
        ),
        "template": (
            "web/templates/"
            "symbol_page.html"
        ),
        "symbol_required": True,
    },
    {
        "position": 4,
        "room_id": "ob_room_trade_center",
        "display_name": "Trade Center",
        "real_route": (
            "/ob/trade-center"
        ),
        "route_pattern": (
            "/ob/trade-center"
        ),
        "template": (
            "web/templates/"
            "trade_center.html"
        ),
        "symbol_required": False,
    },
    {
        "position": 5,
        "room_id": "ob_room_review_center",
        "display_name": "Review Center",
        "real_route": (
            "/ob/review-center"
        ),
        "route_pattern": (
            "/ob/review-center"
        ),
        "template": (
            "web/templates/"
            "review_center.html"
        ),
        "symbol_required": False,
    },
    {
        "position": 6,
        "room_id": "ob_room_owner_console",
        "display_name": "Owner Console",
        "real_route": (
            "/ob/owner-console"
        ),
        "route_pattern": (
            "/ob/owner-console"
        ),
        "template": (
            "web/templates/"
            "owner_console.html"
        ),
        "symbol_required": False,
    },
]


def real_room_by_id(
    room_id: str,
) -> Dict[str, Any] | None:
    for room in REAL_ROOM_REGISTRY:
        if room["room_id"] == room_id:
            return deepcopy(room)

    return None


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": (
            "Real Observatory Room "
            "Route Inventory Contract"
        ),
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "tower_entry_routes": [
            "/tower",
            "/tower/",
        ],
        "walkthrough_route": (
            "/tower/"
            "observatory-walkthrough"
        ),
        "room_count": len(
            REAL_ROOM_REGISTRY
        ),
        "rooms": deepcopy(
            REAL_ROOM_REGISTRY
        ),
        "unresolved_rooms": [],
        "real_surface_integration": True,
        "template_rewrite_required": False,
        "response_overlay_integration": True,
        "default_deny": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2434",
        "safe_to_continue_to_pack_2434": True,
    }


def build_ir_cert_p2433_preview():
    return deepcopy(_build_cached())


def prepare_pack_2434_ob_real_surface():
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2434",
        "name": (
            "Tower Walkthrough Entry "
            "Navigation Integration"
        ),
        "preview_only": True,
        "writes_state": False,
    }
