"""
Pack 2450 — Owner Completion Summary View.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2433 import (
    REAL_ROOM_REGISTRY,
)


PACK_ID = "2450"
ENDPOINT = "/tower/ir-cert-v2450.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": 'Owner Completion Summary View',
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "owner_completion_summary_ready": True,
        "guided_run_route": (
            "/tower/observatory-walkthrough/"
            "guided-start"
        ),
        "progress_route": (
            "/tower/observatory-walkthrough/"
            "progress"
        ),
        "final_receipt_route": (
            "/tower/observatory-walkthrough/"
            "final-receipt"
        ),
        "room_count": len(
            REAL_ROOM_REGISTRY
        ),
        "room_order": [
            room["room_id"]
            for room in REAL_ROOM_REGISTRY
        ],
        "ordered_progression": True,
        "resume_supported": True,
        "per_room_receipts": True,
        "final_receipt": True,
        "tower_progress_badge": True,
        "owner_only": True,
        "tower_clearance_value": (
            "ob_owner_command"
        ),
        "tower_clearance_rank": 900,
        "existing_room_guards_preserved": True,
        "existing_templates_preserved": True,
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
        "next_pack": "2451",
        "safe_to_continue_to_pack_2451": True,
    }


def build_ir_cert_p2450_preview():
    return deepcopy(_build_cached())


def prepare_pack_2451_guided_ob_run():
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2451",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
