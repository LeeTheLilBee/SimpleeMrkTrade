
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import json
import math
import sqlite3


SCHEMA_VERSION = (
    "OB_OWNER_OPERATING_PROFILE_V1"
)

SERVICE_VERSION = (
    "OBRISK001_005_OWNER_OPERATING_PROFILE"
)

PRESET_SOURCE = (
    "OB_PRODUCT_DEFAULT_V1"
)

CUSTOM_SOURCE = (
    "OWNER_CUSTOM_V1"
)


ROOT = (
    Path(__file__).resolve().parents[1]
)

DEFAULT_DB_PATH = (
    ROOT
    / "data"
    / "ob_owner_operating_profiles.sqlite3"
)


# -------------------------------------------------------------------------------------------------
# ACCOUNT REGISTRY
#
# There is intentionally NO default account.
#
# An owner operating profile must be bound to an explicit account.
# -------------------------------------------------------------------------------------------------

ACCOUNT_REGISTRY = {
    "personal": {
        "key":
            "personal",

        "label":
            "Personal",
    },

    "trust": {
        "key":
            "trust",

        "label":
            "Trust",
    },

    "simplee_world_business": {
        "key":
            "simplee_world_business",

        "label":
            "Simplee World / Business",
    },

    "simplee_on_the_go_atm": {
        "key":
            "simplee_on_the_go_atm",

        "label":
            "SimpleeOnTheGo / ATM",
    },

    "the_grounds_apartment": {
        "key":
            "the_grounds_apartment",

        "label":
            "The Grounds / Apartment",
    },

    "proof_demo": {
        "key":
            "proof_demo",

        "label":
            "Proof / Demo",
    },
}


# -------------------------------------------------------------------------------------------------
# GROWTH OBJECTIVES
#
# Growth is intentionally separate from risk.
#
# There are NO return percentages here.
# There is NO promised CAGR.
# There is NO profit target.
# -------------------------------------------------------------------------------------------------

GROWTH_OBJECTIVES = {
    "PRESERVE": {
        "key":
            "PRESERVE",

        "label":
            "Preserve",

        "description":
            (
                "Prioritize capital protection "
                "and highly selective opportunity flow."
            ),
    },

    "STEADY": {
        "key":
            "STEADY",

        "label":
            "Steady",

        "description":
            (
                "Favor controlled, repeatable opportunities "
                "without defining a promised return."
            ),
    },

    "GROWTH": {
        "key":
            "GROWTH",

        "label":
            "Growth",

        "description":
            (
                "Seek meaningful growth opportunities "
                "inside the selected risk envelope."
            ),
    },

    "AGGRESSIVE_GROWTH": {
        "key":
            "AGGRESSIVE_GROWTH",

        "label":
            "Aggressive Growth",

        "description":
            (
                "Seek stronger growth opportunities while "
                "remaining constrained by the independently "
                "selected risk envelope."
            ),
    },

    "CUSTOM": {
        "key":
            "CUSTOM",

        "label":
            "Custom",

        "description":
            (
                "Owner-defined growth posture. "
                "No return target is implied."
            ),
    },
}


# -------------------------------------------------------------------------------------------------
# RISK LABELS
# -------------------------------------------------------------------------------------------------

RISK_LEVELS = {
    "LOW": {
        "key":
            "LOW",

        "label":
            "Low",
    },

    "MODERATE": {
        "key":
            "MODERATE",

        "label":
            "Moderate",
    },

    "ELEVATED": {
        "key":
            "ELEVATED",

        "label":
            "Elevated",
    },

    "HIGH": {
        "key":
            "HIGH",

        "label":
            "High",
    },

    "CUSTOM": {
        "key":
            "CUSTOM",

        "label":
            "Custom",
    },
}


# -------------------------------------------------------------------------------------------------
# SOFTWARE OPERATING ENVELOPES
#
# These are product safety templates.
#
# They are:
#   - visible
#   - editable
#   - inactive until explicit owner confirmation
#
# They are NOT expected-return models.
#
# Percentage fields are expressed in percentage points:
#
#     1.0 = 1%
#    10.0 = 10%
#
# Live automation remains FALSE in every template.
# -------------------------------------------------------------------------------------------------

