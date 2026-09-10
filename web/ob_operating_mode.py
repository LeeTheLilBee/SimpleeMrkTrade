from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Optional
import json
import sqlite3


SCHEMA_VERSION = "OB_OPERATING_MODE_V1"
SERVICE_VERSION = "OBMODE001_010_CANONICAL_OPERATING_MODE"

ACCOUNT_IDENTITY_AUTHORITY = "OB_ACCOUNT_IDENTITY_TRUTH_V1"
EFFECTIVE_POLICY_AUTHORITY = "OB_EFFECTIVE_POLICY_V1"
EVENT_AUTHORITY = "OB_COMMAND_EVENT_CAUSAL_V1"
PENDING_TIME_AUTHORITY = "PENDING_OBTIME"


MODES = (
    "SURVEY",
    "PAPER",
    "MANUAL_LIVE_1",
    "HYBRID",
    "AUTOMATED",
)


FUTURE_LOCKED_MODES = {
    "HYBRID",
    "AUTOMATED",
}


ALLOWED_TRANSITIONS = {
    "SURVEY": {
        "PAPER",
    },

    "PAPER": {
        "SURVEY",
        "MANUAL_LIVE_1",
    },

    "MANUAL_LIVE_1": {
        "PAPER",
        "HYBRID",
    },

    "HYBRID": {
        "MANUAL_LIVE_1",
        "AUTOMATED",
    },

    "AUTOMATED": {
        "HYBRID",
    },
}


MODE_CAPABILITY_MATRIX = {

    "SURVEY": {
        "available_now":
            True,

        "market_analysis_allowed":
            True,

        "owner_review_allowed":
            True,

        "paper_position_lifecycle_allowed":
            False,

        "real_market_context_allowed":
            False,

        "manual_live_handoff_allowed":
            False,

        "owner_manual_broker_action_outside_ob_allowed":
            False,
    },

    "PAPER": {
        "available_now":
            True,

        "market_analysis_allowed":
            True,

        "owner_review_allowed":
            True,

        "paper_position_lifecycle_allowed":
            True,

        "real_market_context_allowed":
            False,

        "manual_live_handoff_allowed":
            False,

        "owner_manual_broker_action_outside_ob_allowed":
            False,
    },

    "MANUAL_LIVE_1": {
        "available_now":
            True,

        "market_analysis_allowed":
            True,

        "owner_review_allowed":
            True,

        "paper_position_lifecycle_allowed":
            False,

        "real_market_context_allowed":
            True,

        "manual_live_handoff_allowed":
            True,

        # This means the OWNER may separately use the brokerage.
        # It does NOT grant OB broker authority.
        "owner_manual_broker_action_outside_ob_allowed":
            True,
    },

    "HYBRID": {
        "available_now":
            False,

        "market_analysis_allowed":
            True,

        "owner_review_allowed":
            True,

        "paper_position_lifecycle_allowed":
            False,

        "real_market_context_allowed":
            False,

        "manual_live_handoff_allowed":
            False,

        "owner_manual_broker_action_outside_ob_allowed":
            False,
    },

    "AUTOMATED": {
        "available_now":
            False,

        "market_analysis_allowed":
            True,

        "owner_review_allowed":
            True,

        "paper_position_lifecycle_allowed":
            False,

        "real_market_context_allowed":
            False,

        "manual_live_handoff_allowed":
            False,

        "owner_manual_broker_action_outside_ob_allowed":
            False,
    },
}


DANGEROUS_CAPABILITIES = {
    "broker_submission_allowed":
        False,

    "capital_movement_allowed":
        False,

    "automatic_contract_selection_allowed":
        False,

    "hybrid_execution_allowed":
        False,

    "automatic_execution_allowed":
        False,
}


ROOT = Path(
    __file__
).resolve().parents[1]


DEFAULT_DB_PATH = (
    ROOT
    / "data"
    / "_local_archives"
    / "ob_operating_mode.sqlite3"
)


