"""
SEARCHABLE LABEL: TOWER_PACK_2373_OBSERVATORY_ROUTE_ALIAS_CONTRACT

Pack 2373 — Canonical Route and Alias Contract
"""

from __future__ import annotations

import re
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2372 import (
    APP_ALIASES,
    APP_ID,
    REQUEST_TYPE,
    REQUEST_TYPE_ALIASES,
    ROOMS,
)


PACK_ID = "2373"
ENDPOINT = "/tower/ir-cert-v2373.json"


def normalize_app_id(value: str) -> str | None:
    normalized = str(value or "").strip().lower()

    if normalized == APP_ID:
        return APP_ID

    if normalized in APP_ALIASES:
        return APP_ID

    return None


def normalize_request_type(value: str) -> str | None:
    normalized = str(value or "").strip().lower()

    if normalized == REQUEST_TYPE:
        return REQUEST_TYPE

    if normalized in REQUEST_TYPE_ALIASES:
        return REQUEST_TYPE

    return None


def _match_symbol_route(
    incoming_path: str,
    pattern: str,
) -> Dict[str, Any] | None:
    escaped = re.escape(pattern)
    escaped = escaped.replace(
        re.escape("<symbol>"),
        r"(?P<symbol>[A-Za-z0-9.\-]+)",
    )

    match = re.fullmatch(escaped, incoming_path)

    if not match:
        return None

    symbol = match.groupdict().get("symbol")

    return {
        "symbol": symbol.upper() if symbol else None,
    }


def resolve_observatory_route(path: str) -> Dict[str, Any]:
    incoming = str(path or "").strip()

    for room in ROOMS:
        patterns = [
            room["canonical_route"],
            *room["accepted_aliases"],
        ]

        for pattern in patterns:
            if "<symbol>" in pattern:
                object_context = _match_symbol_route(
                    incoming,
                    pattern,
                )

                if object_context is not None:
                    return {
                        "allowed": True,
                        "reason_code": (
                            "ob_route_alias_resolved"
                            if pattern != room["canonical_route"]
                            else "ob_canonical_route_resolved"
                        ),
                        "room_id": room["room_id"],
                        "canonical_route": (
                            room["canonical_route"]
                        ),
                        "canonical_path": (
                            room["launch_destination"].format(
                                symbol=object_context["symbol"]
                            )
                        ),
                        "matched_path": incoming,
                        "matched_pattern": pattern,
                        "object_context": object_context,
                    }

            elif incoming == pattern:
                return {
                    "allowed": True,
                    "reason_code": (
                        "ob_route_alias_resolved"
                        if pattern != room["canonical_route"]
                        else "ob_canonical_route_resolved"
                    ),
                    "room_id": room["room_id"],
                    "canonical_route": room["canonical_route"],
                    "canonical_path": (
                        room["launch_destination"]
                    ),
                    "matched_path": incoming,
                    "matched_pattern": pattern,
                    "object_context": {},
                }

    return {
        "allowed": False,
        "reason_code": "ob_route_unmapped_default_deny",
        "room_id": None,
        "canonical_route": None,
        "canonical_path": None,
        "matched_path": incoming,
        "object_context": {},
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    alias_count = sum(
        len(room["accepted_aliases"])
        for room in ROOMS
    )

    return {
        "pack": PACK_ID,
        "pack_name": "Canonical Route and Alias Contract",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "app_id": APP_ID,
        "supported_request_type": REQUEST_TYPE,
        "canonical_route_count": len(ROOMS),
        "accepted_alias_count": alias_count,
        "default_deny": True,
        "unmapped_reason_code": (
            "ob_route_unmapped_default_deny"
        ),
        "ob_route_guessing_enabled": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2374",
        "safe_to_continue_to_pack_2374": True,
    }


def build_ir_cert_p2373_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2374_ir_cert_p2374() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2374",
        "name": "Owner Clearance Translation Contract",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
