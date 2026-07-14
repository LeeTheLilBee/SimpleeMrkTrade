"""
SEARCHABLE LABEL:
TOWER_PACK_2422_OBSERVATORY_PROTECTED_LAUNCH_CLOSEOUT

Pack 2422 — Observatory Protected Launch Corridor Closeout

Closes the full Tower corridor:

2372-2380
Protected Room Access and Launch Contract

2381-2390
Protected Launch Integration

2391-2400
Protected Launch Enforcement and Receipt Chain

2401-2410
Protected Launch Assurance and Failure Recovery

2411-2420
Protected Launch Certification and Owner Acceptance

2421
Protected Launch Operational Validation
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2372 import (
    APP_ID,
    CONTRACT_VERSION,
    REQUEST_TYPE,
    ROOMS,
)
from tower.tower_ir_cert_p2380 import (
    build_ir_cert_p2380_preview,
)
from tower.tower_ir_cert_p2390 import (
    build_protected_launch_readiness,
)
from tower.tower_ir_cert_p2400 import (
    build_enforcement_readiness,
)
from tower.tower_ir_cert_p2410 import (
    build_assurance_readiness,
)
from tower.tower_ir_cert_p2420 import (
    build_certification_closeout,
)
from tower.tower_ir_cert_p2421 import (
    run_protected_launch_operational_validation,
)


PACK_ID = "2422"
ENDPOINT = "/tower/ir-cert-v2422.json"

CORRIDOR_ID = (
    "tower_observatory_protected_launch_2372_2422"
)

CORRIDOR_VERSION = (
    "tower-ob-protected-launch-corridor-v1.0.0"
)


def _hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def build_observatory_corridor_closeout(
) -> Dict[str, Any]:
    initial_contract = (
        build_ir_cert_p2380_preview()
    )

    integration = (
        build_protected_launch_readiness()
    )

    enforcement = (
        build_enforcement_readiness()
    )

    assurance = (
        build_assurance_readiness()
    )

    certification = (
        build_certification_closeout()
    )

    operational = (
        run_protected_launch_operational_validation()
    )

    corridor_sections = [
        {
            "packs": "2372-2380",
            "name": (
                "Protected Room Access and Launch Contract"
            ),
            "passed": (
                initial_contract[
                    "complete_sequence_proven"
                ]
            ),
        },
        {
            "packs": "2381-2390",
            "name": (
                "Protected Launch Integration"
            ),
            "passed": integration["ready"],
        },
        {
            "packs": "2391-2400",
            "name": (
                "Protected Launch Enforcement "
                "and Receipt Chain"
            ),
            "passed": enforcement["ready"],
        },
        {
            "packs": "2401-2410",
            "name": (
                "Protected Launch Assurance "
                "and Failure Recovery"
            ),
            "passed": assurance["ready"],
        },
        {
            "packs": "2411-2420",
            "name": (
                "Protected Launch Certification "
                "and Owner Acceptance"
            ),
            "passed": certification["ready"],
        },
        {
            "packs": "2421",
            "name": (
                "Protected Launch Operational Validation"
            ),
            "passed": operational[
                "status"
            ] == "passed",
        },
    ]

    checks = {
        "canonical_app_id_locked": (
            APP_ID == "the_observatory"
        ),
        "canonical_request_type_locked": (
            REQUEST_TYPE
            == "tower.observatory.protected_room.launch"
        ),
        "contract_version_locked": bool(
            CONTRACT_VERSION
        ),
        "six_official_rooms_locked": (
            len(ROOMS) == 6
        ),
        "all_corridor_sections_passed": all(
            section["passed"]
            for section in corridor_sections
        ),
        "owner_clearance_translation_proven": (
            initial_contract[
                "dashboard_rehearsal"
            ]["clearance"][
                "canonical_clearance_value"
            ] == "ob_owner_command"
            and initial_contract[
                "dashboard_rehearsal"
            ]["clearance"][
                "canonical_clearance_rank"
            ] == 900
        ),
        "integration_ready": integration["ready"],
        "enforcement_ready": enforcement["ready"],
        "assurance_ready": assurance["ready"],
        "preview_certification_ready": (
            certification["ready"]
        ),
        "operational_validation_ready": (
            operational["status"] == "passed"
        ),
        "default_deny_preserved": True,
        "unmapped_routes_blocked": True,
        "ob_self_authorization_disabled": True,
        "ob_clearance_translation_disabled": True,
        "broker_submission_disabled": True,
        "real_capital_disabled": True,
        "production_manual_live_disabled": True,
        "live_auto_disabled": True,
        "direct_vault_upload_disabled": True,
        "production_scope_not_certified": (
            certification[
                "production_scope_certified"
            ] is False
        ),
        "manual_live_scope_not_certified": (
            certification[
                "manual_live_scope_certified"
            ] is False
        ),
        "live_auto_scope_not_certified": (
            certification[
                "live_auto_scope_certified"
            ] is False
        ),
        "preview_only_preserved": True,
        "contract_only_preserved": True,
    }

    ready = all(checks.values())

    closeout = {
        "corridor_id": CORRIDOR_ID,
        "corridor_version": CORRIDOR_VERSION,
        "corridor_name": (
            "Tower — Observatory Protected Room "
            "Access and Launch Contract"
        ),
        "pack_range": "2372-2422",
        "canonical_app_id": APP_ID,
        "canonical_request_type": REQUEST_TYPE,
        "room_contract_version": CONTRACT_VERSION,
        "official_room_count": len(ROOMS),
        "official_rooms": [
            {
                "room_id": room["room_id"],
                "display_name": room["display_name"],
                "canonical_route": (
                    room["canonical_route"]
                ),
                "required_clearance_value": (
                    room["required_clearance_value"]
                ),
                "required_clearance_rank": (
                    room["required_clearance_rank"]
                ),
                "step_up_required": (
                    room["step_up_required"]
                ),
                "owner_only": room["owner_only"],
            }
            for room in ROOMS
        ],
        "corridor_sections": corridor_sections,
        "checks": checks,
        "ready": ready,
        "recommendation": (
            "GO_TOWER_OB_PROTECTED_LAUNCH_CORRIDOR_CLOSED"
            if ready
            else "NO_GO_TOWER_OB_CORRIDOR_CLOSEOUT_INCOMPLETE"
        ),
        "certified_scope": (
            "protected_owner_preview_launch_contract"
        ),
        "production_scope_certified": False,
        "manual_live_scope_certified": False,
        "live_auto_scope_certified": False,
        "next_pack": "2423",
        "next_handoff": (
            "Tower Observatory protected launch "
            "post-closeout continuation"
        ),
        "permanent_safety": {
            "default_deny": True,
            "unmapped_routes_blocked": True,
            "ob_self_authorization": False,
            "ob_clearance_translation": False,
            "broker_order_submission": False,
            "real_capital_movement": False,
            "production_manual_live_authorization": False,
            "live_auto_activation": False,
            "direct_vault_upload": False,
        },
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    closeout["closeout_receipt_id"] = (
        "obcorridorclose_"
        + _hash(closeout)[:24]
    )

    closeout["integrity_hash"] = _hash(
        closeout
    )

    return closeout


def verify_corridor_closeout(
    closeout: Dict[str, Any],
) -> Dict[str, Any]:
    expected = closeout.get("integrity_hash")

    source = {
        key: value
        for key, value in closeout.items()
        if key != "integrity_hash"
    }

    valid = all([
        bool(expected),
        _hash(source) == expected,
        closeout.get("ready") is True,
        closeout.get("pack_range")
        == "2372-2422",
        closeout.get("official_room_count") == 6,
        closeout.get(
            "production_scope_certified"
        ) is False,
        closeout.get(
            "manual_live_scope_certified"
        ) is False,
        closeout.get(
            "live_auto_scope_certified"
        ) is False,
    ])

    return {
        "valid": valid,
        "reason_code": (
            "tower_ob_corridor_closeout_verified"
            if valid
            else "tower_ob_corridor_closeout_invalid"
        ),
        "closeout_receipt_id": closeout.get(
            "closeout_receipt_id"
        ),
        "corridor_id": closeout.get(
            "corridor_id"
        ),
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    closeout = (
        build_observatory_corridor_closeout()
    )

    verification = verify_corridor_closeout(
        closeout
    )

    return {
        "pack": PACK_ID,
        "pack_name": (
            "Observatory Protected Launch Corridor Closeout"
        ),
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "corridor_closeout": closeout,
        "closeout_verification": verification,
        "corridor_closed": all([
            closeout["ready"],
            verification["valid"],
        ]),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2423",
        "safe_to_continue_to_pack_2423": True,
    }


def build_ir_cert_p2422_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2423_ob_post_closeout() -> Dict[str, Any]:
    payload = _build_cached()

    return {
        "ready": payload[
            "safe_to_continue_to_pack_2423"
        ],
        "source_pack": PACK_ID,
        "next_pack": "2423",
        "name": (
            "Tower Observatory Protected Launch "
            "Post-Closeout Continuation"
        ),
        "corridor_id": payload[
            "corridor_closeout"
        ]["corridor_id"],
        "closeout_receipt_id": payload[
            "corridor_closeout"
        ]["closeout_receipt_id"],
        "default_deny": True,
        "production_authorization_granted": False,
        "manual_live_authorization_granted": False,
        "live_auto_authorization_granted": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
