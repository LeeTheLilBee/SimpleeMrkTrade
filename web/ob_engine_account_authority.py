
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Optional
import json
import math


SCHEMA_VERSION = (
    "OB_ENGINE_ACCOUNT_AUTHORITY_V1"
)

ROOT = (
    Path(__file__).resolve().parents[1]
)


# -------------------------------------------------------------------------------------------------
# CURRENT SOURCE ROLES
#
# IMPORTANT:
#
# These roles do NOT claim that every historical data file is broker-live truth.
#
# They define what each existing source is permitted to mean.
# They prevent one source from silently overwriting another source with a different role.
# -------------------------------------------------------------------------------------------------

JSON_SOURCES = {
    "account_snapshot":
        "data/account_snapshot.json",

    "account_state":
        "data/account_state.json",

    "open_positions":
        "data/open_positions.json",

    "closed_positions":
        "data/closed_positions.json",

    "canonical_reporting_snapshot":
        "data/canonical_reporting_snapshot.json",

    "candidate_log":
        "data/candidate_log.json",

    "ledger":
        "data/ledger.json",

    "trade_log":
        "data/trade_log.json",

    "market_universe":
        "data/market_universe.json",

    "pipeline_status":
        "data/pipeline_status.json",
}


CODE_SOURCES = {
    "canonical_engine_adapter":
        "web/static/ob/ob_engine_feed_adapter.js",

    "options_research_contract":
        "web/static/ob/ob_options_research_contract.js",
}


_cache: Dict[str, Dict[str, Any]] = {}


def _path(
    relative_path: str,
    *,
    root: Optional[Path] = None,
) -> Path:
    base = (
        Path(root)
        if root is not None
        else ROOT
    )

    return (
        base
        / relative_path
    )


def _hash_bytes(
    raw: bytes,
) -> str:
    return sha256(
        raw
    ).hexdigest()


def _read_json_source(
    relative_path: str,
    *,
    root: Optional[Path] = None,
):
    path = _path(
        relative_path,
        root=root,
    )

    if not path.exists():
        return (
            None,
            {
                "path":
                    relative_path,

                "status":
                    "missing",

                "sha256":
                    None,

                "shape":
                    None,

                "item_count":
                    None,
            },
        )

    raw = path.read_bytes()

    digest = _hash_bytes(
        raw
    )

    if not raw.strip():
        return (
            None,
            {
                "path":
                    relative_path,

                "status":
                    "empty",

                "sha256":
                    digest,

                "shape":
                    None,

                "item_count":
                    None,
            },
        )

    cache_key = (
        str(path.resolve())
    )

    signature = (
        path.stat().st_mtime_ns,
        len(raw),
        digest,
    )

    cached = _cache.get(
        cache_key
    )

    if (
        cached
        and
        cached.get("signature")
        == signature
    ):
        value = cached.get(
            "value"
        )
    else:
        try:
            value = json.loads(
                raw.decode("utf-8")
            )
        except Exception as exc:
            return (
                None,
                {
                    "path":
                        relative_path,

                    "status":
                        "unreadable",

                    "sha256":
                        digest,

                    "shape":
                        None,

                    "item_count":
                        None,

                    "error_type":
                        type(exc).__name__,
                },
            )

        _cache[
            cache_key
        ] = {
            "signature":
                signature,

            "value":
                value,
        }

    if isinstance(
        value,
        dict,
    ):
        shape = "object"
        item_count = len(
            value
        )

    elif isinstance(
        value,
        list,
    ):
        shape = "array"
        item_count = len(
            value
        )

    else:
        shape = (
            type(value).__name__
        )
        item_count = None

    return (
        value,
        {
            "path":
                relative_path,

            "status":
                "parsed",

            "sha256":
                digest,

            "shape":
                shape,

            "item_count":
                item_count,
        },
    )