RISK_TEMPLATES = {
    "LOW": {
        "max_loss_per_trade_pct":
            0.5,

        "max_position_allocation_pct":
            5.0,

        "daily_loss_cap_pct":
            1.5,

        "max_concurrent_positions":
            2,

        "max_spread_pct":
            8.0,

        "min_option_volume":
            100,

        "min_open_interest":
            500,

        "max_correlated_exposure_pct":
            15.0,

        "max_hold_minutes":
            390,

        "overnight_allowed":
            False,

        "max_implied_volatility_pct":
            80.0,

        "live_automation_allowed":
            False,
    },


    "MODERATE": {
        "max_loss_per_trade_pct":
            1.0,

        "max_position_allocation_pct":
            10.0,

        "daily_loss_cap_pct":
            2.5,

        "max_concurrent_positions":
            3,

        "max_spread_pct":
            10.0,

        "min_option_volume":
            50,

        "min_open_interest":
            250,

        "max_correlated_exposure_pct":
            25.0,

        "max_hold_minutes":
            780,

        "overnight_allowed":
            False,

        "max_implied_volatility_pct":
            120.0,

        "live_automation_allowed":
            False,
    },


    "ELEVATED": {
        "max_loss_per_trade_pct":
            1.5,

        "max_position_allocation_pct":
            15.0,

        "daily_loss_cap_pct":
            4.0,

        "max_concurrent_positions":
            4,

        "max_spread_pct":
            15.0,

        "min_option_volume":
            25,

        "min_open_interest":
            100,

        "max_correlated_exposure_pct":
            35.0,

        "max_hold_minutes":
            1440,

        "overnight_allowed":
            True,

        "max_implied_volatility_pct":
            180.0,

        "live_automation_allowed":
            False,
    },


    "HIGH": {
        "max_loss_per_trade_pct":
            2.0,

        "max_position_allocation_pct":
            20.0,

        "daily_loss_cap_pct":
            5.0,

        "max_concurrent_positions":
            5,

        "max_spread_pct":
            20.0,

        "min_option_volume":
            10,

        "min_open_interest":
            50,

        "max_correlated_exposure_pct":
            50.0,

        "max_hold_minutes":
            2880,

        "overnight_allowed":
            True,

        "max_implied_volatility_pct":
            250.0,

        "live_automation_allowed":
            False,
    },
}


REQUIRED_LIMIT_KEYS = (
    "max_loss_per_trade_pct",
    "max_position_allocation_pct",
    "daily_loss_cap_pct",
    "max_concurrent_positions",
    "max_spread_pct",
    "min_option_volume",
    "min_open_interest",
    "max_correlated_exposure_pct",
    "max_hold_minutes",
    "overnight_allowed",
    "max_implied_volatility_pct",
    "live_automation_allowed",
)


UPPER_BOUND_LIMITS = {
    "max_loss_per_trade_pct",
    "max_position_allocation_pct",
    "daily_loss_cap_pct",
    "max_concurrent_positions",
    "max_spread_pct",
    "max_correlated_exposure_pct",
    "max_hold_minutes",
    "max_implied_volatility_pct",
}


MINIMUM_REQUIREMENTS = {
    "min_option_volume",
    "min_open_interest",
}


PERMISSION_LIMITS = {
    "overnight_allowed",
    "live_automation_allowed",
}


INTEGER_LIMITS = {
    "max_concurrent_positions",
    "min_option_volume",
    "min_open_interest",
    "max_hold_minutes",
}


PERCENTAGE_LIMITS = {
    "max_loss_per_trade_pct",
    "max_position_allocation_pct",
    "daily_loss_cap_pct",
    "max_spread_pct",
    "max_correlated_exposure_pct",
    "max_implied_volatility_pct",
}


LIMIT_UNITS = {
    "max_loss_per_trade_pct":
        "percentage_points",

    "max_position_allocation_pct":
        "percentage_points",

    "daily_loss_cap_pct":
        "percentage_points",

    "max_concurrent_positions":
        "count",

    "max_spread_pct":
        "percentage_points",

    "min_option_volume":
        "contracts",

    "min_open_interest":
        "contracts",

    "max_correlated_exposure_pct":
        "percentage_points",

    "max_hold_minutes":
        "minutes",

    "overnight_allowed":
        "boolean",

    "max_implied_volatility_pct":
        "percentage_points",

    "live_automation_allowed":
        "boolean",
}


