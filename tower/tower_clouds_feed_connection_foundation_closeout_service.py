"""
GP068 — Real feed connection foundation closeout.

The foundation is ready.

Actual source connection starts in GP069.
"""

from __future__ import annotations

try:

    from .tower_clouds_feed_connection_foundation_closeout import (
        TowerCloudsFeedConnectionFoundationCloseout,
    )

    from .tower_clouds_feed_source_trust_service import (
        get_clouds_gp065_status_payload,
    )

    from .tower_clouds_signed_summary_transport_service import (
        get_clouds_gp066_status_payload,
    )

    from .tower_clouds_feed_connection_lifecycle_service import (
        get_clouds_gp067_status_payload,
    )

except ImportError:

    from tower_clouds_feed_connection_foundation_closeout import (
        TowerCloudsFeedConnectionFoundationCloseout,
    )

    from tower_clouds_feed_source_trust_service import (
        get_clouds_gp065_status_payload,
    )

    from tower_clouds_signed_summary_transport_service import (
        get_clouds_gp066_status_payload,
    )

    from tower_clouds_feed_connection_lifecycle_service import (
        get_clouds_gp067_status_payload,
    )


CONCLUSION = (
    "TOWER_CLOUDS_REAL_FEED_CONNECTION_FOUNDATION_"
    "READY_FOR_SOURCE_WAVE_1"
)


SOURCE_WAVE_1 = (

    "tower",

    "observatory",

    "archive_vault",
)


def build_feed_connection_foundation_closeout():

    gp065 = (
        get_clouds_gp065_status_payload()
    )

    gp066 = (
        get_clouds_gp066_status_payload()
    )

    gp067 = (
        get_clouds_gp067_status_payload()
    )


    ready = (
        gp065["status"]
        == "ready"

        and gp065[
            "safe_to_continue"
        ]
        is True

        and gp066["status"]
        == "ready"

        and gp066[
            "safe_to_continue"
        ]
        is True

        and gp067["status"]
        == "ready"

        and gp067[
            "safe_to_continue"
        ]
        is True
    )


    return TowerCloudsFeedConnectionFoundationCloseout(

        checkpoint_id=(
            "tower-clouds-feed-foundation-gp068"
        ),

        source_trust_registry_ready=(
            gp065["status"]
            == "ready"
        ),

        six_source_identity_ready=(
            gp065[
                "canonical_source_count"
            ]
            == 6
        ),

        secret_reference_boundary_ready=(
            gp065[
                "secret_material_count"
            ]
            == 0
        ),

        signed_transport_ready=(
            gp066["status"]
            == "ready"
        ),

        body_integrity_ready=(
            gp066[
                "body_integrity_verified"
            ]
        ),

        signature_verification_ready=(
            gp066[
                "signature_verified"
            ]
        ),

        replay_rejection_ready=(
            gp066[
                "message_id_replay_rejection_ready"
            ]

            and gp066[
                "nonce_replay_rejection_ready"
            ]
        ),

        freshness_gate_ready=(
            gp067[
                "freshness_gate_ready"
            ]
        ),

        disconnected_state_ready=(
            gp067[
                "disconnect_fail_closed"
            ]
        ),

        connected_unverified_state_ready=(
            gp067[
                "connected_unverified_state_ready"
            ]
        ),

        certification_verified_state_ready=(
            gp067[
                "certification_verified_state_ready"
            ]
        ),

        external_verified_state_contract_ready=(
            gp067[
                "external_verified_state_contract_ready"
            ]
        ),

        degraded_state_ready=(
            gp067[
                "degraded_state_ready"
            ]
        ),

        revoked_state_ready=(
            gp067[
                "revoked_state_ready"
            ]
        ),

        certification_fixture_live_claim_blocked=(
            gp067[
                "certification_fixture_counts_as_live"
            ]
            is False
        ),

        ready_for_source_connection_wave_1=(
            ready
        ),

        wave_1_source_ids=(
            SOURCE_WAVE_1
        ),

        real_live_connection_count=0,

        real_live_feeds_connected=False,

        source_endpoints_contacted=False,

        external_transport_attempted=False,

        hosted_tower_integration_verified=False,

        hosted_staging_verified=False,

        external_beta_acceptance_recorded=False,

        externally_beta_ready=False,

        secret_material_persisted=False,

        capital_movement_performed=False,

        downstream_execution_performed=False,

        conclusion=(
            CONCLUSION

            if ready

            else
            "TOWER_CLOUDS_REAL_FEED_CONNECTION_FOUNDATION_BLOCKED"
        ),
    )


