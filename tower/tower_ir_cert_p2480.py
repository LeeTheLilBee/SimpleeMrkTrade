"""
Pack 2480 — Storage Operations Incident Receipt.
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


PACK_ID = "2480"
ENDPOINT = "/tower/ir-cert-v2480.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": 'Storage Operations Incident Receipt',
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "storage_incident_receipt_ready": True,
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
        "next_pack": "2481",
        "safe_to_continue_to_pack_2481": True,
    }


def build_ir_cert_p2480_preview():
    return deepcopy(_build_cached())


def prepare_pack_2481_hosted_assurance():
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2481",
        "fail_closed": True,
        "automatic_restore": False,
        "automatic_cleanup": False,
        "direct_vault_write": False,
    }
