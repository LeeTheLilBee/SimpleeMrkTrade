"""
GP063 — Reconcile GP060 with existing protected Tower launch.
"""

from tower import (
    tower_clouds_native_launch
    as native
)

from tower.tower_clouds_gp060_intake_service import (
    get_clouds_gp062_status_payload,
)

from tower.tower_clouds_intake_contract import (
    CANONICAL_OWNER_ROUTE,
    CANONICAL_OWNER_SERVICE_GETTER,
    CANONICAL_OWNER_SURFACE,
    TOWER_INTAKE_PACKAGE_VERSION,
)


def get_clouds_gp063_status_payload():

    gp062 = (
        get_clouds_gp062_status_payload()
    )

    owner_route_compatible = (
        CANONICAL_OWNER_ROUTE
        == "/clouds"
    )

    owner_surface_compatible = (
        CANONICAL_OWNER_SURFACE
        == "OwnerCommandExperience"
    )

    getter_compatible = (
        CANONICAL_OWNER_SERVICE_GETTER
        == "get_owner_command_experience"
    )

    owner_session_gate = callable(
        getattr(
            native,
            "owner_session_active",
            None,
        )
    )

    step_up_gate = callable(
        getattr(
            native,
            "step_up_active",
            None,
        )
    )

    handoff_gate = callable(
        getattr(
            native,
            "_tower_clouds_integration_handoff_active",
            None,
        )
    )

    default_deny = all(
        (
            owner_session_gate,
            step_up_gate,
            handoff_gate,
        )
    )

    safe = all(
        (
            gp062["status"]
            == "ready",

            TOWER_INTAKE_PACKAGE_VERSION
            == "clouds-gp016-v1",

            owner_route_compatible,

            owner_surface_compatible,

            getter_compatible,

            native.CLOUDS_ACCESS_PATH
            == "/tower/launch/clouds",

            native.CLOUDS_STEP_UP_PATH
            == "/tower/step-up/clouds",

            native.CLOUDS_RETURN_PATH
            == "/tower/return/clouds",

            default_deny,
        )
    )

    return {

        "pack":
        "GP063",

        "section":
        "EXISTING TOWER NATIVE-LAUNCH COMPATIBILITY",

        "status":
        "ready" if safe else "blocked",

        "safe_to_continue":
        safe,

        "legacy_intake_version":
        TOWER_INTAKE_PACKAGE_VERSION,

        "new_intake_version":
        "clouds-gp060-v1",

        "owner_route_compatible":
        owner_route_compatible,

        "owner_surface_compatible":
        owner_surface_compatible,

        "owner_service_getter_compatible":
        getter_compatible,

        "existing_launch_path_preserved":
        (
            native.CLOUDS_ACCESS_PATH
            == "/tower/launch/clouds"
        ),

        "existing_step_up_path_preserved":
        (
            native.CLOUDS_STEP_UP_PATH
            == "/tower/step-up/clouds"
        ),

        "existing_return_path_preserved":
        (
            native.CLOUDS_RETURN_PATH
            == "/tower/return/clouds"
        ),

        "owner_session_gate_present":
        owner_session_gate,

        "step_up_gate_present":
        step_up_gate,

        "handoff_gate_present":
        handoff_gate,

        "default_deny_preserved":
        default_deny,

        "existing_native_launch_modified":
        False,

        "runtime_activation_performed":
        False,

        "source_branch_merged":
        False,

        "downstream_execution_performed":
        False,
    }
