from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from typing import Any, Dict, Optional
import json


SCHEMA_VERSION = "OB_DECISION_CONTEXT_V1"
SERVICE_VERSION = "OBCTX001_005_CANONICAL_DECISION_CONTEXT"

AUTHORITY_ID = SCHEMA_VERSION

TRADE_INTENT_AUTHORITY = "OB_TRADE_INTENT_V1"
ACCOUNT_IDENTITY_AUTHORITY = "OB_ACCOUNT_IDENTITY_TRUTH_V1"
OWNER_PROFILE_AUTHORITY = "OB_OWNER_OPERATING_PROFILE_V1"
EFFECTIVE_POLICY_AUTHORITY = "OB_EFFECTIVE_POLICY_V1"
OWNER_FIT_AUTHORITY = "OB_OWNER_FIT_ELIGIBILITY_V1"
EVENT_AUTHORITY = "OB_COMMAND_EVENT_CAUSAL_V1"

PENDING_MODE_AUTHORITY = "PENDING_OBMODE"
PENDING_PROVENANCE_AUTHORITY = "PENDING_OBDATA011_015"
PENDING_TIME_AUTHORITY = "PENDING_OBTIME"


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


def _object(
    value: Any,
    *,
    label: str,
) -> Dict[str, Any]:

    if not isinstance(value, dict):
        raise ValueError(
            f"{label} must be an object."
        )

    return deepcopy(value)


def _text(
    value: Any,
    *,
    label: str,
) -> str:

    result = (
        ""
        if value is None
        else str(value).strip()
    )

    if not result:
        raise ValueError(
            f"{label} is required."
        )

    return result


def _account_key_from_profile(
    profile: Dict[str, Any],
) -> str:

    account = profile.get("account")

    if not isinstance(account, dict):
        raise ValueError(
            "Owner profile account context is missing."
        )

    return _text(
        account.get("account_key"),
        label="owner profile account_key",
    )


def _optional_owner_fit_account_key(
    owner_fit: Dict[str, Any],
) -> Optional[str]:

    candidates = [
        owner_fit.get("account_key"),
    ]

    for key in (
        "account",
        "account_context",
        "account_identity",
        "policy_ref",
        "effective_policy_ref",
    ):
        nested = owner_fit.get(key)

        if isinstance(nested, dict):
            candidates.append(
                nested.get("account_key")
            )

    for candidate in candidates:

        if (
            candidate is not None
            and
            str(candidate).strip()
        ):
            return str(candidate).strip()

    return None


def _lineage_fingerprint(
    value: Optional[Dict[str, Any]],
    *preferred_keys: str,
) -> Optional[str]:

    if value is None:
        return None

    for key in preferred_keys:
        found = value.get(key)

        if (
            found is not None
            and
            str(found).strip()
        ):
            return str(found).strip()

    return stable_hash(value)


def decision_context_contract() -> Dict[str, Any]:

    return {
        "schema_version":
            SCHEMA_VERSION,

        "authority_id":
            AUTHORITY_ID,

        "immutable_snapshot":
            True,

        "immutability_mechanism":
            "HASH_BOUND_SNAPSHOT",

        "explicit_account_required":
            True,

        "source_authorities_mutated":
            False,

        "candidate_recalculated":
            False,

        "market_score_recalculated":
            False,

        "options_research_recalculated":
            False,

        "owner_profile_mutated":
            False,

        "effective_policy_recalculated":
            False,

        "owner_fit_recalculated":
            False,

        "event_history_mutated":
            False,

        "automatic_contract_selection":
            False,

        "execution_authority":
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

        "pending_future_authorities": {
            "mode_authority":
                PENDING_MODE_AUTHORITY,

            "source_provenance":
                PENDING_PROVENANCE_AUTHORITY,

            "temporal_context":
                PENDING_TIME_AUTHORITY,
        },
    }


def _context_hash_material(
    context: Dict[str, Any],
) -> Dict[str, Any]:

    result = deepcopy(context)

    result.pop(
        "context_id",
        None,
    )

    result.pop(
        "context_fingerprint",
        None,
    )

    return result