def utc_now_iso() -> str:

    return (
        datetime.now(
            timezone.utc
        )
        .replace(
            microsecond=0
        )
        .isoformat()
    )


def canonical_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
        default=str,
    )


def stable_hash(
    value: Any,
) -> str:

    return sha256(
        canonical_json(
            value
        ).encode(
            "utf-8"
        )
    ).hexdigest()


def clean_text(
    value: Any,
    *,
    label: str,
) -> str:

    result = (
        ""
        if value is None
        else str(
            value
        ).strip()
    )

    if not result:
        raise ValueError(
            f"{label} is required."
        )

    return result


def canonical_mode(
    value: Any,
) -> str:

    mode = clean_text(
        value,
        label="mode",
    ).upper()

    if mode not in MODES:
        raise ValueError(
            f"Unknown OB operating mode: {mode}"
        )

    return mode


def known_account(
    account_key: Any,
) -> Dict[str, Any]:

    from web.ob_account_identity_truth import (
        resolve_account_identity,
    )

    identity = (
        resolve_account_identity(
            account_key
        )
    )

    if identity.get(
        "known"
    ) is not True:

        raise ValueError(
            "Operating Mode requires an explicit known account."
        )

    return deepcopy(
        identity
    )


def operating_mode_contract() -> Dict[str, Any]:

    return {
        "schema_version":
            SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "authority":
            SCHEMA_VERSION,

        "account_identity_authority":
            ACCOUNT_IDENTITY_AUTHORITY,

        "effective_policy_authority":
            EFFECTIVE_POLICY_AUTHORITY,

        "event_authority":
            EVENT_AUTHORITY,

        "modes":
            list(
                MODES
            ),

        "future_locked_modes":
            sorted(
                FUTURE_LOCKED_MODES
            ),

        "implicit_default_mode":
            False,

        "global_mode":
            False,

        "account_bound":
            True,

        "explicit_owner_authorization_required":
            True,

        "mode_policy_restriction_only":
            True,

        "operating_mode_is_capital_mode":
            False,

        "mode_capability_matrix":
            deepcopy(
                MODE_CAPABILITY_MATRIX
            ),

        "broker_submission":
            False,

        "capital_movement":
            False,

        "automatic_contract_selection":
            False,

        "hybrid_execution":
            False,

        "automatic_execution":
            False,

        "live_auto_locked":
            True,

        "canonical_time_authority":
            False,

        "future_time_authority":
            PENDING_TIME_AUTHORITY,
    }


def _state_material(
    state: Dict[str, Any],
) -> Dict[str, Any]:

    result = deepcopy(
        state
    )

    result.pop(
        "state_id",
        None,
    )

    result.pop(
        "mode_state_fingerprint",
        None,
    )

    return result


def recompute_mode_state_fingerprint(
    state: Dict[str, Any],
) -> str:

    return stable_hash(
        _state_material(
            state
        )
    )


