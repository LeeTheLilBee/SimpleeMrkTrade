
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import sqlite3


SCHEMA_VERSION = (
    "OB_TRADE_INTENT_V1"
)

SERVICE_VERSION = (
    "OBENG006_010_CANONICAL_TRADE_INTENT"
)


ROOT = (
    Path(__file__).resolve().parents[1]
)


DEFAULT_DB_PATH = (
    ROOT
    / "data"
    / "ob_trade_intents.sqlite3"
)


LIFECYCLE_STATES = (
    "RESEARCH_PENDING",
    "OWNER_FIT_PENDING",
    "OWNER_REVIEW_READY",
    "OWNER_SELECTED",
    "OWNER_DECLINED",
    "TRACKING",
    "CLOSED",
    "BLOCKED",
    "ARCHIVED",
)


ALLOWED_TRANSITIONS = {
    "RESEARCH_PENDING": {
        "OWNER_FIT_PENDING",
        "BLOCKED",
        "ARCHIVED",
    },

    "OWNER_FIT_PENDING": {
        "OWNER_REVIEW_READY",
        "BLOCKED",
        "ARCHIVED",
    },

    "OWNER_REVIEW_READY": {
        "OWNER_SELECTED",
        "OWNER_DECLINED",
        "BLOCKED",
        "ARCHIVED",
    },

    "OWNER_SELECTED": {
        "TRACKING",
        "BLOCKED",
        "ARCHIVED",
    },

    "OWNER_DECLINED": {
        "ARCHIVED",
    },

    "TRACKING": {
        "CLOSED",
        "BLOCKED",
    },

    "CLOSED": {
        "ARCHIVED",
    },

    "BLOCKED": {
        "OWNER_FIT_PENDING",
        "ARCHIVED",
    },

    "ARCHIVED": set(),
}


FORBIDDEN_TRUTHY_KEYS = {
    "ob_selected_contract",
    "user_selected_contract",
    "owner_selected_contract",
    "automatic_contract_selection",
    "brokerage_execution",
    "automatic_execution",
    "submit_order",
    "submit_real_broker_order",
    "place_order",
    "place_trade",
    "auto_execute",
    "real_capital_moved",
    "move_capital",
}


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


def safe_object(
    value: Any,
) -> Dict[str, Any]:
    return (
        deepcopy(value)
        if isinstance(
            value,
            dict,
        )
        else {}
    )


def safe_list(
    value: Any,
) -> List[Any]:
    return (
        deepcopy(value)
        if isinstance(
            value,
            list,
        )
        else []
    )


def clean_text(
    value: Any,
    fallback: str = "",
) -> str:
    if value is None:
        return fallback

    result = str(
        value
    ).strip()

    return (
        result
        if result
        else fallback
    )


def first_present(
    source: Dict[str, Any],
    *keys: str,
):
    for key in keys:
        if (
            key in source
            and
            source.get(key)
            is not None
            and
            source.get(key)
            != ""
        ):
            return source.get(
                key
            )

    return None


def _scan_forbidden_truthy(
    value: Any,
    *,
    path: str = "root",
) -> List[str]:

    violations = []

    if isinstance(
        value,
        dict,
    ):
        for key, nested in (
            value.items()
        ):
            next_path = (
                f"{path}.{key}"
            )

            if (
                key
                in FORBIDDEN_TRUTHY_KEYS
                and bool(nested)
            ):
                violations.append(
                    next_path
                )

            violations.extend(
                _scan_forbidden_truthy(
                    nested,
                    path=next_path,
                )
            )

    elif isinstance(
        value,
        list,
    ):
        for index, nested in enumerate(
            value
        ):
            violations.extend(
                _scan_forbidden_truthy(
                    nested,
                    path=(
                        f"{path}[{index}]"
                    ),
                )
            )

    return violations


def normalize_candidate(
    candidate: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        candidate,
        dict,
    ):
        raise ValueError(
            "OBTradeIntent requires "
            "a canonical candidate object."
        )

    raw = deepcopy(
        candidate
    )

    symbol = clean_text(
        first_present(
            raw,
            "symbol",
            "ticker",
        )
    ).upper()

    if not symbol:
        raise ValueError(
            "Candidate symbol is required."
        )

    candidate_fingerprint = (
        stable_hash(
            raw
        )
    )

    candidate_id = clean_text(
        first_present(
            raw,
            "candidate_id",
            "id",
            "trade_id",
        ),
        (
            "obcand_"
            + candidate_fingerprint[:20]
        ),
    )

    return {
        "candidate_id":
            candidate_id,

        "candidate_fingerprint":
            candidate_fingerprint,

        "symbol":
            symbol,

        "source":
            first_present(
                raw,
                "candidate_source",
                "source",
                "data_source",
            ),

        "as_of":
            first_present(
                raw,
                "as_of",
                "timestamp",
                "generated_at",
                "updated_at",
            ),

        "strategy":
            first_present(
                raw,
                "strategy",
                "setup",
                "setup_type",
            ),

        "direction":
            first_present(
                raw,
                "direction",
                "side",
                "right",
            ),

        "score":
            first_present(
                raw,
                "score",
                "fused_score",
                "rank_score",
            ),

        "rank":
            first_present(
                raw,
                "rank",
                "candidate_rank",
            ),

        "confidence":
            first_present(
                raw,
                "confidence",
                "confidence_label",
            ),

        "entry":
            first_present(
                raw,
                "entry",
                "entry_price",
                "entry_zone",
            ),

        "target":
            first_present(
                raw,
                "target",
                "target_price",
            ),

        "risk":
            first_present(
                raw,
                "risk",
                "risk_label",
                "risk_level",
            ),

        "invalidation":
            first_present(
                raw,
                "invalidation",
                "invalidates_at",
                "stop",
                "stop_price",
            ),

        "expected_hold":
            first_present(
                raw,
                "expected_hold",
                "hold_window",
                "holding_window",
            ),

        "actionable_state":
            first_present(
                raw,
                "actionable_state",
                "status",
                "state",
            ),

        # Exact source payload is retained for provenance.
        # OBTradeIntent does not mutate it into a new candidate.
        "source_payload":
            raw,
    }


