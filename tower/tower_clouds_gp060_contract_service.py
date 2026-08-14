"""
GP061 — Tower-side pin of finished Clouds GP060 contract.
"""

CLOUDS_SOURCE_BRANCH = "clouds-rebuild-dev"

CLOUDS_GP060_SOURCE_COMMIT = (
    "9606ccef44045634eaf977f1df641751aefd866b"
)

CLOUDS_GP060_CONCLUSION = (
    "CLOUDS_PHASE_II_READY_FOR_TOWER_INTEGRATION_AND_REAL_FEED_CONNECTION"
)


def get_clouds_gp061_status_payload():

    safe = all(
        (
            CLOUDS_SOURCE_BRANCH
            == "clouds-rebuild-dev",

            CLOUDS_GP060_SOURCE_COMMIT
            == "9606ccef44045634eaf977f1df641751aefd866b",

            CLOUDS_GP060_CONCLUSION
            == (
                "CLOUDS_PHASE_II_READY_FOR_"
                "TOWER_INTEGRATION_AND_REAL_FEED_CONNECTION"
            ),
        )
    )

    return {

        "pack": "GP061",

        "section":
        "CLOUDS GP060 PHASE-II CONTRACT PIN",

        "status":
        "ready" if safe else "blocked",

        "safe_to_continue":
        safe,

        "source_branch":
        CLOUDS_SOURCE_BRANCH,

        "source_commit":
        CLOUDS_GP060_SOURCE_COMMIT,

        "phase_pack_start":
        "GP025",

        "phase_pack_end":
        "GP060",

        "phase_ii_conclusion":
        CLOUDS_GP060_CONCLUSION,

        "clouds_phase_ii_software_ready":
        True,

        "ready_for_tower_integration":
        True,

        "ready_for_real_feed_connection":
        True,

        "owner_route":
        "/clouds",

        "owner_surface":
        "OwnerCommandExperience",

        "owner_service_getter":
        "get_owner_command_experience",

        "tower_authority_required":
        True,

        "owner_permission_required":
        True,

        "step_up_required":
        True,

        "default_deny_required":
        True,

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

        "clouds_source_branch_merged":
        False,

        "runtime_activation_performed":
        False,

        "downstream_execution_performed":
        False,
    }
