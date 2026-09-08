
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import json
import sqlite3


SCHEMA_VERSION = "OB_COMMAND_EVENT_CAUSAL_V1"
COMMAND_SCHEMA_VERSION = "OB_COMMAND_V1"
EVENT_SCHEMA_VERSION = "OB_DOMAIN_EVENT_V1"
INVALIDATION_SCHEMA_VERSION = "OB_CAUSAL_INVALIDATION_PLAN_V1"

SERVICE_VERSION = (
    "OBEVENT001_010_COMMAND_EVENT_CAUSAL_INVALIDATION"
)


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_DB_PATH = (
    ROOT
    / "data"
    / "_local_archives"
    / "ob_command_event_ledger.sqlite3"
)


FORBIDDEN_TRUTHY_COMMAND_KEYS = {
    "broker_submission",
    "broker_submission_allowed",
    "capital_movement",
    "capital_movement_allowed",
    "automatic_contract_selection",
    "automatic_contract_selection_allowed",
    "automatic_execution",
    "automatic_execution_allowed",
    "auto_execute",
    "hybrid_execution",
    "hybrid_execution_allowed",
    "live_automation_allowed",
    "submit_order",
    "submit_real_broker_order",
    "place_order",
    "place_trade",
    "real_capital_moved",
    "move_capital",
}


ACTOR_TYPES = {
    "OWNER",
    "SYSTEM",
    "AUTHORITY",
}