# -------------------------------------------------------------------------------------------------
# CORE HELPERS
# -------------------------------------------------------------------------------------------------

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


def normalize_account_key(
    value: Any,
) -> str:
    account_key = clean_text(
        value
    ).lower()

    if not account_key:
        raise ValueError(
            "Explicit account_key is required. "
            "OB has no implicit mission-account default."
        )

    if account_key not in ACCOUNT_REGISTRY:
        raise ValueError(
            f"Unknown account_key: {account_key}"
        )

    return account_key


def normalize_growth_key(
    value: Any,
) -> str:
    key = clean_text(
        value
    ).upper()

    if key not in GROWTH_OBJECTIVES:
        raise ValueError(
            f"Unknown growth objective: {value}"
        )

    return key


def normalize_risk_key(
    value: Any,
) -> str:
    key = clean_text(
        value
    ).upper()

    if key not in RISK_LEVELS:
        raise ValueError(
            f"Unknown risk level: {value}"
        )

    return key


def _numeric(
    value: Any,
    *,
    key: str,
) -> float:
    if isinstance(
        value,
        bool,
    ):
        raise ValueError(
            f"{key} must be numeric."
        )

    try:
        result = float(
            value
        )
    except Exception:
        raise ValueError(
            f"{key} must be numeric."
        )

    if not math.isfinite(
        result
    ):
        raise ValueError(
            f"{key} must be finite."
        )

    return result


def validate_limit_value(
    key: str,
    value: Any,
):
    if key not in REQUIRED_LIMIT_KEYS:
        raise ValueError(
            f"Unknown risk-envelope limit: {key}"
        )

    if key in PERMISSION_LIMITS:
        if not isinstance(
            value,
            bool,
        ):
            raise ValueError(
                f"{key} must be boolean."
            )

        # This product phase never permits a profile to switch on
        # live automated trading.
        if (
            key
            ==
            "live_automation_allowed"
            and
            value is True
        ):
            raise ValueError(
                "Live automation cannot be enabled by "
                "an OBRISK001–005 operating profile."
            )

        return bool(
            value
        )

    number = _numeric(
        value,
        key=key,
    )

    if key in INTEGER_LIMITS:
        if not number.is_integer():
            raise ValueError(
                f"{key} must be a whole number."
            )

        number = int(
            number
        )

        if number < 0:
            raise ValueError(
                f"{key} cannot be negative."
            )

        if (
            key
            in {
                "max_concurrent_positions",
                "max_hold_minutes",
            }
            and
            number <= 0
        ):
            raise ValueError(
                f"{key} must be greater than zero."
            )

        return number

    if key in PERCENTAGE_LIMITS:
        if number <= 0:
            raise ValueError(
                f"{key} must be greater than zero."
            )

        # Deliberately generous validation ceiling;
        # this validates software input, not financial suitability.
        if (
            key
            !=
            "max_implied_volatility_pct"
            and
            number > 100
        ):
            raise ValueError(
                f"{key} cannot exceed 100 percentage points."
            )

        if (
            key
            ==
            "max_implied_volatility_pct"
            and
            number > 1000
        ):
            raise ValueError(
                f"{key} exceeds the software validation ceiling."
            )

        return round(
            number,
            6,
        )

    raise ValueError(
        f"No validator exists for {key}."
    )


def normalize_limit_overrides(
    overrides: Optional[
        Dict[str, Any]
    ],
) -> Dict[str, Any]:
    if overrides is None:
        return {}

    if not isinstance(
        overrides,
        dict,
    ):
        raise ValueError(
            "limit_overrides must be an object."
        )

    result = {}

    for key, value in (
        overrides.items()
    ):
        result[
            key
        ] = validate_limit_value(
            key,
            value,
        )

    return result


