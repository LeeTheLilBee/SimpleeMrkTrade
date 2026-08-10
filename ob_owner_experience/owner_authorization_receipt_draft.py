from copy import deepcopy

from .owner_authorization_decision_recording_gate import build_owner_authorization_decision_recording_gate_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

OWNER_AUTHORIZATION_RECEIPT_DRAFT_IDENTITY = {
    "package": "ob_owner_authorization_receipt_draft_gp015",
    "display_title": "Owner Authorization Receipt Draft",
    "decision": "READY_FOR_OWNER_AUTHORIZATION_RECEIPT_DRAFT_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "owner_authorization_granted",
    "authorization_packet_signed",
    "authorization_decision_recorded",
    "decision_receipt_emitted",
    "receipt_finalized",
    "controlled_run_gate_open",
    "controlled_run_authorized",
    "controlled_run_started",
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

TRUE_FLAGS = [
    "gp014_decision_recording_gate_prepared",
    "receipt_draft_prepared",
    "receipt_is_draft_only",
    "append_only_required",
    "redaction_required",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "owner authorization granted",
    "authorization packet signed",
    "authorization decision recorded",
    "decision receipt emitted",
    "receipt finalized",
    "controlled-run gate opening",
    "controlled run authorization",
    "controlled run start",
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


def build_owner_authorization_receipt_draft():
    gp014 = build_owner_authorization_decision_recording_gate_bundle()
    return {
        "receipt_type": "owner_authorization_receipt_draft",
        "source_dependency": "GP014",
        "draft_only": True,
        "final": False,
        "emitted": False,
        "append_only_required": True,
        "redaction_required": True,
        "secret_values_forbidden": True,
        "broker_payload_forbidden": True,
        "money_movement_forbidden": True,
        "decision_record_schema": deepcopy(gp014["decision_record_schema"]),
        "candidate_decision_values": deepcopy(gp014["decision_candidate_values"]),
        "room_scope": deepcopy(gp014["room_scope"]),
        "required_acknowledgements": [
            "Receipt is a draft only.",
            "No owner authorization is granted.",
            "No authorization decision is recorded.",
            "No decision receipt is emitted.",
            "Controlled-run gate remains closed.",
            "Owner walkthrough has not started.",
            "Owner walkthrough has not been accepted.",
            "STAGING_READY is not claimed.",
            "Broker submission remains locked.",
            "Real capital movement remains locked.",
            "Live Auto remains locked.",
        ],
    }


def build_owner_authorization_receipt_draft_status():
    gp014 = build_owner_authorization_decision_recording_gate_bundle()
    draft = build_owner_authorization_receipt_draft()
    all_rooms = (
        len(draft["room_scope"]) == 6
        and [item["room"] for item in draft["room_scope"]] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    )
    return {
        "gp014_decision_recording_gate_prepared": gp014["gate_prepared"] is True,
        "receipt_draft_prepared": True,
        "receipt_is_draft_only": True,
        "append_only_required": True,
        "redaction_required": True,
        "all_six_rooms_scoped": all_rooms,
        "owner_authorization_granted": False,
        "authorization_packet_signed": False,
        "authorization_decision_recorded": False,
        "decision_receipt_emitted": False,
        "receipt_finalized": False,
        "controlled_run_gate_open": False,
        "controlled_run_authorized": False,
        "controlled_run_started": False,
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


def build_owner_authorization_receipt_draft_bundle():
    status = build_owner_authorization_receipt_draft_status()
    draft = build_owner_authorization_receipt_draft()
    adapter = build_real_surface_adapter_contract()
    draft_prepared = (
        status["gp014_decision_recording_gate_prepared"] is True
        and status["receipt_draft_prepared"] is True
        and status["receipt_is_draft_only"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": OWNER_AUTHORIZATION_RECEIPT_DRAFT_IDENTITY["package"],
        "display_title": OWNER_AUTHORIZATION_RECEIPT_DRAFT_IDENTITY["display_title"],
        "decision": OWNER_AUTHORIZATION_RECEIPT_DRAFT_IDENTITY["decision"],
        "draft_prepared": draft_prepared,
        "source_dependency": "GP014",
        "receipt_draft": draft,
        "room_scope": draft["room_scope"],
        "status": status,
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {"live_auto_locked": True},
        "next_build": "OB Owner Authorization Decision Receipt Gate / GP016",
    }


def build_owner_authorization_receipt_draft_handoff():
    bundle = build_owner_authorization_receipt_draft_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "draft_prepared": bundle["draft_prepared"],
        "source_dependency": bundle["source_dependency"],
        "receipt_draft": bundle["receipt_draft"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Treat this as receipt draft only.",
            "Do not emit a receipt from this package.",
            "Do not record authorization from this package.",
            "Do not open the controlled-run gate.",
            "Do not start or accept the owner walkthrough.",
            "Do not claim STAGING_READY.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP016 owner authorization decision receipt gate.",
        ],
    }