def _new_state(
    *,
    account_key: Any,
    mode: Any,
    revision: int,
    previous_mode: Optional[str],
    owner_authorized: bool,
    reason: Any,
    recorded_at: Optional[str] = None,
) -> Dict[str, Any]:

    identity = known_account(
        account_key
    )

    selected = canonical_mode(
        mode
    )

    if selected in FUTURE_LOCKED_MODES:

        raise ValueError(
            (
                f"{selected} remains future locked. "
                "OBMODE001–010 cannot activate it."
            )
        )

    if owner_authorized is not True:

        raise ValueError(
            "Explicit owner authorization is required for mode state."
        )

    if (
        not isinstance(
            revision,
            int,
        )
        or revision < 1
    ):

        raise ValueError(
            "Mode revision must be a positive integer."
        )

    reason_text = clean_text(
        reason,
        label="mode reason",
    )

    capabilities = deepcopy(
        MODE_CAPABILITY_MATRIX[
            selected
        ]
    )

    require_available = (
        capabilities.get(
            "available_now"
        )
        is True
    )

    if not require_available:

        raise ValueError(
            f"{selected} is not available in the current OB phase."
        )

    state = {
        "schema_version":
            SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "authority":
            SCHEMA_VERSION,

        "account_key":
            identity[
                "account_key"
            ],

        "account_identity_fingerprint":
            identity[
                "identity_fingerprint"
            ],

        "mode":
            selected,

        "revision":
            revision,

        "previous_mode":
            previous_mode,

        "owner_authorized":
            True,

        "reason":
            reason_text,

        "recorded_at":
            (
                recorded_at
                or utc_now_iso()
            ),

        # This is an audit timestamp only.
        # Canonical market/session time comes later from OBTIME.
        "time_authority":
            PENDING_TIME_AUTHORITY,

        "canonical_time_claimed":
            False,

        "capabilities":
            capabilities,

        "dangerous_capabilities":
            deepcopy(
                DANGEROUS_CAPABILITIES
            ),

        "mode_policy_restriction_only":
            True,

        "event_authority":
            EVENT_AUTHORITY,

        "event_written_here":
            False,

        "execution_authority":
            False,

        "broker_submission":
            False,

        "capital_movement":
            False,

        "automatic_contract_selection":
            False,

        "hybrid_execution":
            False,

        "automatic_execution":
            False,

        "live_auto_locked":
            True,
    }

    fingerprint = (
        recompute_mode_state_fingerprint(
            state
        )
    )

    state[
        "state_id"
    ] = (
        "obmode_"
        + fingerprint[:28]
    )

    state[
        "mode_state_fingerprint"
    ] = fingerprint

    validate_mode_state(
        state
    )

    return state


def build_initial_mode_state(
    *,
    account_key: Any,
    mode: Any,
    owner_authorized: bool,
    reason: Any,
    recorded_at: Optional[str] = None,
) -> Dict[str, Any]:

    return _new_state(
        account_key=account_key,
        mode=mode,
        revision=1,
        previous_mode=None,
        owner_authorized=owner_authorized,
        reason=reason,
        recorded_at=recorded_at,
    )


def validate_mode_state(
    state: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        state,
        dict,
    ):

        raise ValueError(
            "Operating Mode state must be an object."
        )

    if state.get(
        "schema_version"
    ) != SCHEMA_VERSION:

        raise ValueError(
            "Unknown Operating Mode schema."
        )

    if state.get(
        "authority"
    ) != SCHEMA_VERSION:

        raise ValueError(
            "Operating Mode authority mismatch."
        )

    identity = known_account(
        state.get(
            "account_key"
        )
    )

    if (
        state.get(
            "account_identity_fingerprint"
        )
        != identity[
            "identity_fingerprint"
        ]
    ):

        raise ValueError(
            "Operating Mode account identity fingerprint mismatch."
        )

    mode = canonical_mode(
        state.get(
            "mode"
        )
    )

    if mode in FUTURE_LOCKED_MODES:

        raise ValueError(
            f"{mode} remains future locked."
        )

    if state.get(
        "owner_authorized"
    ) is not True:

        raise ValueError(
            "Operating Mode lacks explicit owner authorization."
        )

    capabilities = state.get(
        "capabilities"
    )

    if capabilities != MODE_CAPABILITY_MATRIX[
        mode
    ]:

        raise ValueError(
            "Operating Mode capability matrix mismatch."
        )

    dangerous = state.get(
        "dangerous_capabilities"
    )

    if dangerous != DANGEROUS_CAPABILITIES:

        raise ValueError(
            "Operating Mode dangerous-capability boundary mismatch."
        )

    for forbidden in (
        "execution_authority",
        "broker_submission",
        "capital_movement",
        "automatic_contract_selection",
        "hybrid_execution",
        "automatic_execution",
    ):

        if state.get(
            forbidden
        ) is not False:

            raise ValueError(
                (
                    "Operating Mode contains forbidden authority: "
                    + forbidden
                )
            )

    if state.get(
        "live_auto_locked"
    ) is not True:

        raise ValueError(
            "Live Auto must remain locked."
        )

    expected = (
        recompute_mode_state_fingerprint(
            state
        )
    )

    if state.get(
        "mode_state_fingerprint"
    ) != expected:

        raise ValueError(
            "Operating Mode fingerprint mismatch."
        )

    if state.get(
        "state_id"
    ) != (
        "obmode_"
        + expected[:28]
    ):

        raise ValueError(
            "Operating Mode state ID mismatch."
        )

    return deepcopy(
        state
    )


