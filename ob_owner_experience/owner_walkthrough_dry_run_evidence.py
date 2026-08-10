from copy import deepcopy

from .route_owner_walkthrough_preparation import (
    build_route_owner_walkthrough_preparation_bundle,
)
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import (
    MUST_NOT_CLAIM,
    PROTECTED_ROUTE_POLICY,
    build_real_surface_adapter_contract,
)

OWNER_WALKTHROUGH_DRY_RUN_EVIDENCE_IDENTITY = {
    "package": "ob_owner_walkthrough_dry_run_evidence_gp011",
    "display_title": "Owner Walkthrough Dry-Run Evidence",
    "decision": "READY_FOR_OWNER_WALKTHROUGH_DRY_RUN_EVIDENCE_WITH_SAFETY_LOCKS_HELD",
    "plain_language": (
        "The six-room owner walkthrough has dry-run evidence prepared from the "
        "GP010 route checklist. This is evidence only. It does not start the real "
        "owner walkthrough, accept the walkthrough, repair Tower return, redeploy "
        "Render, claim staging readiness, or unlock dangerous actions."
    ),
}

OWNER_WALKTHROUGH_DRY_RUN_SCOPE = {
    "dry_run_type": "script_only_no_live_owner_session",
    "source_dependency": "GP010",
    "real_owner_session_started": False,
    "real_owner_walkthrough_started": False,
    "real_owner_walkthrough_accepted": False,
    "live_route_opened": False,
    "tower_return_repaired": False,
    "render_redeployed": False,
    "staging_ready": False,
}

OWNER_WALKTHROUGH_DRY_RUN_REQUIRED_CHECKS = [
    "prepared_by_gp010",
    "route_hint_present",
    "owner_prompt_present",
    "must_confirm_present",
    "must_not_do_present",
    "owner_session_required_confirmed",
    "anonymous_access_denied_confirmed",
    "dangerous_actions_blocked_confirmed",
    "no_staging_readiness_claimed",
    "dry_run_only",
]

OWNER_WALKTHROUGH_DRY_RUN_REQUIRED_FALSE_FLAGS = [
    "real_owner_session_started",
    "real_owner_walkthrough_started",
    "real_owner_walkthrough_accepted",
    "owner_walkthrough_started",
    "owner_walkthrough_accepted",
    "live_route_opened",
    "tower_return_repaired",
    "render_redeployed",
    "production_deploy_enabled",
    "broker_submission_enabled",
    "real_capital_movement_enabled",
    "direct_execution_enabled",
    "automated_execution_enabled",
    "permission_mutation_enabled",
    "secret_reveal_enabled",
    "staging_ready",
]

OWNER_WALKTHROUGH_DRY_RUN_REQUIRED_TRUE_FLAGS = [
    "gp010_preparation_ready",
    "dry_run_evidence_ready",
    "owner_session_required",
    "live_auto_locked",
]

OWNER_WALKTHROUGH_DRY_RUN_NOT_AUTHORIZED = [
    "STAGING_READY",
    "real owner session start",
    "owner walkthrough start",
    "owner walkthrough acceptance",
    "Tower return/session continuity repair",
    "Render redeploy",
    "production deployment",
    "broker submission",
    "real capital movement",
    "direct execution",
    "automated execution",
    "permission mutation",
    "secret reveal",
    "Live Auto unlock",
]


def _script_step_for_room(room_key, preparation_bundle):
    for step in preparation_bundle["walkthrough_script"]:
        if step["room"] == room_key:
            return step
    raise KeyError("Missing walkthrough script step for room: " + str(room_key))


def _route_record_for_room(room_key, preparation_bundle):
    for record in preparation_bundle["route_matrix"]:
        if record["room"] == room_key:
            return record
    raise KeyError("Missing route matrix record for room: " + str(room_key))


def _contains_exact(items, expected):
    return expected in list(items or [])


def _dry_run_record(room_key, preparation_bundle):
    step = _script_step_for_room(room_key, preparation_bundle)
    route = _route_record_for_room(room_key, preparation_bundle)

    checks = {
        "prepared_by_gp010": step.get("prepared") is True and route.get("ready_for_walkthrough_preparation") is True,
        "route_hint_present": bool(step.get("route_hint")) and bool(route.get("route_hint")),
        "owner_prompt_present": bool(step.get("owner_prompt")),
        "must_confirm_present": bool(step.get("must_confirm")),
        "must_not_do_present": bool(step.get("must_not_do")),
        "owner_session_required_confirmed": _contains_exact(step.get("must_confirm"), "Owner session is required."),
        "anonymous_access_denied_confirmed": _contains_exact(step.get("must_confirm"), "Anonymous access is denied."),
        "dangerous_actions_blocked_confirmed": _contains_exact(step.get("must_confirm"), "Dangerous actions are not available."),
        "no_staging_readiness_claimed": _contains_exact(step.get("must_confirm"), "No staging readiness is claimed."),
        "dry_run_only": True,
    }

    evidence_ready = all(checks[key] is True for key in OWNER_WALKTHROUGH_DRY_RUN_REQUIRED_CHECKS)

    return {
        "room": room_key,
        "step": step.get("step"),
        "display_title": step.get("display_title"),
        "route_hint": step.get("route_hint"),
        "component_hint": route.get("component_hint"),
        "data_adapter_hint": route.get("data_adapter_hint"),
        "owner_goal": step.get("owner_goal"),
        "owner_prompt": step.get("owner_prompt"),
        "dry_run_scope": deepcopy(OWNER_WALKTHROUGH_DRY_RUN_SCOPE),
        "checks": checks,
        "evidence_ready": evidence_ready,
        "actual_owner_session_started": False,
        "actual_owner_walkthrough_started": False,
        "actual_owner_walkthrough_accepted": False,
        "actual_route_opened_live": False,
    }


