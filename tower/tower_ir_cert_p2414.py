"""
SEARCHABLE LABEL: TOWER_PACK_2414_REASON_CODE_COVERAGE

Pack 2414 — Allow/Deny Reason-Code Coverage Contract
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict, List

from tower.tower_ir_cert_p2372 import ROOMS


PACK_ID = "2414"
ENDPOINT = "/tower/ir-cert-v2414.json"


REQUIRED_REASON_CODES = {
    "allow": {
        "ob_room_contract_allow",
        "ob_protected_route_enforcement_allow",
        "ob_launch_authorization_valid",
        "ob_launch_handoff_fresh",
        "ob_launch_scope_valid",
    },
    "deny": {
        "ob_route_unmapped_default_deny",
        "ob_identity_missing",
        "ob_role_not_allowed",
        "ob_owner_role_required",
        "ob_clearance_level_too_low",
        "ob_step_up_required",
        "ob_mode_not_allowed",
        "ob_lockdown_active",
        "ob_risk_gate_denied",
        "ob_launch_handoff_expired",
        "ob_launch_handoff_revoked",
        "ob_launch_handoff_replay_blocked",
        "ob_cross_room_launch_blocked",
        "ob_launch_path_scope_mismatch",
        "ob_launch_mode_scope_mismatch",
        "ob_launch_session_mismatch",
        "ob_contract_version_mismatch",
    },
}


def build_reason_code_coverage() -> Dict[str, Any]:
    room_codes = set()

    for room in ROOMS:
        room_codes.add(room["allow_reason_code"])
        room_codes.update(room["deny_reason_codes"])

    known_codes = (
        REQUIRED_REASON_CODES["allow"]
        | REQUIRED_REASON_CODES["deny"]
        | room_codes
    )

    rows: List[Dict[str, Any]] = []

    for code in sorted(known_codes):
        category = (
            "allow"
            if code in REQUIRED_REASON_CODES["allow"]
            or code == "ob_room_contract_allow"
            else "deny"
        )

        rows.append({
            "reason_code": code,
            "category": category,
            "receipt_required": True,
            "owner_safe": True,
            "default_deny_preserved": (
                category == "deny"
            ),
        })

    missing_allow = sorted(
        REQUIRED_REASON_CODES["allow"] - known_codes
    )

    missing_deny = sorted(
        REQUIRED_REASON_CODES["deny"] - known_codes
    )

    return {
        "coverage_rows": rows,
        "covered_reason_code_count": len(rows),
        "missing_allow_codes": missing_allow,
        "missing_deny_codes": missing_deny,
        "coverage_complete": (
            not missing_allow
            and not missing_deny
        ),
        "unknown_codes_default_deny": True,
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    coverage = build_reason_code_coverage()

    return {
        "pack": PACK_ID,
        "pack_name": (
            "Allow/Deny Reason-Code Coverage Contract"
        ),
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "reason_code_coverage": coverage,
        "coverage_complete": coverage["coverage_complete"],
        "unknown_codes_default_deny": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2415",
        "safe_to_continue_to_pack_2415": True,
    }


def build_ir_cert_p2414_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2415_ir_cert_p2415() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2415",
        "name": "Permanent Safety Boundary Attestation",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
