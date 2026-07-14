"""
SEARCHABLE LABEL: TOWER_PACK_2381_PROTECTED_BRIDGE_REQUEST

Pack 2381 — Protected Bridge Request Contract
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
)
from tower.tower_ir_cert_p2373 import (
    normalize_app_id,
    normalize_request_type,
)


PACK_ID = "2381"
ENDPOINT = "/tower/ir-cert-v2381.json"

BRIDGE_REQUEST_VERSION = "tower-ob-bridge-request-v1.0.0"


def _reference(prefix: str, payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return prefix + hashlib.sha256(encoded).hexdigest()[:24]


def build_protected_bridge_request(
    *,
    request_id: str,
    requester_id: str,
    session_id: str,
    app_id: str,
    request_type: str,
    requested_path: str,
    requested_mode: str,
    tower_role: str,
    object_context: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    canonical_app_id = normalize_app_id(app_id)
    canonical_request_type = normalize_request_type(
        request_type
    )

    request = {
        "request_id": request_id,
        "requester_id": requester_id,
        "session_id": session_id,
        "app_id": canonical_app_id,
        "request_type": canonical_request_type,
        "requested_path": requested_path,
        "requested_mode": requested_mode,
        "tower_role": tower_role,
        "object_context": deepcopy(object_context or {}),
        "bridge_request_version": BRIDGE_REQUEST_VERSION,
        "room_contract_version": CONTRACT_VERSION,
        "default_deny": True,
        "ob_self_authorization": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    errors = []

    if canonical_app_id != APP_ID:
        errors.append("ob_app_id_not_supported")

    if canonical_request_type != REQUEST_TYPE:
        errors.append("ob_request_type_not_supported")

    if not requester_id:
        errors.append("ob_identity_missing")

    if not session_id:
        errors.append("tower_session_missing")

    if not requested_path:
        errors.append("ob_requested_path_missing")

    request["valid"] = not errors
    request["reason_code"] = (
        "tower_ob_bridge_request_valid"
        if not errors
        else errors[0]
    )
    request["validation_errors"] = errors
    request["request_integrity_reference"] = _reference(
        "obreq_",
        request,
    )

    return request


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    preview = build_protected_bridge_request(
        request_id="request_preview",
        requester_id="owner_preview",
        session_id="session_preview",
        app_id="ob",
        request_type="ob.protected_room.launch",
        requested_path="/dashboard",
        requested_mode="paper",
        tower_role="owner",
    )

    return {
        "pack": PACK_ID,
        "pack_name": "Protected Bridge Request Contract",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "bridge_request_version": BRIDGE_REQUEST_VERSION,
        "canonical_app_id": APP_ID,
        "canonical_request_type": REQUEST_TYPE,
        "preview_request": preview,
        "default_deny": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2382",
        "safe_to_continue_to_pack_2382": True,
    }


def build_ir_cert_p2381_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2382_ir_cert_p2382() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2382",
        "name": "Pack 101 Bridge Adapter",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
