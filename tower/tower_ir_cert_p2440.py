"""
Pack 2440 — Review Center Real-Surface Walkthrough Integration.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2433 import (
    REAL_ROOM_REGISTRY,
    real_room_by_id,
)


PACK_ID = "2440"
ENDPOINT = "/tower/ir-cert-v2440.json"
TARGET_ROOM_ID = 'ob_room_review_center'


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
        "pack_name": 'Review Center Real-Surface Walkthrough Integration',
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "review_center_real_surface_ready": True,
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
        "next_pack": "2441",
        "safe_to_continue_to_pack_2441": True,
    }


def build_ir_cert_p2440_preview():
    return deepcopy(_build_cached())


def prepare_pack_2441_ob_real_surface():
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2441",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
