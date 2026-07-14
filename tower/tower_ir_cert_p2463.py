"""
Pack 2463 — Hosted Persistence Configuration Contract.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_observatory_walkthrough_store_ops import (
    BACKUP_DIRECTORY_ENVIRONMENT_KEY,
    DEFAULT_BACKUP_DIRECTORY,
    DEFAULT_RETENTION_DAYS,
    RETENTION_DAYS_ENVIRONMENT_KEY,
)


PACK_ID = "2463"
ENDPOINT = "/tower/ir-cert-v2463.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": 'Hosted Persistence Configuration Contract',
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "hosted_configuration_ready": True,
        "backup_directory_environment_key": (
            BACKUP_DIRECTORY_ENVIRONMENT_KEY
        ),
        "default_backup_directory": str(
            DEFAULT_BACKUP_DIRECTORY
        ),
        "retention_days_environment_key": (
            RETENTION_DAYS_ENVIRONMENT_KEY
        ),
        "default_retention_days": (
            DEFAULT_RETENTION_DAYS
        ),
        "schema_version_gate": True,
        "startup_health_check": True,
        "backup_snapshot": True,
        "backup_verification": True,
        "restore_preview": True,
        "explicit_restore_confirmation": True,
        "retention_preview": True,
        "automatic_cleanup": False,
        "owner_export_preview": True,
        "corruption_assessment": True,
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
        "next_pack": "2464",
        "safe_to_continue_to_pack_2464": True,
    }


def build_ir_cert_p2463_preview():
    return deepcopy(_build_cached())


def prepare_pack_2464_persistence_operations():
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2464",
        "direct_vault_write": False,
        "automatic_destructive_action": False,
    }
