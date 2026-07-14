"""
Pack 2476 — Backup Rotation Inventory.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_observatory_walkthrough_hosted_assurance import (
    BACKUP_MAX_AGE_HOURS_ENVIRONMENT_KEY,
    DEFAULT_BACKUP_MAX_AGE_HOURS,
    HOSTED_MODE_ENVIRONMENT_KEY,
    INCIDENT_DIRECTORY_ENVIRONMENT_KEY,
    RETENTION_APPROVAL_DIRECTORY_ENVIRONMENT_KEY,
)


PACK_ID = "2476"
ENDPOINT = "/tower/ir-cert-v2476.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": 'Backup Rotation Inventory',
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "backup_rotation_inventory_ready": True,
        "hosted_mode_environment_key": (
            HOSTED_MODE_ENVIRONMENT_KEY
        ),
        "backup_max_age_environment_key": (
            BACKUP_MAX_AGE_HOURS_ENVIRONMENT_KEY
        ),
        "default_backup_max_age_hours": (
            DEFAULT_BACKUP_MAX_AGE_HOURS
        ),
        "incident_directory_environment_key": (
            INCIDENT_DIRECTORY_ENVIRONMENT_KEY
        ),
        "retention_approval_directory_environment_key": (
            RETENTION_APPROVAL_DIRECTORY_ENVIRONMENT_KEY
        ),
        "runtime_gate": True,
        "startup_fail_closed": True,
        "backup_cadence_readiness": True,
        "backup_rotation_inventory": True,
        "restore_drill": True,
        "production_database_replaced_in_drill": False,
        "retention_approval_queue": True,
        "automatic_cleanup": False,
        "export_evidence_review": True,
        "storage_incident_receipts": True,
        "operations_readiness_board": True,
        "automatic_restore": False,
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
        "next_pack": "2477",
        "safe_to_continue_to_pack_2477": True,
    }


def build_ir_cert_p2476_preview():
    return deepcopy(_build_cached())


def prepare_pack_2477_hosted_assurance():
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2477",
        "fail_closed": True,
        "automatic_restore": False,
        "automatic_cleanup": False,
        "direct_vault_write": False,
    }
