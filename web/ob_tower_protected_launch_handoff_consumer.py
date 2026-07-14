
"""OB GP046 — Tower Protected Launch Handoff Consumer.

Tower remains the authority for identity, clearance, step-up, room mapping,
launch approval, revocation and lockback.

This module only validates, records and consumes Tower-issued rehearsal
handoffs. It cannot grant Tower clearance or production Manual Live authority.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import tempfile


OB_GIANT_PACK_046_TOWER_PROTECTED_LAUNCH_HANDOFF_CONSUMER_SERVICE = True

PACK = "GP046"
CONTRACT_VERSION = "ob.tower_protected_launch_handoff.v1"
CANONICAL_ISSUER = "tower"
DEFAULT_CANONICAL_APP_ID = "observatory"
MAX_HANDOFF_TTL_SECONDS = 15 * 60
CLOCK_SKEW_SECONDS = 60
ZERO_HASH = "0" * 64

ROOM_REGISTRY: Dict[str, Dict[str, Any]] = {
    "dashboard": {
        "room_id": "dashboard",
        "display_name": "Dashboard",
        "canonical_route": "/dashboard",
        "accepted_aliases": [
            "/ob/dashboard",
        ],
        "requires_symbol": False,
    },
    "market_map": {
        "room_id": "market_map",
        "display_name": "Market Map",
        "canonical_route": "/market-map",
        "accepted_aliases": [
            "/ob/market-map",
        ],
        "requires_symbol": False,
    },
    "symbol_page": {
        "room_id": "symbol_page",
        "display_name": "Symbol Page",
        "canonical_route": "/symbol/<symbol>",
        "accepted_aliases": [
            "/ob/symbol/<symbol>",
        ],
        "requires_symbol": True,
    },
    "trade_center": {
        "room_id": "trade_center",
        "display_name": "Trade Center",
        "canonical_route": "/trade-center",
        "accepted_aliases": [
            "/ob/trade-center",
        ],
        "requires_symbol": False,
    },
    "review_center": {
        "room_id": "review_center",
        "display_name": "Review Center",
        "canonical_route": "/review-center",
        "accepted_aliases": [
            "/ob/review-center",
        ],
        "requires_symbol": False,
    },
    "owner_console": {
        "room_id": "owner_console",
        "display_name": "Owner Console",
        "canonical_route": "/owner-console",
        "accepted_aliases": [
            "/ob/owner-console",
        ],
        "requires_symbol": False,
    },
}

ALLOWED_MODES = {
    "survey",
    "paper",
    "manual_live",
}

FORBIDDEN_SECRET_KEYS = {
    "password",
    "secret",
    "access_token",
    "refresh_token",
    "api_key",
    "private_key",
    "raw_file_url",
    "broker_token",
    "broker_secret",
}

SAFETY_REQUIREMENTS = {
    "dry_run_only": True,
    "production_manual_live_authorized": False,
    "broker_submission_enabled": False,
    "real_capital_movement_enabled": False,
    "direct_vault_upload_enabled": False,
    "live_auto_locked": True,
}


def _default_database_path() -> Path:
    configured = (
        os.environ.get("OB_TOWER_LAUNCH_DB_PATH")
        or os.environ.get("OB_DRY_RUN_DB_PATH")
    )

    if configured:
        return Path(configured).expanduser().resolve()

    return (
        Path(tempfile.gettempdir())
        / "ob_tower_protected_launch_gp046.sqlite3"
    )


def _database_path(path: Optional[Any] = None) -> Path:
    if path is None:
        return _default_database_path()

    return Path(path).expanduser().resolve()


def _connect(path: Optional[Any] = None) -> sqlite3.Connection:
    database = _database_path(path)
    database.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        str(database),
        timeout=30,
    )

    connection.row_factory = sqlite3.Row
    connection.execute(
        "PRAGMA foreign_keys = ON"
    )
    connection.execute(
        "PRAGMA journal_mode = WAL"
    )

    return connection


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _json_text(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        default=str,
    )


def _sha256_text(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def _iso(value: datetime) -> str:
    return (
        value.astimezone(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _parse_time(value: Any) -> datetime:
    if isinstance(value, datetime):
        parsed = value

    elif isinstance(value, str):
        rendered = value.strip()

        if rendered.endswith("Z"):
            rendered = (
                rendered[:-1]
                + "+00:00"
            )

        parsed = datetime.fromisoformat(
            rendered
        )

    else:
        raise ValueError(
            "timestamp must be an ISO string"
        )

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=timezone.utc
        )

    return parsed.astimezone(
        timezone.utc
    )


def _now(value: Optional[Any] = None) -> datetime:
    if value is None:
        return datetime.now(
            timezone.utc
        )

    return _parse_time(value)


def _unique(values: Iterable[str]) -> List[str]:
    output: List[str] = []
    seen = set()

    for value in values:
        rendered = str(value or "").strip()

        if not rendered:
            continue

        if rendered in seen:
            continue

        seen.add(rendered)
        output.append(rendered)

    return output


def _accepted_app_ids() -> set:
    configured = os.environ.get(
        "OB_TOWER_ACCEPTED_APP_IDS",
        "",
    )

    values = {
        DEFAULT_CANONICAL_APP_ID,
        "the_observatory",
        "simplee_observatory",
    }

    values.update(
        item.strip()
        for item in configured.split(",")
        if item.strip()
    )

    # "ob" remains intentionally excluded. Pack 101 rejected that alias.
    return {
        value.lower()
        for value in values
    }


def room_registry_payload() -> Dict[str, Any]:
    rooms = []

    for room in ROOM_REGISTRY.values():
        rooms.append(
            {
                **room,
                "allowed_modes": sorted(
                    ALLOWED_MODES
                ),
                "tower_authority_required": True,
                "ob_self_authorization_allowed": False,
            }
        )

    return {
        "ok": True,
        "pack": PACK,
        "contract_version": CONTRACT_VERSION,
        "canonical_app_id": (
            DEFAULT_CANONICAL_APP_ID
        ),
        "rooms": rooms,
        "room_count": len(rooms),
        "tower_maps_routes": True,
        "ob_validates_only": True,
        "production_manual_live_authorized": False,
        "live_auto_locked": True,
    }


def _find_forbidden_secret_keys(
    value: Any,
    prefix: str = "",
) -> List[str]:
    findings: List[str] = []

    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            lowered = key_text.lower()
            location = (
                f"{prefix}.{key_text}"
                if prefix
                else key_text
            )

            if lowered in FORBIDDEN_SECRET_KEYS:
                if item not in (
                    None,
                    "",
                    [],
                    {},
                ):
                    findings.append(
                        location
                    )

            findings.extend(
                _find_forbidden_secret_keys(
                    item,
                    location,
                )
            )

    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(
                _find_forbidden_secret_keys(
                    item,
                    (
                        f"{prefix}[{index}]"
                        if prefix
                        else f"[{index}]"
                    ),
                )
            )

    return findings


def _normalize_safety(
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    source = dict(
        payload.get("safety")
        or {}
    )

    def first(*keys: str) -> Any:
        for key in keys:
            if key in source:
                return source[key]

            if key in payload:
                return payload[key]

        return None

    live_auto_locked = first(
        "live_auto_locked"
    )

    if live_auto_locked is None:
        live_auto_enabled = first(
            "live_auto_enabled"
        )

        if live_auto_enabled is not None:
            live_auto_locked = (
                not bool(
                    live_auto_enabled
                )
            )

    broker_submission = first(
        "broker_submission_enabled",
        "broker_order_submission_enabled",
    )

    return {
        "dry_run_only": first(
            "dry_run_only"
        ),
        "production_manual_live_authorized": first(
            "production_manual_live_authorized"
        ),
        "broker_submission_enabled": (
            broker_submission
        ),
        "real_capital_movement_enabled": first(
            "real_capital_movement_enabled",
            "capital_movement_enabled",
        ),
        "direct_vault_upload_enabled": first(
            "direct_vault_upload_enabled"
        ),
        "live_auto_locked": (
            live_auto_locked
        ),
    }


def _normalize_packet(
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    step_up = payload.get(
        "step_up"
    )

    if not isinstance(step_up, dict):
        step_up = {}

    clearance = payload.get(
        "clearance"
    )

    if not isinstance(clearance, dict):
        clearance = {}

    room_parameters = payload.get(
        "room_parameters"
    )

    if not isinstance(
        room_parameters,
        dict,
    ):
        room_parameters = {}

    return {
        "contract_version": str(
            payload.get(
                "contract_version"
            )
            or ""
        ).strip(),
        "issuer": str(
            payload.get("issuer")
            or payload.get("issued_by")
            or ""
        ).strip(),
        "app_id": str(
            payload.get("app_id")
            or payload.get("application_id")
            or ""
        ).strip(),
        "handoff_id": str(
            payload.get("handoff_id")
            or payload.get("launch_handoff_id")
            or ""
        ).strip(),
        "owner_id": str(
            payload.get("owner_id")
            or payload.get("subject_id")
            or payload.get("user_id")
            or ""
        ).strip(),
        "subject_role": str(
            payload.get("subject_role")
            or payload.get("role")
            or ""
        ).strip(),
        "session_id": str(
            payload.get("session_id")
            or ""
        ).strip(),
        "room_id": str(
            payload.get("room_id")
            or ""
        ).strip(),
        "canonical_route": str(
            payload.get("canonical_route")
            or payload.get("route_path")
            or ""
        ).strip(),
        "room_parameters": (
            room_parameters
        ),
        "mode": str(
            payload.get("mode")
            or ""
        ).strip(),
        "clearance_decision_ref": str(
            payload.get(
                "clearance_decision_ref"
            )
            or payload.get(
                "clearance_reference"
            )
            or clearance.get(
                "decision_ref"
            )
            or clearance.get(
                "reference"
            )
            or ""
        ).strip(),
        "step_up_ref": str(
            payload.get("step_up_ref")
            or payload.get(
                "step_up_reference"
            )
            or payload.get(
                "challenge_id"
            )
            or step_up.get(
                "challenge_id"
            )
            or step_up.get(
                "reference"
            )
            or ""
        ).strip(),
        "step_up_verified": bool(
            payload.get(
                "step_up_verified",
                step_up.get(
                    "verified",
                    False,
                ),
            )
        ),
        "issued_at": str(
            payload.get("issued_at")
            or ""
        ).strip(),
        "expires_at": str(
            payload.get("expires_at")
            or ""
        ).strip(),
        "nonce": str(
            payload.get("nonce")
            or ""
        ).strip(),
        "single_use": payload.get(
            "single_use"
        ),
        "integrity_hash": str(
            payload.get(
                "integrity_hash"
            )
            or payload.get(
                "packet_hash"
            )
            or ""
        ).strip(),
        "signature": str(
            payload.get("signature")
            or ""
        ).strip(),
        "safety": _normalize_safety(
            payload
        ),
    }


def build_tower_launch_integrity_hash(
    payload: Dict[str, Any],
) -> str:
    if not isinstance(payload, dict):
        raise TypeError(
            "payload must be a dictionary"
        )

    signable = dict(payload)

    for key in (
        "integrity_hash",
        "packet_hash",
        "signature",
    ):
        signable.pop(
            key,
            None,
        )

    return _sha256_text(
        _canonical_json(
            signable
        )
    )


def build_tower_launch_signature(
    payload: Dict[str, Any],
    secret: str,
) -> str:
    packet_hash = (
        build_tower_launch_integrity_hash(
            payload
        )
    )

    return hmac.new(
        str(secret).encode(
            "utf-8"
        ),
        packet_hash.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).hexdigest()


def validate_tower_protected_launch_handoff(
    payload: Dict[str, Any],
    *,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    reasons: List[str] = []

    if not isinstance(payload, dict):
        return {
            "valid": False,
            "reason_codes": [
                "payload_must_be_object"
            ],
            "normalized_packet": {},
            "computed_integrity_hash": None,
            "authenticity_mode": (
                "not_evaluated"
            ),
        }

    normalized = _normalize_packet(
        payload
    )

    required_fields = [
        "contract_version",
        "issuer",
        "app_id",
        "handoff_id",
        "owner_id",
        "subject_role",
        "session_id",
        "room_id",
        "canonical_route",
        "mode",
        "clearance_decision_ref",
        "step_up_ref",
        "issued_at",
        "expires_at",
        "nonce",
        "integrity_hash",
    ]

    for field in required_fields:
        if not normalized.get(field):
            reasons.append(
                f"missing_{field}"
            )

    if (
        normalized.get(
            "contract_version"
        )
        and normalized[
            "contract_version"
        ] != CONTRACT_VERSION
    ):
        reasons.append(
            "unsupported_contract_version"
        )

    if (
        normalized.get("issuer")
        and normalized[
            "issuer"
        ].lower()
        != CANONICAL_ISSUER
    ):
        reasons.append(
            "unsupported_issuer"
        )

    if (
        normalized.get("app_id")
        and normalized[
            "app_id"
        ].lower()
        not in _accepted_app_ids()
    ):
        reasons.append(
            "unsupported_app_id"
        )

    if (
        normalized.get(
            "subject_role"
        )
        and normalized[
            "subject_role"
        ].lower()
        != "owner"
    ):
        reasons.append(
            "owner_rehearsal_role_required"
        )

    room = ROOM_REGISTRY.get(
        normalized.get(
            "room_id",
            ""
        )
    )

    if room is None:
        reasons.append(
            "unknown_room_id"
        )

    else:
        accepted_routes = {
            room["canonical_route"],
            *room[
                "accepted_aliases"
            ],
        }

        if (
            normalized.get(
                "canonical_route"
            )
            not in accepted_routes
        ):
            reasons.append(
                "room_route_mismatch"
            )

        if room[
            "requires_symbol"
        ]:
            symbol = str(
                normalized[
                    "room_parameters"
                ].get("symbol")
                or ""
            ).strip().upper()

            if not re.fullmatch(
                r"[A-Z][A-Z0-9.\-]{0,14}",
                symbol,
            ):
                reasons.append(
                    "valid_symbol_required"
                )

    if (
        normalized.get("mode")
        and normalized["mode"]
        not in ALLOWED_MODES
    ):
        reasons.append(
            "unsupported_mode"
        )

    if not normalized.get(
        "step_up_verified"
    ):
        reasons.append(
            "step_up_not_verified"
        )

    if normalized.get(
        "single_use"
    ) is not True:
        reasons.append(
            "single_use_required"
        )

    current_time = _now(now)
    issued_at = None
    expires_at = None

    try:
        issued_at = _parse_time(
            normalized.get(
                "issued_at"
            )
        )

    except Exception:
        if normalized.get(
            "issued_at"
        ):
            reasons.append(
                "invalid_issued_at"
            )

    try:
        expires_at = _parse_time(
            normalized.get(
                "expires_at"
            )
        )

    except Exception:
        if normalized.get(
            "expires_at"
        ):
            reasons.append(
                "invalid_expires_at"
            )

    if issued_at is not None:
        if (
            issued_at.timestamp()
            > current_time.timestamp()
            + CLOCK_SKEW_SECONDS
        ):
            reasons.append(
                "issued_at_in_future"
            )

    if expires_at is not None:
        if (
            expires_at.timestamp()
            <= current_time.timestamp()
        ):
            reasons.append(
                "handoff_expired"
            )

    if (
        issued_at is not None
        and expires_at is not None
    ):
        ttl = (
            expires_at - issued_at
        ).total_seconds()

        if ttl <= 0:
            reasons.append(
                "invalid_handoff_window"
            )

        elif ttl > MAX_HANDOFF_TTL_SECONDS:
            reasons.append(
                "handoff_ttl_too_long"
            )

    nonce = normalized.get(
        "nonce",
        ""
    )

    if nonce and not re.fullmatch(
        r"[A-Za-z0-9_.:\-]{16,200}",
        nonce,
    ):
        reasons.append(
            "invalid_nonce"
        )

    for key, expected in (
        SAFETY_REQUIREMENTS.items()
    ):
        actual = normalized[
            "safety"
        ].get(key)

        if actual is not expected:
            reasons.append(
                f"unsafe_{key}"
            )

    forbidden = (
        _find_forbidden_secret_keys(
            payload
        )
    )

    if forbidden:
        reasons.append(
            "secret_material_forbidden"
        )

    computed_hash = None

    try:
        computed_hash = (
            build_tower_launch_integrity_hash(
                payload
            )
        )

    except Exception:
        reasons.append(
            "packet_not_canonical_json"
        )

    supplied_hash = normalized.get(
        "integrity_hash"
    )

    if supplied_hash:
        if not re.fullmatch(
            r"[a-fA-F0-9]{64}",
            supplied_hash,
        ):
            reasons.append(
                "invalid_integrity_hash_format"
            )

        elif (
            computed_hash
            and not hmac.compare_digest(
                supplied_hash.lower(),
                computed_hash.lower(),
            )
        ):
            reasons.append(
                "integrity_hash_mismatch"
            )

    hmac_secret = os.environ.get(
        "OB_TOWER_LAUNCH_HMAC_SECRET"
    )

    authenticity_mode = (
        "rehearsal_hash_only"
    )

    if hmac_secret:
        authenticity_mode = (
            "environment_hmac_sha256"
        )

        supplied_signature = (
            normalized.get(
                "signature"
            )
        )

        if not supplied_signature:
            reasons.append(
                "missing_tower_signature"
            )

        else:
            expected_signature = (
                build_tower_launch_signature(
                    payload,
                    hmac_secret,
                )
            )

            if not hmac.compare_digest(
                supplied_signature.lower(),
                expected_signature.lower(),
            ):
                reasons.append(
                    "tower_signature_mismatch"
                )

    return {
        "valid": not bool(reasons),
        "reason_codes": _unique(
            reasons
        ),
        "normalized_packet": (
            normalized
        ),
        "computed_integrity_hash": (
            computed_hash
        ),
        "authenticity_mode": (
            authenticity_mode
        ),
        "tower_authenticity_proven": bool(
            hmac_secret
            and not any(
                reason
                in {
                    "missing_tower_signature",
                    "tower_signature_mismatch",
                }
                for reason in reasons
            )
        ),
        "production_authority_granted": False,
    }


def init_launch_database(
    path: Optional[Any] = None,
) -> str:
    database = _database_path(
        path
    )

    with _connect(database) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS
            ob_tower_launch_intakes (
                intake_id TEXT PRIMARY KEY,
                handoff_id TEXT NOT NULL,
                nonce TEXT,
                packet_hash TEXT NOT NULL,
                integrity_hash TEXT,
                decision TEXT NOT NULL,
                reason_codes_json TEXT NOT NULL,
                owner_id TEXT,
                session_id TEXT,
                room_id TEXT,
                canonical_route TEXT,
                mode TEXT,
                issued_at TEXT,
                expires_at TEXT,
                raw_payload_json TEXT NOT NULL,
                normalized_packet_json TEXT NOT NULL,
                authenticity_mode TEXT NOT NULL,
                tower_authenticity_proven INTEGER NOT NULL,
                previous_hash TEXT NOT NULL,
                record_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                consumed_at TEXT,
                consumption_hash TEXT
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_tower_launch_created
            ON ob_tower_launch_intakes(
                created_at
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_tower_launch_decision
            ON ob_tower_launch_intakes(
                decision
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_tower_launch_handoff
            ON ob_tower_launch_intakes(
                handoff_id
            );

            CREATE TABLE IF NOT EXISTS
            ob_tower_launch_nonce_registry (
                nonce TEXT PRIMARY KEY,
                packet_hash TEXT NOT NULL,
                intake_id TEXT NOT NULL,
                registered_at TEXT NOT NULL,
                FOREIGN KEY(intake_id)
                    REFERENCES ob_tower_launch_intakes(
                        intake_id
                    )
            );
            """
        )

    return str(database)


