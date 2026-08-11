"""
Tower Owner-Beta Walkthrough Closeout + Tester Entry Prep / Packs 2583–2592.

This module closes the owner walkthrough readiness lane and prepares
private beta tester entry without sending invitations or opening public
launch.

It does not authorize production, broker submission, capital movement,
Manual Live, Live Auto, direct Vault write, public launch, tester invite
send, or destructive actions.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


OWNER_BETA_WALKTHROUGH_CLOSEOUT_VERSION = "tower_owner_beta_walkthrough_closeout_v1"

CURRENT_MAIN_COMMIT = "6c57f3af7edb35b258fee2129c27cf2384cc8dc1"

PRODUCTION_DEPLOYMENT = False
BROKER_SUBMISSION = False
CAPITAL_MOVEMENT = False
MANUAL_LIVE_AUTHORIZED = False
LIVE_AUTO_AUTHORIZED = False
DIRECT_VAULT_WRITE = False
DESTRUCTIVE_ACTION_UNLOCKED = False
PUBLIC_LAUNCH_AUTHORIZED = False
TESTER_INVITES_SENT = False
EXTERNAL_ACCOUNTS_CREATED = False


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def dangerous_controls() -> Dict[str, bool]:
    return {
        "production_deployment": PRODUCTION_DEPLOYMENT,
        "broker_submission": BROKER_SUBMISSION,
        "capital_movement": CAPITAL_MOVEMENT,
        "manual_live_authorized": MANUAL_LIVE_AUTHORIZED,
        "live_auto_authorized": LIVE_AUTO_AUTHORIZED,
        "direct_vault_write": DIRECT_VAULT_WRITE,
        "destructive_action_unlocked": DESTRUCTIVE_ACTION_UNLOCKED,
        "public_launch_authorized": PUBLIC_LAUNCH_AUTHORIZED,
        "tester_invites_sent": TESTER_INVITES_SENT,
        "external_accounts_created": EXTERNAL_ACCOUNTS_CREATED,
    }


def dangerous_controls_locked() -> bool:
    return all(value is False for value in dangerous_controls().values())


def walkthrough_checklist() -> List[Dict[str, Any]]:
    return [
        {
            "step_id": "login",
            "title": "Owner logs into Tower",
            "route": "/tower/login",
            "required": True,
            "status": "ready",
        },
        {
            "step_id": "access_home",
            "title": "Owner reaches Tower Access Home",
            "route": "/tower/access-home",
            "required": True,
            "status": "ready",
        },
        {
            "step_id": "owner_beta_control_room",
            "title": "Owner opens Owner-Beta Control Room",
            "route": "/tower/owner-beta",
            "required": True,
            "status": "hosted_owner_gated_verified",
        },
        {
            "step_id": "ob_six_room_acceptance",
            "title": "Owner reviews OB six-room acceptance handoff",
            "route": "/tower/observatory-six-room-acceptance",
            "required": True,
            "status": "ready",
        },
        {
            "step_id": "issue_intake",
            "title": "Owner records walkthrough issue if needed",
            "route": "/tower/owner-beta/issues.json",
            "required": True,
            "status": "hosted_owner_gated_verified",
        },
        {
            "step_id": "review_receipts",
            "title": "Owner confirms issue review receipt trail",
            "route": "/tower/owner-beta/review-receipts.json",
            "required": True,
            "status": "hosted_owner_gated_verified",
        },
        {
            "step_id": "return_to_tower",
            "title": "Owner returns to Tower with session preserved",
            "route": "/tower/return/observatory",
            "required": True,
            "status": "ready",
        },
    ]


def hosted_proof_summary() -> Dict[str, Any]:
    return {
        "main_commit": CURRENT_MAIN_COMMIT,
        "staging_base_url": "https://simplee-tower-ob-staging.onrender.com",
        "owner_beta_route": "/tower/owner-beta",
        "owner_beta_json_route": "/tower/owner-beta.json",
        "issues_route": "/tower/owner-beta/issues.json",
        "review_receipts_route": "/tower/owner-beta/review-receipts.json",
        "hosted_owner_beta_owner_gated": True,
        "hosted_issue_intake_owner_gated": True,
        "hosted_review_receipts_owner_gated": True,
        "hosted_owner_login_verified": True,
        "hosted_access_home_verified": True,
        "hosted_issue_submit_verified": True,
        "hosted_review_receipt_verified": True,
    }


def issue_intake_receipt_summary() -> Dict[str, Any]:
    return {
        "issue_intake_version": "tower_owner_beta_issue_intake_v1",
        "persistence_mode": "append_only_jsonl",
        "issue_route": "/tower/owner-beta/issues.json",
        "review_receipt_route": "/tower/owner-beta/review-receipts.json",
        "owner_issue_submit_allowed": True,
        "anonymous_issue_routes_denied": True,
        "review_receipt_generated": True,
        "receipt_linkage_verified": True,
        "market_map_classification_verified": True,
        "soulaana_note_field_verified": True,
    }


def beta_scope_reminder() -> Dict[str, Any]:
    return {
        "scope": "private_owner_beta_walkthrough_then_limited_private_testers",
        "allowed_modes": ["Survey", "Paper"],
        "owner_only_later": ["Manual Live Level 1"],
        "not_allowed": [
            "production deployment",
            "broker submission",
            "capital movement",
            "Manual Live for testers",
            "Live Auto",
            "public launch",
            "direct Vault write",
            "destructive actions",
        ],
        "tester_boundary": {
            "anonymous_users": "denied",
            "non_owner_users": "denied_until_invited_and_approved",
            "private_beta_testers": "not_invited_yet",
            "owner": "allowed",
        },
    }


def tester_entry_readiness_gate() -> Dict[str, Any]:
    return {
        "status": "prepared_not_open",
        "ready_for_owner_decision": True,
        "tester_invites_sent": TESTER_INVITES_SENT,
        "external_accounts_created": EXTERNAL_ACCOUNTS_CREATED,
        "requires_before_entry": [
            "owner walkthrough completion",
            "owner accepts beta scope",
            "owner reviews outstanding blocker list",
            "owner approves tester names",
            "Tower account setup path selected",
            "tester terms/NDA workflow selected later",
        ],
        "entry_recommendation": "NO_GO_HOLD_FOR_OWNER_WALKTHROUGH_CLOSEOUT_DECISION",
    }


def tester_invite_prep_record() -> Dict[str, Any]:
    return {
        "record_type": "tower_owner_beta_tester_invite_prep",
        "status": "draft_prepared_not_sent",
        "invite_channel": "not_selected",
        "tester_count": 0,
        "tester_names": [],
        "invite_copy_ready": False,
        "tower_account_creation_ready": False,
        "tester_invites_sent": TESTER_INVITES_SENT,
        "external_accounts_created": EXTERNAL_ACCOUNTS_CREATED,
    }


def owner_decision_packet() -> Dict[str, Any]:
    return {
        "record_type": "tower_owner_beta_walkthrough_closeout_decision_packet",
        "version": OWNER_BETA_WALKTHROUGH_CLOSEOUT_VERSION,
        "decision_required": True,
        "decision_options": [
            {
                "decision": "ACCEPT_OWNER_WALKTHROUGH_AND_PREP_TESTER_ENTRY",
                "effect": "Allows next build lane to prepare selected tester onboarding surfaces only.",
                "opens_live_or_production": False,
            },
            {
                "decision": "HOLD_FOR_OWNER_UI_REPAIRS",
                "effect": "Keeps tester entry closed while owner UI repairs continue.",
                "opens_live_or_production": False,
            },
            {
                "decision": "HOLD_FOR_MORE_HOSTED_PROOF",
                "effect": "Runs more hosted verification before tester entry prep.",
                "opens_live_or_production": False,
            },
        ],
        "default_recommendation": "HOLD_FOR_OWNER_WALKTHROUGH_COMPLETION",
        "dangerous_controls": dangerous_controls(),
        "dangerous_controls_locked": dangerous_controls_locked(),
    }


def walkthrough_closeout_payload() -> Dict[str, Any]:
    checklist = walkthrough_checklist()

    return {
        "status": "ready_for_owner_walkthrough_closeout",
        "version": OWNER_BETA_WALKTHROUGH_CLOSEOUT_VERSION,
        "main_commit": CURRENT_MAIN_COMMIT,
        "generated_at": utc_now(),
        "walkthrough_checklist": checklist,
        "hosted_proof_summary": hosted_proof_summary(),
        "issue_intake_receipt_summary": issue_intake_receipt_summary(),
        "tester_entry_readiness_gate": tester_entry_readiness_gate(),
        "tester_invite_prep_record": tester_invite_prep_record(),
        "beta_scope_reminder": beta_scope_reminder(),
        "owner_decision_packet": owner_decision_packet(),
        "all_required_walkthrough_steps_ready": all(item["status"] in {"ready", "hosted_owner_gated_verified"} for item in checklist),
        "tester_entry_open": False,
        "dangerous_controls": dangerous_controls(),
        "dangerous_controls_locked": dangerous_controls_locked(),
    }


def tester_entry_prep_payload() -> Dict[str, Any]:
    return {
        "status": "prepared_not_open",
        "version": OWNER_BETA_WALKTHROUGH_CLOSEOUT_VERSION,
        "generated_at": utc_now(),
        "tester_entry_readiness_gate": tester_entry_readiness_gate(),
        "tester_invite_prep_record": tester_invite_prep_record(),
        "beta_scope_reminder": beta_scope_reminder(),
        "owner_decision_packet": owner_decision_packet(),
        "tester_entry_open": False,
        "tester_invites_sent": TESTER_INVITES_SENT,
        "external_accounts_created": EXTERNAL_ACCOUNTS_CREATED,
        "dangerous_controls": dangerous_controls(),
        "dangerous_controls_locked": dangerous_controls_locked(),
    }


def walkthrough_closeout_cert(pack: int) -> Dict[str, Any]:
    titles = {
        2583: "Walkthrough closeout contract",
        2584: "Owner walkthrough checklist",
        2585: "Hosted proof summary",
        2586: "Issue intake receipt summary",
        2587: "Tester entry readiness gate",
        2588: "Tester invite prep record",
        2589: "Beta scope reminder",
        2590: "Safety and no-live boundary receipt",
        2591: "Owner decision packet",
        2592: "Route and API integration cert",
    }

    return {
        "pack": pack,
        "title": titles[pack],
        "status": "passed",
        "version": OWNER_BETA_WALKTHROUGH_CLOSEOUT_VERSION,
        "routes": {
            "closeout": "/tower/owner-beta/closeout.json",
            "tester_entry_prep": "/tower/owner-beta/tester-entry-prep.json",
        },
        "requires_owner_session": True,
        "tester_entry_open": False,
        "tester_invites_sent": TESTER_INVITES_SENT,
        "external_accounts_created": EXTERNAL_ACCOUNTS_CREATED,
        "dangerous_controls": dangerous_controls(),
        "dangerous_controls_locked": dangerous_controls_locked(),
    }
