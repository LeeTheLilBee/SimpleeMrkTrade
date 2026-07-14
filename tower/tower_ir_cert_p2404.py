"""
SEARCHABLE LABEL: TOWER_PACK_2404_SESSION_DRIFT_DETECTOR

Pack 2404 — Protected Session Drift Detector
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2404"
ENDPOINT = "/tower/ir-cert-v2404.json"


def detect_protected_session_drift(
    *,
    handoff: Dict[str, Any],
    current_owner_id: str,
    current_session_id: str,
    current_room_id: str,
    current_path: str,
    current_mode: str,
) -> Dict[str, Any]:
    drift = []

    if handoff.get("owner_id") != current_owner_id:
        drift.append("ob_launch_owner_mismatch")

    if handoff.get("session_id") != current_session_id:
        drift.append("ob_launch_session_mismatch")

    if handoff.get("approved_room_id") != current_room_id:
        drift.append("ob_cross_room_launch_blocked")

    if handoff.get("canonical_path") != current_path:
        drift.append("ob_launch_path_scope_mismatch")

    if handoff.get("mode") != current_mode:
        drift.append("ob_launch_mode_scope_mismatch")

    detected = bool(drift)

    return {
        "drift_detected": detected,
        "allowed": not detected,
        "reason_code": (
            drift[0]
            if detected
            else "ob_protected_session_scope_stable"
        ),
        "drift_codes": drift,
        "required_action": (
            "revoke_and_lockback"
            if detected
            else "continue_protected_session"
        ),
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Protected Session Drift Detector",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "monitored_scope": [
            "owner",
            "session",
            "room",
            "path",
            "mode",
        ],
        "drift_default_deny": True,
        "new_handoff_required_after_drift": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2405",
        "safe_to_continue_to_pack_2405": True,
    }


def build_ir_cert_p2404_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2405_ir_cert_p2405() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2405",
        "name": "Route Contract Drift Detector",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
