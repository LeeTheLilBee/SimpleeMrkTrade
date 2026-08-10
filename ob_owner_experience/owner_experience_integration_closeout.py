from copy import deepcopy

from .six_room_real_surface_acceptance import (
    SIX_ROOM_REAL_SURFACE_ORDER,
    build_six_room_real_surface_acceptance_bundle,
)
from .ui_surface_registry import (
    MUST_NOT_CLAIM,
    PROTECTED_ROUTE_POLICY,
    build_real_surface_adapter_contract,
)

OWNER_EXPERIENCE_INTEGRATION_CLOSEOUT_IDENTITY = {
    "package": "ob_owner_experience_integration_closeout_gp009",
    "display_title": "Owner Experience Integration Closeout",
    "decision": "READY_FOR_OWNER_EXPERIENCE_INTEGRATION_CLOSEOUT_WITH_SAFETY_LOCKS_HELD",
    "plain_language": (
        "The owner-experience simplification lane has a six-room registry, "
        "real-surface contracts for all six protected rooms, and a six-room "
        "acceptance bundle. This is not staging readiness and does not unlock "
        "production deploy, broker submission, money movement, execution, "
        "permission mutation, secret reveal, or Live Auto."
    ),
}

OWNER_EXPERIENCE_CLOSED_PACKAGES = [
    {
        "gp": "GP001",
        "name": "Six-room registry adapter",
        "status": "closed",
    },
    {
        "gp": "GP002",
        "name": "Dashboard real surface",
        "status": "closed",
    },
    {
        "gp": "GP003",
        "name": "Market Map real surface",
        "status": "closed",
    },
    {
        "gp": "GP004",
        "name": "Symbol Page real surface",
        "status": "closed",
    },
    {
        "gp": "GP005",
        "name": "Trade Center real surface",
        "status": "closed",
    },
    {
        "gp": "GP006",
        "name": "Review Center real surface",
        "status": "closed",
    },
    {
        "gp": "GP007",
        "name": "Owner Console real surface",
        "status": "closed",
    },
    {
        "gp": "GP008",
        "name": "Six-room real surface acceptance",
        "status": "closed",
    },
]

OWNER_EXPERIENCE_NOT_AUTHORIZED = [
    "STAGING_READY",
    "production deployment",
    "Render redeploy",
    "owner walkthrough acceptance",
    "Tower return repair",
    "broker submission",
    "real capital movement",
    "direct execution",
    "automated execution",
    "permission mutation",
    "secret reveal",
    "Live Auto unlock",
]

OWNER_EXPERIENCE_CLOSEOUT_REQUIRED_FALSE_FLAGS = [
    "staging_ready",
    "production_deploy_enabled",
    "render_redeployed",
    "owner_walkthrough_accepted",
    "tower_return_repaired",
    "broker_submission_enabled",
    "real_capital_movement_enabled",
    "direct_execution_enabled",
    "automated_execution_enabled",
    "permission_mutation_enabled",
    "secret_reveal_enabled",
]

OWNER_EXPERIENCE_CLOSEOUT_REQUIRED_TRUE_FLAGS = [
    "owner_session_required",
    "live_auto_locked",
]


def _closed_package_names():
    return [item["name"] for item in OWNER_EXPERIENCE_CLOSED_PACKAGES]


def _closed_gp_codes():
    return [item["gp"] for item in OWNER_EXPERIENCE_CLOSED_PACKAGES]


def _registry_summary_from_acceptance(acceptance_bundle):
    summary = []

    for record in acceptance_bundle["matrix"]:
        summary.append(
            {
                "room": record["room"],
                "accepted": record["accepted"],
                "route_hint": record["route_hint"],
                "component_hint": record["component_hint"],
                "data_adapter_hint": record["data_adapter_hint"],
            }
        )

    return summary


def _all_rooms_accepted(acceptance_bundle):
    return (
        acceptance_bundle["accepted"] is True
        and acceptance_bundle["accepted_rooms"] == list(SIX_ROOM_REAL_SURFACE_ORDER)
        and acceptance_bundle["blocked_rooms"] == []
    )


