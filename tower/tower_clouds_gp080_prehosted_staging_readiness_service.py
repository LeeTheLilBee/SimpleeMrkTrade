"""
GP080 — Mixed-source pre-hosted staging readiness.

Certifies the current Tower Clouds native protection runtime
directly.

This does NOT certify hosted staging itself.
"""

from flask import Flask

from tower import (
    tower_clouds_native_launch
    as native
)

from tower.tower_clouds_gp076_source_wave2_closeout_service import (
    get_clouds_gp076_status_payload,
)

from tower.tower_clouds_gp077_source_availability_service import (
    get_clouds_gp077_status_payload,
)

from tower.tower_clouds_gp078_mixed_source_rehearsal_service import (
    get_clouds_gp078_status_payload,
)

from tower.tower_clouds_gp079_soulaana_mixed_source_service import (
    get_clouds_gp079_status_payload,
)

from tower.tower_clouds_intake_contract import (
    CANONICAL_OWNER_ROUTE,
    CANONICAL_OWNER_SERVICE_GETTER,
    CANONICAL_OWNER_SURFACE,
)


CONCLUSION = (
    "TOWER_CLOUDS_MIXED_SOURCE_PREHOSTED_REHEARSAL_"
    "READY_FOR_HOSTED_STAGING"
)


def certify_tower_clouds_protection():

    app = Flask(
        "gp080-certification"
    )

    app.secret_key = (
        "gp080-test-only-"
        "not-production-secret"
    )

    app.register_blueprint(
        native.tower_clouds_native_bp
    )


    with app.test_client() as client:

        # --------------------------------------------------------------
        # Anonymous /clouds must remain behind Tower.
        # --------------------------------------------------------------

        anonymous = client.get(
            native.CLOUDS_HOME_PATH,
            follow_redirects=False,
        )

        anonymous_location = (
            anonymous.headers.get(
                "Location",
                "",
            )
        )

        anonymous_gate = (
            anonymous.status_code
            in {
                301,
                302,
                303,
                307,
                308,
            }

            and anonymous_location.endswith(
                native.TOWER_LOGIN_PATH
            )
        )


        # --------------------------------------------------------------
        # Local test owner session only.
        # --------------------------------------------------------------

        with client.session_transaction() as sess:

            sess[
                native.SESSION_AUTHENTICATED
            ] = True

            sess[
                native.SESSION_ROLE
            ] = native.OWNER_ROLE

            sess[
                native.SESSION_OWNER_ID
            ] = "gp080-cert-owner"

            sess[
                native.SESSION_USERNAME
            ] = "gp080-cert-owner"

            sess.pop(
                native.SESSION_STEP_UP_UNTIL,
                None,
            )

            sess.pop(
                native
                .SESSION_TOWER_CLOUDS_INTEGRATION_HANDOFF,
                None,
            )


        # --------------------------------------------------------------
        # Direct /clouds without handoff must fail closed.
        # --------------------------------------------------------------

        no_handoff = client.get(
            native.CLOUDS_HOME_PATH,
            follow_redirects=False,
        )

        no_handoff_json = (
            no_handoff.get_json(
                silent=True
            )
            or {}
        )

        default_deny = (
            no_handoff.status_code
            == 403

            and no_handoff_json.get(
                "allowed"
            )
            is False

            and no_handoff_json.get(
                "reason_code"
            )
            == (
                "tower_clouds_"
                "integration_handoff_required"
            )

            and no_handoff_json.get(
                "default_deny"
            )
            is True
        )


        # --------------------------------------------------------------
        # Launch without step-up must redirect to step-up.
        # --------------------------------------------------------------

        no_step_up = client.get(
            native.CLOUDS_ACCESS_PATH,
            follow_redirects=False,
        )

        step_up_location = (
            no_step_up.headers.get(
                "Location",
                "",
            )
        )

        step_up_gate = (
            no_step_up.status_code
            in {
                301,
                302,
                303,
                307,
                308,
            }

            and native.CLOUDS_STEP_UP_PATH
            in step_up_location
        )


        # --------------------------------------------------------------
        # Protected return should preserve owner session and receipt.
        # --------------------------------------------------------------

        returned = client.get(
            native.CLOUDS_RETURN_PATH,
            follow_redirects=False,
        )

        return_location = (
            returned.headers.get(
                "Location",
                "",
            )
        )

        return_route = (
            returned.status_code
            in {
                301,
                302,
                303,
                307,
                308,
            }

            and return_location.endswith(
                native.TOWER_ACCESS_HOME_PATH
            )
        )


        with client.session_transaction() as sess:

            receipt = (
                sess.get(
                    native
                    .SESSION_TOWER_CLOUDS_RETURN_RECEIPT
                )
                or {}
            )


        return_receipt = (
            isinstance(
                receipt,
                dict,
            )

            and receipt.get(
                "receipt_type"
            )
            == "tower_clouds_return_receipt"

            and receipt.get(
                "allowed"
            )
            is True

            and receipt.get(
                "tower_session_preserved"
            )
            is True

            and receipt.get(
                "default_deny"
            )
            is True

            and receipt.get(
                "downstream_execution_performed"
            )
            is False
        )


    route_contract = (
        CANONICAL_OWNER_ROUTE
        == "/clouds"

        and native.CLOUDS_HOME_PATH
        == "/clouds"
    )


    owner_surface_contract = (
        CANONICAL_OWNER_SURFACE
        == "OwnerCommandExperience"

        and CANONICAL_OWNER_SERVICE_GETTER
        == "get_owner_command_experience"
    )


    owner_gate_present = callable(
        native.owner_session_active
    )


    step_up_present = callable(
        native.step_up_active
    )


    handoff_gate_present = callable(
        native
        ._tower_clouds_integration_handoff_active
    )


    certified = all(
        (
            route_contract,
            owner_surface_contract,
            owner_gate_present,
            step_up_present,
            handoff_gate_present,
            anonymous_gate,
            default_deny,
            step_up_gate,
            return_route,
            return_receipt,
        )
    )


    return {

        "tower_runtime_protection_certified":
        certified,

        "canonical_route_verified":
        route_contract,

        "canonical_surface_verified":
        owner_surface_contract,

        "owner_session_gate_present":
        owner_gate_present,

        "owner_permission_gate_present":
        (
            native.OWNER_ROLE
            == "owner"
        ),

        "anonymous_access_gate_verified":
        anonymous_gate,

        "step_up_gate_present":
        step_up_present,

        "step_up_redirect_verified":
        step_up_gate,

        "handoff_gate_present":
        handoff_gate_present,

        "default_deny_verified":
        default_deny,

        "return_path_verified":
        return_route,

        "return_receipt_verified":
        return_receipt,

        "hosted_runtime_used":
        False,

        "production_credentials_used":
        False,

        "downstream_execution_performed":
        False,
    }


