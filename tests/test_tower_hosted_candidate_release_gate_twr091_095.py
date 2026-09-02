from copy import deepcopy

from tower.hosted_candidate_release_gate import (
    HOLD,
    READY_FOR_OWNER_REVIEW,
    build_hosted_candidate_release_packet,
    release_recommendation,
    validate_parity_result,
    verify_hosted_candidate_release_packet,
)


def passing_parity():

    return {
        "status": (
            "tower_hosted_candidate_parity_pass"
        ),

        "parity_pass": True,

        "expected_revision": (
            "abc123"
        ),

        "actual_revision": (
            "abc123"
        ),

        "entrypoint": (
            "web.managed_staging:app"
        ),

        "critical_route_count": 11,

        "checks": {
            "expected_revision_valid": True,
            "health_http_200": True,
            "manifest_http_200": True,
            "exact_candidate_revision_match": True,
            "all_critical_routes_present": True,
        },

        "failures": [],

        "deployment_authorized": False,

        "production_promotion_authorized": False,

        "broker_submission_authorized": False,

        "capital_movement_authorized": False,

        "manual_live_authorized": False,

        "live_auto_authorized": False,

        "staging_ready_changed": False,
    }


def failing_parity():

    value = passing_parity()

    value[
        "status"
    ] = (
        "tower_hosted_candidate_parity_fail"
    )

    value[
        "parity_pass"
    ] = False

    value[
        "actual_revision"
    ] = "wrong456"

    value[
        "checks"
    ][
        "exact_candidate_revision_match"
    ] = False

    value[
        "failures"
    ] = [
        (
            "Hosted runtime revision does not "
            "equal the exact expected candidate revision."
        )
    ]

    return value


def test_valid_passing_parity():

    result = (
        validate_parity_result(
            passing_parity()
        )
    )

    assert (
        result[
            "valid"
        ]
        is True
    )

    assert (
        result[
            "parity_pass"
        ]
        is True
    )


def test_passing_parity_recommends_owner_review():

    result = (
        release_recommendation(
            passing_parity()
        )
    )

    assert (
        result[
            "recommendation"
        ]
        == READY_FOR_OWNER_REVIEW
    )

    assert (
        result[
            "owner_review_required"
        ]
        is True
    )


def test_failed_parity_is_hold():

    result = (
        release_recommendation(
            failing_parity()
        )
    )

    assert (
        result[
            "recommendation"
        ]
        == HOLD
    )


def test_release_packet_carries_exact_candidate():

    result = (
        build_hosted_candidate_release_packet(
            passing_parity(),
            created_at_utc=(
                "2026-08-24T14:00:00Z"
            ),
        )
    )

    packet = (
        result[
            "packet"
        ]
    )

    assert (
        packet[
            "expected_revision"
        ]
        == "abc123"
    )

    assert (
        packet[
            "actual_revision"
        ]
        == "abc123"
    )

    assert (
        packet[
            "release_recommendation"
        ]
        == READY_FOR_OWNER_REVIEW
    )


def test_release_packet_never_authorizes_deploy():

    packet = (
        build_hosted_candidate_release_packet(
            passing_parity()
        )[
            "packet"
        ]
    )

    assert (
        packet[
            "deployment_authorized"
        ]
        is False
    )

    assert (
        packet[
            "promotion_authorized"
        ]
        is False
    )

    assert (
        packet[
            "production_promotion_authorized"
        ]
        is False
    )

    assert (
        packet[
            "staging_ready_changed"
        ]
        is False
    )


def test_release_packet_keeps_live_boundaries_closed():

    packet = (
        build_hosted_candidate_release_packet(
            passing_parity()
        )[
            "packet"
        ]
    )

    assert (
        packet[
            "broker_submission_authorized"
        ]
        is False
    )

    assert (
        packet[
            "capital_movement_authorized"
        ]
        is False
    )

    assert (
        packet[
            "manual_live_authorized"
        ]
        is False
    )

    assert (
        packet[
            "live_auto_authorized"
        ]
        is False
    )


def test_packet_integrity_passes():

    packet = (
        build_hosted_candidate_release_packet(
            passing_parity()
        )[
            "packet"
        ]
    )

    verified = (
        verify_hosted_candidate_release_packet(
            packet
        )
    )

    assert (
        verified[
            "valid"
        ]
        is True
    )

    assert (
        verified[
            "integrity_valid"
        ]
        is True
    )


def test_packet_integrity_detects_mutation():

    packet = (
        build_hosted_candidate_release_packet(
            passing_parity()
        )[
            "packet"
        ]
    )

    tampered = deepcopy(
        packet
    )

    tampered[
        "actual_revision"
    ] = "tampered"

    verified = (
        verify_hosted_candidate_release_packet(
            tampered
        )
    )

    assert (
        verified[
            "valid"
        ]
        is False
    )

    assert (
        "packet_integrity_hash_mismatch"
        in verified[
            "errors"
        ]
    )


def test_open_parity_safety_boundary_invalidates_input():

    parity = (
        passing_parity()
    )

    parity[
        "deployment_authorized"
    ] = True

    validated = (
        validate_parity_result(
            parity
        )
    )

    assert (
        validated[
            "valid"
        ]
        is False
    )

    assert any(
        "parity_safety_boundary_open"
        in error

        for error
        in validated[
            "errors"
        ]
    )


def test_malformed_pass_with_failure_is_invalid():

    parity = (
        passing_parity()
    )

    parity[
        "failures"
    ] = [
        "unexpected failure"
    ]

    result = (
        validate_parity_result(
            parity
        )
    )

    assert (
        result[
            "valid"
        ]
        is False
    )


def test_hold_packet_is_still_validly_sealed():

    result = (
        build_hosted_candidate_release_packet(
            failing_parity()
        )
    )

    packet = (
        result[
            "packet"
        ]
    )

    assert (
        packet[
            "release_recommendation"
        ]
        == HOLD
    )

    verified = (
        verify_hosted_candidate_release_packet(
            packet
        )
    )

    assert (
        verified[
            "valid"
        ]
        is True
    )