def _latest_record_hash(
    connection: sqlite3.Connection,
) -> str:
    row = connection.execute(
        """
        SELECT record_hash
        FROM ob_tower_launch_intakes
        ORDER BY rowid DESC
        LIMIT 1
        """
    ).fetchone()

    if row is None:
        return ZERO_HASH

    return str(
        row["record_hash"]
    )


def _public_record(
    row: sqlite3.Row,
) -> Dict[str, Any]:
    normalized = json.loads(
        row[
            "normalized_packet_json"
        ]
    )

    reasons = json.loads(
        row[
            "reason_codes_json"
        ]
    )

    return {
        "intake_id": row[
            "intake_id"
        ],
        "handoff_id": row[
            "handoff_id"
        ],
        "nonce": row["nonce"],
        "packet_hash": row[
            "packet_hash"
        ],
        "integrity_hash": row[
            "integrity_hash"
        ],
        "decision": row[
            "decision"
        ],
        "accepted": (
            row["decision"]
            == "accepted"
        ),
        "reason_codes": reasons,
        "owner_id": row[
            "owner_id"
        ],
        "session_id": row[
            "session_id"
        ],
        "room_id": row[
            "room_id"
        ],
        "canonical_route": row[
            "canonical_route"
        ],
        "mode": row["mode"],
        "issued_at": row[
            "issued_at"
        ],
        "expires_at": row[
            "expires_at"
        ],
        "normalized_packet": (
            normalized
        ),
        "authenticity_mode": row[
            "authenticity_mode"
        ],
        "tower_authenticity_proven": bool(
            row[
                "tower_authenticity_proven"
            ]
        ),
        "previous_hash": row[
            "previous_hash"
        ],
        "record_hash": row[
            "record_hash"
        ],
        "created_at": row[
            "created_at"
        ],
        "consumed_at": row[
            "consumed_at"
        ],
        "consumed": bool(
            row["consumed_at"]
        ),
        "consumption_hash": row[
            "consumption_hash"
        ],
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
    }