def mode_state_reference(
    state: Dict[str, Any],
) -> Dict[str, Any]:

    state = validate_mode_state(
        state
    )

    return {
        "authority":
            SCHEMA_VERSION,

        "state_id":
            state[
                "state_id"
            ],

        "mode_state_fingerprint":
            state[
                "mode_state_fingerprint"
            ],

        "account_key":
            state[
                "account_key"
            ],

        "mode":
            state[
                "mode"
            ],

        "revision":
            state[
                "revision"
            ],

        "owner_authorized":
            True,

        "event_authority":
            EVENT_AUTHORITY,

        "execution_authority":
            False,

        "broker_submission":
            False,

        "capital_movement":
            False,

        "automatic_execution":
            False,
    }


def transition_mode_state(
    current: Dict[str, Any],
    *,
    next_mode: Any,
    owner_authorized: bool,
    reason: Any,
    recorded_at: Optional[str] = None,
) -> Dict[str, Any]:

    current = validate_mode_state(
        current
    )

    target = canonical_mode(
        next_mode
    )

    if target in FUTURE_LOCKED_MODES:

        raise ValueError(
            (
                f"{target} remains future locked. "
                "A later authority pack must explicitly unlock it."
            )
        )

    existing = current[
        "mode"
    ]

    if target == existing:

        return deepcopy(
            current
        )

    if target not in ALLOWED_TRANSITIONS[
        existing
    ]:

        raise ValueError(
            (
                "Illegal Operating Mode transition: "
                f"{existing} -> {target}"
            )
        )

    return _new_state(
        account_key=current[
            "account_key"
        ],
        mode=target,
        revision=current[
            "revision"
        ] + 1,
        previous_mode=existing,
        owner_authorized=owner_authorized,
        reason=reason,
        recorded_at=recorded_at,
    )


def mode_policy_projection(
    state: Dict[str, Any],
) -> Dict[str, Any]:

    state = validate_mode_state(
        state
    )

    return {
        "authority":
            SCHEMA_VERSION,

        "account_key":
            state[
                "account_key"
            ],

        "mode":
            state[
                "mode"
            ],

        "mode_state_reference":
            mode_state_reference(
                state
            ),

        # OBMODE does not create a second risk engine.
        # It provides restriction-only policy input.
        "limits": {
            "live_automation_allowed":
                False,
        },

        "capabilities":
            deepcopy(
                DANGEROUS_CAPABILITIES
            ),

        "behavior":
            deepcopy(
                state[
                    "capabilities"
                ]
            ),

        "restriction_only":
            True,

        "execution_authority":
            False,

        "broker_submission":
            False,

        "capital_movement":
            False,

        "automatic_contract_selection":
            False,

        "hybrid_execution":
            False,

        "automatic_execution":
            False,
    }


def mode_allows_trade_intent_state(
    state: Dict[str, Any],
    lifecycle_state: Any,
) -> bool:

    state = validate_mode_state(
        state
    )

    lifecycle = clean_text(
        lifecycle_state,
        label="Trade Intent lifecycle state",
    ).upper()

    if lifecycle in {
        "RESEARCH_PENDING",
        "OWNER_FIT_PENDING",
        "OWNER_REVIEW_READY",
        "BLOCKED",
        "ARCHIVED",
    }:
        return True

    if lifecycle in {
        "OWNER_SELECTED",
        "TRACKING",
        "CLOSED",
    }:

        return (
            state[
                "mode"
            ]
            in {
                "PAPER",
                "MANUAL_LIVE_1",
            }
        )

    return False