def build_owner_experience_integration_status():
    acceptance = build_six_room_real_surface_acceptance_bundle()
    all_rooms_accepted = _all_rooms_accepted(acceptance)

    return {
        "registry_adapter_closed": True,
        "dashboard_real_surface_closed": "dashboard" in acceptance["accepted_rooms"],
        "market_map_real_surface_closed": "market_map" in acceptance["accepted_rooms"],
        "symbol_page_real_surface_closed": "symbol_page" in acceptance["accepted_rooms"],
        "trade_center_real_surface_closed": "trade_center" in acceptance["accepted_rooms"],
        "review_center_real_surface_closed": "review_center" in acceptance["accepted_rooms"],
        "owner_console_real_surface_closed": "owner_console" in acceptance["accepted_rooms"],
        "six_room_acceptance_closed": all_rooms_accepted,
        "owner_experience_integration_closeout_ready": all_rooms_accepted,
        "all_six_rooms_present": acceptance["surface_status"]["all_six_rooms_present"],
        "all_registry_routes_match": acceptance["surface_status"]["all_registry_routes_match"],
        "all_registry_components_match": acceptance["surface_status"]["all_registry_components_match"],
        "all_data_adapters_match": acceptance["surface_status"]["all_data_adapters_match"],
        "all_routes_protected": acceptance["surface_status"]["all_routes_protected"],
        "anonymous_access_allowed": False,
        "owner_session_required": True,
        "staging_ready": False,
        "production_deploy_enabled": False,
        "render_redeployed": False,
        "owner_walkthrough_accepted": False,
        "tower_return_repaired": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_execution_enabled": False,
        "automated_execution_enabled": False,
        "permission_mutation_enabled": False,
        "secret_reveal_enabled": False,
        "live_auto_locked": True,
    }


def build_owner_experience_integration_closeout_bundle():
    acceptance = build_six_room_real_surface_acceptance_bundle()
    status = build_owner_experience_integration_status()
    adapter = build_real_surface_adapter_contract()

    false_flags_ok = all(
        status.get(key) is False
        for key in OWNER_EXPERIENCE_CLOSEOUT_REQUIRED_FALSE_FLAGS
    )

    true_flags_ok = all(
        status.get(key) is True
        for key in OWNER_EXPERIENCE_CLOSEOUT_REQUIRED_TRUE_FLAGS
    )

    closed = all(
        [
            _all_rooms_accepted(acceptance),
            status["owner_experience_integration_closeout_ready"] is True,
            status["all_routes_protected"] is True,
            status["anonymous_access_allowed"] is False,
            false_flags_ok,
            true_flags_ok,
            "STAGING_READY" in MUST_NOT_CLAIM,
        ]
    )

    return {
        "package": OWNER_EXPERIENCE_INTEGRATION_CLOSEOUT_IDENTITY["package"],
        "display_title": OWNER_EXPERIENCE_INTEGRATION_CLOSEOUT_IDENTITY["display_title"],
        "decision": OWNER_EXPERIENCE_INTEGRATION_CLOSEOUT_IDENTITY["decision"],
        "closed": closed,
        "closed_gp_codes": _closed_gp_codes(),
        "closed_package_names": _closed_package_names(),
        "room_order": list(SIX_ROOM_REAL_SURFACE_ORDER),
        "accepted_rooms": list(acceptance["accepted_rooms"]),
        "blocked_rooms": list(acceptance["blocked_rooms"]),
        "registry_summary": _registry_summary_from_acceptance(acceptance),
        "integration_status": status,
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(OWNER_EXPERIENCE_NOT_AUTHORIZED),
        "release_boundary": {
            "staging_ready": False,
            "production_deploy_enabled": False,
            "render_redeployed": False,
            "owner_walkthrough_accepted": False,
            "tower_return_repaired": False,
            "broker_submission_enabled": False,
            "real_capital_movement_enabled": False,
            "direct_execution_enabled": False,
            "automated_execution_enabled": False,
            "permission_mutation_enabled": False,
            "secret_reveal_enabled": False,
            "live_auto_locked": True,
        },
        "next_build": "OB route and owner walkthrough preparation / GP010",
    }


def build_owner_experience_integration_closeout_handoff():
    bundle = build_owner_experience_integration_closeout_bundle()

    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "closed": bundle["closed"],
        "closed_gp_codes": bundle["closed_gp_codes"],
        "closed_package_names": bundle["closed_package_names"],
        "accepted_rooms": bundle["accepted_rooms"],
        "blocked_rooms": bundle["blocked_rooms"],
        "registry_summary": bundle["registry_summary"],
        "integration_status": bundle["integration_status"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "takeover_summary": (
            "GP009 closes the OB owner-experience simplification integration lane. "
            "GP001 through GP008 are recorded as closed, all six protected rooms "
            "are accepted, and the branch remains blocked from staging readiness "
            "or dangerous actions."
        ),
        "next_builder_notes": [
            "Treat GP001 through GP009 as the closed owner-experience simplification lane.",
            "Keep Tower as the owner access boundary.",
            "Keep six rooms protected behind owner session policy.",
            "Do not claim STAGING_READY.",
            "Do not redeploy Render from this package.",
            "Do not mark owner walkthrough accepted from this package.",
            "Do not claim Tower return/session continuity repaired from this package.",
            "Keep production deploy disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep direct execution disabled.",
            "Keep automated execution disabled.",
            "Keep permission mutations disabled.",
            "Keep secret reveal disabled.",
            "Keep Live Auto locked.",
            "Next build is GP010 route and owner walkthrough preparation.",
        ],
    }