def build_owner_walkthrough_dry_run_evidence_matrix():
    preparation = build_route_owner_walkthrough_preparation_bundle()
    records = []

    for room_key in SIX_ROOM_REAL_SURFACE_ORDER:
        records.append(_dry_run_record(room_key, preparation))

    return records


def build_owner_walkthrough_dry_run_evidence_status():
    preparation = build_route_owner_walkthrough_preparation_bundle()
    matrix = build_owner_walkthrough_dry_run_evidence_matrix()

    all_records_ready = all(record["evidence_ready"] is True for record in matrix)

    return {
        "gp010_preparation_ready": preparation["prepared"] is True,
        "all_six_rooms_present": len(matrix) == 6,
        "all_dry_run_records_ready": all_records_ready,
        "dry_run_evidence_ready": preparation["prepared"] is True and all_records_ready,
        "real_owner_session_started": False,
        "real_owner_walkthrough_started": False,
        "real_owner_walkthrough_accepted": False,
        "owner_walkthrough_started": False,
        "owner_walkthrough_accepted": False,
        "live_route_opened": False,
        "tower_return_repaired": False,
        "render_redeployed": False,
        "production_deploy_enabled": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_execution_enabled": False,
        "automated_execution_enabled": False,
        "permission_mutation_enabled": False,
        "secret_reveal_enabled": False,
        "anonymous_access_allowed": False,
        "owner_session_required": True,
        "staging_ready": False,
        "live_auto_locked": True,
    }


def build_owner_walkthrough_dry_run_evidence_bundle():
    preparation = build_route_owner_walkthrough_preparation_bundle()
    matrix = build_owner_walkthrough_dry_run_evidence_matrix()
    status = build_owner_walkthrough_dry_run_evidence_status()
    adapter = build_real_surface_adapter_contract()

    false_flags_ok = all(
        status.get(key) is False
        for key in OWNER_WALKTHROUGH_DRY_RUN_REQUIRED_FALSE_FLAGS
    )

    true_flags_ok = all(
        status.get(key) is True
        for key in OWNER_WALKTHROUGH_DRY_RUN_REQUIRED_TRUE_FLAGS
    )

    ready = all(
        [
            preparation["prepared"] is True,
            status["dry_run_evidence_ready"] is True,
            all(record["evidence_ready"] is True for record in matrix),
            false_flags_ok,
            true_flags_ok,
            "STAGING_READY" in MUST_NOT_CLAIM,
        ]
    )

    return {
        "package": OWNER_WALKTHROUGH_DRY_RUN_EVIDENCE_IDENTITY["package"],
        "display_title": OWNER_WALKTHROUGH_DRY_RUN_EVIDENCE_IDENTITY["display_title"],
        "decision": OWNER_WALKTHROUGH_DRY_RUN_EVIDENCE_IDENTITY["decision"],
        "ready": ready,
        "source_dependency": "GP010",
        "dry_run_scope": deepcopy(OWNER_WALKTHROUGH_DRY_RUN_SCOPE),
        "room_order": list(SIX_ROOM_REAL_SURFACE_ORDER),
        "dry_run_evidence_matrix": matrix,
        "dry_run_status": status,
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(OWNER_WALKTHROUGH_DRY_RUN_NOT_AUTHORIZED),
        "release_boundary": {
            "real_owner_session_started": False,
            "real_owner_walkthrough_started": False,
            "real_owner_walkthrough_accepted": False,
            "owner_walkthrough_started": False,
            "owner_walkthrough_accepted": False,
            "live_route_opened": False,
            "tower_return_repaired": False,
            "render_redeployed": False,
            "production_deploy_enabled": False,
            "broker_submission_enabled": False,
            "real_capital_movement_enabled": False,
            "direct_execution_enabled": False,
            "automated_execution_enabled": False,
            "permission_mutation_enabled": False,
            "secret_reveal_enabled": False,
            "staging_ready": False,
            "live_auto_locked": True,
        },
        "next_build": "OB owner walkthrough controlled run gate / GP012",
    }


def build_owner_walkthrough_dry_run_evidence_handoff():
    bundle = build_owner_walkthrough_dry_run_evidence_bundle()

    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "ready": bundle["ready"],
        "source_dependency": bundle["source_dependency"],
        "dry_run_scope": bundle["dry_run_scope"],
        "room_order": bundle["room_order"],
        "dry_run_evidence_matrix": bundle["dry_run_evidence_matrix"],
        "dry_run_status": bundle["dry_run_status"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "takeover_summary": (
            "GP011 records dry-run evidence for the six-room owner walkthrough "
            "using the GP010 route checklist. It is evidence only. It does not "
            "start a real owner session, open live routes, accept the walkthrough, "
            "repair Tower return, redeploy Render, claim staging readiness, or "
            "unlock dangerous actions."
        ),
        "next_builder_notes": [
            "Treat this as dry-run evidence only.",
            "Do not start the real owner walkthrough from this package.",
            "Do not mark owner walkthrough accepted from this package.",
            "Do not claim Tower return/session continuity repaired from this package.",
            "Do not open live routes as evidence from this package.",
            "Do not redeploy Render from this package.",
            "Do not claim STAGING_READY.",
            "Keep production deploy disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep direct execution disabled.",
            "Keep automated execution disabled.",
            "Keep permission mutations disabled.",
            "Keep secret reveal disabled.",
            "Keep Live Auto locked.",
            "Next build is GP012 owner walkthrough controlled run gate.",
        ],
    }
