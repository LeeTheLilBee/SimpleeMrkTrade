from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Mapping, Optional
import uuid

from typing import Any, Dict, Iterable, List, Optional

import hashlib

import json

def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

def build_tower_launch_integrity_hash(payload: Dict[str, Any]) -> str:
    if not isinstance(payload, dict):
        raise TypeError('payload must be a dictionary')
    signable = dict(payload)
    for key in ('integrity_hash', 'packet_hash', 'signature'):
        signable.pop(key, None)
    return _sha256_text(_canonical_json(signable))


GP046_CONTRACT_VERSION = 'ob.tower_protected_launch_handoff.v1'

GP046_ROOM_REGISTRY = {'dashboard': {'room_id': 'dashboard', 'display_name': 'Dashboard', 'canonical_route': '/dashboard', 'accepted_aliases': ['/ob/dashboard'], 'requires_symbol': False}, 'market_map': {'room_id': 'market_map', 'display_name': 'Market Map', 'canonical_route': '/market-map', 'accepted_aliases': ['/ob/market-map'], 'requires_symbol': False}, 'symbol_page': {'room_id': 'symbol_page', 'display_name': 'Symbol Page', 'canonical_route': '/symbol/<symbol>', 'accepted_aliases': ['/ob/symbol/<symbol>'], 'requires_symbol': True}, 'trade_center': {'room_id': 'trade_center', 'display_name': 'Trade Center', 'canonical_route': '/trade-center', 'accepted_aliases': ['/ob/trade-center'], 'requires_symbol': False}, 'review_center': {'room_id': 'review_center', 'display_name': 'Review Center', 'canonical_route': '/review-center', 'accepted_aliases': ['/ob/review-center'], 'requires_symbol': False}, 'owner_console': {'room_id': 'owner_console', 'display_name': 'Owner Console', 'canonical_route': '/owner-console', 'accepted_aliases': ['/ob/owner-console'], 'requires_symbol': False}}

NATIVE_CONTRACT_SERVICE_VERSION = (
    "tower-ob-gp046-native-contract-v1"
)

NATIVE_SAFETY_BOUNDARY = {
    "dry_run_only": True,
    "production_manual_live_authorized": False,
    "broker_submission_enabled": False,
    "real_capital_movement_enabled": False,
    "direct_vault_upload_enabled": False,
    "live_auto_locked": True,
}


def _utc_iso(
    value: datetime,
) -> str:
    normalized = value.astimezone(
        timezone.utc
    )

    return (
        normalized.isoformat()
        .replace(
            "+00:00",
            "Z",
        )
    )


def _first_nonempty(
    *values: Any,
) -> Any:
    for value in values:
        if value not in (
            None,
            "",
            [],
            {},
        ):
            return value

    return None


def _resolve_room(
    *,
    legacy_handoff: Mapping[str, Any],
    requested_path: str,
) -> tuple[str, Dict[str, Any]]:
    approved_room_id = str(
        legacy_handoff.get(
            "approved_room_id"
        )
        or legacy_handoff.get(
            "room_id"
        )
        or ""
    ).strip()

    normalized_approved = (
        approved_room_id
        .removeprefix(
            "ob_room_"
        )
    )

    requested_path = str(
        requested_path
        or legacy_handoff.get(
            "canonical_path"
        )
        or legacy_handoff.get(
            "canonical_route"
        )
        or ""
    ).strip()

    for room_id, room in (
        GP046_ROOM_REGISTRY.items()
    ):
        accepted_routes = {
            str(
                room.get(
                    "canonical_route"
                )
                or ""
            ),
            *[
                str(alias)
                for alias
                in (
                    room.get(
                        "accepted_aliases"
                    )
                    or []
                )
            ],
        }

        if (
            room_id
            == approved_room_id
            or room_id
            == normalized_approved
            or requested_path
            in accepted_routes
        ):
            return (
                room_id,
                dict(room),
            )

    raise ValueError(
        "Tower rehearsal room cannot be "
        "resolved through the GP046 registry."
    )


