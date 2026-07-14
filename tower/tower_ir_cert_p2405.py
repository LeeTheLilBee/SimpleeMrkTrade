"""
SEARCHABLE LABEL: TOWER_PACK_2405_ROUTE_CONTRACT_DRIFT

Pack 2405 — Route Contract Drift Detector
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2372 import get_room_by_id
from tower.tower_ir_cert_p2373 import resolve_observatory_route


PACK_ID = "2405"
ENDPOINT = "/tower/ir-cert-v2405.json"


def detect_route_contract_drift(
    *,
    room_id: str,
    expected_canonical_path: str,
    observed_path: str,
    observed_room_id: str | None = None,
) -> Dict[str, Any]:
    room = get_room_by_id(room_id)
    resolved = resolve_observatory_route(observed_path)

    drift = []

    if room is None:
        drift.append("ob_route_unmapped_default_deny")

    if not resolved["allowed"]:
        drift.append(resolved["reason_code"])

    if (
        resolved.get("room_id")
        and resolved.get("room_id") != room_id
    ):
        drift.append("ob_route_contract_room_drift")

    if observed_room_id and observed_room_id != room_id:
        drift.append("ob_route_contract_room_drift")

    if (
        resolved.get("canonical_path")
        and resolved.get("canonical_path")
        != expected_canonical_path
    ):
        drift.append("ob_route_contract_path_drift")

    detected = bool(drift)

    return {
        "drift_detected": detected,
        "allowed": not detected,
        "reason_code": (
            drift[0]
            if detected
            else "ob_route_contract_stable"
        ),
        "drift_codes": drift,
        "room_id": room_id,
        "expected_canonical_path": expected_canonical_path,
        "observed_path": observed_path,
        "resolved_path": resolved.get("canonical_path"),
        "required_action": (
            "deny_and_lockback"
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
        "pack_name": "Route Contract Drift Detector",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "canonical_registry_authority": "tower",
        "ob_route_guessing_enabled": False,
        "unmapped_route_default_deny": True,
        "drift_requires_lockback": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2406",
        "safe_to_continue_to_pack_2406": True,
    }


def build_ir_cert_p2405_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2406_ir_cert_p2406() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2406",
        "name": "Failed Launch Recovery and Lockback",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
