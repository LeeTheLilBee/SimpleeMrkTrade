"""
Pack 2501 — Activation Execution Hold.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_observatory_walkthrough_activation_approval import (
    ACTIVATION_APPROVAL_DIRECTORY_ENVIRONMENT_KEY,
    ACTIVATION_COMMAND_TEMPLATE_ENVIRONMENT_KEY,
)


PACK_ID = "2501"
ENDPOINT = "/tower/ir-cert-v2501.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": 'Activation Execution Hold',
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "activation_execution_hold_ready": True,
        "approval_directory_environment_key": (
            ACTIVATION_APPROVAL_DIRECTORY_ENVIRONMENT_KEY
        ),
        "command_template_environment_key": (
            ACTIVATION_COMMAND_TEMPLATE_ENVIRONMENT_KEY
        ),
        "approval_request": True,
        "owner_step_up_required": True,
        "credential_material_stored": False,
        "scope_freeze": True,
        "activation_window_preview": True,
        "rollback_readiness": True,
        "deployment_command_dry_run": True,
        "shell_invoked": False,
        "owner_decision_receipt": True,
        "execution_hold": True,
        "owner_approval_required": True,
        "activation_performed": False,
        "deployment_command_executed": False,
        "production_database_replaced": False,
        "automatic_restore": False,
        "automatic_cleanup": False,
        "direct_vault_write": False,
        "public_links": False,
        "default_deny": True,
        "broker_order_submission": False,
        "real_capital_movement": False,
        "production_manual_live_authorization": False,
        "live_auto_activation": False,
        "preview_only": True,
        "next_pack": "2502",
        "safe_to_continue_to_pack_2502": True,
    }


def build_ir_cert_p2501_preview():
    return deepcopy(_build_cached())


def prepare_pack_2502_activation_approval():
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2502",
        "execution_hold": True,
        "activation_performed": False,
        "deployment_command_executed": False,
    }
