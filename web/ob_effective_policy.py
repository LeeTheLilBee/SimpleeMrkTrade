
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from typing import Any, Dict, Iterable, List, Optional
import json

from web.ob_account_identity_truth import (
    resolve_account_identity,
)

from web.ob_owner_operating_profile import (
    LIMIT_UNITS,
    MINIMUM_REQUIREMENTS,
    PERMISSION_LIMITS,
    REQUIRED_LIMIT_KEYS,
    UPPER_BOUND_LIMITS,
    most_restrictive_limits,
    validate_limit_value,
    validate_operating_profile,
)


SCHEMA_VERSION = "OB_EFFECTIVE_POLICY_V1"
LAYER_SCHEMA_VERSION = "OB_POLICY_LAYER_V1"
SERVICE_VERSION = "OBPOLICY001_010_POLICY_REGISTRY_MOST_RESTRICTIVE"

OWNER_PROFILE_AUTHORITY = "OB_OWNER_OPERATING_PROFILE_V1"
ACCOUNT_IDENTITY_AUTHORITY = "OB_ACCOUNT_IDENTITY_TRUTH_V1"

MOST_RESTRICTIVE_PRIMITIVE = (
    "OB_OWNER_OPERATING_PROFILE_V1.most_restrictive_limits"
)

NO_POLICY_PERSISTENCE = True
NO_SILENT_POLICY_MUTATION = True
NO_POLICY_WIDENING = True


CAPABILITY_KEYS = (
    "broker_submission_allowed",
    "capital_movement_allowed",
    "automatic_contract_selection_allowed",
    "hybrid_execution_allowed",
    "automatic_execution_allowed",
)


POLICY_SOURCE_REGISTRY = {

    "PRODUCT_PHASE_LOCK": {
        "source_authority":
            SCHEMA_VERSION,

        "status":
            "ACTIVE",

        "runtime_allowed":
            True,

        "owner_confirmation_required":
            False,

        "persistence":
            False,

        "description":
            (
                "Hard current-product phase locks. "
                "This layer can only restrict."
            ),
    },

    "OWNER_OPERATING_PROFILE": {
        "source_authority":
            OWNER_PROFILE_AUTHORITY,

        "status":
            "ACTIVE",

        "runtime_allowed":
            True,

        "owner_confirmation_required":
            True,

        "persistence":
            True,

        "description":
            (
                "Explicitly owner-confirmed per-account operating profile."
            ),
    },

    "EXPLICIT_OWNER_RESTRICTION": {
        "source_authority":
            SCHEMA_VERSION,

        "status":
            "ACTIVE",

        "runtime_allowed":
            True,

        "owner_confirmation_required":
            True,

        "persistence":
            False,

        "description":
            (
                "Explicit non-persistent owner restriction layer. "
                "It may tighten effective policy but can never widen it."
            ),
    },

    "MODE_POLICY": {
        "source_authority":
            "PENDING_OBMODE",

        "status":
            "PENDING",

        "runtime_allowed":
            False,

        "owner_confirmation_required":
            False,

        "persistence":
            False,

        "description":
            "Future mode-capability policy layer.",
    },

    "CAPITAL_POLICY": {
        "source_authority":
            "PENDING_OBCAP",

        "status":
            "PENDING",

        "runtime_allowed":
            False,

        "owner_confirmation_required":
            False,

        "persistence":
            False,

        "description":
            "Future capital-authority restriction layer.",
    },

    "PORTFOLIO_POLICY": {
        "source_authority":
            "PENDING_OBPORT",

        "status":
            "PENDING",

        "runtime_allowed":
            False,

        "owner_confirmation_required":
            False,

        "persistence":
            False,

        "description":
            "Future portfolio-exposure restriction layer.",
    },

    "SAFETY_KERNEL_POLICY": {
        "source_authority":
            "PENDING_OBSAFE",

        "status":
            "PENDING",

        "runtime_allowed":
            False,

        "owner_confirmation_required":
            False,

        "persistence":
            False,

        "description":
            "Future Safety Kernel restriction layer.",
    },
}


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
        canonical_json(value).encode(
            "utf-8"
        )
    ).hexdigest()