def get_tower_protected_launch_handoff(
    intake_id: str,
    *,
    path: Optional[Any] = None,
) -> Optional[Dict[str, Any]]:
    init_launch_database(
        path
    )

    with _connect(path) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_tower_launch_intakes
            WHERE intake_id = ?
            """,
            (
                str(intake_id),
            ),
        ).fetchone()

    if row is None:
        return None

    return _public_record(
        row
    )


def list_tower_protected_launch_handoffs(
    *,
    decision: Optional[str] = None,
    limit: int = 100,
    path: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    init_launch_database(
        path
    )

    limit = max(
        1,
        min(
            int(limit),
            500,
        ),
    )

    query = """
        SELECT *
        FROM ob_tower_launch_intakes
    """

    parameters: List[Any] = []

    if decision:
        query += """
            WHERE decision = ?
        """

        parameters.append(
            str(decision)
        )

    query += """
        ORDER BY rowid DESC
        LIMIT ?
    """

    parameters.append(
        limit
    )

    with _connect(path) as connection:
        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

    return [
        _public_record(row)
        for row in rows
    ]


def _record_hash_material(
    record: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "intake_id": record[
            "intake_id"
        ],
        "handoff_id": record[
            "handoff_id"
        ],
        "nonce": record[
            "nonce"
        ],
        "packet_hash": record[
            "packet_hash"
        ],
        "integrity_hash": record[
            "integrity_hash"
        ],
        "decision": record[
            "decision"
        ],
        "reason_codes": record[
            "reason_codes"
        ],
        "owner_id": record[
            "owner_id"
        ],
        "session_id": record[
            "session_id"
        ],
        "room_id": record[
            "room_id"
        ],
        "canonical_route": record[
            "canonical_route"
        ],
        "mode": record[
            "mode"
        ],
        "issued_at": record[
            "issued_at"
        ],
        "expires_at": record[
            "expires_at"
        ],
        "raw_payload": record[
            "raw_payload"
        ],
        "normalized_packet": record[
            "normalized_packet"
        ],
        "authenticity_mode": record[
            "authenticity_mode"
        ],
        "tower_authenticity_proven": record[
            "tower_authenticity_proven"
        ],
        "previous_hash": record[
            "previous_hash"
        ],
        "created_at": record[
            "created_at"
        ],
    }


def intake_tower_protected_launch_handoff(
    payload: Dict[str, Any],
    *,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_launch_database(
        database
    )

    current_time = _now(
        now
    )

    validation = (
        validate_tower_protected_launch_handoff(
            payload,
            now=current_time,
        )
    )

    normalized = validation[
        "normalized_packet"
    ]

    packet_hash = (
        validation.get(
            "computed_integrity_hash"
        )
        or _sha256_text(
            _json_text(payload)
        )
    )

    nonce = str(
        normalized.get("nonce")
        or ""
    )

    with _connect(database) as connection:
        if nonce:
            existing_nonce = (
                connection.execute(
                    """
                    SELECT
                        nonce,
                        packet_hash,
                        intake_id
                    FROM ob_tower_launch_nonce_registry
                    WHERE nonce = ?
                    """,
                    (
                        nonce,
                    ),
                ).fetchone()
            )

            if existing_nonce is not None:
                if hmac.compare_digest(
                    str(
                        existing_nonce[
                            "packet_hash"
                        ]
                    ),
                    packet_hash,
                ):
                    existing = (
                        get_tower_protected_launch_handoff(
                            existing_nonce[
                                "intake_id"
                            ],
                            path=database,
                        )
                    )

                    return {
                        "ok": bool(
                            existing
                            and existing[
                                "accepted"
                            ]
                        ),
                        "created": False,
                        "idempotent": True,
                        "decision": (
                            existing[
                                "decision"
                            ]
                            if existing
                            else "denied"
                        ),
                        "intake": existing,
                        "reason_codes": (
                            existing[
                                "reason_codes"
                            ]
                            if existing
                            else [
                                "existing_intake_missing"
                            ]
                        ),
                    }

                validation[
                    "reason_codes"
                ] = _unique(
                    [
                        *validation[
                            "reason_codes"
                        ],
                        "nonce_replay_conflict",
                    ]
                )

                validation[
                    "valid"
                ] = False

        decision = (
            "accepted"
            if validation[
                "valid"
            ]
            else "denied"
        )

        created_at = _iso(
            current_time
        )

        intake_id = (
            "ob_launch_"
            + secrets.token_urlsafe(
                18
            ).replace(
                "-",
                "",
            ).replace(
                "_",
                "",
            )
        )

        previous_hash = (
            _latest_record_hash(
                connection
            )
        )

        record = {
            "intake_id": intake_id,
            "handoff_id": str(
                normalized.get(
                    "handoff_id"
                )
                or "missing"
            ),
            "nonce": (
                nonce
                or None
            ),
            "packet_hash": (
                packet_hash
            ),
            "integrity_hash": (
                normalized.get(
                    "integrity_hash"
                )
                or None
            ),
            "decision": decision,
            "reason_codes": (
                validation[
                    "reason_codes"
                ]
            ),
            "owner_id": (
                normalized.get(
                    "owner_id"
                )
                or None
            ),
            "session_id": (
                normalized.get(
                    "session_id"
                )
                or None
            ),
            "room_id": (
                normalized.get(
                    "room_id"
                )
                or None
            ),
            "canonical_route": (
                normalized.get(
                    "canonical_route"
                )
                or None
            ),
            "mode": (
                normalized.get(
                    "mode"
                )
                or None
            ),
            "issued_at": (
                normalized.get(
                    "issued_at"
                )
                or None
            ),
            "expires_at": (
                normalized.get(
                    "expires_at"
                )
                or None
            ),
            "raw_payload": payload,
            "normalized_packet": (
                normalized
            ),
            "authenticity_mode": (
                validation[
                    "authenticity_mode"
                ]
            ),
            "tower_authenticity_proven": (
                validation[
                    "tower_authenticity_proven"
                ]
            ),
            "previous_hash": (
                previous_hash
            ),
            "created_at": (
                created_at
            ),
        }

        record_hash = _sha256_text(
            _canonical_json(
                _record_hash_material(
                    record
                )
            )
        )

        connection.execute(
            """
            INSERT INTO
            ob_tower_launch_intakes (
                intake_id,
                handoff_id,
                nonce,
                packet_hash,
                integrity_hash,
                decision,
                reason_codes_json,
                owner_id,
                session_id,
                room_id,
                canonical_route,
                mode,
                issued_at,
                expires_at,
                raw_payload_json,
                normalized_packet_json,
                authenticity_mode,
                tower_authenticity_proven,
                previous_hash,
                record_hash,
                created_at,
                consumed_at,
                consumption_hash
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL
            )
            """,
            (
                intake_id,
                record[
                    "handoff_id"
                ],
                record["nonce"],
                record[
                    "packet_hash"
                ],
                record[
                    "integrity_hash"
                ],
                decision,
                _json_text(
                    record[
                        "reason_codes"
                    ]
                ),
                record[
                    "owner_id"
                ],
                record[
                    "session_id"
                ],
                record[
                    "room_id"
                ],
                record[
                    "canonical_route"
                ],
                record["mode"],
                record[
                    "issued_at"
                ],
                record[
                    "expires_at"
                ],
                _json_text(
                    payload
                ),
                _json_text(
                    normalized
                ),
                record[
                    "authenticity_mode"
                ],
                int(
                    bool(
                        record[
                            "tower_authenticity_proven"
                        ]
                    )
                ),
                previous_hash,
                record_hash,
                created_at,
            ),
        )

        if (
            decision == "accepted"
            and nonce
        ):
            connection.execute(
                """
                INSERT INTO
                ob_tower_launch_nonce_registry (
                    nonce,
                    packet_hash,
                    intake_id,
                    registered_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    nonce,
                    packet_hash,
                    intake_id,
                    created_at,
                ),
            )

        connection.commit()

    intake = (
        get_tower_protected_launch_handoff(
            intake_id,
            path=database,
        )
    )

    return {
        "ok": decision == "accepted",
        "created": True,
        "idempotent": False,
        "decision": decision,
        "reason_codes": (
            validation[
                "reason_codes"
            ]
        ),
        "intake": intake,
        "production_authority_granted": False,
    }


