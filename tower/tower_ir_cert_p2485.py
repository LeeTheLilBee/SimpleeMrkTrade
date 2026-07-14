"""
Pack 2485 — Startup Gate Wiring.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_observatory_walkthrough_deployment_boundary import (
    DEPLOYMENT_ENVIRONMENT_NAME_KEY,
    DEPLOYMENT_RECORD_DIRECTORY_ENVIRONMENT_KEY,
    SUPPORTED_DEPLOYMENT_ENVIRONMENTS,
)


PACK_ID = "2485"
ENDPOINT = "/tower/ir-cert-v2485.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": 'Startup Gate Wiring',
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "startup_gate_wiring_ready": True,
        "deployment_environment_key": (
            DEPLOYMENT_ENVIRONMENT_NAME_KEY
        ),
        "deployment_record_directory_key": (
            DEPLOYMENT_RECORD_DIRECTORY_ENVIRONMENT_KEY
        ),
        "supported_environments": sorted(
            SUPPORTED_DEPLOYMENT_ENVIRONMENTS
        ),
        "deployment_manifest": True,
        "environment_binding_receipts": True,
        "startup_gate_receipts": True,
        "backup_enforcement_preview": True,
        "restore_drill_evidence": True,
        "retention_owner_decisions": True,
        "incident_review_queue": True,
        "release_evidence_packet": True,
        "activation_recommendation": True,
        "owner_approval_required": True,
        "activation_performed": False,
        "deployment_command_executed": False,
        "production_database_replaced": False,
        "automatic_restore": False,
        "automatic_cleanup": False,
        "tower_owned_storage": True,
        "direct_vault_write": False,
        "public_links": False,
        "owner_only": True,
        "default_deny": True,
        "broker_order_submission": False,
        "real_capital_movement": False,
        "production_manual_live_authorization": False,
        "live_auto_activation": False,
        "preview_only": True,
        "next_pack": "2486",
        "safe_to_continue_to_pack_2486": True,
    }


def build_ir_cert_p2485_preview():
    return deepcopy(_build_cached())


def prepare_pack_2486_deployment_boundary():
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2486",
        "owner_approval_required": True,
        "activation_performed": False,
        "automatic_restore": False,
        "automatic_cleanup": False,
        "direct_vault_write": False,
    }