def normalize_options_research(
    research: Optional[
        Dict[str, Any]
    ],
) -> Dict[str, Any]:

    if research is None:
        return {
            "status":
                "PENDING_RESEARCH",

            "schema_version":
                "OB_OPTIONS_RESEARCH_V1",

            "authority":
                "PENDING_EXISTING_RESEARCH",

            "research_only":
                True,

            "selection_authority":
                "OWNER",

            "selected_contract":
                None,

            "research_payload":
                None,

            "research_fingerprint":
                None,

            "automatic_contract_selection":
                False,

            "brokerage_execution":
                False,

            "automatic_execution":
                False,
        }

    if not isinstance(
        research,
        dict,
    ):
        raise ValueError(
            "Options research must be "
            "a dictionary when supplied."
        )

    violations = (
        _scan_forbidden_truthy(
            research
        )
    )

    if violations:
        raise ValueError(
            "Options research contains "
            "selection/execution authority: "
            + ", ".join(
                violations
            )
        )

    payload = deepcopy(
        research
    )

    fingerprint = (
        stable_hash(
            payload
        )
    )

    return {
        "status":
            "RESEARCH_BOUND",

        "schema_version":
            clean_text(
                payload.get(
                    "schema_version"
                ),
                "OB_OPTIONS_RESEARCH_V1",
            ),

        "authority":
            clean_text(
                payload.get(
                    "authority"
                ),
                "ENGINE_RESEARCH_PROJECTION",
            ),

        "research_only":
            True,

        "selection_authority":
            "OWNER",

        "selected_contract":
            None,

        "research_contracts":
            safe_list(
                payload.get(
                    "research_contracts"
                )
            ),

        "ranked_contracts":
            safe_list(
                payload.get(
                    "ranked_contracts"
                )
            ),

        "options_by_symbol":
            safe_object(
                payload.get(
                    "options_by_symbol"
                )
            ),

        "diagnostics":
            safe_object(
                payload.get(
                    "diagnostics"
                )
            ),

        "research_payload":
            payload,

        "research_fingerprint":
            fingerprint,

        "automatic_contract_selection":
            False,

        "brokerage_execution":
            False,

        "automatic_execution":
            False,
    }


def account_authority_reference() -> Dict[str, Any]:
    """
    Bind only the authority/provenance status from OBENG001–005.

    We deliberately do NOT synthesize a cross-source account balance.
    """

    from web.ob_engine_account_authority import (
        build_authority_bundle,
    )

    bundle = (
        build_authority_bundle()
    )

    account = (
        bundle.get(
            "account_authority",
            {}
        )
    )

    operational = (
        account.get(
            "operational_repository_authority",
            {},
        )
    )

    return {
        "authority_contract":
            (
                bundle.get(
                    "schema_version"
                )
            ),

        "operational_source":
            operational.get(
                "source"
            ),

        "operational_role":
            operational.get(
                "role"
            ),

        "broker_reconciled":
            bool(
                operational.get(
                    "broker_reconciled"
                )
            ),

        "claimed_live_broker_truth":
            bool(
                operational.get(
                    "claimed_live_broker_truth"
                )
            ),

        "reconciliation_status":
            account.get(
                "reconciliation_status"
            ),

        "conflict_fields":
            list(
                account.get(
                    "conflict_fields"
                )
                or []
            ),

        "cross_source_resolved_account":
            None,

        "no_silent_merge":
            True,
    }


def pending_account_context() -> Dict[str, Any]:
    return {
        "status":
            "UNBOUND",

        "account_id":
            None,

        "mission_account":
            None,

        "explicit_owner_choice":
            False,

        "authority":
            "PENDING_ACCOUNT_CONTEXT",

        "implicit_default_allowed":
            False,
    }


def pending_owner_fit() -> Dict[str, Any]:
    return {
        "status":
            "PENDING_OBRISK",

        "evaluated":
            False,

        "eligible":
            None,

        "growth_objective_ref":
            None,

        "risk_envelope_ref":
            None,

        "account_policy_ref":
            None,

        "authority":
            "PENDING_OBRISK_OWNER_FIT",

        "reason":
            (
                "Owner-fit eligibility has not "
                "been evaluated by OBRISK."
            ),
    }


def pending_mode_authority() -> Dict[str, Any]:
    return {
        "status":
            "PENDING_OBMODE",

        "mode":
            None,

        "authority":
            "PENDING_OBMODE",

        "execution_authority":
            False,

        "broker_submission_authority":
            False,

        "capital_movement_authority":
            False,
    }


