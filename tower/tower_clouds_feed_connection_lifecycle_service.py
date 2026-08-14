"""
GP067 — Connection lifecycle /
freshness + disconnect + revoke.

Connection verification is separate from payload certification.
"""

from __future__ import annotations

from datetime import datetime, timezone

try:

    from .tower_clouds_feed_connection_lifecycle import (
        FeedConnectionReceipt,
        FeedConnectionState,
    )

    from .tower_clouds_feed_source_trust_service import (
        get_clouds_feed_source_trust_registry,
    )

    from .tower_clouds_signed_summary_transport_service import (
        CERTIFICATION_SECRET,
        build_gp066_certification_envelope,
        validate_signed_summary_transport,
    )

except ImportError:

    from tower_clouds_feed_connection_lifecycle import (
        FeedConnectionReceipt,
        FeedConnectionState,
    )

    from tower_clouds_feed_source_trust_service import (
        get_clouds_feed_source_trust_registry,
    )

    from tower_clouds_signed_summary_transport_service import (
        CERTIFICATION_SECRET,
        build_gp066_certification_envelope,
        validate_signed_summary_transport,
    )


DEFAULT_FRESHNESS_SECONDS = (
    300
)


def _parse_iso(
    value,
):

    try:

        if (
            value.endswith(
                "Z"
            )
        ):

            value = (
                value[:-1]
                + "+00:00"
            )


        parsed = (
            datetime.fromisoformat(
                value
            )
        )


        if (
            parsed.tzinfo
            is None
        ):

            parsed = (
                parsed.replace(
                    tzinfo=timezone.utc
                )
            )


        return parsed


    except (
        AttributeError,
        TypeError,
        ValueError,
    ):

        return None


def _fresh(
    sent_at,
    now_iso,
    freshness_seconds,
):

    sent = (
        _parse_iso(
            sent_at
        )
    )

    now = (
        _parse_iso(
            now_iso
        )
    )


    if (
        sent is None
        or now is None
    ):

        return False


    age = (
        now
        - sent
    ).total_seconds()


    return (
        age >= 0
        and age
        <= freshness_seconds
    )


