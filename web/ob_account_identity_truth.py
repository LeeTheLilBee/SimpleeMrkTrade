
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from typing import Any, Dict, Iterable
import json

from web.ob_owner_operating_profile import (
    ACCOUNT_REGISTRY,
)


SCHEMA_VERSION = "OB_ACCOUNT_IDENTITY_TRUTH_V1"
SERVICE_VERSION = "OBAUTH006_010_ACCOUNT_IDENTITY_TRUTH_TAXONOMY"

ACCOUNT_NAMESPACE_AUTHORITY = "OB_OWNER_OPERATING_PROFILE_V1"
ACCOUNT_RECONCILIATION_AUTHORITY = "OB_ENGINE_ACCOUNT_AUTHORITY_V1"
SIMULATED_ACCOUNT_AUTHORITY = "OB_PROOF_DEMO_ACCOUNT_V1"

NO_DEFAULT_ACCOUNT = True


TRUTH_STATES = {
    "CURRENT",
    "UNKNOWN",
    "CONFLICT",
    "STALE",
}


ORIGIN_CLASSES = {
    "REPOSITORY_STATE",
    "PROJECTED",
    "HISTORICAL",
    "OWNER_ENTERED",
    "SIMULATED",
    "UNKNOWN",
}


SOURCE_ROLE_TAXONOMY = {

    "account_operational_state": {
        "authority":
            "data/account_state.json",

        "origin_class":
            "REPOSITORY_STATE",

        "role":
            "DURABLE_REPOSITORY_OPERATIONAL_STATE",

        "may_overwrite_operational_state":
            True,

        "may_claim_live_broker_truth":
            False,
    },

    "account_snapshot_projection": {
        "authority":
            "data/account_snapshot.json",

        "origin_class":
            "PROJECTED",

        "role":
            "LIGHTWEIGHT_PROJECTION_ONLY",

        "may_overwrite_operational_state":
            False,

        "may_claim_live_broker_truth":
            False,
    },

    "performance_reporting": {
        "authority":
            "data/canonical_reporting_snapshot.json",

        "origin_class":
            "HISTORICAL",

        "role":
            "HISTORICAL_REPORTING_ONLY",

        "may_overwrite_operational_state":
            False,

        "may_claim_live_broker_truth":
            False,
    },

    "owner_operating_profile": {
        "authority":
            "OB_OWNER_OPERATING_PROFILE_V1",

        "origin_class":
            "OWNER_ENTERED",

        "role":
            "OWNER_CONFIRMED_POLICY_INPUT",

        "may_overwrite_operational_state":
            False,

        "may_claim_live_broker_truth":
            False,
    },

    "proof_demo_account": {
        "authority":
            "OB_PROOF_DEMO_ACCOUNT_V1",

        "origin_class":
            "SIMULATED",

        "role":
            "SIMULATED_ACCOUNT_STATE_ONLY",

        "may_overwrite_operational_state":
            False,

        "may_claim_live_broker_truth":
            False,
    },
}


_MISSING = object()


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


def account_namespace() -> Dict[str, Dict[str, Any]]:

    result = {}

    for key, record in ACCOUNT_REGISTRY.items():

        result[key] = {
            "key":
                key,

            "label":
                record["label"],

            "namespace_authority":
                ACCOUNT_NAMESPACE_AUTHORITY,

            "account_class":
                (
                    "SIMULATED_PROOF_DEMO"
                    if key == "proof_demo"
                    else "MISSION_ACCOUNT"
                ),

            "capital_truth_class":
                (
                    "SIMULATED_ONLY"
                    if key == "proof_demo"
                    else "UNKNOWN_UNTIL_CAPITAL_AUTHORITY"
                ),
        }

    return result


