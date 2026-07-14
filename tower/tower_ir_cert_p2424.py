"""
Pack 2424 — Owner Access and Session Guard
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2372 import ROOMS


PACK_ID = "2424"
ENDPOINT = "/tower/ir-cert-v2424.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Owner Access and Session Guard",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "owner_session_guard_ready": True,
        "walkthrough_route": (
            "/tower/observatory-walkthrough"
        ),
        "official_room_count": len(ROOMS),
        "official_room_ids": [
            room["room_id"]
            for room in ROOMS
        ],
        "owner_only": True,
        "tower_clearance_value": (
            "ob_owner_command"
        ),
        "tower_clearance_rank": 900,
        "default_deny": True,
        "unmapped_routes_blocked": True,
        "ob_self_authorization": False,
        "broker_order_submission": False,
        "real_capital_movement": False,
        "production_manual_live_authorization": False,
        "live_auto_activation": False,
        "direct_vault_upload": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2425",
        "safe_to_continue_to_pack_2425": True,
    }


def build_ir_cert_p2424_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2425_ob_walkthrough() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2425",
        "name": "Six-Room Walkthrough Manifest",
        "walkthrough_route": (
            "/tower/observatory-walkthrough"
        ),
        "default_deny": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