def resolve_db_path(
    path: Optional[Path] = None,
) -> Path:

    selected = (
        Path(path)
        if path is not None
        else DEFAULT_DB_PATH
    )

    selected.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return selected


def initialize_store(
    path: Optional[Path] = None,
) -> Path:

    selected = resolve_db_path(
        path
    )

    with sqlite3.connect(
        selected
    ) as conn:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS
            operating_mode_state (
                account_key TEXT PRIMARY KEY,
                mode TEXT NOT NULL,
                revision INTEGER NOT NULL,
                mode_state_fingerprint TEXT NOT NULL,
                state_json TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS
            operating_mode_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_key TEXT NOT NULL,
                mode TEXT NOT NULL,
                revision INTEGER NOT NULL,
                mode_state_fingerprint TEXT NOT NULL,
                state_json TEXT NOT NULL
            )
            """
        )

        conn.commit()

    return selected


def get_operating_mode(
    account_key: Any,
    *,
    path: Optional[Path] = None,
) -> Optional[Dict[str, Any]]:

    identity = known_account(
        account_key
    )

    selected = initialize_store(
        path
    )

    with sqlite3.connect(
        selected
    ) as conn:

        row = conn.execute(
            """
            SELECT state_json
            FROM operating_mode_state
            WHERE account_key = ?
            """,
            (
                identity[
                    "account_key"
                ],
            ),
        ).fetchone()

    if row is None:
        return None

    state = json.loads(
        row[0]
    )

    return validate_mode_state(
        state
    )


def _persist_state(
    state: Dict[str, Any],
    *,
    path: Optional[Path] = None,
) -> Dict[str, Any]:

    state = validate_mode_state(
        state
    )

    selected = initialize_store(
        path
    )

    raw = canonical_json(
        state
    )

    with sqlite3.connect(
        selected
    ) as conn:

        conn.execute(
            """
            INSERT INTO operating_mode_state (
                account_key,
                mode,
                revision,
                mode_state_fingerprint,
                state_json
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(account_key)
            DO UPDATE SET
                mode=excluded.mode,
                revision=excluded.revision,
                mode_state_fingerprint=excluded.mode_state_fingerprint,
                state_json=excluded.state_json
            """,
            (
                state[
                    "account_key"
                ],
                state[
                    "mode"
                ],
                state[
                    "revision"
                ],
                state[
                    "mode_state_fingerprint"
                ],
                raw,
            ),
        )

        conn.execute(
            """
            INSERT INTO operating_mode_history (
                account_key,
                mode,
                revision,
                mode_state_fingerprint,
                state_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                state[
                    "account_key"
                ],
                state[
                    "mode"
                ],
                state[
                    "revision"
                ],
                state[
                    "mode_state_fingerprint"
                ],
                raw,
            ),
        )

        conn.commit()

    return deepcopy(
        state
    )


def activate_operating_mode(
    *,
    account_key: Any,
    mode: Any,
    owner_authorized: bool,
    reason: Any,
    path: Optional[Path] = None,
) -> Dict[str, Any]:

    existing = get_operating_mode(
        account_key,
        path=path,
    )

    if existing is None:

        state = build_initial_mode_state(
            account_key=account_key,
            mode=mode,
            owner_authorized=owner_authorized,
            reason=reason,
        )

    else:

        target = canonical_mode(
            mode
        )

        if target == existing[
            "mode"
        ]:

            return {
                "ok":
                    True,

                "changed":
                    False,

                "idempotent":
                    True,

                "state":
                    existing,
            }

        state = transition_mode_state(
            existing,
            next_mode=target,
            owner_authorized=owner_authorized,
            reason=reason,
        )

    persisted = _persist_state(
        state,
        path=path,
    )

    return {
        "ok":
            True,

        "changed":
            True,

        "idempotent":
            False,

        "state":
            persisted,

        "state_reference":
            mode_state_reference(
                persisted
            ),
    }