def account_identity_contract() -> Dict[str, Any]:

    namespace = account_namespace()

    return {
        "schema_version":
            SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "account_namespace_authority":
            ACCOUNT_NAMESPACE_AUTHORITY,

        "account_reconciliation_authority":
            ACCOUNT_RECONCILIATION_AUTHORITY,

        "simulated_account_authority":
            SIMULATED_ACCOUNT_AUTHORITY,

        "account_keys":
            list(
                namespace.keys()
            ),

        "implicit_default_account":
            False,

        "unknown_account_fallback":
            False,

        "truth_states":
            sorted(
                TRUTH_STATES
            ),

        "origin_classes":
            sorted(
                ORIGIN_CLASSES
            ),

        "source_roles":
            deepcopy(
                SOURCE_ROLE_TAXONOMY
            ),

        "unknown_stays_unknown":
            True,

        "conflict_stays_conflict":
            True,

        "stale_stays_stale":
            True,

        "simulated_stays_simulated":
            True,

        "owner_entered_stays_owner_entered":
            True,

        "projection_may_overwrite_operational_state":
            False,

        "historical_reporting_may_overwrite_operational_state":
            False,

        "repository_state_claims_live_broker_truth":
            False,

        "simulation_claims_live_broker_truth":
            False,

        "automatic_account_selection":
            False,

        "broker_submission":
            False,

        "capital_movement":
            False,

        "automatic_execution":
            False,
    }


def resolve_account_identity(
    account_key: Any,
) -> Dict[str, Any]:

    key = (
        ""
        if account_key is None
        else str(
            account_key
        ).strip()
    )

    namespace = account_namespace()

    if key not in namespace:

        result = {
            "schema_version":
                SCHEMA_VERSION,

            "known":
                False,

            "status":
                "UNKNOWN",

            "requested_account_key":
                key or None,

            "account_key":
                None,

            "label":
                None,

            "namespace_authority":
                ACCOUNT_NAMESPACE_AUTHORITY,

            "implicit_default_used":
                False,

            "reason":
                "unknown_or_missing_account_identity",
        }

        return {
            **result,

            "identity_fingerprint":
                stable_hash(
                    result
                ),
        }

    record = deepcopy(
        namespace[
            key
        ]
    )

    result = {
        "schema_version":
            SCHEMA_VERSION,

        "known":
            True,

        "status":
            "KNOWN",

        **record,

        "account_key":
            key,

        "implicit_default_used":
            False,
    }

    return {
        **result,

        "identity_fingerprint":
            stable_hash(
                result
            ),
    }


def classify_truth_claim(
    *,
    account_key: Any,
    source_role: Any,
    value: Any = _MISSING,
    stale: bool = False,
    conflict: bool = False,
) -> Dict[str, Any]:

    identity = resolve_account_identity(
        account_key
    )

    role_key = (
        ""
        if source_role is None
        else str(
            source_role
        ).strip()
    )

    role = SOURCE_ROLE_TAXONOMY.get(
        role_key
    )

    value_present = (
        value is not _MISSING
    )

    if not identity["known"]:

        truth_state = "UNKNOWN"
        origin_class = "UNKNOWN"
        exposed_value = None
        reason = "unknown_account_identity"

    elif role is None:

        truth_state = "UNKNOWN"
        origin_class = "UNKNOWN"
        exposed_value = None
        reason = "unknown_source_role"

    elif conflict:

        truth_state = "CONFLICT"
        origin_class = role["origin_class"]
        exposed_value = None
        reason = "explicit_conflict"

    elif not value_present:

        truth_state = "UNKNOWN"
        origin_class = role["origin_class"]
        exposed_value = None
        reason = "value_missing"

    elif stale:

        truth_state = "STALE"
        origin_class = role["origin_class"]
        exposed_value = value
        reason = "claim_stale"

    else:

        truth_state = "CURRENT"
        origin_class = role["origin_class"]
        exposed_value = value
        reason = "claim_current"

    claim = {
        "schema_version":
            SCHEMA_VERSION,

        "account_identity":
            identity,

        "account_key":
            (
                identity["account_key"]
                if identity["known"]
                else None
            ),

        "source_role":
            (
                role_key
                if role is not None
                else None
            ),

        "source_authority":
            (
                role["authority"]
                if role is not None
                else None
            ),

        "source_role_contract":
            (
                deepcopy(
                    role
                )
                if role is not None
                else None
            ),

        "truth_state":
            truth_state,

        "origin_class":
            origin_class,

        "value_present":
            value_present,

        "value":
            exposed_value,

        "reason":
            reason,

        "may_claim_live_broker_truth":
            False,

        "broker_submission":
            False,

        "capital_movement":
            False,
    }

    return {
        **claim,

        "claim_fingerprint":
            stable_hash(
                claim
            ),
    }