def recompute_context_fingerprint(
    context: Dict[str, Any],
) -> str:

    return stable_hash(
        _context_hash_material(
            context
        )
    )


def build_decision_context(
    *,
    trade_intent: Dict[str, Any],
    account_identity: Dict[str, Any],
    owner_profile: Dict[str, Any],
    effective_policy: Dict[str, Any],
    owner_fit: Dict[str, Any],
    causal_event: Optional[
        Dict[str, Any]
    ] = None,
    invalidation_plan: Optional[
        Dict[str, Any]
    ] = None,
    authority_registry: Optional[
        Dict[str, Any]
    ] = None,
) -> Dict[str, Any]:

    # ------------------------------------------------------------------------------------------
    # CRITICAL OBCTX BUG FIX:
    #
    # validate_trade_intent() returns a VALIDATION SUMMARY.
    # It does NOT return the Trade Intent.
    #
    # Never do:
    #
    #     trade_intent = validate_trade_intent(trade_intent)
    #
    # Correct behavior:
    #
    #     validate_trade_intent(trade_intent)
    #     bound_intent = deepcopy(trade_intent)
    # ------------------------------------------------------------------------------------------

    from web.ob_trade_intent import (
        validate_trade_intent,
    )

    from web.ob_authority_registry import (
        build_canonical_authority_registry,
    )

    validate_trade_intent(
        trade_intent
    )

    bound_intent = deepcopy(
        trade_intent
    )

    identity = _object(
        account_identity,
        label="account_identity",
    )

    profile = _object(
        owner_profile,
        label="owner_profile",
    )

    policy = _object(
        effective_policy,
        label="effective_policy",
    )

    fit = _object(
        owner_fit,
        label="owner_fit",
    )

    if identity.get("known") is not True:
        raise ValueError(
            "Decision Context requires an explicit known account identity."
        )

    account_key = _text(
        identity.get("account_key"),
        label="account identity account_key",
    )

    identity_fingerprint = _text(
        identity.get("identity_fingerprint"),
        label="account identity fingerprint",
    )

    profile_account_key = (
        _account_key_from_profile(
            profile
        )
    )

    if profile_account_key != account_key:
        raise ValueError(
            "Owner profile crosses Decision Context account boundary."
        )

    profile_id = _text(
        profile.get("profile_id"),
        label="owner profile_id",
    )

    profile_revision = profile.get(
        "revision"
    )

    if not isinstance(
        profile_revision,
        int,
    ):
        raise ValueError(
            "Owner profile revision is required."
        )

    profile_hash = _text(
        profile.get("profile_hash"),
        label="owner profile_hash",
    )

    policy_account_key = _text(
        policy.get("account_key"),
        label="effective policy account_key",
    )

    if policy_account_key != account_key:
        raise ValueError(
            "Effective Policy crosses Decision Context account boundary."
        )

    policy_id = _text(
        policy.get("policy_id"),
        label="effective policy_id",
    )

    policy_fingerprint = _text(
        policy.get("policy_fingerprint"),
        label="effective policy fingerprint",
    )

    fit_fingerprint = _text(
        fit.get("evaluation_fingerprint"),
        label="Owner Fit evaluation fingerprint",
    )

    fit_account_key = (
        _optional_owner_fit_account_key(
            fit
        )
    )

    if (
        fit_account_key is not None
        and
        fit_account_key != account_key
    ):
        raise ValueError(
            "Owner Fit crosses Decision Context account boundary."
        )

    candidate = _object(
        bound_intent.get("candidate"),
        label="Trade Intent candidate",
    )

    candidate_fingerprint = _text(
        candidate.get(
            "candidate_fingerprint"
        ),
        label="candidate fingerprint",
    )

    options_research = _object(
        bound_intent.get(
            "options_research"
        ),
        label="Trade Intent options research",
    )

    research_fingerprint = (
        options_research.get(
            "research_fingerprint"
        )
    )

    if (
        research_fingerprint is not None
        and
        not str(
            research_fingerprint
        ).strip()
    ):
        research_fingerprint = None

    intent_id = _text(
        bound_intent.get("intent_id"),
        label="Trade Intent ID",
    )

    intent_hash = _text(
        bound_intent.get("intent_hash"),
        label="Trade Intent hash",
    )

    lifecycle_state = _text(
        bound_intent.get(
            "lifecycle_state"
        ),
        label="Trade Intent lifecycle state",
    )

    mode_snapshot = _object(
        bound_intent.get(
            "mode_authority"
        ),
        label="Trade Intent mode authority",
    )

    if (
        mode_snapshot.get("status")
        !=
        "PENDING_OBMODE"
        or
        mode_snapshot.get("authority")
        !=
        PENDING_MODE_AUTHORITY
    ):
        raise ValueError(
            "OBCTX001–005 may only bind the explicit pending OBMODE placeholder."
        )

    for forbidden_mode_key in (
        "execution_authority",
        "broker_submission_authority",
        "capital_movement_authority",
    ):
        if (
            mode_snapshot.get(
                forbidden_mode_key
            )
            is not False
        ):
            raise ValueError(
                "Pending mode placeholder contains forbidden authority."
            )

    registry = (
        deepcopy(
            authority_registry
        )
        if authority_registry
        is not None
        else
        build_canonical_authority_registry()
    )

    registry_validation = registry.get(
        "validation"
    )

    if (
        not isinstance(
            registry_validation,
            dict,
        )
        or
        registry_validation.get(
            "valid"
        )
        is not True
    ):
        raise ValueError(
            "Decision Context requires a valid canonical authority registry."
        )

    registry_fingerprint = _text(
        registry.get(
            "registry_fingerprint"
        ),
        label="authority registry fingerprint",
    )

    context_record = (
        registry.get(
            "authority_records",
            {},
        ).get(
            "decision_context"
        )
    )

    if (
        not isinstance(
            context_record,
            dict,
        )
        or
        context_record.get(
            "authority_id"
        )
        !=
        AUTHORITY_ID
    ):
        raise ValueError(
            "OB_DECISION_CONTEXT_V1 is not the active canonical Decision Context authority."
        )

    if (
        "decision_context"
        in
        registry.get(
            "pending_authority_slots",
            {},
        )
    ):
        raise ValueError(
            "Decision Context cannot remain both active and pending."
        )

    event_snapshot = (
        deepcopy(
            causal_event
        )
        if isinstance(
            causal_event,
            dict,
        )
        else None
    )

    invalidation_snapshot = (
        deepcopy(
            invalidation_plan
        )
        if isinstance(
            invalidation_plan,
            dict,
        )
        else None
    )

    context = {
        "schema_version":
            SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "authority":
            AUTHORITY_ID,

        "account_key":
            account_key,

        "registry_reference": {
            "schema_version":
                registry.get(
                    "schema_version"
                ),

            "registry_fingerprint":
                registry_fingerprint,

            "decision_context_authority":
                AUTHORITY_ID,
        },

        "trade_intent_reference": {
            "authority":
                TRADE_INTENT_AUTHORITY,

            "intent_id":
                intent_id,

            "intent_hash":
                intent_hash,

            "lifecycle_state":
                lifecycle_state,
        },

        "candidate_snapshot": {
            "authority":
                "existing_canonical_engine_feed",

            "candidate_id":
                candidate.get(
                    "candidate_id"
                ),

            "candidate_fingerprint":
                candidate_fingerprint,

            "snapshot":
                candidate,
        },

        "options_research_snapshot": {
            "authority":
                (
                    options_research.get(
                        "authority"
                    )
                    or
                    "OB_OPTIONS_RESEARCH_V1"
                ),

            "status":
                options_research.get(
                    "status"
                ),

            "research_fingerprint":
                research_fingerprint,

            "snapshot":
                options_research,
        },

        "account_identity_snapshot": {
            "authority":
                ACCOUNT_IDENTITY_AUTHORITY,

            "account_key":
                account_key,

            "identity_fingerprint":
                identity_fingerprint,

            "snapshot":
                identity,
        },

        "owner_profile_snapshot": {
            "authority":
                OWNER_PROFILE_AUTHORITY,

            "profile_id":
                profile_id,

            "revision":
                profile_revision,

            "profile_hash":
                profile_hash,

            "snapshot":
                profile,
        },

        "effective_policy_snapshot": {
            "authority":
                EFFECTIVE_POLICY_AUTHORITY,

            "policy_id":
                policy_id,

            "policy_fingerprint":
                policy_fingerprint,

            "snapshot":
                policy,
        },

        "owner_fit_snapshot": {
            "authority":
                OWNER_FIT_AUTHORITY,

            "evaluation_fingerprint":
                fit_fingerprint,

            "snapshot":
                fit,
        },

        "causal_lineage": {
            "event_authority":
                EVENT_AUTHORITY,

            "causal_event":
                event_snapshot,

            "event_fingerprint":
                _lineage_fingerprint(
                    event_snapshot,
                    "event_fingerprint",
                ),

            "invalidation_plan":
                invalidation_snapshot,

            "invalidation_plan_fingerprint":
                _lineage_fingerprint(
                    invalidation_snapshot,
                    "invalidation_plan_fingerprint",
                    "plan_fingerprint",
                ),
        },

        "future_authorities": {
            "mode_authority": {
                "status":
                    "PENDING",

                "authority_id":
                    PENDING_MODE_AUTHORITY,

                "trade_intent_placeholder":
                    mode_snapshot,
            },

            "source_provenance": {
                "status":
                    "PENDING",

                "authority_id":
                    PENDING_PROVENANCE_AUTHORITY,

                "snapshot":
                    None,
            },

            "temporal_context": {
                "status":
                    "PENDING",

                "authority_id":
                    PENDING_TIME_AUTHORITY,

                "snapshot":
                    None,
            },
        },

        "boundaries":
            decision_context_contract(),
    }

    fingerprint = (
        recompute_context_fingerprint(
            context
        )
    )

    context[
        "context_id"
    ] = (
        "obctx_"
        + fingerprint[:28]
    )

    context[
        "context_fingerprint"
    ] = fingerprint

    validate_decision_context(
        context
    )

    return context