def build_native_gp046_handoff(
    *,
    legacy_handoff: Mapping[str, Any],
    owner_id: str,
    session_id: str,
    requested_path: str,
    mode: str,
    step_up_reference: str,
    mission_account_id: str,
    symbol: str,
    rehearsal_status: str,
    now: Optional[datetime] = None,
    ttl_seconds: int = 300,
    nonce: Optional[str] = None,
) -> Dict[str, Any]:
    if not isinstance(
        legacy_handoff,
        Mapping,
    ):
        raise TypeError(
            "legacy_handoff must be a mapping."
        )

    now = (
        now
        or datetime.now(
            timezone.utc
        )
    )

    if now.tzinfo is None:
        now = now.replace(
            tzinfo=timezone.utc
        )

    if str(
        rehearsal_status
        or ""
    ).strip().lower() != "passed":
        raise ValueError(
            "Tower rehearsal must pass before "
            "a GP046 handoff can be issued."
        )

    owner_id = str(
        owner_id
        or legacy_handoff.get(
            "owner_id"
        )
        or ""
    ).strip()

    session_id = str(
        session_id
        or legacy_handoff.get(
            "session_id"
        )
        or ""
    ).strip()

    step_up_reference = str(
        step_up_reference
        or legacy_handoff.get(
            "step_up_reference"
        )
        or legacy_handoff.get(
            "step_up_ref"
        )
        or ""
    ).strip()

    if not owner_id:
        raise ValueError(
            "owner_id is required."
        )

    if not session_id:
        raise ValueError(
            "session_id is required."
        )

    if not step_up_reference:
        raise ValueError(
            "A verified Tower step-up reference "
            "is required."
        )

    room_id, room = _resolve_room(
        legacy_handoff=legacy_handoff,
        requested_path=requested_path,
    )

    clearance_reference = str(
        _first_nonempty(
            legacy_handoff.get(
                "clearance_decision_reference"
            ),
            legacy_handoff.get(
                "clearance_decision_ref"
            ),
            legacy_handoff.get(
                "decision_ref"
            ),
        )
        or ""
    ).strip()

    if not clearance_reference:
        raise ValueError(
            "Tower clearance-decision reference "
            "is required."
        )

    handoff_id = str(
        legacy_handoff.get(
            "handoff_id"
        )
        or (
            "tower_gp046_handoff_"
            + uuid.uuid4().hex
        )
    ).strip()

    packet = {
        "contract_version": (
            GP046_CONTRACT_VERSION
        ),
        "issuer": "tower",
        "app_id": "observatory",
        "handoff_id": handoff_id,
        "owner_id": owner_id,
        "subject_role": "owner",
        "session_id": session_id,
        "room_id": room_id,
        "canonical_route": (
            room[
                "canonical_route"
            ]
        ),
        "room_parameters": {
            "mission_account_id": str(
                mission_account_id
                or ""
            ).strip(),
            "symbol": str(
                symbol
                or ""
            ).strip().upper(),
        },
        "mode": str(
            mode
            or legacy_handoff.get(
                "mode"
            )
            or "paper"
        ).strip().lower(),
        "clearance_decision_ref": (
            clearance_reference
        ),
        "step_up_ref": (
            step_up_reference
        ),
        "step_up_verified": True,
        "issued_at": _utc_iso(
            now
        ),
        "expires_at": _utc_iso(
            now
            + timedelta(
                seconds=int(
                    ttl_seconds
                )
            )
        ),
        "nonce": str(
            nonce
            or (
                "tower_gp046_nonce_"
                + uuid.uuid4().hex
            )
        ),
        "single_use": True,
        "safety": dict(
            NATIVE_SAFETY_BOUNDARY
        ),
    }

    if not packet[
        "room_parameters"
    ][
        "mission_account_id"
    ]:
        raise ValueError(
            "mission_account_id is required."
        )

    if not packet[
        "room_parameters"
    ][
        "symbol"
    ]:
        raise ValueError(
            "symbol is required."
        )

    packet[
        "integrity_hash"
    ] = (
        build_tower_launch_integrity_hash(
            packet
        )
    )

    return packet


def run_owner_rehearsal(
    *,
    owner_id: str,
    session_id: str,
    requested_path: str,
    mode: str,
    step_up_reference: str,
    mission_account_id: str,
    symbol: str,
) -> Dict[str, Any]:
    from tower.tower_ir_cert_p2380 import (
        run_owner_rehearsal as
        run_legacy_owner_rehearsal,
    )

    legacy_result = (
        run_legacy_owner_rehearsal(
            owner_id=owner_id,
            session_id=session_id,
            requested_path=requested_path,
            mode=mode,
            step_up_reference=(
                step_up_reference
            ),
            mission_account_id=(
                mission_account_id
            ),
            symbol=symbol,
        )
    )

    legacy_handoff = (
        legacy_result.get(
            "launch_handoff"
        )
    )

    native_handoff = (
        build_native_gp046_handoff(
            legacy_handoff=(
                legacy_handoff
            ),
            owner_id=owner_id,
            session_id=session_id,
            requested_path=(
                requested_path
            ),
            mode=mode,
            step_up_reference=(
                step_up_reference
            ),
            mission_account_id=(
                mission_account_id
            ),
            symbol=symbol,
            rehearsal_status=(
                legacy_result.get(
                    "status"
                )
            ),
        )
    )

    result = dict(
        legacy_result
    )

    result[
        "legacy_launch_handoff"
    ] = legacy_handoff

    result[
        "launch_handoff"
    ] = native_handoff

    result[
        "gp046_native_contract"
    ] = True

    result[
        "gp046_contract_version"
    ] = (
        GP046_CONTRACT_VERSION
    )

    result[
        "native_contract_service_version"
    ] = (
        NATIVE_CONTRACT_SERVICE_VERSION
    )

    result[
        "runtime_contract_adapter_required"
    ] = False

    return result