def reconcile_truth_claims(
    claims: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:

    normalized = [
        deepcopy(
            claim
        )
        for claim in claims
        if isinstance(
            claim,
            dict,
        )
    ]

    if not normalized:

        result = {
            "schema_version":
                SCHEMA_VERSION,

            "truth_state":
                "UNKNOWN",

            "account_key":
                None,

            "resolved_value":
                None,

            "origin_classes":
                [],

            "source_roles":
                [],

            "claim_count":
                0,

            "reason":
                "no_claims",

            "silent_merge":
                False,
        }

        return {
            **result,

            "resolution_fingerprint":
                stable_hash(
                    result
                ),
        }

    account_keys = {
        claim.get(
            "account_key"
        )
        for claim in normalized
        if claim.get(
            "account_key"
        )
        is not None
    }

    origin_classes = sorted({
        str(
            claim.get(
                "origin_class"
            )
        )
        for claim in normalized
        if claim.get(
            "origin_class"
        )
    })

    source_roles = sorted({
        str(
            claim.get(
                "source_role"
            )
        )
        for claim in normalized
        if claim.get(
            "source_role"
        )
    })

    states = [
        claim.get(
            "truth_state"
        )
        for claim in normalized
    ]

    known_value_claims = [
        claim
        for claim in normalized
        if claim.get(
            "truth_state"
        )
        in {
            "CURRENT",
            "STALE",
        }
        and
        claim.get(
            "value_present"
        )
        is True
    ]

    distinct_values = {
        stable_hash(
            claim.get(
                "value"
            )
        )
        for claim in known_value_claims
    }

    if len(
        account_keys
    ) > 1:

        truth_state = "CONFLICT"
        resolved_value = None
        reason = "account_identity_conflict"

    elif (
        "CONFLICT"
        in states
    ):

        truth_state = "CONFLICT"
        resolved_value = None
        reason = "claim_conflict_preserved"

    elif len(
        distinct_values
    ) > 1:

        truth_state = "CONFLICT"
        resolved_value = None
        reason = "cross_source_value_conflict"

    elif (
        "UNKNOWN"
        in states
    ):

        truth_state = "UNKNOWN"
        resolved_value = None
        reason = "unknown_claim_preserved"

    elif (
        "STALE"
        in states
    ):

        truth_state = "STALE"
        resolved_value = (
            known_value_claims[0]["value"]
            if known_value_claims
            else None
        )
        reason = "stale_claim_preserved"

    elif known_value_claims:

        truth_state = "CURRENT"
        resolved_value = (
            known_value_claims[0]["value"]
        )
        reason = "claims_agree"

    else:

        truth_state = "UNKNOWN"
        resolved_value = None
        reason = "no_resolvable_value"

    result = {
        "schema_version":
            SCHEMA_VERSION,

        "truth_state":
            truth_state,

        "account_key":
            (
                next(
                    iter(
                        account_keys
                    )
                )
                if len(
                    account_keys
                )
                == 1
                else None
            ),

        "resolved_value":
            resolved_value,

        "origin_classes":
            origin_classes,

        "source_roles":
            source_roles,

        "claim_count":
            len(
                normalized
            ),

        "reason":
            reason,

        "silent_merge":
            False,

        "live_broker_truth_claimed":
            False,

        "broker_submission":
            False,

        "capital_movement":
            False,
    }

    return {
        **result,

        "resolution_fingerprint":
            stable_hash(
                result
            ),
    }
