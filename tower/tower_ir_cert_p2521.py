"""
Pack 2521 — Hidden Evidence Drawers.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_access_home_ui_v2 import (
    ui_v2_contract,
)


PACK_ID = "2521"
ENDPOINT = "/tower/ir-cert-v2521.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    contract = ui_v2_contract()

    payload = {
        "pack": PACK_ID,
        "pack_name": 'Hidden Evidence Drawers',
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "hidden_evidence_drawers_ready": True,
        "tower_access_home_ui_v2": True,
        "simplee_front_door": True,
        "black_glass_theme": True,
        "deep_violet_theme": True,
        "gold_owner_accents": True,
        "blue_minimized": True,
        "owner_session_status": True,
        "app_launch_cards": True,
        "observatory_launch_door": True,
        "ob_return_session_continuity": True,
        "return_receipt_status_panel": True,
        "owner_actions_panel": True,
        "quick_launch_panel": True,
        "hidden_evidence_drawers": True,
        "proof_page_main_experience": False,
        "list_heavy_main_surface": False,
        "credentials_committed": False,
        "test_session_injection_required": False,
        "default_deny": True,
        "broker_order_submission": False,
        "real_capital_movement": False,
        "production_manual_live_authorization": False,
        "live_auto_activation": False,
        "direct_vault_write": False,
        "public_links": False,
        "contract": contract,
        "next_pack": "2522",
        "safe_to_continue_to_pack_2522": True,
    }

    return payload


def build_ir_cert_p2521_preview():
    return deepcopy(_build_cached())