def build_effective_limits(
    risk_key: str,
    limit_overrides: Optional[
        Dict[str, Any]
    ] = None,
) -> Dict[str, Any]:
    risk_key = (
        normalize_risk_key(
            risk_key
        )
    )

    overrides = (
        normalize_limit_overrides(
            limit_overrides
        )
    )

    if risk_key == "CUSTOM":
        missing = [
            key
            for key
            in REQUIRED_LIMIT_KEYS
            if key not in overrides
        ]

        if missing:
            raise ValueError(
                "CUSTOM risk requires every "
                "risk-envelope limit. Missing: "
                + ", ".join(
                    missing
                )
            )

        effective = {
            key:
                overrides[
                    key
                ]
            for key
            in REQUIRED_LIMIT_KEYS
        }

    else:
        effective = deepcopy(
            RISK_TEMPLATES[
                risk_key
            ]
        )

        effective.update(
            overrides
        )

    # Hard phase boundary regardless of preset or owner override.
    effective[
        "live_automation_allowed"
    ] = False

    for key in (
        REQUIRED_LIMIT_KEYS
    ):
        if key not in effective:
            raise ValueError(
                f"Effective risk envelope "
                f"is missing {key}."
            )

        effective[
            key
        ] = (
            validate_limit_value(
                key,
                effective[
                    key
                ],
            )
        )

    return effective


def growth_objective_payload(
    growth_key: str,
) -> Dict[str, Any]:
    key = normalize_growth_key(
        growth_key
    )

    source = GROWTH_OBJECTIVES[
        key
    ]

    return {
        "key":
            source[
                "key"
            ],

        "label":
            source[
                "label"
            ],

        "description":
            source[
                "description"
            ],

        # Explicit doctrine:
        "numeric_return_target_defined":
            False,

        "return_guarantee":
            False,

        "risk_level_implied":
            False,
    }


def risk_envelope_payload(
    risk_key: str,
    effective_limits: Dict[
        str,
        Any
    ],
) -> Dict[str, Any]:
    key = normalize_risk_key(
        risk_key
    )

    return {
        "key":
            key,

        "label":
            RISK_LEVELS[
                key
            ][
                "label"
            ],

        "effective_limits":
            deepcopy(
                effective_limits
            ),

        "limit_units":
            deepcopy(
                LIMIT_UNITS
            ),

        "live_automation_allowed":
            False,
    }


# -------------------------------------------------------------------------------------------------
# DRAFT
# -------------------------------------------------------------------------------------------------

def _draft_hash_material(
    draft: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "schema_version":
            draft.get(
                "schema_version"
            ),

        "draft_id":
            draft.get(
                "draft_id"
            ),

        "account":
            draft.get(
                "account"
            ),

        "growth_objective":
            draft.get(
                "growth_objective"
            ),

        "risk_envelope":
            draft.get(
                "risk_envelope"
            ),

        "preset_source":
            draft.get(
                "preset_source"
            ),

        "owner_confirmation_required":
            True,
    }


def recompute_draft_hash(
    draft: Dict[str, Any],
) -> str:
    return stable_hash(
        _draft_hash_material(
            draft
        )
    )


def draft_operating_profile(
    account_key: str,
    growth_objective: str,
    risk_level: str,
    limit_overrides: Optional[
        Dict[str, Any]
    ] = None,
) -> Dict[str, Any]:
    account_key = (
        normalize_account_key(
            account_key
        )
    )

    growth_key = (
        normalize_growth_key(
            growth_objective
        )
    )

    risk_key = (
        normalize_risk_key(
            risk_level
        )
    )

    effective_limits = (
        build_effective_limits(
            risk_key,
            limit_overrides,
        )
    )

    preset_source = (
        CUSTOM_SOURCE
        if risk_key == "CUSTOM"
        else PRESET_SOURCE
    )

    identity_material = {
        "account_key":
            account_key,

        "growth_key":
            growth_key,

        "risk_key":
            risk_key,

        "effective_limits":
            effective_limits,

        "preset_source":
            preset_source,
    }

    draft_id = (
        "obopdraft_"
        + stable_hash(
            identity_material
        )[:24]
    )

    draft = {
        "schema_version":
            SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "draft_id":
            draft_id,

        "status":
            "DRAFT",

        "account": {
            "account_key":
                account_key,

            "display_label":
                ACCOUNT_REGISTRY[
                    account_key
                ][
                    "label"
                ],

            "explicit_owner_choice_required":
                True,

            "implicit_default_allowed":
                False,
        },

        "growth_objective":
            growth_objective_payload(
                growth_key
            ),

        "risk_envelope":
            risk_envelope_payload(
                risk_key,
                effective_limits,
            ),

        "preset_source":
            preset_source,

        "owner_confirmed":
            False,

        "owner_confirmation_required":
            True,

        "active":
            False,

        "created_at":
            utc_now_iso(),

        "boundaries":
            profile_boundaries(),
    }

    draft[
        "draft_hash"
    ] = recompute_draft_hash(
        draft
    )

    return draft