def get_clouds_gp068_status_payload():

    closeout = (
        build_feed_connection_foundation_closeout()
    )


    safe = (
        closeout
        .source_trust_registry_ready
        is True

        and closeout
        .six_source_identity_ready
        is True

        and closeout
        .secret_reference_boundary_ready
        is True

        and closeout
        .signed_transport_ready
        is True

        and closeout
        .body_integrity_ready
        is True

        and closeout
        .signature_verification_ready
        is True

        and closeout
        .replay_rejection_ready
        is True

        and closeout
        .freshness_gate_ready
        is True

        and closeout
        .disconnected_state_ready
        is True

        and closeout
        .connected_unverified_state_ready
        is True

        and closeout
        .certification_verified_state_ready
        is True

        and closeout
        .external_verified_state_contract_ready
        is True

        and closeout
        .degraded_state_ready
        is True

        and closeout
        .revoked_state_ready
        is True

        and closeout
        .certification_fixture_live_claim_blocked
        is True

        and closeout
        .ready_for_source_connection_wave_1
        is True

        and closeout
        .wave_1_source_ids
        == (
            "tower",
            "observatory",
            "archive_vault",
        )

        and closeout
        .real_live_connection_count
        == 0

        and closeout
        .real_live_feeds_connected
        is False

        and closeout
        .source_endpoints_contacted
        is False

        and closeout
        .external_transport_attempted
        is False

        and closeout
        .hosted_tower_integration_verified
        is False

        and closeout
        .hosted_staging_verified
        is False

        and closeout
        .external_beta_acceptance_recorded
        is False

        and closeout
        .externally_beta_ready
        is False

        and closeout
        .secret_material_persisted
        is False

        and closeout
        .capital_movement_performed
        is False

        and closeout
        .downstream_execution_performed
        is False

        and closeout.conclusion
        == CONCLUSION
    )


    return {

        "pack":
        "GP068",

        "section":
        (
            "REAL FEED CONNECTION "
            "FOUNDATION CLOSEOUT"
        ),

        "status":
        (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue":
        safe,

        "six_source_identity_ready":
        True,

        "secret_reference_boundary_ready":
        True,

        "signed_transport_ready":
        True,

        "body_integrity_ready":
        True,

        "signature_verification_ready":
        True,

        "replay_rejection_ready":
        True,

        "freshness_gate_ready":
        True,

        "disconnected_state_ready":
        True,

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

        "certification_fixture_live_claim_blocked":
        True,

        "ready_for_source_connection_wave_1":
        True,

        "wave_1_source_ids":
        [
            "tower",
            "observatory",
            "archive_vault",
        ],

        "real_live_connection_count":
        0,

        "real_live_feeds_connected":
        False,

        "source_endpoints_contacted":
        False,

        "external_transport_attempted":
        False,

        "hosted_tower_integration_verified":
        False,

        "hosted_staging_verified":
        False,

        "external_beta_acceptance_recorded":
        False,

        "externally_beta_ready":
        False,

        "secret_material_persisted":
        False,

        "capital_movement_performed":
        False,

        "downstream_execution_performed":
        False,

        "conclusion":
        closeout.conclusion,

        "next_pack":
        (
            "GP069 — SOURCE CONNECTION WAVE 1 / "
            "TOWER SOURCE SUMMARY CONNECTION"
        ),
    }