def policy_source_registry() -> Dict[str, Any]:
    return deepcopy(
        POLICY_SOURCE_REGISTRY
    )


def restriction_rule_for(
    key: str,
) -> str:

    if key in UPPER_BOUND_LIMITS:
        return "LOWER_WINS"

    if key in MINIMUM_REQUIREMENTS:
        return "HIGHER_WINS"

    if key in PERMISSION_LIMITS:
        return "FALSE_WINS"

    raise ValueError(
        f"No restriction rule exists for {key}."
    )


def _known_account(
    account_key: Any,
) -> Dict[str, Any]:

    identity = resolve_account_identity(
        account_key
    )

    if identity.get(
        "known"
    ) is not True:
        raise ValueError(
            "Effective policy requires an explicit known account."
        )

    return identity


def _normalize_limits(
    limits: Optional[
        Dict[str, Any]
    ],
) -> Dict[str, Any]:

    if limits is None:
        return {}

    if not isinstance(
        limits,
        dict,
    ):
        raise ValueError(
            "Policy limits must be an object."
        )

    result = {}

    for key, value in limits.items():

        if key not in REQUIRED_LIMIT_KEYS:
            raise ValueError(
                f"Unknown policy limit: {key}"
            )

        result[
            key
        ] = validate_limit_value(
            key,
            value,
        )

    return result


def _normalize_capabilities(
    capabilities: Optional[
        Dict[str, Any]
    ],
    *,
    restriction_only: bool,
) -> Dict[str, bool]:

    if capabilities is None:
        return {}

    if not isinstance(
        capabilities,
        dict,
    ):
        raise ValueError(
            "Policy capabilities must be an object."
        )

    result = {}

    for key, value in capabilities.items():

        if key not in CAPABILITY_KEYS:
            raise ValueError(
                f"Unknown policy capability: {key}"
            )

        if not isinstance(
            value,
            bool,
        ):
            raise ValueError(
                f"{key} must be boolean."
            )

        if (
            restriction_only
            and
            value is True
        ):
            raise ValueError(
                (
                    "Explicit restriction layers cannot "
                    f"grant capability: {key}"
                )
            )

        result[
            key
        ] = value

    return result


def _layer_material(
    layer: Dict[str, Any],
) -> Dict[str, Any]:

    return {
        key:
            deepcopy(
                value
            )
        for key, value
        in layer.items()
        if key
        !=
        "layer_fingerprint"
    }


def recompute_layer_fingerprint(
    layer: Dict[str, Any],
) -> str:

    return stable_hash(
        _layer_material(
            layer
        )
    )