def evaluate_feed_connection(
    source_id,
    *,
    envelope=None,
    validation=None,
    external_transport_connected=False,
    external_endpoint_verified=False,
    revoked=False,
    now_iso,
    freshness_seconds=(
        DEFAULT_FRESHNESS_SECONDS
    ),
):

    reasons = []


    if revoked:

        state = (
            FeedConnectionState
            .REVOKED.value
        )

        reasons.append(
            "connection_revoked"
        )

        fresh = False

        authenticated = False

        replay_rejected = False

        certification_fixture = (
            bool(
                envelope
                and envelope
                .certification_fixture_only
            )
        )

        live_claim = False


    elif not external_transport_connected:

        state = (
            FeedConnectionState
            .DISCONNECTED.value
        )

        reasons.append(
            "external_transport_not_connected"
        )

        fresh = False

        authenticated = False

        replay_rejected = False

        certification_fixture = (
            bool(
                envelope
                and envelope
                .certification_fixture_only
            )
        )

        live_claim = False


    elif not external_endpoint_verified:

        state = (
            FeedConnectionState
            .CONNECTED_UNVERIFIED.value
        )

        reasons.append(
            "external_endpoint_not_verified"
        )

        fresh = False

        authenticated = False

        replay_rejected = False

        certification_fixture = (
            bool(
                envelope
                and envelope
                .certification_fixture_only
            )
        )

        live_claim = False


    else:

        certification_fixture = (
            bool(
                envelope
                and envelope
                .certification_fixture_only
            )
        )


        authenticated = (
            validation is not None

            and validation
            .accepted_for_connection_evaluation
            is True

            and validation
            .signature_verified
            is True
        )


        replay_rejected = (
            validation is not None

            and validation
            .replay_rejected
            is True
        )


        fresh = (
            envelope is not None

            and _fresh(
                envelope.sent_at,
                now_iso,
                freshness_seconds,
            )
        )


        live_claim = (
            envelope is not None

            and envelope.payload.get(
                "mode"
            )
            == "live"

            and envelope.payload.get(
                "source_claims_live"
            )
            is True
        )


        if (
            not authenticated
            or replay_rejected
            or not fresh
        ):

            state = (
                FeedConnectionState
                .DEGRADED.value
            )


            if not authenticated:

                reasons.append(
                    "message_authentication_failed"
                )


            if replay_rejected:

                reasons.append(
                    "replay_rejected"
                )


            if not fresh:

                reasons.append(
                    "message_stale_or_timestamp_invalid"
                )


        elif certification_fixture:

            state = (
                FeedConnectionState
                .CERTIFICATION_VERIFIED.value
            )

            reasons.append(
                "certification_fixture_not_real_connection"
            )


        else:

            state = (
                FeedConnectionState
                .EXTERNAL_VERIFIED.value
            )


    counts_as_real_live = (
        state
        == FeedConnectionState
        .EXTERNAL_VERIFIED.value

        and external_transport_connected

        and external_endpoint_verified

        and authenticated

        and fresh

        and not replay_rejected

        and not certification_fixture

        and live_claim

        and not revoked
    )


    current_available = (
        counts_as_real_live
    )


    safe_current = (
        counts_as_real_live
    )


    attention_required = (
        state
        in {
            FeedConnectionState
            .CONNECTED_UNVERIFIED.value,

            FeedConnectionState
            .DEGRADED.value,

            FeedConnectionState
            .REVOKED.value,
        }
    )


    return FeedConnectionReceipt(

        source_id=(
            source_id
        ),

        connection_state=(
            state
        ),

        external_transport_connected=(
            external_transport_connected
        ),

        external_endpoint_verified=(
            external_endpoint_verified
        ),

        authenticated_message=(
            authenticated
        ),

        fresh_message=(
            fresh
        ),

        replay_rejected=(
            replay_rejected
        ),

        revoked=(
            revoked
        ),

        certification_fixture_only=(
            certification_fixture
        ),

        live_payload_claim=(
            live_claim
        ),

        counts_as_real_live_connection=(
            counts_as_real_live
        ),

        owner_current_state_available=(
            current_available
        ),

        safe_to_interpret_as_current=(
            safe_current
        ),

        connection_attention_required=(
            attention_required
        ),

        reason_codes=tuple(
            reasons
        ),

        capital_movement_performed=False,

        downstream_execution_performed=False,
    )


def get_default_disconnected_connection_receipts():

    registry = (
        get_clouds_feed_source_trust_registry()
    )


    return tuple(

        evaluate_feed_connection(

            item.source_id,

            external_transport_connected=False,

            external_endpoint_verified=False,

            now_iso=(
                "2026-08-14T22:01:00Z"
            ),
        )

        for item
        in registry.sources
    )


def get_gp067_certification_scenarios():

    envelope = (
        build_gp066_certification_envelope()
    )


    valid = (
        validate_signed_summary_transport(

            envelope,

            secret=(
                CERTIFICATION_SECRET
            ),
        )
    )


    certification_verified = (
        evaluate_feed_connection(

            "tower",

            envelope=envelope,

            validation=valid,

            external_transport_connected=True,

            external_endpoint_verified=True,

            now_iso=(
                "2026-08-14T22:01:00Z"
            ),
        )
    )


    connected_unverified = (
        evaluate_feed_connection(

            "tower",

            envelope=envelope,

            validation=valid,

            external_transport_connected=True,

            external_endpoint_verified=False,

            now_iso=(
                "2026-08-14T22:01:00Z"
            ),
        )
    )


    replay_validation = (
        validate_signed_summary_transport(

            envelope,

            secret=(
                CERTIFICATION_SECRET
            ),

            seen_message_ids=(
                envelope.message_id,
            ),
        )
    )


    replay_degraded = (
        evaluate_feed_connection(

            "tower",

            envelope=envelope,

            validation=(
                replay_validation
            ),

            external_transport_connected=True,

            external_endpoint_verified=True,

            now_iso=(
                "2026-08-14T22:01:00Z"
            ),
        )
    )


    stale_degraded = (
        evaluate_feed_connection(

            "tower",

            envelope=envelope,

            validation=valid,

            external_transport_connected=True,

            external_endpoint_verified=True,

            now_iso=(
                "2026-08-14T23:00:00Z"
            ),
        )
    )


    revoked = (
        evaluate_feed_connection(

            "tower",

            envelope=envelope,

            validation=valid,

            external_transport_connected=True,

            external_endpoint_verified=True,

            revoked=True,

            now_iso=(
                "2026-08-14T22:01:00Z"
            ),
        )
    )


    return {

        "certification_verified":
        certification_verified,

        "connected_unverified":
        connected_unverified,

        "replay_degraded":
        replay_degraded,

        "stale_degraded":
        stale_degraded,

        "revoked":
        revoked,
    }


