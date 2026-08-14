"""
GP079 — Soulaana mixed-source explanation layer.

Explanation precedes raw evidence.

Missing source data does not become business danger.
"""

from tower.tower_clouds_gp077_source_availability_service import (
    build_source_availability_matrix,
    get_clouds_gp077_status_payload,
)

from tower.tower_clouds_gp078_mixed_source_rehearsal_service import (
    get_clouds_gp078_status_payload,
)


def build_soulaana_mixed_source_brief():

    rows = (
        build_source_availability_matrix()
    )


    projection_sources = [
        item[
            "source_id"
        ]
        for item
        in rows
        if item[
            "safe_fallback"
        ]
        == "projection_reference_only"
    ]


    unavailable_sources = [
        item[
            "source_id"
        ]
        for item
        in rows
        if item[
            "safe_fallback"
        ]
        == "withhold_current_claim"
    ]


    return {

        "lead_explanation":
        (
            "I can safely show planning/reference context "
            "for Tower, The Observatory, and Archive Vault. "
            "I do not yet have verified current operating data "
            "for The Teller, The Grounds, or ATM Operations."
        ),

        "what_it_means":
        (
            "The ecosystem connection work is progressing, "
            "but none of these six sources is being presented "
            "to you as verified live operating truth yet."
        ),

        "why_it_matters":
        (
            "That keeps me from turning test, projection, "
            "or missing information into fake current business facts."
        ),

        "what_changed":
        (
            "All six source contracts now have defined Clouds seams. "
            "Three mature sources have source-owned publisher "
            "certification, while three remain contract-only until "
            "their operational systems are connected."
        ),

        "what_needs_attention":
        (
            "Nothing here is a business emergency. "
            "The remaining work is integration work: verify hosted "
            "source transport and later connect operational systems "
            "as those systems become available."
        ),

        "what_can_wait":
        (
            "The Teller, Grounds, and ATM operational feeds can remain "
            "unavailable during the Clouds staging rehearsal as long "
            "as I keep them visibly unavailable and do not invent "
            "current state."
        ),

        "next_action":
        (
            "Proceed to a protected hosted staging rehearsal where "
            "Tower access, Clouds launch, mixed-source degradation, "
            "Soulaana explanations, and Tower return are exercised."
        ),

        "no_action_needed_message":
        (
            "No owner business action is required because a source "
            "is missing. Missing data is a system visibility state, "
            "not proof that the business itself is in trouble."
        ),

        "projection_source_ids":
        projection_sources,

        "unavailable_source_ids":
        unavailable_sources,

        "raw_evidence_first":
        False,

        "soulaana_explanation_first":
        True,

        "false_all_clear_given":
        False,

        "business_danger_invented":
        False,

        "automatic_business_decision_performed":
        False,

        "downstream_execution_performed":
        False,
    }


def get_clouds_gp079_status_payload():

    gp077 = (
        get_clouds_gp077_status_payload()
    )

    gp078 = (
        get_clouds_gp078_status_payload()
    )

    brief = (
        build_soulaana_mixed_source_brief()
    )


    safe = (
        gp077["status"]
        == "ready"

        and gp078["status"]
        == "ready"

        and brief[
            "projection_source_ids"
        ]
        == [
            "observatory",
            "tower",
            "archive_vault",
        ]

        and brief[
            "unavailable_source_ids"
        ]
        == [
            "teller",
            "grounds",
            "atm_operations",
        ]

        and brief[
            "soulaana_explanation_first"
        ]
        is True

        and brief[
            "raw_evidence_first"
        ]
        is False

        and brief[
            "false_all_clear_given"
        ]
        is False

        and brief[
            "business_danger_invented"
        ]
        is False

        and brief[
            "automatic_business_decision_performed"
        ]
        is False

        and brief[
            "downstream_execution_performed"
        ]
        is False
    )


    return {

        "pack":
        "GP079",

        "section":
        (
            "SOULAANA MIXED-SOURCE "
            "EXPLANATION LAYER"
        ),

        "status":
        (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue":
        safe,

        **brief,

        "real_live_feeds_connected":
        False,

        "hosted_staging_verified":
        False,

        "externally_beta_ready":
        False,

        "capital_movement_performed":
        False,

        "next_pack":
        (
            "GP080 — PRE-HOSTED "
            "STAGING READINESS CLOSEOUT"
        ),
    }
