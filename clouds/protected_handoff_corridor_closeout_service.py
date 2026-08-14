"""
GP040 — Protected Handoff Corridor Closeout /
External Boundary Seal.

PERFORMANCE REPAIR
------------------

GP039 already verifies GP038 readiness.

GP038 already verifies GP037 readiness.

Therefore GP040 must NOT separately invoke all three
upstream status payloads again.

GP040 asks GP039 exactly once and treats a green GP039
certification as proof that the GP037 -> GP038 -> GP039
upstream certification chain is intact.

This changes computation shape only.

No authorization, delivery, receipt, Tower, or downstream
safety boundary is weakened.
"""

from __future__ import annotations

try:
    from .external_handoff_receipt_service import (
        get_clouds_gp039_status_payload,
    )

    from .protected_handoff_corridor_closeout import (
        ProtectedHandoffCorridorCloseout,
    )

except ImportError:
    from external_handoff_receipt_service import (
        get_clouds_gp039_status_payload,
    )

    from protected_handoff_corridor_closeout import (
        ProtectedHandoffCorridorCloseout,
    )


CLOSEOUT_CONCLUSION = (
    "CLOUDS_PHASE_II_HANDOFF_CORRIDOR_READY_FOR_"
    "EXTERNAL_TOWER_INTEGRATION"
)


def _get_verified_upstream_chain():
    """
    Single upstream certification call.

    GP039.safe_to_continue is fail-closed and already
    requires the GP038 chain to be green.

    GP038.safe_to_continue already requires GP037 green.
    """

    gp039 = (
        get_clouds_gp039_status_payload()
    )

    upstream_ready = (
        gp039.get("pack")
        == "GP039"

        and gp039.get("status")
        == "ready"

        and gp039.get(
            "safe_to_continue"
        )
        is True

        and gp039.get(
            "receipt_validator_ready"
        )
        is True

        and gp039.get(
            "fixture_only"
        )
        is True

        and gp039.get(
            "external_receipt_connected"
        )
        is False

        and gp039.get(
            "external_receipt_verified"
        )
        is False

        and gp039.get(
            "external_acceptance_verified"
        )
        is False

        and gp039.get(
            "tower_receipt_verified"
        )
        is False

        and gp039.get(
            "handoff_delivered"
        )
        is False

        and gp039.get(
            "downstream_execution_performed"
        )
        is False
    )

    return (
        gp039,
        upstream_ready,
    )


def get_protected_handoff_corridor_closeout():
    (
        gp039,
        upstream_ready,
    ) = (
        _get_verified_upstream_chain()
    )


    corridor_complete = (
        upstream_ready
        is True
    )


    return (
        ProtectedHandoffCorridorCloseout(
            closeout_id=(
                "clouds-phase-ii-"
                "handoff-corridor-closeout"
            ),

            clouds_side_corridor_complete=(
                corridor_complete
            ),

            # GP039 readiness is the transitive
            # certification of GP038 + GP037.
            release_execution_ready=(
                upstream_ready
            ),

            delivery_attempt_record_ready=(
                upstream_ready
            ),

            external_receipt_validator_ready=(
                gp039[
                    "receipt_validator_ready"
                ]
            ),

            external_delivery_adapter_required=True,

            external_transport_invoked=False,

            tower_contacted=False,

            external_delivery_attempted=False,

            external_receipt_connected=False,

            external_receipt_verified=False,

            external_acceptance_verified=False,

            tower_receipt_verified=False,

            handoff_delivered=False,

            ready_for_external_tower_integration=(
                corridor_complete
            ),

            approval_performed=False,

            capital_movement_performed=False,

            downstream_execution_performed=False,

            conclusion=(
                CLOSEOUT_CONCLUSION
                if corridor_complete
                else (
                    "CLOUDS_PHASE_II_"
                    "HANDOFF_CORRIDOR_BLOCKED"
                )
            ),

            soulaana_summary=(
                "The Clouds side of the protected "
                "handoff corridor is complete."
                if corridor_complete
                else
                (
                    "The protected handoff corridor "
                    "is not ready to close yet."
                )
            ),

            soulaana_what_this_means=(
                "Clouds can prepare, authorize, freeze, "
                "release, and validate its side of the "
                "handoff boundary without taking over "
                "Tower's authority."
                if corridor_complete
                else
                (
                    "One or more upstream protected "
                    "handoff checks still needs attention."
                )
            ),

            soulaana_what_can_wait=(
                "Real Tower delivery can wait until the "
                "external adapter is connected. I will "
                "not pretend Tower received anything."
            ),

            soulaana_next_step=(
                "Move into the six-source real summary "
                "feed adapter layer. The actual Tower "
                "transport and receipt remain separate "
                "integration work."
                if corridor_complete
                else
                (
                    "Repair the upstream handoff "
                    "certification before proceeding."
                )
            ),
        )
    )


def get_protected_handoff_corridor_closeout_payload():
    return (
        get_protected_handoff_corridor_closeout()
        .to_dict()
    )


def get_clouds_gp040_status_payload():
    closeout = (
        get_protected_handoff_corridor_closeout()
    )


    safe = (
        closeout
        .clouds_side_corridor_complete
        is True

        and closeout
        .release_execution_ready
        is True

        and closeout
        .delivery_attempt_record_ready
        is True

        and closeout
        .external_receipt_validator_ready
        is True

        and closeout
        .external_delivery_adapter_required
        is True

        and closeout
        .external_transport_invoked
        is False

        and closeout
        .tower_contacted
        is False

        and closeout
        .external_delivery_attempted
        is False

        and closeout
        .external_receipt_connected
        is False

        and closeout
        .external_receipt_verified
        is False

        and closeout
        .external_acceptance_verified
        is False

        and closeout
        .tower_receipt_verified
        is False

        and closeout
        .handoff_delivered
        is False

        and closeout
        .ready_for_external_tower_integration
        is True

        and closeout
        .approval_performed
        is False

        and closeout
        .capital_movement_performed
        is False

        and closeout
        .downstream_execution_performed
        is False

        and closeout.conclusion
        == CLOSEOUT_CONCLUSION
    )


    return {
        "pack": "GP040",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "PROTECTED HANDOFF CORRIDOR CLOSEOUT / "
            "EXTERNAL BOUNDARY SEAL"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": (
            safe
        ),

        "clouds_side_corridor_complete": (
            closeout
            .clouds_side_corridor_complete
        ),

        "upstream_chain_verified_through_gp039": (
            True
            if safe
            else False
        ),

        "release_execution_ready": (
            closeout.release_execution_ready
        ),

        "delivery_attempt_record_ready": (
            closeout
            .delivery_attempt_record_ready
        ),

        "external_receipt_validator_ready": (
            closeout
            .external_receipt_validator_ready
        ),

        "external_delivery_adapter_required": True,

        "external_transport_invoked": False,

        "tower_contacted": False,

        "external_delivery_attempted": False,

        "external_receipt_connected": False,

        "external_receipt_verified": False,

        "external_acceptance_verified": False,

        "tower_receipt_verified": False,

        "handoff_delivered": False,

        "ready_for_external_tower_integration": (
            closeout
            .ready_for_external_tower_integration
        ),

        "approval_performed": False,

        "capital_movement_performed": False,

        "downstream_execution_performed": False,

        "status_chain_recalculation_reduced": True,

        "tower_authority_changed": False,

        "conclusion": (
            closeout.conclusion
        ),

        "next_pack": (
            "GP041 — TOWER + OBSERVATORY REAL "
            "SUMMARY FEED ADAPTER CONTRACTS"
        ),
    }
