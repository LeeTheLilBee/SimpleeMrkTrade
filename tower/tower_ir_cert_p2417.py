"""
SEARCHABLE LABEL: TOWER_PACK_2417_OWNER_ACCEPTANCE_RECEIPT

Pack 2417 — Owner Acceptance Receipt
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2417"
ENDPOINT = "/tower/ir-cert-v2417.json"


def _hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def create_owner_acceptance_receipt(
    *,
    owner_id: str,
    decision_draft: Dict[str, Any],
    owner_decision: str,
    decided_at: str,
) -> Dict[str, Any]:
    permitted = {
        "accept_preview_contract",
        "hold_preview_contract",
        "reject_preview_contract",
    }

    normalized = str(owner_decision or "").strip().lower()

    valid = normalized in permitted

    receipt = {
        "owner_id": owner_id,
        "decision_draft_id": decision_draft.get(
            "decision_draft_id"
        ),
        "owner_decision": normalized,
        "decision_valid": valid,
        "decided_at": decided_at,
        "preview_contract_accepted": (
            valid
            and normalized == "accept_preview_contract"
            and decision_draft.get("acceptable") is True
        ),
        "production_authorization_granted": False,
        "manual_live_authorization_granted": False,
        "live_auto_authorization_granted": False,
        "default_deny_preserved": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    receipt["reason_code"] = (
        "tower_ob_preview_contract_owner_accepted"
        if receipt["preview_contract_accepted"]
        else (
            "tower_ob_owner_decision_invalid"
            if not valid
            else "tower_ob_preview_contract_not_accepted"
        )
    )

    receipt["owner_acceptance_receipt_id"] = (
        "obaccept_" + _hash(receipt)[:24]
    )
    receipt["integrity_hash"] = _hash(receipt)

    return receipt


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Owner Acceptance Receipt",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "accepted_decisions": [
            "accept_preview_contract",
            "hold_preview_contract",
            "reject_preview_contract",
        ],
        "production_authorization_granted": False,
        "manual_live_authorization_granted": False,
        "live_auto_authorization_granted": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2418",
        "safe_to_continue_to_pack_2418": True,
    }


def build_ir_cert_p2417_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2418_ir_cert_p2418() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2418",
        "name": "Certification Seal and Integrity Contract",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