def consume_tower_protected_launch_handoff(
    intake_id: str,
    *,
    owner_id: Optional[str] = None,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_launch_database(
        database
    )

    current_time = _now(
        now
    )

    with _connect(database) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_tower_launch_intakes
            WHERE intake_id = ?
            """,
            (
                str(intake_id),
            ),
        ).fetchone()

        if row is None:
            return {
                "ok": False,
                "consumed": False,
                "reason_code": (
                    "launch_intake_not_found"
                ),
            }

        if row["decision"] != "accepted":
            return {
                "ok": False,
                "consumed": False,
                "reason_code": (
                    "launch_intake_not_accepted"
                ),
            }

        if row["consumed_at"]:
            return {
                "ok": False,
                "consumed": False,
                "reason_code": (
                    "handoff_already_consumed"
                ),
                "intake": _public_record(
                    row
                ),
            }

        if (
            owner_id
            and row["owner_id"]
            and str(owner_id)
            != str(row["owner_id"])
        ):
            return {
                "ok": False,
                "consumed": False,
                "reason_code": (
                    "owner_identity_mismatch"
                ),
            }

        try:
            expires_at = (
                _parse_time(
                    row[
                        "expires_at"
                    ]
                )
            )

        except Exception:
            return {
                "ok": False,
                "consumed": False,
                "reason_code": (
                    "invalid_stored_expiration"
                ),
            }

        if (
            expires_at.timestamp()
            <= current_time.timestamp()
        ):
            return {
                "ok": False,
                "consumed": False,
                "reason_code": (
                    "handoff_expired_before_consumption"
                ),
            }

        consumed_at = _iso(
            current_time
        )

        consumption_material = {
            "intake_id": row[
                "intake_id"
            ],
            "handoff_id": row[
                "handoff_id"
            ],
            "packet_hash": row[
                "packet_hash"
            ],
            "owner_id": row[
                "owner_id"
            ],
            "room_id": row[
                "room_id"
            ],
            "consumed_at": (
                consumed_at
            ),
            "single_use": True,
            "production_authority_granted": False,
        }

        consumption_hash = (
            _sha256_text(
                _canonical_json(
                    consumption_material
                )
            )
        )

        connection.execute(
            """
            UPDATE ob_tower_launch_intakes
            SET
                consumed_at = ?,
                consumption_hash = ?
            WHERE intake_id = ?
              AND consumed_at IS NULL
            """,
            (
                consumed_at,
                consumption_hash,
                str(intake_id),
            ),
        )

        connection.commit()

    intake = (
        get_tower_protected_launch_handoff(
            intake_id,
            path=database,
        )
    )

    return {
        "ok": True,
        "consumed": True,
        "reason_code": (
            "handoff_consumed"
        ),
        "intake": intake,
        "production_authority_granted": False,
    }


def verify_tower_protected_launch_handoff(
    intake_id: str,
    *,
    path: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_launch_database(
        database
    )

    with _connect(database) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_tower_launch_intakes
            WHERE intake_id = ?
            """,
            (
                str(intake_id),
            ),
        ).fetchone()

        if row is None:
            return {
                "verified": False,
                "reason_codes": [
                    "launch_intake_not_found"
                ],
            }

        raw_payload = json.loads(
            row[
                "raw_payload_json"
            ]
        )

        normalized = json.loads(
            row[
                "normalized_packet_json"
            ]
        )

        reasons = json.loads(
            row[
                "reason_codes_json"
            ]
        )

        record = {
            "intake_id": row[
                "intake_id"
            ],
            "handoff_id": row[
                "handoff_id"
            ],
            "nonce": row["nonce"],
            "packet_hash": row[
                "packet_hash"
            ],
            "integrity_hash": row[
                "integrity_hash"
            ],
            "decision": row[
                "decision"
            ],
            "reason_codes": reasons,
            "owner_id": row[
                "owner_id"
            ],
            "session_id": row[
                "session_id"
            ],
            "room_id": row[
                "room_id"
            ],
            "canonical_route": row[
                "canonical_route"
            ],
            "mode": row["mode"],
            "issued_at": row[
                "issued_at"
            ],
            "expires_at": row[
                "expires_at"
            ],
            "raw_payload": raw_payload,
            "normalized_packet": normalized,
            "authenticity_mode": row[
                "authenticity_mode"
            ],
            "tower_authenticity_proven": bool(
                row[
                    "tower_authenticity_proven"
                ]
            ),
            "previous_hash": row[
                "previous_hash"
            ],
            "created_at": row[
                "created_at"
            ],
        }

        computed_record_hash = (
            _sha256_text(
                _canonical_json(
                    _record_hash_material(
                        record
                    )
                )
            )
        )

        packet_hash = (
            build_tower_launch_integrity_hash(
                raw_payload
            )
        )

        checks = {
            "record_hash_matches": (
                computed_record_hash
                == row[
                    "record_hash"
                ]
            ),
            "packet_hash_matches": (
                packet_hash
                == row[
                    "packet_hash"
                ]
            ),
            "integrity_hash_matches": (
                not row[
                    "integrity_hash"
                ]
                or hmac.compare_digest(
                    str(
                        row[
                            "integrity_hash"
                        ]
                    ).lower(),
                    packet_hash.lower(),
                )
            ),
            "previous_hash_valid": True,
            "consumption_hash_valid": True,
        }

        if (
            row["previous_hash"]
            != ZERO_HASH
        ):
            previous = connection.execute(
                """
                SELECT 1
                FROM ob_tower_launch_intakes
                WHERE record_hash = ?
                LIMIT 1
                """,
                (
                    row[
                        "previous_hash"
                    ],
                ),
            ).fetchone()

            checks[
                "previous_hash_valid"
            ] = previous is not None

        if row["consumed_at"]:
            consumption_material = {
                "intake_id": row[
                    "intake_id"
                ],
                "handoff_id": row[
                    "handoff_id"
                ],
                "packet_hash": row[
                    "packet_hash"
                ],
                "owner_id": row[
                    "owner_id"
                ],
                "room_id": row[
                    "room_id"
                ],
                "consumed_at": row[
                    "consumed_at"
                ],
                "single_use": True,
                "production_authority_granted": False,
            }

            expected_consumption_hash = (
                _sha256_text(
                    _canonical_json(
                        consumption_material
                    )
                )
            )

            checks[
                "consumption_hash_valid"
            ] = hmac.compare_digest(
                str(
                    row[
                        "consumption_hash"
                    ]
                    or ""
                ),
                expected_consumption_hash,
            )

    return {
        "verified": all(
            checks.values()
        ),
        "checks": checks,
        "intake_id": str(
            intake_id
        ),
        "record_hash": row[
            "record_hash"
        ],
        "decision": row[
            "decision"
        ],
        "consumed": bool(
            row["consumed_at"]
        ),
        "production_authority_granted": False,
    }


