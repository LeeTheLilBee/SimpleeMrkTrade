"""
SEARCHABLE LABEL: TOWER_PACK_2374_OWNER_CLEARANCE_TRANSLATION

Pack 2374 — Owner Clearance Translation Contract

Tower owns translation. OB receives only canonical clearance.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2374"
ENDPOINT = "/tower/ir-cert-v2374.json"

TRANSLATION_CONTRACT_VERSION = (
    "tower-ob-clearance-translation-v1.0.0"
)

ROLE_TRANSLATIONS = {
    "owner": {
        "canonical_clearance_value": "ob_owner_command",
        "canonical_clearance_rank": 900,
        "reason_code": (
            "tower_owner_role_translated_to_ob_owner_command"
        ),
    },
    "authorized_operator": {
        "canonical_clearance_value": (
            "ob_protected_workflow"
        ),
        "canonical_clearance_rank": 500,
        "reason_code": (
            "tower_operator_role_translated_to_ob_workflow"
        ),
    },
    "authorized_observer": {
        "canonical_clearance_value": "ob_protected_read",
        "canonical_clearance_rank": 300,
        "reason_code": (
            "tower_observer_role_translated_to_ob_read"
        ),
    },
}


def _decision_reference(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return "obclr_" + hashlib.sha256(encoded).hexdigest()[:24]


def translate_tower_clearance(
    *,
    subject_id: str,
    tower_role: str,
    identity_verified: bool,
    account_active: bool,
    risk_state: str,
    lockdown_state: str,
) -> Dict[str, Any]:
    role = str(tower_role or "").strip().lower()

    base = {
        "subject_id": subject_id,
        "tower_role": role,
        "identity_verified": bool(identity_verified),
        "account_active": bool(account_active),
        "risk_state": risk_state,
        "lockdown_state": lockdown_state,
        "contract_version": TRANSLATION_CONTRACT_VERSION,
        "preview_only": True,
        "writes_state": False,
    }

    if not identity_verified:
        result = {
            **base,
            "allowed": False,
            "reason_code": "ob_identity_missing",
            "canonical_clearance_value": None,
            "canonical_clearance_rank": 0,
        }

    elif not account_active:
        result = {
            **base,
            "allowed": False,
            "reason_code": "tower_account_not_active",
            "canonical_clearance_value": None,
            "canonical_clearance_rank": 0,
        }

    elif risk_state != "acceptable":
        result = {
            **base,
            "allowed": False,
            "reason_code": "ob_risk_gate_denied",
            "canonical_clearance_value": None,
            "canonical_clearance_rank": 0,
        }

    elif lockdown_state not in {
        "normal",
        "tower_guarded_default_deny",
    }:
        result = {
            **base,
            "allowed": False,
            "reason_code": "ob_lockdown_active",
            "canonical_clearance_value": None,
            "canonical_clearance_rank": 0,
        }

    elif role not in ROLE_TRANSLATIONS:
        result = {
            **base,
            "allowed": False,
            "reason_code": (
                "tower_role_has_no_ob_clearance_translation"
            ),
            "canonical_clearance_value": None,
            "canonical_clearance_rank": 0,
        }

    else:
        translated = ROLE_TRANSLATIONS[role]

        result = {
            **base,
            "allowed": True,
            **translated,
        }

    result["clearance_decision_reference"] = (
        _decision_reference(result)
    )

    return result


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    owner_example = translate_tower_clearance(
        subject_id="owner_preview",
        tower_role="owner",
        identity_verified=True,
        account_active=True,
        risk_state="acceptable",
        lockdown_state="tower_guarded_default_deny",
    )

    return {
        "pack": PACK_ID,
        "pack_name": "Owner Clearance Translation Contract",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "translation_contract_version": (
            TRANSLATION_CONTRACT_VERSION
        ),
        "accepted_tower_roles": sorted(
            ROLE_TRANSLATIONS
        ),
        "owner_translation": owner_example,
        "raw_owner_string_is_ob_clearance": False,
        "owner_role_policy_lowered": False,
        "tower_translation_required": True,
        "ob_translation_enabled": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2375",
        "safe_to_continue_to_pack_2375": True,
    }


def build_ir_cert_p2374_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2375_ir_cert_p2375() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2375",
        "name": "Step-Up Room Access Matrix",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