def _build_layer(
    *,
    layer_id: str,
    layer_class: str,
    account_key: str,
    source_authority: str,
    limits: Optional[
        Dict[str, Any]
    ],
    capabilities: Optional[
        Dict[str, Any]
    ],
    source_ref: Optional[
        Dict[str, Any]
    ] = None,
    owner_confirmed: bool,
    restriction_only: bool,
) -> Dict[str, Any]:

    layer_id = str(
        layer_id
        or ""
    ).strip()

    if not layer_id:
        raise ValueError(
            "Policy layer_id is required."
        )

    layer_class = str(
        layer_class
        or ""
    ).strip()

    config = POLICY_SOURCE_REGISTRY.get(
        layer_class
    )

    if not config:
        raise ValueError(
            f"Unknown policy layer class: {layer_class}"
        )

    if config[
        "status"
    ] != "ACTIVE":

        raise ValueError(
            (
                f"Policy layer {layer_class} "
                "is not active yet."
            )
        )

    if config[
        "runtime_allowed"
    ] is not True:

        raise ValueError(
            (
                f"Policy layer {layer_class} "
                "is not runtime-authorized."
            )
        )

    if (
        source_authority
        !=
        config[
            "source_authority"
        ]
    ):
        raise ValueError(
            (
                f"Wrong source authority for "
                f"{layer_class}."
            )
        )

    identity = _known_account(
        account_key
    )

    if (
        config[
            "owner_confirmation_required"
        ]
        and
        owner_confirmed is not True
    ):
        raise ValueError(
            (
                f"{layer_class} requires "
                "explicit owner confirmation."
            )
        )

    normalized_limits = (
        _normalize_limits(
            limits
        )
    )

    normalized_capabilities = (
        _normalize_capabilities(
            capabilities,
            restriction_only=
                restriction_only,
        )
    )

    layer = {
        "schema_version":
            LAYER_SCHEMA_VERSION,

        "policy_authority":
            SCHEMA_VERSION,

        "layer_id":
            layer_id,

        "layer_class":
            layer_class,

        "status":
            "ACTIVE",

        "account_key":
            identity[
                "account_key"
            ],

        "account_identity_fingerprint":
            identity[
                "identity_fingerprint"
            ],

        "source_authority":
            source_authority,

        "source_ref":
            deepcopy(
                source_ref
                or {}
            ),

        "owner_confirmed":
            bool(
                owner_confirmed
            ),

        "limits":
            normalized_limits,

        "capabilities":
            normalized_capabilities,

        "restriction_only":
            bool(
                restriction_only
            ),

        "persistent_here":
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

    layer[
        "layer_fingerprint"
    ] = recompute_layer_fingerprint(
        layer
    )

    return layer


def validate_policy_layer(
    layer: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        layer,
        dict,
    ):
        raise ValueError(
            "Policy layer must be an object."
        )

    if (
        layer.get(
            "schema_version"
        )
        !=
        LAYER_SCHEMA_VERSION
    ):
        raise ValueError(
            "Unknown policy-layer schema."
        )

    layer_class = str(
        layer.get(
            "layer_class"
        )
        or ""
    )

    config = POLICY_SOURCE_REGISTRY.get(
        layer_class
    )

    if not config:
        raise ValueError(
            f"Unknown policy layer class: {layer_class}"
        )

    if config[
        "status"
    ] != "ACTIVE":

        raise ValueError(
            f"Policy layer {layer_class} is pending."
        )

    if (
        layer.get(
            "source_authority"
        )
        !=
        config[
            "source_authority"
        ]
    ):
        raise ValueError(
            "Policy layer source authority mismatch."
        )

    _known_account(
        layer.get(
            "account_key"
        )
    )

    if (
        config[
            "owner_confirmation_required"
        ]
        and
        layer.get(
            "owner_confirmed"
        )
        is not True
    ):
        raise ValueError(
            "Policy layer lacks required owner confirmation."
        )

    _normalize_limits(
        layer.get(
            "limits"
        )
    )

    _normalize_capabilities(
        layer.get(
            "capabilities"
        ),
        restriction_only=
            bool(
                layer.get(
                    "restriction_only"
                )
            ),
    )

    expected = recompute_layer_fingerprint(
        layer
    )

    if (
        layer.get(
            "layer_fingerprint"
        )
        !=
        expected
    ):
        raise ValueError(
            "Policy layer fingerprint mismatch."
        )

    if (
        layer.get(
            "execution_authority"
        )
        is not False
        or
        layer.get(
            "broker_submission"
        )
        is not False
        or
        layer.get(
            "capital_movement"
        )
        is not False
        or
        layer.get(
            "automatic_contract_selection"
        )
        is not False
        or
        layer.get(
            "automatic_execution"
        )
        is not False
    ):
        raise ValueError(
            "Policy layer contains forbidden authority."
        )

    return deepcopy(
        layer
    )


def product_phase_policy_layer(
    account_key: str,
) -> Dict[str, Any]:

    identity = _known_account(
        account_key
    )

    return _build_layer(
        layer_id=(
            "product_phase_lock:"
            + identity[
                "account_key"
            ]
        ),

        layer_class=
            "PRODUCT_PHASE_LOCK",

        account_key=
            identity[
                "account_key"
            ],

        source_authority=
            SCHEMA_VERSION,

        limits={
            "live_automation_allowed":
                False,
        },

        capabilities={
            key:
                False
            for key
            in CAPABILITY_KEYS
        },

        source_ref={
            "phase":
                "CURRENT_OB_BUILD_PHASE",

            "live_automation_locked":
                True,

            "broker_submission_locked":
                True,

            "capital_movement_locked":
                True,

            "hybrid_execution_locked":
                True,

            "automatic_execution_locked":
                True,
        },

        owner_confirmed=
            False,

        restriction_only=
            True,
    )


def owner_profile_policy_layer(
    profile: Dict[str, Any],
) -> Dict[str, Any]:

    profile = validate_operating_profile(
        profile,
        require_active=True,
    )

    account = profile[
        "account"
    ]

    risk = profile[
        "risk_envelope"
    ]

    boundaries = (
        profile.get(
            "boundaries"
        )
        or {}
    )

    account_key = account[
        "account_key"
    ]

    return _build_layer(
        layer_id=(
            "owner_profile:"
            + profile[
                "profile_id"
            ]
        ),

        layer_class=
            "OWNER_OPERATING_PROFILE",

        account_key=
            account_key,

        source_authority=
            OWNER_PROFILE_AUTHORITY,

        limits=
            risk[
                "effective_limits"
            ],

        capabilities={
            "broker_submission_allowed":
                bool(
                    boundaries.get(
                        "broker_submission"
                    )
                ),

            "capital_movement_allowed":
                bool(
                    boundaries.get(
                        "capital_movement"
                    )
                ),

            "automatic_contract_selection_allowed":
                bool(
                    boundaries.get(
                        "automatic_contract_selection"
                    )
                ),

            "hybrid_execution_allowed":
                bool(
                    boundaries.get(
                        "hybrid_execution"
                    )
                ),

            "automatic_execution_allowed":
                bool(
                    boundaries.get(
                        "automatic_execution"
                    )
                ),
        },

        source_ref={
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

            "owner_id":
                profile[
                    "owner_id"
                ],
        },

        owner_confirmed=
            True,

        restriction_only=
            False,
    )


def bound_owner_profile_policy_layer(
    intent: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        intent,
        dict,
    ):
        raise ValueError(
            "Trade Intent must be an object."
        )

    account_context = (
        intent.get(
            "account_context"
        )
        or {}
    )

    owner_fit = (
        intent.get(
            "owner_fit"
        )
        or {}
    )

    risk_ref = (
        owner_fit.get(
            "risk_envelope_ref"
        )
        or {}
    )

    account_ref = (
        owner_fit.get(
            "account_policy_ref"
        )
        or {}
    )

    if (
        account_context.get(
            "status"
        )
        !=
        "BOUND"
    ):
        raise ValueError(
            (
                "Effective policy requires "
                "BOUND account context."
            )
        )

    if (
        account_context.get(
            "explicit_owner_choice"
        )
        is not True
    ):
        raise ValueError(
            "Effective policy requires explicit owner account choice."
        )

    account_key = account_context.get(
        "account_key"
    )

    identity = _known_account(
        account_key
    )

    required_profile_ref = {
        "profile_id":
            account_context.get(
                "profile_id"
            ),

        "profile_revision":
            account_context.get(
                "profile_revision"
            ),

        "profile_hash":
            account_context.get(
                "profile_hash"
            ),
    }

    if not all(
        required_profile_ref.values()
    ):
        raise ValueError(
            "Bound profile identity is incomplete."
        )

    for key, value in required_profile_ref.items():

        if (
            risk_ref.get(
                key
            )
            !=
            value
        ):
            raise ValueError(
                (
                    "Risk-envelope profile binding "
                    f"mismatch: {key}"
                )
            )

    if (
        account_ref.get(
            "account_key"
        )
        !=
        identity[
            "account_key"
        ]
    ):
        raise ValueError(
            "Account-policy reference account mismatch."
        )

    if (
        account_ref.get(
            "profile_id"
        )
        !=
        required_profile_ref[
            "profile_id"
        ]
    ):
        raise ValueError(
            "Account-policy profile binding mismatch."
        )

    if (
        account_ref.get(
            "profile_revision"
        )
        !=
        required_profile_ref[
            "profile_revision"
        ]
    ):
        raise ValueError(
            "Account-policy revision binding mismatch."
        )

    limits = risk_ref.get(
        "effective_limits"
    )

    if not isinstance(
        limits,
        dict,
    ):
        raise ValueError(
            "Bound risk-envelope limits are missing."
        )

    missing = [
        key
        for key
        in REQUIRED_LIMIT_KEYS
        if key
        not in limits
    ]

    if missing:
        raise ValueError(
            (
                "Bound risk envelope is incomplete: "
                + ", ".join(
                    missing
                )
            )
        )

    normalized_limits = {
        key:
            validate_limit_value(
                key,
                limits[
                    key
                ],
            )
        for key
        in REQUIRED_LIMIT_KEYS
    }

    if (
        normalized_limits[
            "live_automation_allowed"
        ]
        is not False
    ):
        raise ValueError(
            "Bound owner profile cannot enable live automation."
        )

    return _build_layer(
        layer_id=(
            "bound_owner_profile:"
            + str(
                required_profile_ref[
                    "profile_id"
                ]
            )
        ),

        layer_class=
            "OWNER_OPERATING_PROFILE",

        account_key=
            identity[
                "account_key"
            ],

        source_authority=
            OWNER_PROFILE_AUTHORITY,

        limits=
            normalized_limits,

        capabilities={
            key:
                False
            for key
            in CAPABILITY_KEYS
        },

        source_ref={
            **required_profile_ref,

            "risk_key":
                risk_ref.get(
                    "risk_key"
                ),

            "binding_authority":
                (
                    "OB_TRADE_INTENT_V1."
                    "bind_owner_operating_profile"
                ),
        },

        owner_confirmed=
            True,

        restriction_only=
            False,
    )


def explicit_owner_restriction_layer(
    *,
    account_key: str,
    restriction_id: str,
    restrictions: Dict[str, Any],
    owner_confirmed: bool,
    capability_restrictions: Optional[
        Dict[str, Any]
    ] = None,
) -> Dict[str, Any]:

    restriction_id = str(
        restriction_id
        or ""
    ).strip()

    if not restriction_id:
        raise ValueError(
            "restriction_id is required."
        )

    if owner_confirmed is not True:
        raise ValueError(
            "Explicit owner confirmation is required."
        )

    normalized = _normalize_limits(
        restrictions
    )

    if not normalized:
        raise ValueError(
            "At least one restriction is required."
        )

    return _build_layer(
        layer_id=(
            "owner_restriction:"
            + restriction_id
        ),

        layer_class=
            "EXPLICIT_OWNER_RESTRICTION",

        account_key=
            account_key,

        source_authority=
            SCHEMA_VERSION,

        limits=
            normalized,

        capabilities=
            capability_restrictions
            or {},

        source_ref={
            "restriction_id":
                restriction_id,

            "adoption_persisted":
                False,

            "future_event_authority":
                "PENDING_OBEVENT",
        },

        owner_confirmed=
            True,

        restriction_only=
            True,
    )


def _limit_entries(
    *,
    key: str,
    layers: Iterable[
        Dict[str, Any]
    ],
) -> List[Dict[str, Any]]:

    result = []

    for layer in layers:

        limits = layer.get(
            "limits"
        ) or {}

        if (
            key not in limits
            or
            limits.get(
                key
            )
            is None
        ):
            continue

        result.append(
            {
                "layer_id":
                    layer[
                        "layer_id"
                    ],

                "layer_class":
                    layer[
                        "layer_class"
                    ],

                "source_authority":
                    layer[
                        "source_authority"
                    ],

                "value":
                    limits[
                        key
                    ],
            }
        )

    return result


def _is_tighter(
    *,
    key: str,
    baseline: Any,
    effective: Any,
) -> bool:

    if key in UPPER_BOUND_LIMITS:
        return effective < baseline

    if key in MINIMUM_REQUIREMENTS:
        return effective > baseline

    if key in PERMISSION_LIMITS:
        return (
            baseline is True
            and
            effective is False
        )

    raise RuntimeError(
        f"No restriction rule for {key}."
    )


def _is_wider(
    *,
    key: str,
    baseline: Any,
    effective: Any,
) -> bool:

    if key in UPPER_BOUND_LIMITS:
        return effective > baseline

    if key in MINIMUM_REQUIREMENTS:
        return effective < baseline

    if key in PERMISSION_LIMITS:
        return (
            baseline is False
            and
            effective is True
        )

    raise RuntimeError(
        f"No restriction rule for {key}."
    )


def resolve_effective_policy(
    *,
    account_key: str,
    layers: Iterable[
        Dict[str, Any]
    ],
) -> Dict[str, Any]:

    identity = _known_account(
        account_key
    )

    normalized_layers = [
        validate_policy_layer(
            layer
        )
        for layer
        in layers
    ]

    if not normalized_layers:
        raise ValueError(
            "Effective policy requires policy layers."
        )

    normalized_layers = sorted(
        normalized_layers,
        key=lambda item: (
            item[
                "layer_class"
            ],
            item[
                "layer_id"
            ],
        ),
    )

    layer_ids = [
        layer[
            "layer_id"
        ]
        for layer
        in normalized_layers
    ]

    for layer in normalized_layers:

        if (
            layer[
                "account_key"
            ]
            !=
            identity[
                "account_key"
            ]
        ):
            raise ValueError(
                "Policy layers may not cross account boundaries."
            )

    owner_layers = [
        layer
        for layer
        in normalized_layers
        if layer[
            "layer_class"
        ]
        ==
        "OWNER_OPERATING_PROFILE"
    ]

    if len(
        owner_layers
    ) != 1:

        raise ValueError(
            (
                "Effective policy requires exactly one "
                "owner operating profile layer."
            )
        )

    product_layers = [
        layer
        for layer
        in normalized_layers
        if layer[
            "layer_class"
        ]
        ==
        "PRODUCT_PHASE_LOCK"
    ]

    if len(
        product_layers
    ) != 1:

        raise ValueError(
            (
                "Effective policy requires exactly one "
                "product-phase lock layer."
            )
        )

    if (
        len(
            layer_ids
        )
        !=
        len(
            set(
                layer_ids
            )
        )
    ):
        raise ValueError(
            "Duplicate policy layer_id."
        )

    effective_limits = (
        most_restrictive_limits(
            *[
                layer[
                    "limits"
                ]
                for layer
                in normalized_layers
            ]
        )
    )

    missing = [
        key
        for key
        in REQUIRED_LIMIT_KEYS
        if effective_limits.get(
            key
        )
        is None
    ]

    if missing:
        raise ValueError(
            (
                "Effective policy is incomplete: "
                + ", ".join(
                    missing
                )
            )
        )

    baseline = deepcopy(
        owner_layers[0][
            "limits"
        ]
    )

    per_limit_resolution = {}

    tightened_keys = []
    widened_keys = []

    for key in REQUIRED_LIMIT_KEYS:

        selected = effective_limits[
            key
        ]

        baseline_value = baseline[
            key
        ]

        entries = _limit_entries(
            key=key,
            layers=normalized_layers,
        )

        winners = [
            entry[
                "layer_id"
            ]
            for entry
            in entries
            if entry[
                "value"
            ]
            ==
            selected
        ]

        tightened = _is_tighter(
            key=key,
            baseline=baseline_value,
            effective=selected,
        )

        widened = _is_wider(
            key=key,
            baseline=baseline_value,
            effective=selected,
        )

        if tightened:
            tightened_keys.append(
                key
            )

        if widened:
            widened_keys.append(
                key
            )

        per_limit_resolution[
            key
        ] = {
            "rule":
                restriction_rule_for(
                    key
                ),

            "unit":
                LIMIT_UNITS[
                    key
                ],

            "owner_profile_baseline":
                baseline_value,

            "effective_value":
                selected,

            "contributors":
                entries,

            "winning_layer_ids":
                sorted(
                    winners
                ),

            "tightened_from_owner_profile":
                tightened,

            "widened_from_owner_profile":
                widened,
        }

    if widened_keys:
        raise RuntimeError(
            (
                "Effective policy attempted to widen "
                "owner policy: "
                + ", ".join(
                    sorted(
                        widened_keys
                    )
                )
            )
        )

    if (
        effective_limits[
            "live_automation_allowed"
        ]
        is not False
    ):
        raise RuntimeError(
            "Effective policy may not unlock live automation."
        )

    effective_capabilities = {}

    capability_resolution = {}

    for key in CAPABILITY_KEYS:

        entries = [
            {
                "layer_id":
                    layer[
                        "layer_id"
                    ],

                "layer_class":
                    layer[
                        "layer_class"
                    ],

                "value":
                    layer[
                        "capabilities"
                    ][
                        key
                    ],
            }
            for layer
            in normalized_layers
            if key
            in layer.get(
                "capabilities",
                {},
            )
        ]

        values = [
            entry[
                "value"
            ]
            for entry
            in entries
        ]

        # No explicit grant = deny.
        # Any False = deny.
        selected = (
            bool(
                values
            )
            and
            all(
                value is True
                for value
                in values
            )
        )

        effective_capabilities[
            key
        ] = selected

        capability_resolution[
            key
        ] = {
            "rule":
                "FALSE_WINS_DEFAULT_DENY",

            "contributors":
                entries,

            "effective_value":
                selected,
        }

    if any(
        effective_capabilities.values()
    ):
        raise RuntimeError(
            "OBPOLICY may not grant execution/capital capability."
        )

    material = {
        "schema_version":
            SCHEMA_VERSION,

        "account_key":
            identity[
                "account_key"
            ],

        "account_identity_fingerprint":
            identity[
                "identity_fingerprint"
            ],

        "layer_fingerprints":
            [
                layer[
                    "layer_fingerprint"
                ]
                for layer
                in normalized_layers
            ],

        "effective_limits":
            effective_limits,

        "effective_capabilities":
            effective_capabilities,

        "per_limit_resolution":
            per_limit_resolution,

        "capability_resolution":
            capability_resolution,
    }

    policy_fingerprint = stable_hash(
        material
    )

    policy_id = (
        "obpolicy_"
        + policy_fingerprint[:28]
    )

    source_layer_refs = [
        {
            "layer_id":
                layer[
                    "layer_id"
                ],

            "layer_class":
                layer[
                    "layer_class"
                ],

            "source_authority":
                layer[
                    "source_authority"
                ],

            "layer_fingerprint":
                layer[
                    "layer_fingerprint"
                ],

            "source_ref":
                deepcopy(
                    layer[
                        "source_ref"
                    ]
                ),
        }
        for layer
        in normalized_layers
    ]

    reference = {
        "authority":
            SCHEMA_VERSION,

        "policy_id":
            policy_id,

        "policy_fingerprint":
            policy_fingerprint,

        "account_key":
            identity[
                "account_key"
            ],

        "effective_limits":
            deepcopy(
                effective_limits
            ),

        "effective_capabilities":
            deepcopy(
                effective_capabilities
            ),

        "layer_fingerprints":
            [
                item[
                    "layer_fingerprint"
                ]
                for item
                in source_layer_refs
            ],

        "tightened_keys":
            sorted(
                tightened_keys
            ),

        "owner_profile_widened":
            False,
    }

    return {
        "ok":
            True,

        "schema_version":
            SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "authority":
            SCHEMA_VERSION,

        "policy_id":
            policy_id,

        "policy_fingerprint":
            policy_fingerprint,

        "status":
            "RESOLVED",

        "account_identity":
            identity,

        "account_key":
            identity[
                "account_key"
            ],

        "source_layers":
            source_layer_refs,

        "effective_limits":
            deepcopy(
                effective_limits
            ),

        "per_limit_resolution":
            per_limit_resolution,

        "effective_capabilities":
            effective_capabilities,

        "capability_resolution":
            capability_resolution,

        "tightened_keys":
            sorted(
                tightened_keys
            ),

        "widened_keys":
            [],

        "owner_profile_widened":
            False,

        "most_restrictive_primitive":
            MOST_RESTRICTIVE_PRIMITIVE,

        "silent_policy_mutation":
            False,

        "policy_persisted":
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

        "reference":
            reference,
    }


def resolve_effective_policy_for_profile(
    profile: Dict[str, Any],
    *,
    extra_layers: Optional[
        Iterable[
            Dict[str, Any]
        ]
    ] = None,
) -> Dict[str, Any]:

    owner_layer = (
        owner_profile_policy_layer(
            profile
        )
    )

    account_key = owner_layer[
        "account_key"
    ]

    product_layer = (
        product_phase_policy_layer(
            account_key
        )
    )

    layers = [
        owner_layer,
        product_layer,
    ]

    if extra_layers is not None:
        layers.extend(
            list(
                extra_layers
            )
        )

    return resolve_effective_policy(
        account_key=
            account_key,

        layers=
            layers,
    )


def resolve_effective_policy_for_intent(
    intent: Dict[str, Any],
    *,
    extra_layers: Optional[
        Iterable[
            Dict[str, Any]
        ]
    ] = None,
) -> Dict[str, Any]:

    owner_layer = (
        bound_owner_profile_policy_layer(
            intent
        )
    )

    account_key = owner_layer[
        "account_key"
    ]

    product_layer = (
        product_phase_policy_layer(
            account_key
        )
    )

    layers = [
        owner_layer,
        product_layer,
    ]

    if extra_layers is not None:
        layers.extend(
            list(
                extra_layers
            )
        )

    return resolve_effective_policy(
        account_key=
            account_key,

        layers=
            layers,
    )


def effective_policy_contract() -> Dict[str, Any]:

    return {
        "schema_version":
            SCHEMA_VERSION,

        "layer_schema_version":
            LAYER_SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "authority":
            "CANONICAL_EFFECTIVE_POLICY",

        "account_identity_authority":
            ACCOUNT_IDENTITY_AUTHORITY,

        "owner_profile_authority":
            OWNER_PROFILE_AUTHORITY,

        "most_restrictive_primitive":
            MOST_RESTRICTIVE_PRIMITIVE,

        "policy_source_registry":
            policy_source_registry(),

        "upper_bound_rule":
            "LOWER_WINS",

        "minimum_requirement_rule":
            "HIGHER_WINS",

        "permission_rule":
            "FALSE_WINS",

        "missing_capability_rule":
            "DEFAULT_DENY",

        "policy_widening":
            False,

        "silent_policy_mutation":
            False,

        "policy_persistence":
            False,

        "owner_profile_mutation":
            False,

        "market_truth_mutation":
            False,

        "candidate_score_mutation":
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

        "future_policy_authorities": {
            "mode_policy":
                "PENDING_OBMODE",

            "capital_policy":
                "PENDING_OBCAP",

            "portfolio_policy":
                "PENDING_OBPORT",

            "safety_kernel_policy":
                "PENDING_OBSAFE",
        },
    }