def tower_protected_launch_status(
    *,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_launch_database(
        database
    )

    current = _iso(
        _now(now)
    )

    with _connect(database) as connection:
        totals = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(
                    CASE
                        WHEN decision = 'accepted'
                        THEN 1 ELSE 0
                    END
                ) AS accepted,
                SUM(
                    CASE
                        WHEN decision = 'denied'
                        THEN 1 ELSE 0
                    END
                ) AS denied,
                SUM(
                    CASE
                        WHEN consumed_at IS NOT NULL
                        THEN 1 ELSE 0
                    END
                ) AS consumed,
                SUM(
                    CASE
                        WHEN decision = 'accepted'
                         AND consumed_at IS NULL
                         AND expires_at > ?
                        THEN 1 ELSE 0
                    END
                ) AS active_unconsumed
            FROM ob_tower_launch_intakes
            """,
            (
                current,
            ),
        ).fetchone()

    return {
        "ok": True,
        "pack": PACK,
        "contract_version": CONTRACT_VERSION,
        "database_path": str(
            database
        ),
        "total": int(
            totals["total"]
            or 0
        ),
        "accepted": int(
            totals["accepted"]
            or 0
        ),
        "denied": int(
            totals["denied"]
            or 0
        ),
        "consumed": int(
            totals["consumed"]
            or 0
        ),
        "active_unconsumed": int(
            totals[
                "active_unconsumed"
            ]
            or 0
        ),
        "canonical_room_count": len(
            ROOM_REGISTRY
        ),
        "tower_maps_routes": True,
        "ob_self_authorization_allowed": False,
        "http_intake_enabled": (
            os.environ.get(
                "OB_TOWER_LAUNCH_HTTP_INTAKE_ENABLED",
                "0",
            )
            == "1"
        ),
        "hmac_verification_configured": bool(
            os.environ.get(
                "OB_TOWER_LAUNCH_HMAC_SECRET"
            )
        ),
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
    }