def validate_draft(
    draft: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(
        draft,
        dict,
    ):
        raise ValueError(
            "Operating-profile draft must be an object."
        )

    if (
        draft.get(
            "schema_version"
        )
        !=
        SCHEMA_VERSION
    ):
        raise ValueError(
            "Unknown operating-profile schema."
        )

    if (
        draft.get(
            "status"
        )
        !=
        "DRAFT"
    ):
        raise ValueError(
            "Operating profile is not a DRAFT."
        )

    account = draft.get(
        "account"
    )

    if not isinstance(
        account,
        dict,
    ):
        raise ValueError(
            "Draft account context is missing."
        )

    normalize_account_key(
        account.get(
            "account_key"
        )
    )

    growth = draft.get(
        "growth_objective"
    )

    risk = draft.get(
        "risk_envelope"
    )

    if not isinstance(
        growth,
        dict,
    ):
        raise ValueError(
            "Growth objective is missing."
        )

    if not isinstance(
        risk,
        dict,
    ):
        raise ValueError(
            "Risk envelope is missing."
        )

    normalize_growth_key(
        growth.get(
            "key"
        )
    )

    normalize_risk_key(
        risk.get(
            "key"
        )
    )

    effective_limits = risk.get(
        "effective_limits"
    )

    if not isinstance(
        effective_limits,
        dict,
    ):
        raise ValueError(
            "Effective limits are missing."
        )

    for key in (
        REQUIRED_LIMIT_KEYS
    ):
        if key not in effective_limits:
            raise ValueError(
                f"Draft is missing limit: {key}"
            )

        validate_limit_value(
            key,
            effective_limits[
                key
            ],
        )

    expected = (
        recompute_draft_hash(
            draft
        )
    )

    if (
        draft.get(
            "draft_hash"
        )
        !=
        expected
    ):
        raise ValueError(
            "Operating-profile draft hash mismatch."
        )

    return deepcopy(
        draft
    )


# -------------------------------------------------------------------------------------------------
# PERSISTENCE
# -------------------------------------------------------------------------------------------------

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


def init_profile_db(
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
            ob_owner_operating_profiles (
                profile_id TEXT PRIMARY KEY,
                owner_id TEXT NOT NULL,
                account_key TEXT NOT NULL,
                revision INTEGER NOT NULL,
                record_status TEXT NOT NULL,
                profile_hash TEXT NOT NULL,
                profile_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE (
                    owner_id,
                    account_key,
                    revision
                )
            )
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_ob_owner_profile_active
            ON ob_owner_operating_profiles (
                owner_id,
                account_key,
                record_status,
                revision DESC
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

        "per_account":
            True,

        "explicit_activation_only":
            True,
    }


# -------------------------------------------------------------------------------------------------
# ACTIVE PROFILE INTEGRITY
#
# Status/timestamps are intentionally excluded from the immutable configuration hash.
#
# This lets an old profile be marked RETIRED without changing the profile configuration
# fingerprint that an earlier TradeIntent may have referenced.
# -------------------------------------------------------------------------------------------------

def _profile_hash_material(
    profile: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "schema_version":
            profile.get(
                "schema_version"
            ),

        "profile_id":
            profile.get(
                "profile_id"
            ),

        "owner_id":
            profile.get(
                "owner_id"
            ),

        "account":
            profile.get(
                "account"
            ),

        "revision":
            profile.get(
                "revision"
            ),

        "growth_objective":
            profile.get(
                "growth_objective"
            ),

        "risk_envelope":
            profile.get(
                "risk_envelope"
            ),

        "preset_source":
            profile.get(
                "preset_source"
            ),

        "owner_confirmed":
            profile.get(
                "owner_confirmed"
            ),

        "boundaries":
            profile.get(
                "boundaries"
            ),
    }


def recompute_profile_hash(
    profile: Dict[str, Any],
) -> str:
    return stable_hash(
        _profile_hash_material(
            profile
        )
    )


def validate_operating_profile(
    profile: Dict[str, Any],
    *,
    require_active: bool = True,
) -> Dict[str, Any]:
    if not isinstance(
        profile,
        dict,
    ):
        raise ValueError(
            "Operating profile must be an object."
        )

    if (
        profile.get(
            "schema_version"
        )
        !=
        SCHEMA_VERSION
    ):
        raise ValueError(
            "Unknown operating-profile schema."
        )

    status = profile.get(
        "status"
    )

    if status not in {
        "ACTIVE",
        "RETIRED",
    }:
        raise ValueError(
            f"Invalid operating-profile status: {status}"
        )

    if (
        require_active
        and
        status != "ACTIVE"
    ):
        raise ValueError(
            "Operating profile is not ACTIVE."
        )

    if (
        profile.get(
            "owner_confirmed"
        )
        is not True
    ):
        raise ValueError(
            "Operating profile was not explicitly owner-confirmed."
        )

    owner_id = clean_text(
        profile.get(
            "owner_id"
        )
    )

    if not owner_id:
        raise ValueError(
            "Operating profile owner_id is required."
        )

    account = profile.get(
        "account"
    )

    if not isinstance(
        account,
        dict,
    ):
        raise ValueError(
            "Operating profile account context is missing."
        )

    normalize_account_key(
        account.get(
            "account_key"
        )
    )

    growth = profile.get(
        "growth_objective"
    )

    risk = profile.get(
        "risk_envelope"
    )

    if not isinstance(
        growth,
        dict,
    ):
        raise ValueError(
            "Growth objective is missing."
        )

    if not isinstance(
        risk,
        dict,
    ):
        raise ValueError(
            "Risk envelope is missing."
        )

    normalize_growth_key(
        growth.get(
            "key"
        )
    )

    normalize_risk_key(
        risk.get(
            "key"
        )
    )

    limits = risk.get(
        "effective_limits"
    )

    if not isinstance(
        limits,
        dict,
    ):
        raise ValueError(
            "Risk envelope limits are missing."
        )

    for key in (
        REQUIRED_LIMIT_KEYS
    ):
        if key not in limits:
            raise ValueError(
                f"Active profile missing limit: {key}"
            )

        validate_limit_value(
            key,
            limits[
                key
            ],
        )

    expected = (
        recompute_profile_hash(
            profile
        )
    )

    if (
        profile.get(
            "profile_hash"
        )
        !=
        expected
    ):
        raise ValueError(
            "Operating-profile integrity hash mismatch."
        )

    return deepcopy(
        profile
    )


def activate_operating_profile(
    owner_id: str,
    draft: Dict[str, Any],
    *,
    owner_confirmed: bool,
    path: Optional[
        Path
    ] = None,
) -> Dict[str, Any]:
    owner_id = clean_text(
        owner_id
    )

    if not owner_id:
        raise ValueError(
            "owner_id is required."
        )

    if owner_confirmed is not True:
        raise ValueError(
            "Explicit owner confirmation is required "
            "before an operating profile can become ACTIVE."
        )

    draft = validate_draft(
        draft
    )

    init_profile_db(
        path
    )

    account = deepcopy(
        draft[
            "account"
        ]
    )

    account_key = (
        account[
            "account_key"
        ]
    )

    now = (
        utc_now_iso()
    )

    with connect(
        path
    ) as conn:
        revision_row = conn.execute(
            """
            SELECT
                COALESCE(
                    MAX(revision),
                    0
                )
                AS max_revision
            FROM
                ob_owner_operating_profiles
            WHERE
                owner_id = ?
                AND account_key = ?
            """,
            (
                owner_id,
                account_key,
            ),
        ).fetchone()

        revision = (
            int(
                revision_row[
                    "max_revision"
                ]
                or 0
            )
            + 1
        )

        profile_identity = {
            "owner_id":
                owner_id,

            "account_key":
                account_key,

            "revision":
                revision,

            "draft_hash":
                draft[
                    "draft_hash"
                ],
        }

        profile_id = (
            "obop_"
            + stable_hash(
                profile_identity
            )[:28]
        )

        profile = {
            "schema_version":
                SCHEMA_VERSION,

            "service_version":
                SERVICE_VERSION,

            "profile_id":
                profile_id,

            "owner_id":
                owner_id,

            "account":
                account,

            "revision":
                revision,

            "status":
                "ACTIVE",

            "growth_objective":
                deepcopy(
                    draft[
                        "growth_objective"
                    ]
                ),

            "risk_envelope":
                deepcopy(
                    draft[
                        "risk_envelope"
                    ]
                ),

            "preset_source":
                draft[
                    "preset_source"
                ],

            "owner_confirmed":
                True,

            "created_at":
                now,

            "updated_at":
                now,

            "activated_at":
                now,

            "retired_at":
                None,

            "boundaries":
                profile_boundaries(),
        }

        profile[
            "profile_hash"
        ] = (
            recompute_profile_hash(
                profile
            )
        )

        # Retire previous ACTIVE revision(s) for this exact owner/account.
        active_rows = conn.execute(
            """
            SELECT
                profile_id,
                profile_json
            FROM
                ob_owner_operating_profiles
            WHERE
                owner_id = ?
                AND account_key = ?
                AND record_status = 'ACTIVE'
            """,
            (
                owner_id,
                account_key,
            ),
        ).fetchall()

        for row in active_rows:
            old_profile = json.loads(
                row[
                    "profile_json"
                ]
            )

            old_profile[
                "status"
            ] = "RETIRED"

            old_profile[
                "updated_at"
            ] = now

            old_profile[
                "retired_at"
            ] = now

            # Configuration fingerprint stays stable because lifecycle
            # status/timestamps are intentionally not hash material.
            validate_operating_profile(
                old_profile,
                require_active=False,
            )

            conn.execute(
                """
                UPDATE
                    ob_owner_operating_profiles
                SET
                    record_status = 'RETIRED',
                    profile_json = ?,
                    updated_at = ?
                WHERE
                    profile_id = ?
                """,
                (
                    canonical_json(
                        old_profile
                    ),
                    now,
                    row[
                        "profile_id"
                    ],
                ),
            )

        conn.execute(
            """
            INSERT INTO
                ob_owner_operating_profiles (
                    profile_id,
                    owner_id,
                    account_key,
                    revision,
                    record_status,
                    profile_hash,
                    profile_json,
                    created_at,
                    updated_at
                )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                profile[
                    "profile_id"
                ],

                owner_id,

                account_key,

                revision,

                "ACTIVE",

                profile[
                    "profile_hash"
                ],

                canonical_json(
                    profile
                ),

                now,

                now,
            ),
        )

        conn.commit()

    return {
        "ok":
            True,

        "activated":
            True,

        "profile":
            profile,
    }


def get_active_operating_profile(
    owner_id: str,
    account_key: str,
    *,
    path: Optional[
        Path
    ] = None,
) -> Optional[
    Dict[str, Any]
]:
    owner_id = clean_text(
        owner_id
    )

    if not owner_id:
        raise ValueError(
            "owner_id is required."
        )

    account_key = (
        normalize_account_key(
            account_key
        )
    )

    init_profile_db(
        path
    )

    with connect(
        path
    ) as conn:
        row = conn.execute(
            """
            SELECT
                profile_json
            FROM
                ob_owner_operating_profiles
            WHERE
                owner_id = ?
                AND account_key = ?
                AND record_status = 'ACTIVE'
            ORDER BY
                revision DESC
            LIMIT 1
            """,
            (
                owner_id,
                account_key,
            ),
        ).fetchone()

    if row is None:
        return None

    profile = json.loads(
        row[
            "profile_json"
        ]
    )

    return (
        validate_operating_profile(
            profile,
            require_active=True,
        )
    )


def list_operating_profile_history(
    owner_id: str,
    account_key: str,
    *,
    path: Optional[
        Path
    ] = None,
) -> List[
    Dict[str, Any]
]:
    owner_id = clean_text(
        owner_id
    )

    if not owner_id:
        raise ValueError(
            "owner_id is required."
        )

    account_key = (
        normalize_account_key(
            account_key
        )
    )

    init_profile_db(
        path
    )

    with connect(
        path
    ) as conn:
        rows = conn.execute(
            """
            SELECT
                revision,
                record_status,
                profile_json
            FROM
                ob_owner_operating_profiles
            WHERE
                owner_id = ?
                AND account_key = ?
            ORDER BY
                revision ASC
            """,
            (
                owner_id,
                account_key,
            ),
        ).fetchall()

    result = []

    for row in rows:
        profile = json.loads(
            row[
                "profile_json"
            ]
        )

        validate_operating_profile(
            profile,
            require_active=False,
        )

        profile[
            "record_status"
        ] = row[
            "record_status"
        ]

        result.append(
            profile
        )

    return result


# -------------------------------------------------------------------------------------------------
# MOST-RESTRICTIVE-WINS COMPOSITION
#
# This does NOT claim the future Safety Kernel is already built.
#
# It merely creates deterministic policy-composition semantics that the
# account policy / mode authority / Safety Kernel can reuse later.
#
# Upper bounds:
#     LOWER wins.
#
# Minimum liquidity requirements:
#     HIGHER wins.
#
# Permissions:
#     FALSE wins.
# -------------------------------------------------------------------------------------------------

def most_restrictive_limits(
    *layers: Optional[
        Dict[str, Any]
    ],
) -> Dict[str, Any]:
    result = {}

    for key in (
        REQUIRED_LIMIT_KEYS
    ):
        values = []

        for layer in layers:
            if not isinstance(
                layer,
                dict,
            ):
                continue

            if (
                key not in layer
                or
                layer.get(
                    key
                )
                is None
            ):
                continue

            values.append(
                validate_limit_value(
                    key,
                    layer[
                        key
                    ],
                )
            )

        if not values:
            result[
                key
            ] = None

            continue

        if key in UPPER_BOUND_LIMITS:
            result[
                key
            ] = min(
                values
            )

        elif key in MINIMUM_REQUIREMENTS:
            result[
                key
            ] = max(
                values
            )

        elif key in PERMISSION_LIMITS:
            result[
                key
            ] = all(
                value is True
                for value
                in values
            )

        else:
            raise RuntimeError(
                f"No restriction rule exists for {key}."
            )

    return result


# -------------------------------------------------------------------------------------------------
# CONTRACT / BOUNDARIES
# -------------------------------------------------------------------------------------------------

def profile_boundaries() -> Dict[str, Any]:
    return {
        "per_account":
            True,

        "explicit_account_selection_required":
            True,

        "implicit_account_default":
            False,

        "growth_and_risk_independent":
            True,

        "owner_confirmation_required":
            True,

        "software_policy_templates":
            True,

        "expected_return_target":
            False,

        "profit_guarantee":
            False,

        "investment_advice_claim":
            False,

        "owner_fit_calculated_here":
            False,

        "candidate_ranking_calculated_here":
            False,

        "market_truth_modified":
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


def account_registry() -> Dict[str, Any]:
    return deepcopy(
        ACCOUNT_REGISTRY
    )


def growth_objectives() -> Dict[str, Any]:
    return deepcopy(
        GROWTH_OBJECTIVES
    )


def risk_levels() -> Dict[str, Any]:
    return deepcopy(
        RISK_LEVELS
    )


def risk_templates() -> Dict[str, Any]:
    return deepcopy(
        RISK_TEMPLATES
    )


def operating_profile_contract() -> Dict[str, Any]:
    return {
        "schema_version":
            SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "authority":
            "OWNER_OPERATING_PROFILE",

        "profile_authority":
            SCHEMA_VERSION,

        "per_account":
            True,

        "implicit_default_account":
            False,

        "accounts":
            account_registry(),

        "growth_objectives":
            growth_objectives(),

        "risk_levels":
            risk_levels(),

        "risk_templates":
            risk_templates(),

        "limit_units":
            deepcopy(
                LIMIT_UNITS
            ),

        "preset_source":
            PRESET_SOURCE,

        "custom_source":
            CUSTOM_SOURCE,

        "owner_confirmation_required":
            True,

        "growth_and_risk_independent":
            True,

        "most_restrictive_policy_available":
            True,

        "owner_fit_authority":
            "PENDING_OBRISK006_010",

        "boundaries":
            profile_boundaries(),
    }
