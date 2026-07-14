"""
Pack 2435 — Protected Room Preview Context Contract.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2433 import (
    REAL_ROOM_REGISTRY,
    real_room_by_id,
)


PACK_ID = "2435"
ENDPOINT = "/tower/ir-cert-v2435.json"
TARGET_ROOM_ID = None


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    target_room = (
        real_room_by_id(
            TARGET_ROOM_ID
        )
        if TARGET_ROOM_ID
        else None
    )

    return {
        "pack": PACK_ID,
        "pack_name": 'Protected Room Preview Context Contract',
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "protected_preview_context_ready": True,
        "target_room": target_room,
        "real_room_count": len(
            REAL_ROOM_REGISTRY
        ),
        "tower_entry_routes": [
            "/tower",
            "/tower/",
        ],
        "walkthrough_route": (
            "/tower/"
            "observatory-walkthrough"
        ),
        "real_surface_open_route": (
            "/tower/"
            "observatory-walkthrough/"
            "open/<room_id>"
        ),
        "response_overlay_integration": True,
        "existing_room_guard_preserved": True,
        "existing_templates_preserved": True,
        "owner_only": True,
        "tower_clearance_value": (
            "ob_owner_command"
        ),
        "tower_clearance_rank": 900,
        "default_deny": True,
        "unmapped_routes_blocked": True,
        "broker_order_submission": False,
        "real_capital_movement": False,
        "production_manual_live_authorization": False,
        "live_auto_activation": False,
        "direct_vault_upload": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2436",
        "safe_to_continue_to_pack_2436": True,
    }


def build_ir_cert_p2435_preview():
    return deepcopy(_build_cached())


def prepare_pack_2436_ob_real_surface():
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2436",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