COMMAND_STATUSES = {
    "REQUESTED",
    "ACCEPTED",
    "REJECTED",
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


def clean_text(
    value: Any,
) -> str:
    return (
        ""
        if value is None
        else str(
            value
        ).strip()
    )


def safe_object(
    value: Any,
) -> Dict[str, Any]:
    return (
        deepcopy(
            value
        )
        if isinstance(
            value,
            dict,
        )
        else {}
    )


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

        for key, nested in value.items():

            next_path = (
                f"{path}.{key}"
            )

            if (
                key
                in
                FORBIDDEN_TRUTHY_COMMAND_KEYS
                and
                bool(
                    nested
                )
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


def _registry() -> Dict[str, Any]:

    from web.ob_authority_registry import (
        build_canonical_authority_registry,
    )

    return (
        build_canonical_authority_registry()
    )


def active_authority_ids() -> set[str]:

    registry = _registry()

    return {
        record[
            "authority_id"
        ]
        for record
        in registry[
            "authority_records"
        ].values()
    }


def _command_material(
    command: Dict[str, Any],
) -> Dict[str, Any]:

    return {
        "schema_version":
            command.get(
                "schema_version"
            ),

        "command_type":
            command.get(
                "command_type"
            ),

        "target_authority":
            command.get(
                "target_authority"
            ),

        "actor_type":
            command.get(
                "actor_type"
            ),

        "actor_id":
            command.get(
                "actor_id"
            ),

        "account_key":
            command.get(
                "account_key"
            ),

        "payload":
            safe_object(
                command.get(
                    "payload"
                )
            ),

        "idempotency_key":
            command.get(
                "idempotency_key"
            ),

        "expected_state_ref":
            command.get(
                "expected_state_ref"
            ),

        "correlation_id":
            command.get(
                "correlation_id"
            ),

        "causation_event_id":
            command.get(
                "causation_event_id"
            ),
    }


def recompute_command_fingerprint(
    command: Dict[str, Any],
) -> str:

    return stable_hash(
        _command_material(
            command
        )
    )


def build_command(
    *,
    command_type: Any,
    target_authority: Any,
    actor_id: Any,
    payload: Optional[
        Dict[str, Any]
    ],
    idempotency_key: Any,
    actor_type: Any = "OWNER",
    account_key: Any = None,
    expected_state_ref: Any = None,
    correlation_id: Any = None,
    causation_event_id: Any = None,
) -> Dict[str, Any]:

    command_type = clean_text(
        command_type
    ).upper()

    target_authority = clean_text(
        target_authority
    )

    actor_id = clean_text(
        actor_id
    )

    actor_type = clean_text(
        actor_type
    ).upper()

    idempotency_key = clean_text(
        idempotency_key
    )

    account_key = (
        clean_text(
            account_key
        )
        or None
    )

    expected_state_ref = (
        clean_text(
            expected_state_ref
        )
        or None
    )

    causation_event_id = (
        clean_text(
            causation_event_id
        )
        or None
    )

    if not command_type:
        raise ValueError(
            "command_type is required."
        )

    if not target_authority:
        raise ValueError(
            "target_authority is required."
        )

    if target_authority not in (
        active_authority_ids()
    ):
        raise ValueError(
            (
                "Command target is not an active "
                f"canonical authority: {target_authority}"
            )
        )

    if (
        target_authority
        ==
        SCHEMA_VERSION
    ):
        raise ValueError(
            "OBEVENT may not command itself."
        )

    if actor_type not in (
        ACTOR_TYPES
    ):
        raise ValueError(
            (
                "actor_type must be one of: "
                + ", ".join(
                    sorted(
                        ACTOR_TYPES
                    )
                )
            )
        )

    if not actor_id:
        raise ValueError(
            "actor_id is required."
        )

    if not idempotency_key:
        raise ValueError(
            "idempotency_key is required."
        )

    payload = safe_object(
        payload
    )

    violations = (
        _scan_forbidden_truthy(
            payload
        )
    )

    if violations:
        raise ValueError(
            (
                "Current OBEVENT phase forbids "
                "execution/capital authority requests: "
                + ", ".join(
                    violations
                )
            )
        )

    if (
        causation_event_id
        is not None
        and
        not clean_text(
            correlation_id
        )
    ):
        raise ValueError(
            (
                "A command caused by another event "
                "must carry that causal chain's correlation_id."
            )
        )

    provisional = {
        "schema_version":
            COMMAND_SCHEMA_VERSION,

        "command_type":
            command_type,

        "target_authority":
            target_authority,

        "actor_type":
            actor_type,

        "actor_id":
            actor_id,

        "account_key":
            account_key,

        "payload":
            payload,

        "idempotency_key":
            idempotency_key,

        "expected_state_ref":
            expected_state_ref,

        "correlation_id":
            (
                clean_text(
                    correlation_id
                )
                or None
            ),

        "causation_event_id":
            causation_event_id,
    }

    provisional_fp = (
        stable_hash(
            provisional
        )
    )

    if (
        provisional[
            "correlation_id"
        ]
        is None
    ):
        provisional[
            "correlation_id"
        ] = (
            "obcorr_"
            + provisional_fp[:24]
        )

    fingerprint = (
        stable_hash(
            provisional
        )
    )

    command_id = (
        "obcmd_"
        + fingerprint[:28]
    )

    return {
        **provisional,

        "command_id":
            command_id,

        "command_fingerprint":
            fingerprint,

        "requested_at":
            utc_now_iso(),

        "status":
            "REQUESTED",

        "request_is_truth":
            False,

        "domain_mutation_performed_here":
            False,

        "execution_authority":
            False,

        "broker_submission":
            False,

        "capital_movement":
            False,

        "automatic_contract_selection":
            False,

        "automatic_execution":
            False,
    }


def validate_command(
    command: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        command,
        dict,
    ):
        raise ValueError(
            "Command must be an object."
        )

    if (
        command.get(
            "schema_version"
        )
        !=
        COMMAND_SCHEMA_VERSION
    ):
        raise ValueError(
            "Unknown command schema."
        )

    if (
        command.get(
            "status"
        )
        not in
        COMMAND_STATUSES
    ):
        raise ValueError(
            "Unknown command status."
        )

    target = clean_text(
        command.get(
            "target_authority"
        )
    )

    if target not in (
        active_authority_ids()
    ):
        raise ValueError(
            "Command target authority is not active."
        )

    if target == SCHEMA_VERSION:
        raise ValueError(
            "OBEVENT may not command itself."
        )

    if (
        clean_text(
            command.get(
                "actor_type"
            )
        ).upper()
        not in
        ACTOR_TYPES
    ):
        raise ValueError(
            "Invalid actor_type."
        )

    if not clean_text(
        command.get(
            "actor_id"
        )
    ):
        raise ValueError(
            "Command actor_id missing."
        )

    if not clean_text(
        command.get(
            "idempotency_key"
        )
    ):
        raise ValueError(
            "Command idempotency_key missing."
        )

    violations = (
        _scan_forbidden_truthy(
            command.get(
                "payload"
            )
        )
    )

    if violations:
        raise ValueError(
            "Command contains forbidden authority request."
        )

    expected_fp = (
        recompute_command_fingerprint(
            command
        )
    )

    if (
        command.get(
            "command_fingerprint"
        )
        !=
        expected_fp
    ):
        raise ValueError(
            "Command fingerprint mismatch."
        )

    expected_id = (
        "obcmd_"
        + expected_fp[:28]
    )

    if (
        command.get(
            "command_id"
        )
        !=
        expected_id
    ):
        raise ValueError(
            "Command ID mismatch."
        )

    if (
        command.get(
            "request_is_truth"
        )
        is not False
    ):
        raise ValueError(
            "Command request may not claim truth."
        )

    for field in (
        "domain_mutation_performed_here",
        "execution_authority",
        "broker_submission",
        "capital_movement",
        "automatic_contract_selection",
        "automatic_execution",
    ):
        if (
            command.get(
                field
            )
            is not False
        ):
            raise ValueError(
                (
                    "Command envelope contains "
                    f"forbidden authority: {field}"
                )
            )

    return deepcopy(
        command
    )


def _event_material(
    event: Dict[str, Any],
) -> Dict[str, Any]:

    return {
        "schema_version":
            event.get(
                "schema_version"
            ),

        "command_id":
            event.get(
                "command_id"
            ),

        "source_authority":
            event.get(
                "source_authority"
            ),

        "event_type":
            event.get(
                "event_type"
            ),

        "aggregate_type":
            event.get(
                "aggregate_type"
            ),

        "aggregate_id":
            event.get(
                "aggregate_id"
            ),

        "before_state_ref":
            event.get(
                "before_state_ref"
            ),

        "after_state_ref":
            event.get(
                "after_state_ref"
            ),

        "payload":
            safe_object(
                event.get(
                    "payload"
                )
            ),

        "correlation_id":
            event.get(
                "correlation_id"
            ),

        "causation_event_id":
            event.get(
                "causation_event_id"
            ),
    }


def recompute_event_fingerprint(
    event: Dict[str, Any],
) -> str:

    return stable_hash(
        _event_material(
            event
        )
    )


def build_accepted_event(
    command: Dict[str, Any],
    *,
    source_authority: Any,
    event_type: Any,
    aggregate_type: Any,
    aggregate_id: Any,
    before_state_ref: Any,
    after_state_ref: Any,
    payload: Optional[
        Dict[str, Any]
    ] = None,
) -> Dict[str, Any]:

    command = validate_command(
        command
    )

    source_authority = clean_text(
        source_authority
    )

    event_type = clean_text(
        event_type
    ).upper()

    aggregate_type = clean_text(
        aggregate_type
    ).upper()

    aggregate_id = clean_text(
        aggregate_id
    )

    before_state_ref = clean_text(
        before_state_ref
    )

    after_state_ref = clean_text(
        after_state_ref
    )

    if (
        source_authority
        !=
        command[
            "target_authority"
        ]
    ):
        raise ValueError(
            (
                "Accepted event source authority must "
                "equal the command target authority."
            )
        )

    if source_authority == SCHEMA_VERSION:
        raise ValueError(
            "OBEVENT may not emit domain truth about itself."
        )

    if not event_type:
        raise ValueError(
            "event_type is required."
        )

    if not aggregate_type:
        raise ValueError(
            "aggregate_type is required."
        )

    if not aggregate_id:
        raise ValueError(
            "aggregate_id is required."
        )

    if not before_state_ref:
        raise ValueError(
            "before_state_ref is required."
        )

    if not after_state_ref:
        raise ValueError(
            "after_state_ref is required."
        )

    if (
        before_state_ref
        ==
        after_state_ref
    ):
        raise ValueError(
            (
                "Accepted event requires an actual "
                "accepted state change."
            )
        )

    event = {
        "schema_version":
            EVENT_SCHEMA_VERSION,

        "command_id":
            command[
                "command_id"
            ],

        "source_authority":
            source_authority,

        "event_type":
            event_type,

        "aggregate_type":
            aggregate_type,

        "aggregate_id":
            aggregate_id,

        "before_state_ref":
            before_state_ref,

        "after_state_ref":
            after_state_ref,

        "payload":
            safe_object(
                payload
            ),

        "correlation_id":
            command[
                "correlation_id"
            ],

        "causation_event_id":
            command.get(
                "causation_event_id"
            ),

        "occurred_at":
            utc_now_iso(),

        "accepted_change":
            True,

        "request_is_truth":
            False,

        "domain_mutation_performed_here":
            False,

        "execution_authority":
            False,

        "broker_submission":
            False,

        "capital_movement":
            False,

        "automatic_contract_selection":
            False,

        "automatic_execution":
            False,
    }

    fingerprint = (
        recompute_event_fingerprint(
            event
        )
    )

    event[
        "event_fingerprint"
    ] = fingerprint

    event[
        "event_id"
    ] = (
        "obevt_"
        + fingerprint[:28]
    )

    return event


def validate_event(
    event: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        event,
        dict,
    ):
        raise ValueError(
            "Event must be an object."
        )

    if (
        event.get(
            "schema_version"
        )
        !=
        EVENT_SCHEMA_VERSION
    ):
        raise ValueError(
            "Unknown event schema."
        )

    source_authority = clean_text(
        event.get(
            "source_authority"
        )
    )

    if (
        source_authority
        not in
        active_authority_ids()
    ):
        raise ValueError(
            "Event source authority is not active."
        )

    if source_authority == SCHEMA_VERSION:
        raise ValueError(
            "OBEVENT may not be its own domain event source."
        )

    if (
        event.get(
            "accepted_change"
        )
        is not True
    ):
        raise ValueError(
            "Domain event must represent an accepted change."
        )

    if (
        clean_text(
            event.get(
                "before_state_ref"
            )
        )
        ==
        clean_text(
            event.get(
                "after_state_ref"
            )
        )
    ):
        raise ValueError(
            "Domain event does not contain a state change."
        )

    expected_fp = (
        recompute_event_fingerprint(
            event
        )
    )

    if (
        event.get(
            "event_fingerprint"
        )
        !=
        expected_fp
    ):
        raise ValueError(
            "Event fingerprint mismatch."
        )

    expected_id = (
        "obevt_"
        + expected_fp[:28]
    )

    if (
        event.get(
            "event_id"
        )
        !=
        expected_id
    ):
        raise ValueError(
            "Event ID mismatch."
        )

    if (
        event.get(
            "request_is_truth"
        )
        is not False
    ):
        raise ValueError(
            "Event may not rewrite command request into truth."
        )

    for field in (
        "domain_mutation_performed_here",
        "execution_authority",
        "broker_submission",
        "capital_movement",
        "automatic_contract_selection",
        "automatic_execution",
    ):

        if (
            event.get(
                field
            )
            is not False
        ):
            raise ValueError(
                (
                    "Event envelope contains "
                    f"forbidden authority: {field}"
                )
            )

    return deepcopy(
        event
    )


def _reverse_dependency_graph(
    registry: Dict[str, Any],
) -> Dict[str, set[str]]:

    reverse = {}

    for record in (
        registry[
            "authority_records"
        ].values()
    ):

        authority_id = (
            record[
                "authority_id"
            ]
        )

        reverse.setdefault(
            authority_id,
            set(),
        )

    for record in (
        registry[
            "authority_records"
        ].values()
    ):

        dependent = (
            record[
                "authority_id"
            ]
        )

        for upstream in (
            record.get(
                "inputs"
            )
            or []
        ):

            reverse.setdefault(
                upstream,
                set(),
            ).add(
                dependent
            )

    return reverse


def _invalidation_material(
    plan: Dict[str, Any],
) -> Dict[str, Any]:

    return {
        "schema_version":
            plan.get(
                "schema_version"
            ),

        "event_id":
            plan.get(
                "event_id"
            ),

        "event_fingerprint":
            plan.get(
                "event_fingerprint"
            ),

        "source_authority":
            plan.get(
                "source_authority"
            ),

        "registry_fingerprint":
            plan.get(
                "registry_fingerprint"
            ),

        "direct_dependents":
            list(
                plan.get(
                    "direct_dependents"
                )
                or []
            ),

        "transitive_dependents":
            list(
                plan.get(
                    "transitive_dependents"
                )
                or []
            ),

        "recompute_order":
            list(
                plan.get(
                    "recompute_order"
                )
                or []
            ),
    }


def recompute_invalidation_fingerprint(
    plan: Dict[str, Any],
) -> str:

    return stable_hash(
        _invalidation_material(
            plan
        )
    )


def build_invalidation_plan(
    event: Dict[str, Any],
) -> Dict[str, Any]:

    event = validate_event(
        event
    )

    registry = _registry()

    reverse = (
        _reverse_dependency_graph(
            registry
        )
    )

    source = event[
        "source_authority"
    ]

    direct = sorted(
        reverse.get(
            source,
            set(),
        )
    )

    distance = {}
    queue = [
        (
            item,
            1,
        )
        for item
        in direct
    ]

    while queue:

        node, depth = (
            queue.pop(0)
        )

        prior = distance.get(
            node
        )

        if (
            prior is not None
            and
            prior <= depth
        ):
            continue

        distance[
            node
        ] = depth

        for child in sorted(
            reverse.get(
                node,
                set(),
            )
        ):
            queue.append(
                (
                    child,
                    depth + 1,
                )
            )

    distance.pop(
        source,
        None,
    )

    transitive = sorted(
        distance
    )

    recompute_order = [
        item[
            0
        ]
        for item
        in sorted(
            distance.items(),
            key=lambda item: (
                item[
                    1
                ],
                item[
                    0
                ],
            ),
        )
    ]

    plan = {
        "schema_version":
            INVALIDATION_SCHEMA_VERSION,

        "event_id":
            event[
                "event_id"
            ],

        "event_fingerprint":
            event[
                "event_fingerprint"
            ],

        "source_authority":
            source,

        "registry_fingerprint":
            registry[
                "registry_fingerprint"
            ],

        "direct_dependents":
            direct,

        "transitive_dependents":
            transitive,

        "recompute_order":
            recompute_order,

        "invalidation_required":
            bool(
                transitive
            ),

        "effect":
            (
                "MARK_DEPENDENT_RESULT_STALE_"
                "OR_RECOMPUTE_REQUIRED"
            ),

        "domain_state_mutated":
            False,

        "durable_domain_state_deleted":
            False,

        "whole_system_invalidated":
            False,

        "cause_event_id":
            event[
                "event_id"
            ],
    }

    fingerprint = (
        recompute_invalidation_fingerprint(
            plan
        )
    )

    plan[
        "plan_fingerprint"
    ] = fingerprint

    plan[
        "invalidation_id"
    ] = (
        "obinv_"
        + fingerprint[:28]
    )

    return plan


def validate_invalidation_plan(
    plan: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        plan,
        dict,
    ):
        raise ValueError(
            "Invalidation plan must be an object."
        )

    if (
        plan.get(
            "schema_version"
        )
        !=
        INVALIDATION_SCHEMA_VERSION
    ):
        raise ValueError(
            "Unknown invalidation-plan schema."
        )

    expected = (
        recompute_invalidation_fingerprint(
            plan
        )
    )

    if (
        plan.get(
            "plan_fingerprint"
        )
        !=
        expected
    ):
        raise ValueError(
            "Invalidation-plan fingerprint mismatch."
        )

    if (
        plan.get(
            "invalidation_id"
        )
        !=
        (
            "obinv_"
            + expected[:28]
        )
    ):
        raise ValueError(
            "Invalidation-plan ID mismatch."
        )

    if (
        plan.get(
            "domain_state_mutated"
        )
        is not False
        or
        plan.get(
            "durable_domain_state_deleted"
        )
        is not False
        or
        plan.get(
            "whole_system_invalidated"
        )
        is not False
    ):
        raise ValueError(
            "Invalidation plan exceeds OBEVENT authority."
        )

    return deepcopy(
        plan
    )


def resolve_db_path(
    path: Optional[
        Path
    ] = None,
) -> Path:

    return (
        Path(
            path
        )
        if path is not None
        else DEFAULT_DB_PATH
    )


def connect(
    path: Optional[
        Path
    ] = None,
):

    selected = (
        resolve_db_path(
            path
        )
    )

    selected.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    conn = sqlite3.connect(
        str(
            selected
        )
    )

    conn.row_factory = (
        sqlite3.Row
    )

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conn


def init_event_store(
    path: Optional[
        Path
    ] = None,
) -> Dict[str, Any]:

    selected = (
        resolve_db_path(
            path
        )
    )

    selected.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with connect(
        selected
    ) as conn:

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS commands (
                command_id TEXT PRIMARY KEY,
                schema_version TEXT NOT NULL,
                command_type TEXT NOT NULL,
                target_authority TEXT NOT NULL,
                actor_type TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                account_key TEXT,
                idempotency_key TEXT NOT NULL,
                command_fingerprint TEXT NOT NULL,
                command_json TEXT NOT NULL,
                status TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS
            idx_obevent_command_status
            ON commands (
                status,
                created_at
            );

            CREATE TABLE IF NOT EXISTS events (
                sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL UNIQUE,
                schema_version TEXT NOT NULL,
                command_id TEXT NOT NULL UNIQUE,
                source_authority TEXT NOT NULL,
                event_type TEXT NOT NULL,
                aggregate_type TEXT NOT NULL,
                aggregate_id TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                causation_event_id TEXT,
                event_fingerprint TEXT NOT NULL,
                event_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(command_id)
                    REFERENCES commands(command_id)
            );

            CREATE INDEX IF NOT EXISTS
            idx_obevent_source
            ON events (
                source_authority,
                sequence_id
            );

            CREATE INDEX IF NOT EXISTS
            idx_obevent_correlation
            ON events (
                correlation_id,
                sequence_id
            );

            CREATE TABLE IF NOT EXISTS invalidations (
                event_id TEXT PRIMARY KEY,
                invalidation_id TEXT NOT NULL UNIQUE,
                plan_fingerprint TEXT NOT NULL,
                plan_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(event_id)
                    REFERENCES events(event_id)
            );
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
                selected
            ),

        "request_is_truth":
            False,

        "domain_mutation_performed_here":
            False,

        "existing_domain_logs_replaced":
            False,
    }


def _row_command(
    row: sqlite3.Row,
) -> Dict[str, Any]:

    command = json.loads(
        row[
            "command_json"
        ]
    )

    command[
        "status"
    ] = row[
        "status"
    ]

    command[
        "result"
    ] = json.loads(
        row[
            "result_json"
        ]
        or "{}"
    )

    validate_command(
        command
    )

    return command


def get_command(
    command_id: Any,
    *,
    path: Optional[
        Path
    ] = None,
) -> Optional[
    Dict[str, Any]
]:

    command_id = clean_text(
        command_id
    )

    if not command_id:
        raise ValueError(
            "command_id is required."
        )

    init_event_store(
        path
    )

    with connect(
        path
    ) as conn:

        row = conn.execute(
            """
            SELECT *
            FROM commands
            WHERE command_id = ?
            """,
            (
                command_id,
            ),
        ).fetchone()

    if row is None:
        return None

    return _row_command(
        row
    )


def get_event(
    event_id: Any,
    *,
    path: Optional[
        Path
    ] = None,
) -> Optional[
    Dict[str, Any]
]:

    event_id = clean_text(
        event_id
    )

    if not event_id:
        raise ValueError(
            "event_id is required."
        )

    init_event_store(
        path
    )

    with connect(
        path
    ) as conn:

        row = conn.execute(
            """
            SELECT event_json
            FROM events
            WHERE event_id = ?
            """,
            (
                event_id,
            ),
        ).fetchone()

    if row is None:
        return None

    event = json.loads(
        row[
            "event_json"
        ]
    )

    return validate_event(
        event
    )


def get_invalidation_plan(
    event_id: Any,
    *,
    path: Optional[
        Path
    ] = None,
) -> Optional[
    Dict[str, Any]
]:

    event_id = clean_text(
        event_id
    )

    init_event_store(
        path
    )

    with connect(
        path
    ) as conn:

        row = conn.execute(
            """
            SELECT plan_json
            FROM invalidations
            WHERE event_id = ?
            """,
            (
                event_id,
            ),
        ).fetchone()

    if row is None:
        return None

    plan = json.loads(
        row[
            "plan_json"
        ]
    )

    return validate_invalidation_plan(
        plan
    )


def record_command_request(
    command: Dict[str, Any],
    *,
    path: Optional[
        Path
    ] = None,
) -> Dict[str, Any]:

    command = validate_command(
        command
    )

    init_event_store(
        path
    )

    causation_event_id = (
        command.get(
            "causation_event_id"
        )
    )

    if causation_event_id:

        parent = get_event(
            causation_event_id,
            path=path,
        )

        if parent is None:
            raise ValueError(
                (
                    "Causation event does not exist "
                    "in this canonical ledger."
                )
            )

        if (
            parent[
                "correlation_id"
            ]
            !=
            command[
                "correlation_id"
            ]
        ):
            raise ValueError(
                "Causal correlation_id mismatch."
            )

    now = utc_now_iso()

    with connect(
        path
    ) as conn:

        existing = conn.execute(
            """
            SELECT *
            FROM commands
            WHERE command_id = ?
            """,
            (
                command[
                    "command_id"
                ],
            ),
        ).fetchone()

        if existing is not None:

            stored = _row_command(
                existing
            )

            if (
                stored[
                    "command_fingerprint"
                ]
                !=
                command[
                    "command_fingerprint"
                ]
            ):
                raise ValueError(
                    "Command ID collision."
                )

            return {
                "ok":
                    True,

                "created":
                    False,

                "idempotent":
                    True,

                "command":
                    stored,
            }

        conn.execute(
            """
            INSERT INTO commands (
                command_id,
                schema_version,
                command_type,
                target_authority,
                actor_type,
                actor_id,
                account_key,
                idempotency_key,
                command_fingerprint,
                command_json,
                status,
                result_json,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                command[
                    "command_id"
                ],

                command[
                    "schema_version"
                ],

                command[
                    "command_type"
                ],

                command[
                    "target_authority"
                ],

                command[
                    "actor_type"
                ],

                command[
                    "actor_id"
                ],

                command.get(
                    "account_key"
                ),

                command[
                    "idempotency_key"
                ],

                command[
                    "command_fingerprint"
                ],

                canonical_json(
                    command
                ),

                "REQUESTED",

                "{}",

                now,

                now,
            ),
        )

        conn.commit()

    return {
        "ok":
            True,

        "created":
            True,

        "idempotent":
            False,

        "command":
            deepcopy(
                command
            ),
    }


def mark_command_rejected(
    command_id: Any,
    *,
    authority_id: Any,
    reason: Any,
    evidence: Optional[
        Dict[str, Any]
    ] = None,
    path: Optional[
        Path
    ] = None,
) -> Dict[str, Any]:

    command_id = clean_text(
        command_id
    )

    authority_id = clean_text(
        authority_id
    )

    reason = clean_text(
        reason
    )

    if not reason:
        raise ValueError(
            "Rejection reason is required."
        )

    command = get_command(
        command_id,
        path=path,
    )

    if command is None:
        raise KeyError(
            command_id
        )

    if (
        command[
            "target_authority"
        ]
        !=
        authority_id
    ):
        raise ValueError(
            "Only the target authority may reject this command."
        )

    if (
        command[
            "status"
        ]
        ==
        "ACCEPTED"
    ):
        raise ValueError(
            "Accepted command cannot later be rejected."
        )

    if (
        command[
            "status"
        ]
        ==
        "REJECTED"
    ):

        prior = (
            command.get(
                "result"
            )
            or {}
        )

        if (
            prior.get(
                "reason"
            )
            !=
            reason
        ):
            raise ValueError(
                "Rejected command outcome cannot be silently rewritten."
            )

        return {
            "ok":
                True,

            "rejected":
                True,

            "idempotent":
                True,

            "command":
                command,
        }

    result = {
        "status":
            "REJECTED",

        "authority_id":
            authority_id,

        "reason":
            reason,

        "evidence":
            safe_object(
                evidence
            ),

        "rejected_at":
            utc_now_iso(),

        "domain_event_emitted":
            False,
    }

    result[
        "result_fingerprint"
    ] = stable_hash(
        result
    )

    now = utc_now_iso()

    with connect(
        path
    ) as conn:

        conn.execute(
            """
            UPDATE commands
            SET
                status = 'REJECTED',
                result_json = ?,
                updated_at = ?
            WHERE command_id = ?
            """,
            (
                canonical_json(
                    result
                ),
                now,
                command_id,
            ),
        )

        conn.commit()

    return {
        "ok":
            True,

        "rejected":
            True,

        "idempotent":
            False,

        "command":
            get_command(
                command_id,
                path=path,
            ),
    }


def record_accepted_event(
    event: Dict[str, Any],
    *,
    path: Optional[
        Path
    ] = None,
) -> Dict[str, Any]:

    event = validate_event(
        event
    )

    init_event_store(
        path
    )

    command = get_command(
        event[
            "command_id"
        ],
        path=path,
    )

    if command is None:
        raise ValueError(
            "Accepted event has no recorded command request."
        )

    if (
        command[
            "target_authority"
        ]
        !=
        event[
            "source_authority"
        ]
    ):
        raise ValueError(
            "Event source does not own the command."
        )

    if (
        command[
            "status"
        ]
        ==
        "REJECTED"
    ):
        raise ValueError(
            "Rejected command cannot emit an accepted domain event."
        )

    if (
        event.get(
            "causation_event_id"
        )
    ):

        parent = get_event(
            event[
                "causation_event_id"
            ],
            path=path,
        )

        if parent is None:
            raise ValueError(
                "Event causation parent is missing."
            )

        if (
            parent[
                "correlation_id"
            ]
            !=
            event[
                "correlation_id"
            ]
        ):
            raise ValueError(
                "Event correlation chain mismatch."
            )

    existing = get_event(
        event[
            "event_id"
        ],
        path=path,
    )

    if existing is not None:

        if (
            existing[
                "event_fingerprint"
            ]
            !=
            event[
                "event_fingerprint"
            ]
        ):
            raise ValueError(
                "Event ID collision."
            )

        return {
            "ok":
                True,

            "accepted":
                True,

            "created":
                False,

            "idempotent":
                True,

            "event":
                existing,

            "invalidation":
                get_invalidation_plan(
                    event[
                        "event_id"
                    ],
                    path=path,
                ),
        }

    if (
        command[
            "status"
        ]
        ==
        "ACCEPTED"
    ):
        raise ValueError(
            "One command may produce only one canonical accepted event."
        )

    plan = (
        build_invalidation_plan(
            event
        )
    )

    result = {
        "status":
            "ACCEPTED",

        "authority_id":
            event[
                "source_authority"
            ],

        "event_id":
            event[
                "event_id"
            ],

        "event_fingerprint":
            event[
                "event_fingerprint"
            ],

        "invalidation_id":
            plan[
                "invalidation_id"
            ],

        "accepted_at":
            utc_now_iso(),
    }

    result[
        "result_fingerprint"
    ] = stable_hash(
        result
    )

    now = utc_now_iso()

    with connect(
        path
    ) as conn:

        conn.execute(
            """
            INSERT INTO events (
                event_id,
                schema_version,
                command_id,
                source_authority,
                event_type,
                aggregate_type,
                aggregate_id,
                correlation_id,
                causation_event_id,
                event_fingerprint,
                event_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event[
                    "event_id"
                ],

                event[
                    "schema_version"
                ],

                event[
                    "command_id"
                ],

                event[
                    "source_authority"
                ],

                event[
                    "event_type"
                ],

                event[
                    "aggregate_type"
                ],

                event[
                    "aggregate_id"
                ],

                event[
                    "correlation_id"
                ],

                event.get(
                    "causation_event_id"
                ),

                event[
                    "event_fingerprint"
                ],

                canonical_json(
                    event
                ),

                now,
            ),
        )

        conn.execute(
            """
            INSERT INTO invalidations (
                event_id,
                invalidation_id,
                plan_fingerprint,
                plan_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                event[
                    "event_id"
                ],

                plan[
                    "invalidation_id"
                ],

                plan[
                    "plan_fingerprint"
                ],

                canonical_json(
                    plan
                ),

                now,
            ),
        )

        conn.execute(
            """
            UPDATE commands
            SET
                status = 'ACCEPTED',
                result_json = ?,
                updated_at = ?
            WHERE command_id = ?
            """,
            (
                canonical_json(
                    result
                ),

                now,

                command[
                    "command_id"
                ],
            ),
        )

        conn.commit()

    return {
        "ok":
            True,

        "accepted":
            True,

        "created":
            True,

        "idempotent":
            False,

        "event":
            deepcopy(
                event
            ),

        "invalidation":
            deepcopy(
                plan
            ),
    }


def list_events(
    *,
    path: Optional[
        Path
    ] = None,
) -> List[
    Dict[str, Any]
]:

    init_event_store(
        path
    )

    with connect(
        path
    ) as conn:

        rows = conn.execute(
            """
            SELECT event_json
            FROM events
            ORDER BY sequence_id ASC
            """
        ).fetchall()

    return [
        validate_event(
            json.loads(
                row[
                    "event_json"
                ]
            )
        )
        for row
        in rows
    ]


def causal_chain(
    event_id: Any,
    *,
    path: Optional[
        Path
    ] = None,
) -> List[
    Dict[str, Any]
]:

    event_id = clean_text(
        event_id
    )

    if not event_id:
        raise ValueError(
            "event_id is required."
        )

    result = []
    seen = set()

    current = get_event(
        event_id,
        path=path,
    )

    if current is None:
        raise KeyError(
            event_id
        )

    while current is not None:

        current_id = (
            current[
                "event_id"
            ]
        )

        if current_id in seen:
            raise RuntimeError(
                "Causal event cycle detected."
            )

        seen.add(
            current_id
        )

        result.append(
            current
        )

        parent_id = (
            current.get(
                "causation_event_id"
            )
        )

        if not parent_id:
            break

        current = get_event(
            parent_id,
            path=path,
        )

        if current is None:
            raise RuntimeError(
                "Causal parent disappeared from durable ledger."
            )

    result.reverse()

    return result


def replay_event_ledger(
    *,
    path: Optional[
        Path
    ] = None,
) -> Dict[str, Any]:

    events = list_events(
        path=path,
    )

    replay = []

    for event in events:

        plan = get_invalidation_plan(
            event[
                "event_id"
            ],
            path=path,
        )

        if plan is None:
            raise RuntimeError(
                "Accepted event lacks durable invalidation evidence."
            )

        replay.append(
            {
                "event":
                    event,

                "invalidation":
                    plan,
            }
        )

    material = {
        "event_fingerprints": [
            item[
                "event"
            ][
                "event_fingerprint"
            ]
            for item
            in replay
        ],

        "invalidation_fingerprints": [
            item[
                "invalidation"
            ][
                "plan_fingerprint"
            ]
            for item
            in replay
        ],
    }

    return {
        "schema_version":
            SCHEMA_VERSION,

        "event_count":
            len(
                replay
            ),

        "replay":
            replay,

        "replay_fingerprint":
            stable_hash(
                material
            ),

        "domain_state_reapplied":
            False,

        "audit_replay_only":
            True,
    }


def command_event_contract() -> Dict[str, Any]:

    return {
        "schema_version":
            SCHEMA_VERSION,

        "command_schema_version":
            COMMAND_SCHEMA_VERSION,

        "event_schema_version":
            EVENT_SCHEMA_VERSION,

        "invalidation_schema_version":
            INVALIDATION_SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "authority":
            "CANONICAL_COMMAND_EVENT_CAUSALITY",

        "request_equals_truth":
            False,

        "command_requests_change":
            True,

        "domain_authority_validates_and_mutates":
            True,

        "event_records_accepted_change":
            True,

        "rejected_command_emits_domain_event":
            False,

        "command_idempotence":
            True,

        "accepted_event_idempotence":
            True,

        "correlation_chain":
            True,

        "causation_chain":
            True,

        "dependency_aware_invalidation":
            True,

        "whole_system_invalidation":
            False,

        "recompute_only_structural_dependents":
            True,

        "event_replay":
            True,

        "replay_mutates_domain_state":
            False,

        "existing_domain_event_logs_replaced":
            False,

        "existing_domain_histories": {
            "OB_TRADE_INTENT_V1":
                "DOMAIN_LOCAL_SQLITE_EVENT_HISTORY",

            "OB_PROOF_DEMO_ACCOUNT_V1":
                "DOMAIN_LOCAL_SIMULATED_EVENT_HISTORY",

            "OB_OWNER_OPERATING_PROFILE_V1":
                "DOMAIN_LOCAL_REVISION_HISTORY",
        },

        "ledger_path":
            str(
                DEFAULT_DB_PATH
            ),

        "ledger_is_local_generated_state":
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

        "live_auto_locked":
            True,
    }
