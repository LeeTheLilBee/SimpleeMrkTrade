"""
Pack 2462 — Persistence Readiness Checkpoint.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_observatory_walkthrough_store import (
    DATABASE_ENVIRONMENT_KEY,
    DEFAULT_DATABASE_PATH,
    SCHEMA_VERSION,
)


PACK_ID = "2462"
ENDPOINT = "/tower/ir-cert-v2462.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": 'Persistence Readiness Checkpoint',
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "persistence_readiness_ready": True,
        "database_environment_key": (
            DATABASE_ENVIRONMENT_KEY
        ),
        "default_database_path": str(
            DEFAULT_DATABASE_PATH
        ),
        "schema_version": SCHEMA_VERSION,
        "tower_owned_storage": True,
        "archive_vault_storage": False,
        "public_storage": False,
        "direct_vault_write": False,
        "progress_persistence": True,
        "room_receipt_persistence": True,
        "final_receipt_persistence": True,
        "owner_history": True,
        "lost_session_resume": True,
        "integrity_verification": True,
        "history_route": (
            "/tower/observatory-walkthrough/history"
        ),
        "detail_route": (
            "/tower/observatory-walkthrough/"
            "history/<walkthrough_id>"
        ),
        "owner_only": True,
        "default_deny": True,
        "broker_order_submission": False,
        "real_capital_movement": False,
        "production_manual_live_authorization": False,
        "live_auto_activation": False,
        "preview_only": True,
        "contract_only": True,
        "next_pack": "2463",
        "safe_to_continue_to_pack_2463": True,
    }


def build_ir_cert_p2462_preview():
    return deepcopy(_build_cached())


def prepare_pack_2463_guided_run_persistence():
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2463",
        "preview_only": True,
        "direct_vault_write": False,
    }
