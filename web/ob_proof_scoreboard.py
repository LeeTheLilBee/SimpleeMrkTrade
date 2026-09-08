from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Optional
import json
import math

from web.ob_proof_demo_account import (
    ACCOUNT_KEY,
    CAPITAL_CLASS,
    SCHEMA_VERSION as SOURCE_SCHEMA_VERSION,
    get_account_state,
    list_positions,
)


SCHEMA_VERSION = "OB_PROOF_SANITIZED_SCOREBOARD_V1"
SERVICE_VERSION = "OBPROOF006_010_SANITIZED_SCOREBOARD_PROJECTION"

SOURCE_AUTHORITY = "OB_PROOF_DEMO_ACCOUNT_V1"
SOURCE_ACCOUNT_KEY = ACCOUNT_KEY
SOURCE_CAPITAL_CLASS = CAPITAL_CLASS

PUBLIC_TRUTH_DISCLOSURE = (
    "SIMULATED / PAPER RESULTS — NOT LIVE BROKER PERFORMANCE"
)

CALCULATION_BASIS = (
    "completed_closed_paper_positions_only"
)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def stable_hash(value: Any) -> str:
    return sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()


def finite_number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None

    try:
        number = float(value)
    except Exception:
        return None

    if not math.isfinite(number):
        return None

    return round(number, 8)


def scoreboard_contract() -> Dict[str, Any]:
    return {
        "schema_version":
            SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "authority":
            SCHEMA_VERSION,

        "source_authority":
            SOURCE_AUTHORITY,

        "source_schema_version":
            SOURCE_SCHEMA_VERSION,

        "source_account_key":
            SOURCE_ACCOUNT_KEY,

        "source_capital_class":
            SOURCE_CAPITAL_CLASS,

        "projection_only":
            True,

        "durable_write":
            False,

        "source_state_mutation":
            False,

        "market_truth_mutation":
            False,

        "candidate_rank_recalculation":
            False,

        "owner_fit_recalculation":
            False,

        "broker_linked":
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

        "public_safe":
            True,

        "aggregate_only":
            True,

        "closed_samples_only":
            True,

        "open_position_details_exposed":
            False,

        "symbols_exposed":
            False,

        "instrument_ids_exposed":
            False,

        "candidate_fingerprints_exposed":
            False,

        "owner_fit_fingerprints_exposed":
            False,

        "entry_exit_prices_exposed":
            False,

        "position_timestamps_exposed":
            False,

        "source_payload_exposed":
            False,

        "opening_demo_cash_exposed":
            False,

        "demo_cash_exposed":
            False,

        "demo_equity_exposed":
            False,

        "unrealized_pnl_exposed":
            False,

        "live_mark_to_market_claimed":
            False,

        "live_broker_performance_claimed":
            False,

        "truth_disclosure":
            PUBLIC_TRUTH_DISCLOSURE,

        "calculation_basis":
            CALCULATION_BASIS,
    }


def sample_size_band(count: int) -> str:
    if count <= 0:
        return "NONE"

    if count <= 4:
        return "1_4"

    if count <= 19:
        return "5_19"

    return "20_PLUS"


def build_sanitized_scoreboard(
    *,
    db_path: Optional[Path] = None,
) -> Dict[str, Any]:

    state = get_account_state(
        db_path=db_path
    )

    contract = scoreboard_contract()

    if not state.get("activated"):
        core = {
            "schema_version":
                SCHEMA_VERSION,

            "authority":
                SCHEMA_VERSION,

            "truth_class":
                "SIMULATED_ONLY",

            "truth_disclosure":
                PUBLIC_TRUTH_DISCLOSURE,

            "calculation_basis":
                CALCULATION_BASIS,

            "scoreboard_status":
                "NOT_ACTIVATED",

            "completed_sample_count":
                0,

            "sample_size_band":
                "NONE",

            "wins":
                0,

            "losses":
                0,

            "flat":
                0,

            "win_rate_pct":
                None,

            "net_realized_paper_pnl":
                None,

            "average_realized_paper_pnl":
                None,

            "gross_positive_paper_pnl":
                None,

            "gross_negative_paper_pnl":
                None,

            "profit_factor":
                None,

            "open_samples_included":
                False,

            "live_marks_included":
                False,

            "real_broker_data_included":
                False,

            "public_safe":
                True,

            "aggregate_only":
                True,
        }

        return {
            **contract,
            "scoreboard":
                core,

            "projection_fingerprint":
                stable_hash(core),
        }

    closed = list_positions(
        status="CLOSED",
        db_path=db_path,
    )

    realized_values = []

    for position in closed:
        value = finite_number(
            position.get("realized_pnl")
        )

        if value is not None:
            realized_values.append(
                value
            )

    completed = len(realized_values)

    wins = sum(
        1
        for value in realized_values
        if value > 0
    )

    losses = sum(
        1
        for value in realized_values
        if value < 0
    )

    flat = sum(
        1
        for value in realized_values
        if value == 0
    )

    net = (
        round(
            sum(realized_values),
            8,
        )
        if completed
        else 0.0
    )

    average = (
        round(
            net / completed,
            8,
        )
        if completed
        else None
    )

    gross_positive = (
        round(
            sum(
                value
                for value in realized_values
                if value > 0
            ),
            8,
        )
        if completed
        else 0.0
    )

    gross_negative = (
        round(
            abs(
                sum(
                    value
                    for value in realized_values
                    if value < 0
                )
            ),
            8,
        )
        if completed
        else 0.0
    )

    win_rate = (
        round(
            (wins / completed) * 100.0,
            4,
        )
        if completed
        else None
    )

    profit_factor = (
        round(
            gross_positive / gross_negative,
            6,
        )
        if gross_negative > 0
        else None
    )

    core = {
        "schema_version":
            SCHEMA_VERSION,

        "authority":
            SCHEMA_VERSION,

        "truth_class":
            "SIMULATED_ONLY",

        "truth_disclosure":
            PUBLIC_TRUTH_DISCLOSURE,

        "calculation_basis":
            CALCULATION_BASIS,

        "scoreboard_status":
            (
                "HAS_COMPLETED_SAMPLES"
                if completed
                else "READY_NO_COMPLETED_SAMPLES"
            ),

        "completed_sample_count":
            completed,

        "sample_size_band":
            sample_size_band(
                completed
            ),

        "wins":
            wins,

        "losses":
            losses,

        "flat":
            flat,

        "win_rate_pct":
            win_rate,

        "net_realized_paper_pnl":
            net,

        "average_realized_paper_pnl":
            average,

        "gross_positive_paper_pnl":
            gross_positive,

        "gross_negative_paper_pnl":
            gross_negative,

        "profit_factor":
            profit_factor,

        "open_samples_included":
            False,

        "live_marks_included":
            False,

        "real_broker_data_included":
            False,

        "public_safe":
            True,

        "aggregate_only":
            True,
    }

    return {
        **contract,

        "scoreboard":
            core,

        "projection_fingerprint":
            stable_hash(core),
    }
