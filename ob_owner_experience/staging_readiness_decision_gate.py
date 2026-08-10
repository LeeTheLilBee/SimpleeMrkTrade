from copy import deepcopy
from functools import lru_cache

from .integrated_owner_walkthrough_controlled_route_check import build_integrated_owner_walkthrough_controlled_route_check_bundle
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_staging_readiness_decision_gate_gp025",
    "display_title": "Staging Readiness Decision Gate",
    "decision": "NO_GO_HOLD_STAGING_READY_NOT_CLAIMED_PENDING_ACTUAL_TOWER_ROUTE_WORK",
}

FALSE_FLAGS = [
    "staging_ready",
    "staging_readiness_granted",
    "render_redeployed",
    "production_deploy_enabled",
    "live_routes_opened",
    "controlled_route_check_executed",
    "owner_walkthrough_started",
    "owner_walkthrough_accepted",
    "tower_return_repaired",
    "broker_submission_enabled",
    "real_capital_movement_enabled",
    "direct_execution_enabled",
    "automated_execution_enabled",
    "permission_mutation_enabled",
    "secret_reveal_enabled",
]

TRUE_FLAGS = [
    "gp024_controlled_route_check_ready",
    "decision_gate_ready",
    "no_go_hold_recommended",
    "actual_tower_route_work_required",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "staging readiness granted",
    "Render redeploy",
    "production deployment",
    "live route opening",
    "controlled route check execution",
    "owner walkthrough start",
    "owner walkthrough acceptance",
    "Tower return/session continuity repair live claim",
    "broker submission",
    "real capital movement",
    "direct execution",
    "automated execution",
    "permission mutation",
    "secret reveal",
    "Live Auto unlock",
]


@lru_cache(maxsize=1)
def _gp024():
    return build_integrated_owner_walkthrough_controlled_route_check_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_staging_readiness_decision_record():
    gp024 = _gp024()
    return {
        "decision": IDENTITY["decision"],
        "recommendation": "NO_GO_HOLD",
        "reason": (
            "OB walkthrough preparation and integration contracts are ready, but "
            "actual Tower route implementation, live route verification, Tower "
            "return/session continuity repair, controlled route check execution, "
            "and owner walkthrough evidence have not occurred."
        ),
        "source_dependency": "GP024",
        "gp024_controlled_route_check_ready": gp024["controlled_route_check_ready"] is True,
        "staging_ready": False,
        "staging_readiness_granted": False,
        "actual_tower_route_work_required": True,
        "render_redeploy_required_later": True,
        "owner_controlled_walkthrough_required_later": True,
    }


def build_staging_readiness_decision_gate_status():
    gp024 = _gp024()
    return {
        "gp024_controlled_route_check_ready": gp024["controlled_route_check_ready"] is True,
        "decision_gate_ready": True,
        "no_go_hold_recommended": True,
        "actual_tower_route_work_required": True,
        "staging_ready": False,
        "staging_readiness_granted": False,
        "render_redeployed": False,
        "production_deploy_enabled": False,
        "live_routes_opened": False,
        "controlled_route_check_executed": False,
        "owner_walkthrough_started": False,
        "owner_walkthrough_accepted": False,
        "tower_return_repaired": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_execution_enabled": False,
        "automated_execution_enabled": False,
        "permission_mutation_enabled": False,
        "secret_reveal_enabled": False,
        "anonymous_access_allowed": False,
        "owner_session_required": True,
        "live_auto_locked": True,
    }


def build_staging_readiness_decision_gate_bundle():
    record = build_staging_readiness_decision_record()
    status = build_staging_readiness_decision_gate_status()
    adapter = _adapter()
    ready = (
        status["gp024_controlled_route_check_ready"] is True
        and status["decision_gate_ready"] is True
        and status["no_go_hold_recommended"] is True
        and status["actual_tower_route_work_required"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "decision_gate_ready": ready,
        "source_dependency": "GP024",
        "recommendation": "NO_GO_HOLD",
        "gate_state": "closed_pending_actual_tower_route_work",
        "decision_record": record,
        "status": status,
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {"live_auto_locked": True},
        "next_build": "Tower OB actual route implementation and return repair / GP026",
    }


def build_staging_readiness_decision_gate_handoff():
    bundle = build_staging_readiness_decision_gate_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "decision_gate_ready": bundle["decision_gate_ready"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "decision_record": bundle["decision_record"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Decision is NO_GO_HOLD for staging readiness.",
            "Do not claim STAGING_READY.",
            "Proceed next to actual Tower OB route implementation and return repair.",
            "Actual Tower route work is still required.",
            "Actual Tower return/session continuity repair is still required.",
            "Controlled route check execution is still required.",
            "Owner walkthrough evidence is still required.",
            "Do not redeploy Render from this package.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP026 Tower OB actual route implementation and return repair.",
        ],
    }