def _read_code_source(
    relative_path: str,
    *,
    root: Optional[Path] = None,
):
    path = _path(
        relative_path,
        root=root,
    )

    if not path.exists():
        return (
            "",
            {
                "path":
                    relative_path,

                "status":
                    "missing",

                "sha256":
                    None,

                "bytes":
                    None,
            },
        )

    raw = path.read_bytes()

    try:
        content = raw.decode(
            "utf-8"
        )
    except Exception:
        content = ""

    return (
        content,
        {
            "path":
                relative_path,

            "status":
                (
                    "present"
                    if content
                    else "unreadable"
                ),

            "sha256":
                _hash_bytes(
                    raw
                ),

            "bytes":
                len(raw),
        },
    )


def _safe_object(
    value,
):
    return (
        value
        if isinstance(
            value,
            dict,
        )
        else {}
    )


def _safe_list(
    value,
):
    return (
        value
        if isinstance(
            value,
            list,
        )
        else []
    )


def _first_present(
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


def _number(
    value,
):
    if isinstance(
        value,
        bool,
    ):
        return None

    if isinstance(
        value,
        (
            int,
            float,
        ),
    ):
        number = float(
            value
        )

        if math.isfinite(
            number
        ):
            return number

        return None

    if isinstance(
        value,
        str,
    ):
        try:
            number = float(
                value.strip()
            )

            if math.isfinite(
                number
            ):
                return number
        except Exception:
            pass

    return None


def _normalized_value(
    value,
    *,
    integer=False,
):
    if integer:
        number = _number(
            value
        )

        if number is None:
            return None

        return int(
            round(number)
        )

    number = _number(
        value
    )

    if number is not None:
        return round(
            number,
            6,
        )

    if value is None:
        return None

    return str(
        value
    ).strip()


def _account_view(
    value,
):
    source = _safe_object(
        value
    )

    return {
        "account_value":
            _first_present(
                source,
                "estimated_account_value",
                "equity",
                "account_value",
                "balance",
            ),

        "equity":
            _first_present(
                source,
                "equity",
                "estimated_account_value",
                "account_value",
                "balance",
            ),

        "cash":
            _first_present(
                source,
                "cash",
            ),

        "buying_power":
            _first_present(
                source,
                "buying_power",
            ),

        "open_positions":
            _first_present(
                source,
                "open_positions",
                "open_position_count",
            ),

        "realized_pnl":
            _first_present(
                source,
                "realized_pnl",
                "realized",
            ),

        "unrealized_pnl":
            _first_present(
                source,
                "open_unrealized_pnl",
                "unrealized_pnl",
                "unrealized",
            ),
    }


def _compare_field(
    field: str,
    source_values: Dict[str, Any],
):
    integer = (
        field
        == "open_positions"
    )

    present = {}

    for source_name, raw in (
        source_values.items()
    ):
        normalized = (
            _normalized_value(
                raw,
                integer=integer,
            )
        )

        if normalized is not None:
            present[
                source_name
            ] = normalized

    if len(
        present
    ) < 2:
        return {
            "status":
                "insufficient_overlap",

            "values":
                present,

            "resolved_value":
                None,

            "silent_merge":
                False,
        }

    values = list(
        present.values()
    )

    first = values[0]

    if integer:
        agree = all(
            value
            == first
            for value in values[1:]
        )

    elif all(
        isinstance(
            value,
            (
                int,
                float,
            ),
        )
        for value in values
    ):
        agree = all(
            abs(
                float(value)
                - float(first)
            )
            <= 0.01
            for value in values[1:]
        )

    else:
        agree = all(
            value
            == first
            for value in values[1:]
        )

    if agree:
        return {
            "status":
                "agree",

            "values":
                present,

            # This is merely the agreed comparison result.
            # It is NOT permission to overwrite any durable source.
            "resolved_value":
                first,

            "silent_merge":
                False,
        }

    return {
        "status":
            "conflict",

        "values":
            present,

        # Critical boundary:
        # conflicting sources NEVER receive a synthesized value.
        "resolved_value":
            None,

        "silent_merge":
            False,
    }


def build_source_registry(
    *,
    root: Optional[Path] = None,
):
    registry = {}

    values = {}

    for (
        source_name,
        relative_path,
    ) in JSON_SOURCES.items():
        (
            value,
            state,
        ) = _read_json_source(
            relative_path,
            root=root,
        )

        registry[
            source_name
        ] = state

        values[
            source_name
        ] = value

    for (
        source_name,
        relative_path,
    ) in CODE_SOURCES.items():
        (
            content,
            state,
        ) = _read_code_source(
            relative_path,
            root=root,
        )

        registry[
            source_name
        ] = state

        values[
            source_name
        ] = content

    return (
        registry,
        values,
    )


def build_account_authority(
    values: Dict[str, Any],
):
    lightweight = _account_view(
        values.get(
            "account_snapshot"
        )
    )

    durable_raw = _safe_object(
        values.get(
            "account_state"
        )
    )

    durable = _account_view(
        durable_raw
    )

    reporting_raw = _safe_object(
        values.get(
            "canonical_reporting_snapshot"
        )
    )

    reporting_account = _account_view(
        reporting_raw.get(
            "final_account_snapshot",
            {},
        )
    )

    fields = [
        "account_value",
        "equity",
        "cash",
        "buying_power",
        "open_positions",
        "realized_pnl",
        "unrealized_pnl",
    ]

    checks = {}

    for field in fields:
        checks[
            field
        ] = _compare_field(
            field,
            {
                "lightweight_snapshot":
                    lightweight.get(
                        field
                    ),

                "durable_state":
                    durable.get(
                        field
                    ),

                "canonical_reporting":
                    reporting_account.get(
                        field
                    ),
            },
        )

    conflicts = [
        field
        for field, result
        in checks.items()
        if (
            result.get(
                "status"
            )
            == "conflict"
        )
    ]

    agreements = [
        field
        for field, result
        in checks.items()
        if (
            result.get(
                "status"
            )
            == "agree"
        )
    ]

    if conflicts:
        reconciliation_status = (
            "conflict"
        )

    elif agreements:
        reconciliation_status = (
            "consistent_overlap"
        )

    else:
        reconciliation_status = (
            "insufficient_overlap"
        )

    activity_log = _safe_list(
        durable_raw.get(
            "activity_log"
        )
    )

    trade_history = _safe_list(
        durable_raw.get(
            "trade_history"
        )
    )

    return {
        "schema_version":
            SCHEMA_VERSION,

        "operational_repository_authority": {
            "source":
                "data/account_state.json",

            "role":
                (
                    "durable_repository_account_state"
                ),

            "broker_reconciled":
                False,

            "claimed_live_broker_truth":
                False,

            "view":
                durable,

            "activity_event_count":
                len(
                    activity_log
                ),

            "trade_history_count":
                len(
                    trade_history
                ),
        },

        "lightweight_snapshot": {
            "source":
                "data/account_snapshot.json",

            "role":
                (
                    "projection_and_compatibility_only"
                ),

            "may_overwrite_durable_state":
                False,

            "view":
                lightweight,
        },

        "reporting_account": {
            "source":
                (
                    "data/"
                    "canonical_reporting_snapshot.json"
                ),

            "role":
                "historical_reporting_only",

            "may_overwrite_durable_state":
                False,

            "view":
                reporting_account,
        },

        "overlap_checks":
            checks,

        "reconciliation_status":
            reconciliation_status,

        "conflict_fields":
            conflicts,

        "agreed_fields":
            agreements,

        "no_silent_merge":
            True,

        "conflict_is_data":
            True,

        "cross_source_resolved_account":
            None,
    }


def build_position_authority(
    values: Dict[str, Any],
    account_authority: Dict[str, Any],
):
    open_raw = values.get(
        "open_positions"
    )

    closed_raw = values.get(
        "closed_positions"
    )

    reporting = _safe_object(
        values.get(
            "canonical_reporting_snapshot"
        )
    )

    reporting_ledger = _safe_list(
        reporting.get(
            "ledger"
        )
    )

    durable_view = (
        account_authority
        .get(
            "operational_repository_authority",
            {},
        )
        .get(
            "view",
            {},
        )
    )

    durable_count = (
        durable_view.get(
            "open_positions"
        )
    )

    if isinstance(
        open_raw,
        list,
    ):
        open_records_status = (
            "explicit_store"
        )

        open_record_count = len(
            open_raw
        )

    else:
        open_records_status = (
            "unresolved"
        )

        open_record_count = None

    if isinstance(
        closed_raw,
        list,
    ):
        closed_records_status = (
            "explicit_store"
        )

        closed_record_count = len(
            closed_raw
        )

    else:
        closed_records_status = (
            "unresolved"
        )

        closed_record_count = None

    return {
        "schema_version":
            SCHEMA_VERSION,

        "open_position_records": {
            "source":
                "data/open_positions.json",

            "authority_status":
                open_records_status,

            "record_count":
                open_record_count,

            "empty_or_unreadable_means_zero":
                False,
        },

        "closed_position_records": {
            "source":
                "data/closed_positions.json",

            "authority_status":
                closed_records_status,

            "record_count":
                closed_record_count,

            "empty_or_unreadable_means_zero":
                False,
        },

        "durable_account_open_position_count": {
            "source":
                "data/account_state.json",

            "count":
                durable_count,

            "count_only":
                True,

            "may_synthesize_position_records":
                False,
        },

        "reporting_history": {
            "source":
                (
                    "data/"
                    "canonical_reporting_snapshot.json"
                ),

            "ledger_count":
                len(
                    reporting_ledger
                ),

            "role":
                "historical_reporting",

            "may_be_treated_as_open_positions":
                False,
        },

        "no_synthetic_position_records":
            True,
    }


def build_reporting_authority(
    values: Dict[str, Any],
):
    reporting = _safe_object(
        values.get(
            "canonical_reporting_snapshot"
        )
    )

    ledger = _safe_list(
        reporting.get(
            "ledger"
        )
    )

    performance = _safe_object(
        reporting.get(
            "performance"
        )
    )

    analytics = _safe_object(
        reporting.get(
            "analytics"
        )
    )

    final_account = _safe_object(
        reporting.get(
            "final_account_snapshot"
        )
    )

    return {
        "schema_version":
            SCHEMA_VERSION,

        "source":
            (
                "data/"
                "canonical_reporting_snapshot.json"
            ),

        "authority":
            "historical_performance_reporting",

        "ledger_count":
            len(
                ledger
            ),

        "performance_present":
            bool(
                performance
            ),

        "analytics_present":
            bool(
                analytics
            ),

        "final_account_snapshot_present":
            bool(
                final_account
            ),

        "may_override_operational_account_state":
            False,

        "may_authorize_execution":
            False,
    }


def build_authority_registry(
    values: Dict[str, Any],
):
    adapter_source = str(
        values.get(
            "canonical_engine_adapter"
        )
        or ""
    )

    options_source = str(
        values.get(
            "options_research_contract"
        )
        or ""
    )

    return {
        "schema_version":
            SCHEMA_VERSION,

        "market_candidate_truth": {
            "authority":
                "existing_canonical_engine_feed",

            "projection_layer":
                (
                    "web/static/ob/"
                    "ob_engine_feed_adapter.js"
                ),

            "adapter_no_second_engine_boundary":
                (
                    "This is NOT another engine"
                    in adapter_source
                ),

            "calculates_new_candidates":
                False,

            "calculates_new_market_scores":
                False,

            "calculates_new_positions":
                False,

            "second_engine_created":
                False,
        },

        "options_research": {
            "authority":
                "OB_OPTIONS_RESEARCH_V1",

            "contract":
                (
                    "web/static/ob/"
                    "ob_options_research_contract.js"
                ),

            "contract_present":
                (
                    "OB_OPTIONS_RESEARCH_V1"
                    in options_source
                ),

            "research_only":
                True,

            "owner_selection_authority":
                True,

            "automatic_contract_selection":
                False,

            "brokerage_execution":
                False,

            "fake_option_fallback":
                False,
        },

        "account_operational_state": {
            "authority":
                "data/account_state.json",

            "authority_scope":
                "durable_repository_state",

            "claimed_broker_reconciled":
                False,

            "claimed_live_broker_truth":
                False,
        },

        "account_snapshot_projection": {
            "authority":
                "data/account_snapshot.json",

            "authority_scope":
                "lightweight_projection_only",

            "may_overwrite_operational_state":
                False,
        },

        "performance_reporting": {
            "authority":
                (
                    "data/"
                    "canonical_reporting_snapshot.json"
                ),

            "authority_scope":
                "historical_reporting_only",

            "may_overwrite_operational_state":
                False,
        },

        "position_records": {
            "open_store":
                "data/open_positions.json",

            "closed_store":
                "data/closed_positions.json",

            "empty_store_interpreted_as_zero":
                False,

            "synthetic_record_fallback":
                False,
        },
    }


def build_authority_bundle(
    *,
    root: Optional[Path] = None,
):
    (
        source_registry,
        values,
    ) = build_source_registry(
        root=root,
    )

    account_authority = (
        build_account_authority(
            values
        )
    )

    position_authority = (
        build_position_authority(
            values,
            account_authority,
        )
    )

    reporting_authority = (
        build_reporting_authority(
            values
        )
    )

    authority_registry = (
        build_authority_registry(
            values
        )
    )

    return {
        "schema_version":
            SCHEMA_VERSION,

        "authority_registry":
            authority_registry,

        "account_authority":
            account_authority,

        "position_authority":
            position_authority,

        "reporting_authority":
            reporting_authority,

        "authority_source_registry":
            source_registry,

        "boundaries": {
            "read_only_projection":
                True,

            "second_engine_created":
                False,

            "candidate_recalculation":
                False,

            "market_score_recalculation":
                False,

            "account_conflict_auto_resolution":
                False,

            "synthetic_position_records":
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
        },
    }


def augment_engine_feed_response(
    response,
):
    """
    Add authority/provenance metadata to the existing engine feed response.

    The original feed remains the market/candidate engine authority.
    This function calculates NO market values, NO candidates, NO P/L,
    and NO execution instructions.
    """
    from flask import (
        jsonify,
        make_response,
    )

    original = make_response(
        response
    )

    payload = original.get_json(
        silent=True
    )

    if not isinstance(
        payload,
        dict,
    ):
        return original

    bundle = build_authority_bundle()

    payload[
        "authority_contract_version"
    ] = SCHEMA_VERSION

    payload[
        "authority_registry"
    ] = bundle[
        "authority_registry"
    ]

    payload[
        "account_authority"
    ] = bundle[
        "account_authority"
    ]

    payload[
        "position_authority"
    ] = bundle[
        "position_authority"
    ]

    payload[
        "reporting_authority"
    ] = bundle[
        "reporting_authority"
    ]

    payload[
        "authority_source_registry"
    ] = bundle[
        "authority_source_registry"
    ]

    payload[
        "authority_boundaries"
    ] = bundle[
        "boundaries"
    ]

    augmented = jsonify(
        payload
    )

    augmented.status_code = (
        original.status_code
    )

    # Preserve selected non-content response headers without copying stale
    # Content-Length / Content-Type from the pre-augmentation response.
    for header in [
        "Cache-Control",
        "ETag",
        "Last-Modified",
        "Expires",
    ]:
        if header in original.headers:
            augmented.headers[
                header
            ] = original.headers[
                header
            ]

    return augmented