def intent_boundaries() -> Dict[str, Any]:
    return {
        "mode_neutral":
            True,

        "existing_engine_is_candidate_authority":
            True,

        "existing_options_research_reused":
            True,

        "second_engine_created":
            False,

        "candidate_recalculation":
            False,

        "market_score_recalculation":
            False,

        "owner_fit_auto_assumed":
            False,

        "implicit_account_selection":
            False,

        "automatic_contract_selection":
            False,

        "broker_submission":
            False,

        "capital_movement":
            False,

        "hybrid_execution":
            False,

        "automatic_execution":
            False,

        "live_auto_locked":
            True,
    }


def _hash_material(
    intent: Dict[str, Any],
) -> Dict[str, Any]:

    return {
        "schema_version":
            intent.get(
                "schema_version"
            ),

        "intent_id":
            intent.get(
                "intent_id"
            ),

        "candidate":
            intent.get(
                "candidate"
            ),

        "options_research":
            intent.get(
                "options_research"
            ),

        "account_authority":
            intent.get(
                "account_authority"
            ),

        "account_context":
            intent.get(
                "account_context"
            ),

        "owner_fit":
            intent.get(
                "owner_fit"
            ),

        "mode_authority":
            intent.get(
                "mode_authority"
            ),

        "lifecycle_state":
            intent.get(
                "lifecycle_state"
            ),

        "boundaries":
            intent.get(
                "boundaries"
            ),
    }


def recompute_intent_hash(
    intent: Dict[str, Any],
) -> str:
    return stable_hash(
        _hash_material(
            intent
        )
    )


def build_trade_intent(
    payload: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        payload,
        dict,
    ):
        raise ValueError(
            "Trade intent payload must be an object."
        )

    violations = (
        _scan_forbidden_truthy(
            payload
        )
    )

    if violations:
        raise ValueError(
            "OBTradeIntent cannot carry "
            "execution/selection authority: "
            + ", ".join(
                violations
            )
        )

    candidate = (
        normalize_candidate(
            payload.get(
                "candidate"
            )
        )
    )

    options = (
        normalize_options_research(
            payload.get(
                "options_research"
            )
        )
    )

    candidate_fingerprint = (
        candidate[
            "candidate_fingerprint"
        ]
    )

    intent_id = (
        "obti_"
        + candidate_fingerprint[:28]
    )

    state = (
        "OWNER_FIT_PENDING"
        if (
            options.get(
                "status"
            )
            ==
            "RESEARCH_BOUND"
        )
        else "RESEARCH_PENDING"
    )

    now = (
        utc_now_iso()
    )

    intent = {
        "schema_version":
            SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "intent_id":
            intent_id,

        "created_at":
            now,

        "updated_at":
            now,

        "candidate":
            candidate,

        "options_research":
            options,

        "account_authority":
            account_authority_reference(),

        "account_context":
            pending_account_context(),

        "owner_fit":
            pending_owner_fit(),

        "mode_authority":
            pending_mode_authority(),

        "lifecycle_state":
            state,

        "lifecycle_history": [
            {
                "state":
                    state,

                "timestamp":
                    now,

                "reason":
                    (
                        "canonical_intent_created"
                    ),
            }
        ],

        "manual_live_bridge": {
            "downstream_service":
                (
                    "web."
                    "ob_manual_live_"
                    "candidate_decision_handoff"
                ),

            "ready":
                False,

            "blocked_until": [
                "owner_fit_evaluated",
                "explicit_account_context",
                "Manual Live mode authority",
            ],
        },

        "hybrid_bridge": {
            "ready":
                False,

            "blocked_until": [
                "OBHYB authority",
                "owner authorization",
                "Safety Kernel",
            ],
        },

        "automated_bridge": {
            "ready":
                False,

            "blocked_until": [
                "OBAUTO authority",
                "Safety Kernel",
                "graduation gate",
            ],
        },

        "boundaries":
            intent_boundaries(),
    }

    intent[
        "intent_hash"
    ] = (
        recompute_intent_hash(
            intent
        )
    )

    return intent


def validate_trade_intent(
    intent: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        intent,
        dict,
    ):
        raise ValueError(
            "Trade intent must be an object."
        )

    if (
        intent.get(
            "schema_version"
        )
        != SCHEMA_VERSION
    ):
        raise ValueError(
            "Unknown trade intent schema."
        )

    state = intent.get(
        "lifecycle_state"
    )

    if state not in (
        LIFECYCLE_STATES
    ):
        raise ValueError(
            f"Invalid lifecycle state: {state}"
        )

    violations = (
        _scan_forbidden_truthy(
            intent.get(
                "boundaries",
                {}
            )
        )
    )

    if violations:
        raise ValueError(
            "Trade intent boundaries "
            "contain forbidden authority."
        )

    expected = (
        recompute_intent_hash(
            intent
        )
    )

    actual = (
        intent.get(
            "intent_hash"
        )
    )

    if expected != actual:
        raise ValueError(
            "Trade intent integrity hash mismatch."
        )

    return {
        "ok":
            True,

        "intent_id":
            intent.get(
                "intent_id"
            ),

        "state":
            state,

        "integrity_verified":
            True,
    }


