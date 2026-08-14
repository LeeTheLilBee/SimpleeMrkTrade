"""
GP064 — Tower↔Clouds GP060 reconciliation closeout.
"""

from tower.tower_clouds_gp060_contract_service import (
    get_clouds_gp061_status_payload,
)

from tower.tower_clouds_gp060_intake_service import (
    get_clouds_gp062_status_payload,
)

from tower.tower_clouds_gp060_launch_reconciliation_service import (
    get_clouds_gp063_status_payload,
)


CONCLUSION = (
    "TOWER_CLOUDS_GP060_CONTRACT_RECONCILED_"
    "READY_FOR_PROTECTED_RUNTIME_INTEGRATION"
)


def get_clouds_gp064_status_payload():

    gp061 = (
        get_clouds_gp061_status_payload()
    )

    gp062 = (
        get_clouds_gp062_status_payload()
    )

    gp063 = (
        get_clouds_gp063_status_payload()
    )

    safe = all(
        (
            gp061["status"]
            == "ready",

            gp062["status"]
            == "ready",

            gp063["status"]
            == "ready",

            gp061[
                "safe_to_continue"
            ]
            is True,

            gp062[
                "safe_to_continue"
            ]
            is True,

            gp063[
                "safe_to_continue"
            ]
            is True,

            gp063[
                "default_deny_preserved"
            ]
            is True,
        )
    )

    return {

        "pack":
        "GP064",

        "section":
        "TOWER↔CLOUDS GP060 CONTRACT RECONCILIATION CLOSEOUT",

        "status":
        "ready" if safe else "blocked",

        "safe_to_continue":
        safe,

        "gp060_source_commit_pinned":
        True,

        "gp060_capabilities_recognized":
        True,

        "owner_route_reconciled":
        gp063[
            "owner_route_compatible"
        ],

        "owner_surface_reconciled":
        gp063[
            "owner_surface_compatible"
        ],

        "owner_session_preserved":
        gp063[
            "owner_session_gate_present"
        ],

        "owner_permission_preserved":
        gp062[
            "requires_owner_permission"
        ],

        "step_up_preserved":
        gp063[
            "step_up_gate_present"
        ],

        "default_deny_preserved":
        gp063[
            "default_deny_preserved"
        ],

        "existing_launch_preserved":
        gp063[
            "existing_launch_path_preserved"
        ],

        "existing_return_preserved":
        gp063[
            "existing_return_path_preserved"
        ],

        "legacy_contract_preserved":
        gp062[
            "legacy_gp016_gp017_contract_preserved"
        ],

        "ready_for_protected_runtime_integration":
        safe,

        "clouds_source_branch_merged":
        False,

        "real_live_feeds_connected":
        False,

        "hosted_tower_integration_verified":
        False,

        "hosted_staging_verified":
        False,

        "external_beta_acceptance_recorded":
        False,

        "externally_beta_ready":
        False,

        "runtime_activation_performed":
        False,

        "capital_movement_performed":
        False,

        "downstream_execution_performed":
        False,

        "conclusion":
        (
            CONCLUSION
            if safe
            else
            "TOWER_CLOUDS_GP060_CONTRACT_RECONCILIATION_BLOCKED"
        ),

        "next_pack":
        (
            "GP065 — REAL FEED CONNECTION "
            "AUTHENTICATION FOUNDATION"
        ),
    }