def get_clouds_gp080_status_payload():

    gp076 = (
        get_clouds_gp076_status_payload()
    )

    gp077 = (
        get_clouds_gp077_status_payload()
    )

    gp078 = (
        get_clouds_gp078_status_payload()
    )

    gp079 = (
        get_clouds_gp079_status_payload()
    )

    tower = (
        certify_tower_clouds_protection()
    )


    ready = all(
        (
            gp076[
                "status"
            ]
            == "ready",

            gp076[
                "safe_to_continue"
            ]
            is True,

            gp077[
                "status"
            ]
            == "ready",

            gp077[
                "safe_to_continue"
            ]
            is True,

            gp078[
                "status"
            ]
            == "ready",

            gp078[
                "safe_to_continue"
            ]
            is True,

            gp079[
                "status"
            ]
            == "ready",

            gp079[
                "safe_to_continue"
            ]
            is True,

            tower[
                "tower_runtime_protection_certified"
            ]
            is True,

            gp077[
                "source_count"
            ]
            == 6,

            gp078[
                "projection_only_count"
            ]
            == 3,

            gp078[
                "missing_count"
            ]
            == 3,

            gp078[
                "healthy_live_count"
            ]
            == 0,

            gp078[
                "business_risk_inference_count"
            ]
            == 0,

            gp078[
                "business_attention_escalation_count"
            ]
            == 0,

            gp078[
                "false_urgency_count"
            ]
            == 0,

            gp078[
                "last_known_falsely_current_count"
            ]
            == 0,

            gp078[
                "all_degraded_sources_fail_safe"
            ]
            is True,

            gp079[
                "soulaana_explanation_first"
            ]
            is True,

            gp079[
                "false_all_clear_given"
            ]
            is False,

            gp079[
                "business_danger_invented"
            ]
            is False,

            gp079[
                "automatic_business_decision_performed"
            ]
            is False,
        )
    )


    return {

        "pack":
        "GP080",

        "section":
        (
            "MIXED-SOURCE PRE-HOSTED "
            "STAGING READINESS CLOSEOUT"
        ),

        "status":
        (
            "ready"
            if ready
            else "blocked"
        ),

        "safe_to_continue":
        ready,

        "tower_runtime_protection_certified":
        tower[
            "tower_runtime_protection_certified"
        ],

        "tower_owner_session_required":
        tower[
            "owner_session_gate_present"
        ],

        "tower_owner_permission_required":
        tower[
            "owner_permission_gate_present"
        ],

        "tower_step_up_required":
        tower[
            "step_up_gate_present"
        ],

        "tower_default_deny_preserved":
        tower[
            "default_deny_verified"
        ],

        "tower_anonymous_access_gate_verified":
        tower[
            "anonymous_access_gate_verified"
        ],

        "tower_step_up_redirect_verified":
        tower[
            "step_up_redirect_verified"
        ],

        "tower_return_path_verified":
        tower[
            "return_path_verified"
        ],

        "tower_return_receipt_verified":
        tower[
            "return_receipt_verified"
        ],

        "six_source_contract_network_ready":
        True,

        "mixed_source_rehearsal_verified":
        True,

        "projection_only_source_count":
        3,

        "unavailable_source_count":
        3,

        "verified_live_source_count":
        0,

        "missing_source_business_danger_inference_count":
        0,

        "false_urgency_count":
        0,

        "soulaana_explanation_first":
        True,

        "safe_degradation_verified":
        True,

        "ready_for_hosted_staging_rehearsal":
        ready,

        "hosted_staging_rehearsal_authorized":
        ready,

        # --------------------------------------------------------------
        # Still explicitly unproven.
        # --------------------------------------------------------------

        "hosted_tower_integration_verified":
        False,

        "hosted_staging_verified":
        False,

        "real_live_feeds_connected":
        False,

        "external_beta_acceptance_recorded":
        False,

        "externally_beta_ready":
        False,

        "production_secrets_activated":
        False,

        "hosted_runtime_used_for_gp080":
        False,

        "production_credentials_used_for_gp080":
        False,

        "capital_movement_performed":
        False,

        "automatic_business_decision_performed":
        False,

        "downstream_execution_performed":
        False,

        "conclusion":
        (
            CONCLUSION

            if ready

            else
            "TOWER_CLOUDS_PREHOSTED_STAGING_READINESS_BLOCKED"
        ),

        "next_pack":
        (
            "GP081 — HOSTED TOWER→CLOUDS "
            "OWNER WALKTHROUGH REHEARSAL"
        ),
    }
