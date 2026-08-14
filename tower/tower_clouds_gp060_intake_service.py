"""
GP062 — Tower GP060 intake/integrity v2.
"""

import hashlib
import json

from tower.tower_clouds_gp060_contract_service import (
    get_clouds_gp061_status_payload,
)


GP060_INTAKE_VERSION = (
    "clouds-gp060-v1"
)


def _hash(payload):

    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def build_tower_clouds_gp060_intake():

    gp061 = (
        get_clouds_gp061_status_payload()
    )

    base = {

        "intake_version":
        GP060_INTAKE_VERSION,

        "source_commit":
        gp061["source_commit"],

        "owner_route":
        gp061["owner_route"],

        "owner_surface":
        gp061["owner_surface"],

        "owner_service_getter":
        gp061["owner_service_getter"],

        "requires_owner_session":
        True,

        "requires_owner_permission":
        True,

        "requires_step_up":
        True,

        "default_deny_required":
        True,

        "legacy_gp016_gp017_contract_preserved":
        True,

        "source_branch_merge_required_for_this_pack":
        False,

        "source_branch_merged":
        False,

        "runtime_activation_performed":
        False,

        "real_live_feeds_connected":
        False,

        "hosted_tower_integration_verified":
        False,

        "hosted_staging_verified":
        False,

        "external_beta_acceptance_recorded":
        False,

        "downstream_execution_performed":
        False,
    }

    return {
        **base,
        "integrity_hash":
        _hash(base),
    }


def validate_tower_clouds_gp060_intake(
    intake,
):

    errors = []

    body = dict(intake)

    integrity_hash = (
        body.pop(
            "integrity_hash",
            "",
        )
    )

    if (
        intake.get(
            "intake_version"
        )
        != GP060_INTAKE_VERSION
    ):
        errors.append(
            "intake_version_invalid"
        )

    if (
        integrity_hash
        != _hash(body)
    ):
        errors.append(
            "integrity_hash_invalid"
        )

    for key in (
        "requires_owner_session",
        "requires_owner_permission",
        "requires_step_up",
        "default_deny_required",
        "legacy_gp016_gp017_contract_preserved",
    ):

        if (
            intake.get(key)
            is not True
        ):
            errors.append(
                f"{key}_must_be_true"
            )

    for key in (
        "source_branch_merge_required_for_this_pack",
        "source_branch_merged",
        "runtime_activation_performed",
        "real_live_feeds_connected",
        "hosted_tower_integration_verified",
        "hosted_staging_verified",
        "external_beta_acceptance_recorded",
        "downstream_execution_performed",
    ):

        if (
            intake.get(key)
            is not False
        ):
            errors.append(
                f"{key}_must_be_false"
            )

    return (
        not errors,
        tuple(errors),
    )


def get_clouds_gp062_status_payload():

    gp061 = (
        get_clouds_gp061_status_payload()
    )

    intake = (
        build_tower_clouds_gp060_intake()
    )

    valid, errors = (
        validate_tower_clouds_gp060_intake(
            intake
        )
    )

    safe = (
        gp061["status"]
        == "ready"

        and valid
    )

    return {

        "pack":
        "GP062",

        "section":
        "TOWER GP060 INTAKE / INTEGRITY CONTRACT V2",

        "status":
        "ready" if safe else "blocked",

        "safe_to_continue":
        safe,

        "intake_version":
        intake[
            "intake_version"
        ],

        "integrity_hash_present":
        bool(
            intake[
                "integrity_hash"
            ]
        ),

        "requires_owner_session":
        True,

        "requires_owner_permission":
        True,

        "requires_step_up":
        True,

        "default_deny_required":
        True,

        "legacy_gp016_gp017_contract_preserved":
        True,

        "source_branch_merged":
        False,

        "runtime_activation_performed":
        False,

        "real_live_feeds_connected":
        False,

        "hosted_tower_integration_verified":
        False,

        "hosted_staging_verified":
        False,

        "external_beta_acceptance_recorded":
        False,

        "validation_errors":
        list(errors),

        "downstream_execution_performed":
        False,
    }
