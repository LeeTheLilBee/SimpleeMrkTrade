"""
Pack 2505 — Tower Owner Session.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_human_login_ob_launch import (
    ACCESS_HOME_PATH,
    LOGIN_PATH,
    LOGOUT_PATH,
    OBSERVATORY_LAUNCH_PATH,
    OBSERVATORY_STEP_UP_PATH,
    START_PATH,
)


PACK_ID = "2505"
ENDPOINT = "/tower/ir-cert-v2505.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": 'Tower Owner Session',
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "tower_owner_session_ready": True,
        "tower_start_path": START_PATH,
        "tower_login_path": LOGIN_PATH,
        "tower_access_home_path": ACCESS_HOME_PATH,
        "observatory_launch_path": OBSERVATORY_LAUNCH_PATH,
        "observatory_step_up_path": OBSERVATORY_STEP_UP_PATH,
        "logout_path": LOGOUT_PATH,
        "human_login_form": True,
        "owner_credential_verification": True,
        "owner_session_establishment": True,
        "tower_access_home": True,
        "observatory_launch_card": True,
        "owner_permission_gate": True,
        "owner_step_up_gate": True,
        "protected_ob_handoff": True,
        "launch_receipt": True,
        "logout_session_clear": True,
        "credentials_committed": False,
        "test_session_injection_required": False,
        "default_deny": True,
        "broker_order_submission": False,
        "real_capital_movement": False,
        "production_manual_live_authorization": False,
        "live_auto_activation": False,
        "direct_vault_write": False,
        "public_links": False,
        "next_pack": "2506",
        "safe_to_continue_to_pack_2506": True,
    }


def build_ir_cert_p2505_preview():
    return deepcopy(_build_cached())