def db_path(
    path: Optional[
        Path
    ] = None,
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


def connect(
    path: Optional[
        Path
    ] = None,
):
    conn = sqlite3.connect(
        db_path(
            path
        )
    )

    conn.row_factory = (
        sqlite3.Row
    )

    return conn


def init_trade_intent_db(
    path: Optional[
        Path
    ] = None,
) -> Dict[str, Any]:

    with connect(
        path
    ) as conn:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS
            ob_trade_intents (
                intent_id TEXT PRIMARY KEY,
                schema_version TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                lifecycle_state TEXT NOT NULL,
                candidate_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                candidate_fingerprint TEXT NOT NULL,
                research_fingerprint TEXT,
                intent_hash TEXT NOT NULL,
                intent_json TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS
            ob_trade_intent_events (
                event_id INTEGER
                    PRIMARY KEY AUTOINCREMENT,

                intent_id TEXT NOT NULL,
                state TEXT NOT NULL,
                event_type TEXT NOT NULL,
                reason TEXT NOT NULL,
                evidence_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_ob_trade_intent_state
            ON ob_trade_intents (
                lifecycle_state,
                updated_at
            )
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_ob_trade_intent_symbol
            ON ob_trade_intents (
                symbol,
                updated_at
            )
            """
        )

        conn.commit()

    return {
        "ok":
            True,

        "schema_version":
            SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "db_path":
            str(
                db_path(
                    path
                )
            ),

        "mode_neutral":
            True,

        "explicit_creation_only":
            True,

        "auto_created_on_engine_feed_read":
            False,
    }


def _store_intent(
    intent: Dict[str, Any],
    path: Optional[
        Path
    ] = None,
) -> None:

    validate_trade_intent(
        intent
    )

    candidate = (
        intent[
            "candidate"
        ]
    )

    research = (
        intent[
            "options_research"
        ]
    )

    with connect(
        path
    ) as conn:

        conn.execute(
            """
            INSERT INTO ob_trade_intents (
                intent_id,
                schema_version,
                created_at,
                updated_at,
                lifecycle_state,
                candidate_id,
                symbol,
                candidate_fingerprint,
                research_fingerprint,
                intent_hash,
                intent_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(intent_id)
            DO UPDATE SET
                updated_at=excluded.updated_at,
                lifecycle_state=excluded.lifecycle_state,
                research_fingerprint=excluded.research_fingerprint,
                intent_hash=excluded.intent_hash,
                intent_json=excluded.intent_json
            """,
            (
                intent[
                    "intent_id"
                ],

                intent[
                    "schema_version"
                ],

                intent[
                    "created_at"
                ],

                intent[
                    "updated_at"
                ],

                intent[
                    "lifecycle_state"
                ],

                candidate[
                    "candidate_id"
                ],

                candidate[
                    "symbol"
                ],

                candidate[
                    "candidate_fingerprint"
                ],

                research.get(
                    "research_fingerprint"
                ),

                intent[
                    "intent_hash"
                ],

                canonical_json(
                    intent
                ),
            ),
        )

        conn.commit()


def _write_event(
    *,
    intent_id: str,
    state: str,
    event_type: str,
    reason: str,
    evidence: Optional[
        Dict[str, Any]
    ] = None,
    path: Optional[
        Path
    ] = None,
) -> None:

    with connect(
        path
    ) as conn:

        conn.execute(
            """
            INSERT INTO ob_trade_intent_events (
                intent_id,
                state,
                event_type,
                reason,
                evidence_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                intent_id,
                state,
                event_type,
                reason,
                canonical_json(
                    evidence or {}
                ),
                utc_now_iso(),
            ),
        )

        conn.commit()


def create_trade_intent(
    payload: Dict[str, Any],
    path: Optional[
        Path
    ] = None,
) -> Dict[str, Any]:

    init_trade_intent_db(
        path
    )

    intent = (
        build_trade_intent(
            payload
        )
    )

    existing = (
        get_trade_intent(
            intent[
                "intent_id"
            ],
            path=path,
        )
    )

    if existing:
        return {
            "ok":
                True,

            "created":
                False,

            "idempotent":
                True,

            "intent":
                existing,
        }

    _store_intent(
        intent,
        path=path,
    )

    _write_event(
        intent_id=(
            intent[
                "intent_id"
            ]
        ),

        state=(
            intent[
                "lifecycle_state"
            ]
        ),

        event_type=(
            "INTENT_CREATED"
        ),

        reason=(
            "canonical_trade_intent_created"
        ),

        evidence={
            "candidate_fingerprint":
                intent[
                    "candidate"
                ][
                    "candidate_fingerprint"
                ],

            "research_fingerprint":
                intent[
                    "options_research"
                ].get(
                    "research_fingerprint"
                ),
        },

        path=path,
    )

    return {
        "ok":
            True,

        "created":
            True,

        "idempotent":
            False,

        "intent":
            intent,
    }


def get_trade_intent(
    intent_id: str,
    path: Optional[
        Path
    ] = None,
) -> Optional[
    Dict[str, Any]
]:

    init_trade_intent_db(
        path
    )

    with connect(
        path
    ) as conn:

        row = conn.execute(
            """
            SELECT intent_json
            FROM ob_trade_intents
            WHERE intent_id = ?
            """,
            (
                intent_id,
            ),
        ).fetchone()

    if row is None:
        return None

    intent = json.loads(
        row[
            "intent_json"
        ]
    )

    validate_trade_intent(
        intent
    )

    return intent


def list_trade_intent_events(
    intent_id: str,
    path: Optional[
        Path
    ] = None,
) -> List[
    Dict[str, Any]
]:

    init_trade_intent_db(
        path
    )

    with connect(
        path
    ) as conn:

        rows = conn.execute(
            """
            SELECT *
            FROM ob_trade_intent_events
            WHERE intent_id = ?
            ORDER BY event_id ASC
            """,
            (
                intent_id,
            ),
        ).fetchall()

    results = []

    for row in rows:
        results.append(
            {
                "event_id":
                    row[
                        "event_id"
                    ],

                "intent_id":
                    row[
                        "intent_id"
                    ],

                "state":
                    row[
                        "state"
                    ],

                "event_type":
                    row[
                        "event_type"
                    ],

                "reason":
                    row[
                        "reason"
                    ],

                "evidence":
                    json.loads(
                        row[
                            "evidence_json"
                        ]
                        or "{}"
                    ),

                "created_at":
                    row[
                        "created_at"
                    ],
            }
        )

    return results


def bind_options_research(
    intent_id: str,
    research: Dict[str, Any],
    path: Optional[
        Path
    ] = None,
) -> Dict[str, Any]:

    intent = (
        get_trade_intent(
            intent_id,
            path=path,
        )
    )

    if not intent:
        raise KeyError(
            f"Trade intent not found: {intent_id}"
        )

    if (
        intent[
            "lifecycle_state"
        ]
        !=
        "RESEARCH_PENDING"
    ):
        raise ValueError(
            "Options research may only be bound "
            "while RESEARCH_PENDING."
        )

    normalized = (
        normalize_options_research(
            research
        )
    )

    if (
        normalized[
            "status"
        ]
        !=
        "RESEARCH_BOUND"
    ):
        raise ValueError(
            "Source-backed options research "
            "was not supplied."
        )

    now = (
        utc_now_iso()
    )

    intent[
        "options_research"
    ] = normalized

    intent[
        "lifecycle_state"
    ] = (
        "OWNER_FIT_PENDING"
    )

    intent[
        "updated_at"
    ] = now

    intent[
        "lifecycle_history"
    ].append(
        {
            "state":
                "OWNER_FIT_PENDING",

            "timestamp":
                now,

            "reason":
                "source_backed_options_research_bound",
        }
    )

    intent[
        "intent_hash"
    ] = (
        recompute_intent_hash(
            intent
        )
    )

    _store_intent(
        intent,
        path=path,
    )

    _write_event(
        intent_id=intent_id,
        state="OWNER_FIT_PENDING",
        event_type="OPTIONS_RESEARCH_BOUND",
        reason="source_backed_options_research_bound",
        evidence={
            "research_fingerprint":
                normalized[
                    "research_fingerprint"
                ],
        },
        path=path,
    )

    return {
        "ok":
            True,

        "intent":
            intent,
    }


def transition_trade_intent(
    intent_id: str,
    next_state: str,
    *,
    reason: str,
    evidence: Optional[
        Dict[str, Any]
    ] = None,
    path: Optional[
        Path
    ] = None,
) -> Dict[str, Any]:

    intent = (
        get_trade_intent(
            intent_id,
            path=path,
        )
    )

    if not intent:
        raise KeyError(
            f"Trade intent not found: {intent_id}"
        )

    current = (
        intent[
            "lifecycle_state"
        ]
    )

    if next_state not in (
        ALLOWED_TRANSITIONS[
            current
        ]
    ):
        raise ValueError(
            f"Illegal OBTradeIntent transition: "
            f"{current} -> {next_state}"
        )

    gated_states = {
        "OWNER_REVIEW_READY",
        "OWNER_SELECTED",
        "TRACKING",
        "CLOSED",
    }

    if (
        next_state
        in gated_states
    ):
        owner_fit = (
            intent[
                "owner_fit"
            ]
        )

        account_context = (
            intent[
                "account_context"
            ]
        )

        if (
            owner_fit.get(
                "evaluated"
            )
            is not True
        ):
            raise ValueError(
                "OBRISK owner-fit evaluation "
                "is required before owner review."
            )

        if (
            owner_fit.get(
                "eligible"
            )
            is not True
            or
            owner_fit.get(
                "status"
            )
            !=
            "NOW"
        ):
            raise ValueError(
                "OBRISK owner-fit candidate must be eligible NOW "
                "before owner review."
            )

        if (
            account_context.get(
                "status"
            )
            !=
            "BOUND"
        ):
            raise ValueError(
                "Explicit account context is required."
            )

    if (
        next_state
        in {
            "OWNER_SELECTED",
            "TRACKING",
            "CLOSED",
        }
    ):
        mode = (
            intent[
                "mode_authority"
            ]
        )

        if (
            mode.get(
                "status"
            )
            !=
            "BOUND"
        ):
            raise ValueError(
                "OBMODE authority is required."
            )

    now = (
        utc_now_iso()
    )

    intent[
        "lifecycle_state"
    ] = (
        next_state
    )

    intent[
        "updated_at"
    ] = (
        now
    )

    intent[
        "lifecycle_history"
    ].append(
        {
            "state":
                next_state,

            "timestamp":
                now,

            "reason":
                clean_text(
                    reason,
                    "lifecycle_transition",
                ),

            "evidence":
                deepcopy(
                    evidence or {}
                ),
        }
    )

    intent[
        "intent_hash"
    ] = (
        recompute_intent_hash(
            intent
        )
    )

    _store_intent(
        intent,
        path=path,
    )

    _write_event(
        intent_id=intent_id,
        state=next_state,
        event_type="STATE_TRANSITION",
        reason=reason,
        evidence=evidence,
        path=path,
    )

    return {
        "ok":
            True,

        "intent":
            intent,
    }


def manual_live_handoff_payload(
    intent: Dict[str, Any],
    *,
    owner_id: str,
) -> Dict[str, Any]:
    """
    Produce the payload shape already accepted by GP041.

    This bridge is intentionally LOCKED today because OBRISK and
    OBMODE have not yet bound their authority into the intent.
    """

    validate_trade_intent(
        intent
    )

    owner_fit = (
        intent[
            "owner_fit"
        ]
    )

    account = (
        intent[
            "account_context"
        ]
    )

    mode = (
        intent[
            "mode_authority"
        ]
    )

    blockers = []

    if (
        owner_fit.get(
            "evaluated"
        )
        is not True
    ):
        blockers.append(
            "owner_fit_not_evaluated"
        )
    elif (
        owner_fit.get(
            "eligible"
        )
        is not True
        or
        owner_fit.get(
            "status"
        )
        !=
        "NOW"
    ):
        blockers.append(
            "owner_fit_not_eligible_now"
        )

    if (
        account.get(
            "status"
        )
        !=
        "BOUND"
    ):
        blockers.append(
            "account_context_not_bound"
        )

    if (
        mode.get(
            "status"
        )
        !=
        "BOUND"
        or
        mode.get(
            "mode"
        )
        !=
        "MANUAL_LIVE_1"
    ):
        blockers.append(
            "manual_live_mode_not_bound"
        )

    if blockers:
        raise ValueError(
            "Manual Live bridge is locked: "
            + ", ".join(
                blockers
            )
        )

    candidate = deepcopy(
        intent[
            "candidate"
        ][
            "source_payload"
        ]
    )

    candidate[
        "candidate_id"
    ] = (
        intent[
            "candidate"
        ][
            "candidate_id"
        ]
    )

    candidate[
        "symbol"
    ] = (
        intent[
            "candidate"
        ][
            "symbol"
        ]
    )

    candidate[
        "ob_trade_intent"
    ] = {
        "intent_id":
            intent[
                "intent_id"
            ],

        "intent_hash":
            intent[
                "intent_hash"
            ],

        "candidate_fingerprint":
            intent[
                "candidate"
            ][
                "candidate_fingerprint"
            ],

        "schema_version":
            SCHEMA_VERSION,
    }

    return {
        "owner_id":
            clean_text(
                owner_id,
                "owner",
            ),

        "candidate":
            candidate,

        "decision_status":
            "queued_for_owner_decision",

        "decision_intent":
            "review_candidate",

        "lane":
            "Manual Live Level 1",

        "review_lane":
            (
                "Canonical OBTradeIntent "
                "→ Candidate Decision Handoff"
            ),

        "handoff_reason":
            (
                "Canonical trade intent is ready "
                "for owner Manual Live review."
            ),

        # Explicit safety flags:
        "real_broker_order_submitted":
            False,

        "broker_api_used":
            False,

        "real_capital_moved":
            False,

        "auto_execute":
            False,
    }


def trade_intent_contract() -> Dict[str, Any]:

    return {
        "schema_version":
            SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "authority":
            "CANONICAL_OB_TRADE_INTENT",

        "mode_neutral":
            True,

        "candidate_authority":
            "EXISTING_CANONICAL_ENGINE",

        "options_research_authority":
            "OB_OPTIONS_RESEARCH_V1",

        "owner_fit_authority":
            "PENDING_OBRISK",

        # OBRISK006–010 concrete owner-fit evaluator.
        #
        # The generic field above remains PENDING_OBRISK for
        # sealed OBENG lifecycle compatibility.
        "owner_fit_eligibility_authority":
            "OB_OWNER_FIT_ELIGIBILITY_V1",

        "mode_authority":
            "PENDING_OBMODE",

        "account_authority":
            "OB_ENGINE_ACCOUNT_AUTHORITY_V1",

        "durable_persistence":
            True,

        "persistence_format":
            "SQLite",

        "explicit_creation_only":
            True,

        "auto_created_on_engine_feed_read":
            False,

        "manual_live_downstream":
            (
                "OB_GIANT_PACK_041_REAL_"
                "CANDIDATE_TO_DECISION_HANDOFF"
            ),

        "hybrid_downstream":
            "LOCKED_PENDING_OBHYB",

        "automated_downstream":
            "LOCKED_PENDING_OBAUTO",

        "lifecycle_states":
            list(
                LIFECYCLE_STATES
            ),

        "boundaries":
            intent_boundaries(),
    }


# OBRISK001-005_OWNER_OPERATING_PROFILE_BINDING
#
# Bind an explicitly owner-confirmed, per-account operating profile into the
# existing canonical OBTradeIntent.
#
# IMPORTANT:
#
# This DOES NOT evaluate the candidate against the risk envelope yet.
#
# That belongs to OBRISK006–010.
#
# Therefore:
#
#     account_context → BOUND
#
# but:
#
#     owner_fit.evaluated → False
#     owner_fit.status    → PENDING_OBRISK_ELIGIBILITY
#     lifecycle_state     → remains unchanged
#
# Mode authority also remains untouched / PENDING_OBMODE.
#

def bind_owner_operating_profile(
    intent_id: str,
    profile: Dict[str, Any],
    path: Optional[
        Path
    ] = None,
) -> Dict[str, Any]:

    from web.ob_owner_operating_profile import (
        SCHEMA_VERSION
        as OWNER_PROFILE_SCHEMA_VERSION,
    )

    from web.ob_owner_operating_profile import (
        validate_operating_profile,
    )

    profile = (
        validate_operating_profile(
            profile,
            require_active=True,
        )
    )

    intent = (
        get_trade_intent(
            intent_id,
            path=path,
        )
    )

    if not intent:
        raise KeyError(
            f"Trade intent not found: {intent_id}"
        )

    current_state = (
        intent[
            "lifecycle_state"
        ]
    )

    if current_state not in {
        "RESEARCH_PENDING",
        "OWNER_FIT_PENDING",
    }:
        raise ValueError(
            "Owner operating profile may only be bound "
            "before owner-fit review has advanced."
        )

    account = deepcopy(
        profile[
            "account"
        ]
    )

    growth = deepcopy(
        profile[
            "growth_objective"
        ]
    )

    risk = deepcopy(
        profile[
            "risk_envelope"
        ]
    )

    now = (
        utc_now_iso()
    )

    intent[
        "account_context"
    ] = {
        "status":
            "BOUND",

        "account_key":
            account[
                "account_key"
            ],

        "display_label":
            account[
                "display_label"
            ],

        "explicit_owner_choice":
            True,

        "implicit_default_allowed":
            False,

        "authority":
            OWNER_PROFILE_SCHEMA_VERSION,

        "owner_id":
            profile[
                "owner_id"
            ],

        "profile_id":
            profile[
                "profile_id"
            ],

        "profile_revision":
            profile[
                "revision"
            ],

        "profile_hash":
            profile[
                "profile_hash"
            ],
    }

    intent[
        "owner_fit"
    ] = {
        "status":
            "PENDING_OBRISK_ELIGIBILITY",

        "evaluated":
            False,

        "eligible":
            None,

        "growth_objective_ref": {
            "profile_id":
                profile[
                    "profile_id"
                ],

            "growth_key":
                growth[
                    "key"
                ],

            "growth_label":
                growth[
                    "label"
                ],
        },

        "risk_envelope_ref": {
            "profile_id":
                profile[
                    "profile_id"
                ],

            "profile_revision":
                profile[
                    "revision"
                ],

            "profile_hash":
                profile[
                    "profile_hash"
                ],

            "risk_key":
                risk[
                    "key"
                ],

            "risk_label":
                risk[
                    "label"
                ],

            "effective_limits":
                deepcopy(
                    risk[
                        "effective_limits"
                    ]
                ),

            "limit_units":
                deepcopy(
                    risk.get(
                        "limit_units",
                        {},
                    )
                ),
        },

        "account_policy_ref": {
            "account_key":
                account[
                    "account_key"
                ],

            "display_label":
                account[
                    "display_label"
                ],

            "profile_id":
                profile[
                    "profile_id"
                ],

            "profile_revision":
                profile[
                    "revision"
                ],
        },

        "authority":
            "PENDING_OBRISK_OWNER_FIT_ELIGIBILITY",

        "reason":
            (
                "Owner operating profile is bound. "
                "Candidate eligibility has not yet been "
                "evaluated by OBRISK006–010."
            ),
    }

    # Manual remains deliberately blocked.
    manual_bridge = (
        intent.get(
            "manual_live_bridge"
        )
    )

    if isinstance(
        manual_bridge,
        dict,
    ):
        manual_bridge[
            "ready"
        ] = False

        manual_bridge[
            "blocked_until"
        ] = [
            "OBRISK006-010 owner-fit eligibility",
            "Manual Live mode authority",
        ]

    # Do NOT touch mode_authority here.
    intent[
        "updated_at"
    ] = now

    intent[
        "lifecycle_history"
    ].append(
        {
            "state":
                current_state,

            "timestamp":
                now,

            "reason":
                "owner_operating_profile_bound",

            "evidence": {
                "profile_id":
                    profile[
                        "profile_id"
                    ],

                "profile_revision":
                    profile[
                        "revision"
                    ],

                "profile_hash":
                    profile[
                        "profile_hash"
                    ],

                "account_key":
                    account[
                        "account_key"
                    ],

                "growth_key":
                    growth[
                        "key"
                    ],

                "risk_key":
                    risk[
                        "key"
                    ],
            },
        }
    )

    intent[
        "intent_hash"
    ] = (
        recompute_intent_hash(
            intent
        )
    )

    _store_intent(
        intent,
        path=path,
    )

    _write_event(
        intent_id=(
            intent[
                "intent_id"
            ]
        ),

        state=current_state,

        event_type=(
            "OWNER_OPERATING_PROFILE_BOUND"
        ),

        reason=(
            "explicit_owner_profile_bound"
        ),

        evidence={
            "profile_id":
                profile[
                    "profile_id"
                ],

            "profile_revision":
                profile[
                    "revision"
                ],

            "profile_hash":
                profile[
                    "profile_hash"
                ],

            "account_key":
                account[
                    "account_key"
                ],

            "growth_key":
                growth[
                    "key"
                ],

            "risk_key":
                risk[
                    "key"
                ],
        },

        path=path,
    )

    return {
        "ok":
            True,

        "bound":
            True,

        "owner_fit_evaluated":
            False,

        "intent":
            intent,
    }
# OBRISK006-010_OWNER_FIT_ELIGIBILITY_BINDING
#
# Evaluate the EXISTING canonical candidate + EXISTING options research against
# the explicitly owner-confirmed, per-account operating profile already bound by
# OBRISK001–005.
#
# This is an OWNER-REVIEW eligibility gate only.
#
# NOW      -> may advance to OWNER_REVIEW_READY
# WATCH    -> stays OWNER_FIT_PENDING
# NOT_YET  -> stays OWNER_FIT_PENDING and remains visible as market truth
#
# NONE of these buckets authorizes broker submission, capital movement, Hybrid
# execution, or Automated execution.
#
def apply_owner_fit_eligibility(
    intent_id: str,
    *,
    evaluation_context: Optional[
        Dict[str, Any]
    ] = None,
    path: Optional[
        Path
    ] = None,
) -> Dict[str, Any]:

    from web.ob_owner_fit_eligibility import (
        SCHEMA_VERSION
        as OWNER_FIT_SCHEMA_VERSION,
    )

    from web.ob_owner_fit_eligibility import (
        evaluate_owner_fit,
    )

    intent = (
        get_trade_intent(
            intent_id,
            path=path,
        )
    )

    if not intent:
        raise KeyError(
            f"Trade intent not found: {intent_id}"
        )

    if (
        intent.get(
            "lifecycle_state"
        )
        !=
        "OWNER_FIT_PENDING"
    ):
        raise ValueError(
            "Owner-fit eligibility may only be evaluated "
            "while OWNER_FIT_PENDING."
        )

    account_context = (
        intent.get(
            "account_context",
            {}
        )
    )

    if (
        account_context.get(
            "status"
        )
        !=
        "BOUND"
    ):
        raise ValueError(
            "Explicit owner account context must be BOUND "
            "before OBRISK006–010 evaluation."
        )

    candidate_before = deepcopy(
        intent[
            "candidate"
        ]
    )

    options_before = deepcopy(
        intent[
            "options_research"
        ]
    )

    result = (
        evaluate_owner_fit(
            intent,
            context=(
                evaluation_context
                or {}
            ),
        )
    )

    owner_fit = deepcopy(
        result[
            "owner_fit"
        ]
    )

    if (
        owner_fit.get(
            "authority"
        )
        !=
        OWNER_FIT_SCHEMA_VERSION
    ):
        raise ValueError(
            "Owner-fit authority mismatch."
        )

    if (
        intent[
            "candidate"
        ]
        !=
        candidate_before
    ):
        raise RuntimeError(
            "OBRISK006–010 changed canonical candidate truth."
        )

    if (
        intent[
            "options_research"
        ]
        !=
        options_before
    ):
        raise RuntimeError(
            "OBRISK006–010 changed canonical options research."
        )

    bucket = (
        owner_fit[
            "bucket"
        ]
    )

    now = (
        utc_now_iso()
    )

    intent[
        "owner_fit"
    ] = owner_fit

    if bucket == "NOW":
        intent[
            "lifecycle_state"
        ] = (
            "OWNER_REVIEW_READY"
        )

        history_state = (
            "OWNER_REVIEW_READY"
        )

        history_reason = (
            "owner_fit_now_ready_for_owner_review"
        )

    else:
        # WATCH and NOT_YET remain visible and re-evaluable.
        # They are not collapsed into execution-style BLOCKED.
        intent[
            "lifecycle_state"
        ] = (
            "OWNER_FIT_PENDING"
        )

        history_state = (
            "OWNER_FIT_PENDING"
        )

        history_reason = (
            "owner_fit_"
            + bucket.lower()
        )

    intent[
        "updated_at"
    ] = now

    intent[
        "lifecycle_history"
    ].append(
        {
            "state":
                history_state,

            "timestamp":
                now,

            "reason":
                history_reason,

            "evidence": {
                "owner_fit_authority":
                    OWNER_FIT_SCHEMA_VERSION,

                "bucket":
                    bucket,

                "eligible":
                    owner_fit.get(
                        "eligible"
                    ),

                "evaluation_fingerprint":
                    owner_fit.get(
                        "evaluation_fingerprint"
                    ),

                "market_truth_mutated":
                    False,

                "market_score_recalculated":
                    False,

                "contract_selected":
                    False,
            },
        }
    )

    manual_bridge = (
        intent.get(
            "manual_live_bridge"
        )
    )

    if isinstance(
        manual_bridge,
        dict,
    ):
        manual_bridge[
            "ready"
        ] = False

        if bucket == "NOW":
            manual_bridge[
                "blocked_until"
            ] = [
                "Manual Live mode authority",
                "explicit owner security/contract choice",
            ]
        else:
            manual_bridge[
                "blocked_until"
            ] = [
                "owner_fit status NOW",
                "Manual Live mode authority",
            ]

    # OBMODE remains a separate authority pack.
    # Do NOT touch mode_authority here.

    intent[
        "intent_hash"
    ] = (
        recompute_intent_hash(
            intent
        )
    )

    _store_intent(
        intent,
        path=path,
    )

    _write_event(
        intent_id=(
            intent[
                "intent_id"
            ]
        ),

        state=(
            intent[
                "lifecycle_state"
            ]
        ),

        event_type=(
            "OWNER_FIT_ELIGIBILITY_EVALUATED"
        ),

        reason=(
            history_reason
        ),

        evidence={
            "owner_fit_authority":
                OWNER_FIT_SCHEMA_VERSION,

            "bucket":
                bucket,

            "eligible":
                owner_fit.get(
                    "eligible"
                ),

            "evaluation_fingerprint":
                owner_fit.get(
                    "evaluation_fingerprint"
                ),

            "hard_failure_reasons":
                deepcopy(
                    owner_fit.get(
                        "hard_failure_reasons",
                        [],
                    )
                ),

            "watch_reasons":
                deepcopy(
                    owner_fit.get(
                        "watch_reasons",
                        [],
                    )
                ),
        },

        path=path,
    )

    return {
        "ok":
            True,

        "evaluated":
            True,

        "bucket":
            bucket,

        "eligible":
            owner_fit.get(
                "eligible"
            ),

        "advanced_to_owner_review":
            (
                bucket
                ==
                "NOW"
            ),

        "intent":
            intent,
    }