def get_clouds_gp067_status_payload():

    disconnected = (
        get_default_disconnected_connection_receipts()
    )


    scenarios = (
        get_gp067_certification_scenarios()
    )


    certification = (
        scenarios[
            "certification_verified"
        ]
    )


    unverified = (
        scenarios[
            "connected_unverified"
        ]
    )


    replay = (
        scenarios[
            "replay_degraded"
        ]
    )


    stale = (
        scenarios[
            "stale_degraded"
        ]
    )


    revoked = (
        scenarios[
            "revoked"
        ]
    )


    real_live_count = sum(
        item
        .counts_as_real_live_connection
        is True

        for item
        in disconnected
    )


    safe = (
        len(
            disconnected
        )
        == 6

        and all(
            item.connection_state
            == FeedConnectionState
            .DISCONNECTED.value

            for item
            in disconnected
        )

        and real_live_count
        == 0

        and certification
        .connection_state
        == FeedConnectionState
        .CERTIFICATION_VERIFIED.value

        and certification
        .authenticated_message
        is True

        and certification
        .fresh_message
        is True

        and certification
        .certification_fixture_only
        is True

        and certification
        .counts_as_real_live_connection
        is False

        and certification
        .owner_current_state_available
        is False

        and unverified
        .connection_state
        == FeedConnectionState
        .CONNECTED_UNVERIFIED.value

        and unverified
        .counts_as_real_live_connection
        is False

        and replay
        .connection_state
        == FeedConnectionState
        .DEGRADED.value

        and replay
        .replay_rejected
        is True

        and replay
        .counts_as_real_live_connection
        is False

        and stale
        .connection_state
        == FeedConnectionState
        .DEGRADED.value

        and stale
        .fresh_message
        is False

        and stale
        .counts_as_real_live_connection
        is False

        and revoked
        .connection_state
        == FeedConnectionState
        .REVOKED.value

        and revoked.revoked
        is True

        and revoked
        .counts_as_real_live_connection
        is False

        and all(
            item
            .downstream_execution_performed
            is False

            for item
            in disconnected
        )
    )


    return {

        "pack":
        "GP067",

        "section":
        (
            "CONNECTION LIFECYCLE / "
            "FRESHNESS + DISCONNECT + REVOKE"
        ),

        "status":
        (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue":
        safe,

        "canonical_connection_slot_count":
        6,

        "default_disconnected_count":
        6,

        "connected_unverified_state_ready":
        True,

        "certification_verified_state_ready":
        True,

        "external_verified_state_contract_ready":
        True,

        "degraded_state_ready":
        True,

        "revoked_state_ready":
        True,

        "freshness_gate_ready":
        True,

        "replay_degradation_ready":
        True,

        "disconnect_fail_closed":
        True,

        "certification_fixture_counts_as_live":
        False,

        "real_live_connection_count":
        0,

        "real_live_feeds_connected":
        False,

        "owner_current_state_from_fixture":
        False,

        "external_transport_attempted":
        False,

        "capital_movement_performed":
        False,

        "downstream_execution_performed":
        False,

        "next_pack":
        (
            "GP068 — REAL FEED CONNECTION "
            "FOUNDATION CLOSEOUT"
        ),
    }
