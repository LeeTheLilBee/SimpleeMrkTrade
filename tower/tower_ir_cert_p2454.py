"""
Pack 2454 — Durable Guided-Run Ledger.
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


PACK_ID = "2454"
ENDPOINT = "/tower/ir-cert-v2454.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": 'Durable Guided-Run Ledger',
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "durable_run_ledger_ready": True,
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
        "next_pack": "2455",
        "safe_to_continue_to_pack_2455": True,
    }


def build_ir_cert_p2454_preview():
    return deepcopy(_build_cached())


def prepare_pack_2455_guided_run_persistence():
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2455",
        "preview_only": True,
        "direct_vault_write": False,
    }