def validate_decision_context(
    context: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(
        context,
        dict,
    ):
        raise ValueError(
            "Decision Context must be an object."
        )

    if (
        context.get(
            "schema_version"
        )
        !=
        SCHEMA_VERSION
    ):
        raise ValueError(
            "Unknown Decision Context schema."
        )

    if (
        context.get(
            "authority"
        )
        !=
        AUTHORITY_ID
    ):
        raise ValueError(
            "Decision Context authority mismatch."
        )

    account_key = _text(
        context.get(
            "account_key"
        ),
        label="Decision Context account_key",
    )

    registry_ref = _object(
        context.get(
            "registry_reference"
        ),
        label="registry_reference",
    )

    _text(
        registry_ref.get(
            "registry_fingerprint"
        ),
        label="registry fingerprint",
    )

    if (
        registry_ref.get(
            "decision_context_authority"
        )
        !=
        AUTHORITY_ID
    ):
        raise ValueError(
            "Decision Context registry authority mismatch."
        )

    trade_intent_ref = _object(
        context.get(
            "trade_intent_reference"
        ),
        label="trade_intent_reference",
    )

    _text(
        trade_intent_ref.get(
            "intent_id"
        ),
        label="Trade Intent ID",
    )

    _text(
        trade_intent_ref.get(
            "intent_hash"
        ),
        label="Trade Intent hash",
    )

    candidate = _object(
        context.get(
            "candidate_snapshot"
        ),
        label="candidate_snapshot",
    )

    _text(
        candidate.get(
            "candidate_fingerprint"
        ),
        label="candidate fingerprint",
    )

    identity = _object(
        context.get(
            "account_identity_snapshot"
        ),
        label="account_identity_snapshot",
    )

    if (
        identity.get(
            "account_key"
        )
        !=
        account_key
    ):
        raise ValueError(
            "Decision Context identity/account mismatch."
        )

    profile = _object(
        context.get(
            "owner_profile_snapshot"
        ),
        label="owner_profile_snapshot",
    )

    _text(
        profile.get(
            "profile_id"
        ),
        label="owner profile ID",
    )

    _text(
        profile.get(
            "profile_hash"
        ),
        label="owner profile hash",
    )

    policy = _object(
        context.get(
            "effective_policy_snapshot"
        ),
        label="effective_policy_snapshot",
    )

    _text(
        policy.get(
            "policy_fingerprint"
        ),
        label="effective policy fingerprint",
    )

    fit = _object(
        context.get(
            "owner_fit_snapshot"
        ),
        label="owner_fit_snapshot",
    )

    _text(
        fit.get(
            "evaluation_fingerprint"
        ),
        label="Owner Fit evaluation fingerprint",
    )

    future = _object(
        context.get(
            "future_authorities"
        ),
        label="future_authorities",
    )

    expected_future = {
        "mode_authority":
            PENDING_MODE_AUTHORITY,

        "source_provenance":
            PENDING_PROVENANCE_AUTHORITY,

        "temporal_context":
            PENDING_TIME_AUTHORITY,
    }

    for key, authority_id in (
        expected_future.items()
    ):

        record = _object(
            future.get(key),
            label=f"future authority {key}",
        )

        if (
            record.get("status")
            !=
            "PENDING"
            or
            record.get(
                "authority_id"
            )
            !=
            authority_id
        ):
            raise ValueError(
                f"Future authority placeholder invalid: {key}"
            )

    boundaries = _object(
        context.get(
            "boundaries"
        ),
        label="Decision Context boundaries",
    )

    if (
        boundaries.get(
            "immutable_snapshot"
        )
        is not True
    ):
        raise ValueError(
            "Decision Context must be immutable/hash-bound."
        )

    for forbidden_key in (
        "source_authorities_mutated",
        "candidate_recalculated",
        "market_score_recalculated",
        "options_research_recalculated",
        "owner_profile_mutated",
        "effective_policy_recalculated",
        "owner_fit_recalculated",
        "event_history_mutated",
        "automatic_contract_selection",
        "execution_authority",
        "broker_submission",
        "capital_movement",
        "hybrid_execution",
        "automatic_execution",
    ):
        if (
            boundaries.get(
                forbidden_key
            )
            is not False
        ):
            raise ValueError(
                "Decision Context contains forbidden authority/effect: "
                + forbidden_key
            )

    if (
        boundaries.get(
            "live_auto_locked"
        )
        is not True
    ):
        raise ValueError(
            "Live Auto must remain locked."
        )

    expected_fingerprint = (
        recompute_context_fingerprint(
            context
        )
    )

    actual_fingerprint = _text(
        context.get(
            "context_fingerprint"
        ),
        label="Decision Context fingerprint",
    )

    if (
        expected_fingerprint
        !=
        actual_fingerprint
    ):
        raise ValueError(
            "Decision Context fingerprint mismatch."
        )

    expected_context_id = (
        "obctx_"
        + expected_fingerprint[:28]
    )

    if (
        context.get(
            "context_id"
        )
        !=
        expected_context_id
    ):
        raise ValueError(
            "Decision Context ID mismatch."
        )

    return {
        "ok":
            True,

        "schema_version":
            SCHEMA_VERSION,

        "context_id":
            expected_context_id,

        "account_key":
            account_key,

        "integrity_verified":
            True,

        "immutable_hash_bound_snapshot":
            True,
    }


def decision_context_reference(
    context: Dict[str, Any],
) -> Dict[str, Any]:

    validation = (
        validate_decision_context(
            context
        )
    )

    return {
        "authority":
            AUTHORITY_ID,

        "context_id":
            validation[
                "context_id"
            ],

        "context_fingerprint":
            context[
                "context_fingerprint"
            ],

        "account_key":
            validation[
                "account_key"
            ],

        "integrity_verified":
            True,
    }
