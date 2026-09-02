"""
Tower hosted candidate release decision packet / TWR091–TWR095.

This layer consumes the fail-closed hosted candidate parity result from
TWR086–TWR090 and converts it into one immutable-style owner-review packet.

It does NOT deploy.
It does NOT promote.
It does NOT mutate STAGING_READY.
It does NOT authorize broker or capital actions.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Mapping


RELEASE_PACKET_SCHEMA = (
    "tower.hosted-candidate-release-packet.v1"
)

READY_FOR_OWNER_REVIEW = (
    "READY_FOR_OWNER_REVIEW"
)

HOLD = (
    "HOLD"
)


def _utc_now() -> str:
    return (
        datetime.now(
            timezone.utc
        )
        .isoformat()
        .replace(
            "+00:00",
            "Z",
        )
    )


def _canonical_json(
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


def _sha256(
    value: Any,
) -> str:

    return hashlib.sha256(
        _canonical_json(
            value
        ).encode(
            "utf-8"
        )
    ).hexdigest()


def _clean_revision(
    value: Any,
) -> str:

    return str(
        value
        or ""
    ).strip().lower()


def validate_parity_result(
    parity_result: Mapping[
        str,
        Any,
    ],
) -> dict[str, Any]:

    errors: list[str] = []

    if not isinstance(
        parity_result,
        Mapping,
    ):

        return {
            "valid": False,
            "errors": [
                "parity_result_not_mapping",
            ],
        }


    expected_revision = (
        _clean_revision(
            parity_result.get(
                "expected_revision"
            )
        )
    )

    actual_revision = (
        _clean_revision(
            parity_result.get(
                "actual_revision"
            )
        )
    )

    if not expected_revision:
        errors.append(
            "expected_revision_missing"
        )

    if not actual_revision:
        errors.append(
            "actual_revision_missing"
        )


    checks = (
        parity_result.get(
            "checks",
            {}
        )
    )

    if not isinstance(
        checks,
        Mapping,
    ):

        errors.append(
            "checks_not_mapping"
        )

        checks = {}


    failures = (
        parity_result.get(
            "failures",
            []
        )
    )

    if not isinstance(
        failures,
        list,
    ):

        errors.append(
            "failures_not_list"
        )

        failures = []


    parity_pass = (
        parity_result.get(
            "parity_pass"
        )
        is True
    )


    if (
        parity_pass
        and failures
    ):

        errors.append(
            "pass_contains_failures"
        )


    if (
        parity_pass
        and not checks
    ):

        errors.append(
            "pass_missing_checks"
        )


    if (
        parity_pass
        and not all(
            value is True
            for value
            in checks.values()
        )
    ):

        errors.append(
            "pass_contains_failed_check"
        )


    if (
        parity_pass
        and expected_revision
        != actual_revision
    ):

        errors.append(
            "pass_revision_mismatch"
        )


    # TWR086–090 itself must remain non-authorizing.
    for field in (
        "deployment_authorized",
        "production_promotion_authorized",
        "broker_submission_authorized",
        "capital_movement_authorized",
        "manual_live_authorized",
        "live_auto_authorized",
        "staging_ready_changed",
    ):

        if (
            parity_result.get(
                field
            )
            is not False
        ):

            errors.append(
                f"parity_safety_boundary_open:{field}"
            )


    return {
        "valid": (
            len(
                errors
            )
            == 0
        ),

        "errors": errors,

        "expected_revision": (
            expected_revision
        ),

        "actual_revision": (
            actual_revision
        ),

        "parity_pass": (
            parity_pass
        ),

        "checks": dict(
            checks
        ),

        "failures": list(
            failures
        ),
    }


def release_recommendation(
    parity_result: Mapping[
        str,
        Any,
    ],
) -> dict[str, Any]:

    validation = (
        validate_parity_result(
            parity_result
        )
    )


    ready = (
        validation[
            "valid"
        ]
        and validation[
            "parity_pass"
        ]
    )


    return {
        "status": (
            "tower_hosted_candidate_ready_for_owner_review"
            if ready
            else "tower_hosted_candidate_hold"
        ),

        "recommendation": (
            READY_FOR_OWNER_REVIEW
            if ready
            else HOLD
        ),

        "owner_review_required": True,

        "parity_valid": (
            validation[
                "valid"
            ]
        ),

        "parity_pass": (
            validation[
                "parity_pass"
            ]
        ),

        "validation_errors": (
            validation[
                "errors"
            ]
        ),

        "parity_failures": (
            validation[
                "failures"
            ]
        ),

        "deployment_authorized": False,

        "promotion_authorized": False,

        "production_promotion_authorized": False,

        "staging_ready_changed": False,

        "broker_submission_authorized": False,

        "capital_movement_authorized": False,

        "manual_live_authorized": False,

        "live_auto_authorized": False,
    }


def build_hosted_candidate_release_packet(
    parity_result: Mapping[
        str,
        Any,
    ],
    *,
    created_at_utc: str | None = None,
) -> dict[str, Any]:

    validation = (
        validate_parity_result(
            parity_result
        )
    )

    recommendation = (
        release_recommendation(
            parity_result
        )
    )


    packet = {
        "schema_version": (
            RELEASE_PACKET_SCHEMA
        ),

        "packet_type": (
            "TOWER_HOSTED_CANDIDATE_RELEASE_DECISION"
        ),

        "created_at_utc": (
            created_at_utc
            or _utc_now()
        ),

        "expected_revision": (
            validation[
                "expected_revision"
            ]
        ),

        "actual_revision": (
            validation[
                "actual_revision"
            ]
        ),

        "entrypoint": str(
            parity_result.get(
                "entrypoint",
                "",
            )
            or ""
        ).strip(),

        "critical_route_count": int(
            parity_result.get(
                "critical_route_count",
                0,
            )
            or 0
        ),

        "parity_status": (
            parity_result.get(
                "status"
            )
        ),

        "parity_pass": (
            validation[
                "parity_pass"
            ]
        ),

        "parity_valid": (
            validation[
                "valid"
            ]
        ),

        "checks": deepcopy(
            validation[
                "checks"
            ]
        ),

        "failures": deepcopy(
            validation[
                "failures"
            ]
        ),

        "validation_errors": deepcopy(
            validation[
                "errors"
            ]
        ),

        "release_recommendation": (
            recommendation[
                "recommendation"
            ]
        ),

        "owner_review_required": True,

        "owner_decision_recorded": False,

        "deployment_authorized": False,

        "promotion_authorized": False,

        "production_promotion_authorized": False,

        "staging_ready_changed": False,

        "broker_submission_authorized": False,

        "capital_movement_authorized": False,

        "manual_live_authorized": False,

        "live_auto_authorized": False,
    }


    packet[
        "packet_integrity_hash"
    ] = _sha256(
        packet
    )


    return {
        "status": (
            "tower_hosted_candidate_release_packet_ready"
        ),

        "packet": packet,

        "release_recommendation": (
            packet[
                "release_recommendation"
            ]
        ),

        "owner_review_required": True,

        "deployment_authorized": False,

        "promotion_authorized": False,

        "staging_ready_changed": False,
    }


def verify_hosted_candidate_release_packet(
    packet: Mapping[
        str,
        Any,
    ],
) -> dict[str, Any]:

    if not isinstance(
        packet,
        Mapping,
    ):

        return {
            "status": (
                "tower_hosted_candidate_release_packet_invalid"
            ),

            "valid": False,

            "integrity_valid": False,

            "errors": [
                "packet_not_mapping",
            ],
        }


    working = dict(
        packet
    )

    supplied_hash = (
        working.pop(
            "packet_integrity_hash",
            None,
        )
    )

    computed_hash = (
        _sha256(
            working
        )
    )


    errors: list[str] = []


    if (
        packet.get(
            "schema_version"
        )
        != RELEASE_PACKET_SCHEMA
    ):

        errors.append(
            "schema_version_mismatch"
        )


    if (
        packet.get(
            "packet_type"
        )
        != "TOWER_HOSTED_CANDIDATE_RELEASE_DECISION"
    ):

        errors.append(
            "packet_type_mismatch"
        )


    if (
        not supplied_hash
        or supplied_hash
        != computed_hash
    ):

        errors.append(
            "packet_integrity_hash_mismatch"
        )


    for field in (
        "deployment_authorized",
        "promotion_authorized",
        "production_promotion_authorized",
        "staging_ready_changed",
        "broker_submission_authorized",
        "capital_movement_authorized",
        "manual_live_authorized",
        "live_auto_authorized",
    ):

        if (
            packet.get(
                field
            )
            is not False
        ):

            errors.append(
                f"release_safety_boundary_open:{field}"
            )


    if (
        packet.get(
            "owner_review_required"
        )
        is not True
    ):

        errors.append(
            "owner_review_not_required"
        )


    valid = (
        not errors
    )


    return {
        "status": (
            "tower_hosted_candidate_release_packet_valid"
            if valid
            else "tower_hosted_candidate_release_packet_invalid"
        ),

        "valid": valid,

        "integrity_valid": (
            supplied_hash
            == computed_hash
            and bool(
                supplied_hash
            )
        ),

        "supplied_hash": (
            supplied_hash
        ),

        "computed_hash": (
            computed_hash
        ),

        "errors": errors,
    }
