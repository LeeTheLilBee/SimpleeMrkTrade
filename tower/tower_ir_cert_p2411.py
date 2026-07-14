"""
SEARCHABLE LABEL: TOWER_PACK_2411_PROTECTED_LAUNCH_EVIDENCE_BUNDLE

Pack 2411 — Protected Launch Evidence Bundle
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2389 import (
    run_six_room_protected_rehearsal,
)
from tower.tower_ir_cert_p2399 import (
    run_six_room_enforcement_rehearsal,
)
from tower.tower_ir_cert_p2408 import (
    run_six_room_failure_rehearsal,
)


PACK_ID = "2411"
ENDPOINT = "/tower/ir-cert-v2411.json"


def _hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def build_protected_launch_evidence_bundle() -> Dict[str, Any]:
    integration = run_six_room_protected_rehearsal()
    enforcement = run_six_room_enforcement_rehearsal()
    failure = run_six_room_failure_rehearsal()

    evidence = {
        "integration_rehearsal_status": integration["status"],
        "integration_room_count": integration["room_count"],
        "enforcement_rehearsal_status": enforcement["status"],
        "enforcement_room_count": enforcement["room_count"],
        "failure_rehearsal_status": failure["status"],
        "failure_room_count": failure["room_count"],
        "default_deny_proven": all([
            integration["default_deny_passed"],
            enforcement["default_deny_restored"],
            failure["all_default_deny_restored"],
        ]),
        "replay_blocking_proven": (
            enforcement["replay_blocking_passed"]
        ),
        "receipt_chain_proven": (
            enforcement["receipt_chain_passed"]
        ),
        "failure_recovery_proven": (
            failure["all_sessions_locked_back"]
            and failure["all_new_handoffs_required"]
        ),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    evidence["evidence_bundle_id"] = (
        "obevidence_" + _hash(evidence)[:24]
    )
    evidence["integrity_hash"] = _hash(evidence)

    return evidence


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    bundle = build_protected_launch_evidence_bundle()

    return {
        "pack": PACK_ID,
        "pack_name": "Protected Launch Evidence Bundle",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "evidence_bundle": bundle,
        "evidence_complete": all([
            bundle["integration_rehearsal_status"] == "passed",
            bundle["enforcement_rehearsal_status"] == "passed",
            bundle["failure_rehearsal_status"] == "passed",
            bundle["default_deny_proven"],
            bundle["replay_blocking_proven"],
            bundle["receipt_chain_proven"],
            bundle["failure_recovery_proven"],
        ]),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2412",
        "safe_to_continue_to_pack_2412": True,
    }


def build_ir_cert_p2411_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2412_ir_cert_p2412() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2412",
        "name": "Contract Version Pin and Compatibility Gate",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
