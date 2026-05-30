# =============================================================================
# THE TOWER — STATUS SUMMARY
# FILE: tower/tower_status.py
# =============================================================================

from typing import Any, Dict

from tower.audit import get_audit_summary, verify_audit_chain
from tower.security_events import get_security_summary
from tower.user_store import list_users
from tower.evidence_capsules import get_evidence_summary
from tower.export_vault import get_export_summary
from tower.admin_action_gate import get_admin_action_summary
from tower.step_up import get_step_up_summary
from tower.security_inbox import get_security_inbox_summary, get_security_review_queue_summary, get_security_inbox_action_summary


def _pack032_base_get_tower_status() -> Dict[str, Any]:
    """
    Gives The Tower dashboard-friendly numbers.

    Baby version:
    This counts users, locked users, open security alerts, and audit health.
    """

    users = list_users()
    audit = get_audit_summary()
    security = get_security_summary()
    evidence = get_evidence_summary()
    export_summary = get_export_summary()
    admin_actions = get_admin_action_summary()
    step_up = get_step_up_summary()
    security_inbox = get_security_inbox_summary()
    security_review_queue = get_security_review_queue_summary()
    security_inbox_actions = get_security_inbox_action_summary()
    chain = verify_audit_chain()

    status_counts = {}
    role_counts = {}
    account_type_counts = {}

    for user in users:
        user_status = user.get("status", "unknown")
        role = user.get("role", "unknown")
        account_type = user.get("account_type", "unknown")

        status_counts[user_status] = status_counts.get(user_status, 0) + 1
        role_counts[role] = role_counts.get(role, 0) + 1
        account_type_counts[account_type] = account_type_counts.get(account_type, 0) + 1

    return {
        "tower_name": "The Tower",
        "control_identity": "control_tower_security_command_center",
        "total_users": len(users),
        "user_status_counts": status_counts,
        "role_counts": role_counts,
        "account_type_counts": account_type_counts,
        "audit_chain_ok": chain.get("ok"),
        "audit_total_events": audit.get("total_events"),
        "audit_high_risk_events": audit.get("high_risk_events"),
        "security_total_events": security.get("total_security_events"),
        "security_open_events": security.get("open"),
        "security_critical_events": security.get("critical"),
        "security_high_events": security.get("high"),
        "evidence_total_capsules": evidence.get("total_capsules"),
        "evidence_open_capsules": evidence.get("open"),
        "evidence_closed_capsules": evidence.get("closed"),
        "export_total_exports": export_summary.get("total_exports"),
        "export_approved": export_summary.get("approved"),
        "export_denied": export_summary.get("denied"),
        "export_step_up_required": export_summary.get("step_up_required"),
        "export_revoked": export_summary.get("revoked"),
        "admin_action_total": admin_actions.get("total_admin_actions"),
        "admin_action_approved": admin_actions.get("approved"),
        "admin_action_step_up_required": admin_actions.get("step_up_required"),
        "admin_action_executed": admin_actions.get("executed"),
        "admin_action_revoked": admin_actions.get("revoked"),
        "step_up_total": step_up.get("total_step_up_challenges"),
        "step_up_pending": step_up.get("pending"),
        "step_up_approved": step_up.get("approved"),
        "step_up_used": step_up.get("used"),
        "step_up_expired": step_up.get("expired"),
        "security_inbox_total": security_inbox.get("total_inbox_items"),
        "security_inbox_open": security_inbox.get("open"),
        "security_inbox_reviewing": security_inbox.get("reviewing"),
        "security_inbox_resolved": security_inbox.get("resolved"),
        "security_inbox_critical": security_inbox.get("critical"),
        "security_inbox_high": security_inbox.get("high"),
        "security_review_groups": security_review_queue.get("total_review_groups"),
        "security_review_urgent_groups": security_review_queue.get("urgent"),
        "security_review_high_groups": security_review_queue.get("high"),
        "security_review_largest_group": security_review_queue.get("largest_group_size"),
        "security_inbox_items_with_notes": security_inbox_actions.get("with_review_notes"),
        "security_inbox_escalated": security_inbox_actions.get("escalated"),
        "security_inbox_quarantine_requested": security_inbox_actions.get("quarantine_requested"),
        "security_inbox_step_up_requested": security_inbox_actions.get("step_up_requested"),
        "apps_seen_in_audit": audit.get("apps", {}),
        "risk_states_seen_in_audit": audit.get("risk_states", {}),
    }


# ================================================================================
# PACK032_DOOR_AUDIT_STATUS_ENRICHMENT
# ================================================================================
def _pack032_load_door_swipe_status_summary():
    try:
        from tower.door_audit_capsules import summarize_door_swipe_audit_capsules
        summary = summarize_door_swipe_audit_capsules(limit=6)
        if not isinstance(summary, dict):
            return {
                "door_swipe_audit_ok": False,
                "door_swipe_audit_reason": "bad_summary_payload",
            }

        recent = summary.get("last", [])
        if not isinstance(recent, list):
            recent = []

        return {
            "door_swipe_audit_ok": bool(summary.get("ok")),
            "door_swipe_audit_total": int(summary.get("total", 0) or 0),
            "door_swipe_audit_allowed": int(summary.get("allowed", 0) or 0),
            "door_swipe_audit_denied": int(summary.get("denied", 0) or 0),
            "door_swipe_audit_surfaced": int(summary.get("surfaced", 0) or 0),
            "door_swipe_audit_by_reason": summary.get("by_reason", {}) if isinstance(summary.get("by_reason"), dict) else {},
            "door_swipe_audit_by_door": summary.get("by_door", {}) if isinstance(summary.get("by_door"), dict) else {},
            "door_swipe_audit_recent": recent,
            "door_swipe_audit_path": summary.get("path"),
        }
    except Exception as exc:
        return {
            "door_swipe_audit_ok": False,
            "door_swipe_audit_reason": f"{type(exc).__name__}: {exc}",
            "door_swipe_audit_total": 0,
            "door_swipe_audit_allowed": 0,
            "door_swipe_audit_denied": 0,
            "door_swipe_audit_surfaced": 0,
            "door_swipe_audit_recent": [],
        }


def get_tower_status(*args, **kwargs):
    payload = _pack032_base_get_tower_status(*args, **kwargs)
    if not isinstance(payload, dict):
        payload = {
            "ok": False,
            "tower_name": "The Tower",
            "reason_code": "tower_status_bad_payload",
            "human_reason": "Base Tower status returned a non-dict payload.",
        }

    payload.update(_pack032_load_door_swipe_status_summary())
    payload.update(_pack034_load_door_swipe_security_inbox_summary())
    return payload


# ================================================================================
# PACK034_DOOR_SECURITY_INBOX_STATUS_ENRICHMENT
# ================================================================================
def _pack034_load_door_swipe_security_inbox_summary():
    try:
        from tower.door_audit_capsules import summarize_door_swipe_security_inbox
        summary = summarize_door_swipe_security_inbox(limit=6)
        if not isinstance(summary, dict):
            return {
                "door_swipe_security_inbox_ok": False,
                "door_swipe_security_inbox_reason": "bad_summary_payload",
            }

        recent = summary.get("last", [])
        if not isinstance(recent, list):
            recent = []

        return {
            "door_swipe_security_inbox_ok": bool(summary.get("ok")),
            "door_swipe_security_inbox_total": int(summary.get("total", 0) or 0),
            "door_swipe_security_inbox_open": int(summary.get("open", 0) or 0),
            "door_swipe_security_inbox_by_status": summary.get("by_status", {}) if isinstance(summary.get("by_status"), dict) else {},
            "door_swipe_security_inbox_by_severity": summary.get("by_severity", {}) if isinstance(summary.get("by_severity"), dict) else {},
            "door_swipe_security_inbox_by_reason": summary.get("by_reason", {}) if isinstance(summary.get("by_reason"), dict) else {},
            "door_swipe_security_inbox_recent": recent,
            "door_swipe_security_inbox_path": summary.get("path"),
        }
    except Exception as exc:
        return {
            "door_swipe_security_inbox_ok": False,
            "door_swipe_security_inbox_reason": f"{type(exc).__name__}: {exc}",
            "door_swipe_security_inbox_total": 0,
            "door_swipe_security_inbox_open": 0,
            "door_swipe_security_inbox_recent": [],
        }



# ================================================================================
# PACK057_OBJECT_AUDIT_STATUS_WRAPPER
# ================================================================================
# Adds OB object audit capsule totals to get_tower_status() without rewriting the
# original status function shape.
# ================================================================================

def _pack057_get_object_audit_status_fields():
    try:
        from tower.ob_object_audit_capsules import summarize_ob_object_audit_capsules

        summary = summarize_ob_object_audit_capsules(limit=8)
        return {
            "ob_object_audit_ok": bool(summary.get("ok")),
            "ob_object_audit_total": int(summary.get("total", 0) or 0),
            "ob_object_audit_allowed": int(summary.get("allowed", 0) or 0),
            "ob_object_audit_denied": int(summary.get("denied", 0) or 0),
            "ob_object_audit_by_reason": summary.get("by_reason", {}),
            "ob_object_audit_by_object_type": summary.get("by_object_type", {}),
            "ob_object_audit_by_severity": summary.get("by_severity", {}),
            "ob_object_audit_recent": summary.get("recent", []),
            "ob_object_audit_human_reason": summary.get("human_reason", ""),
            "ob_object_audit_soulaana": summary.get("soulaana_translation", ""),
        }
    except Exception as exc:
        return {
            "ob_object_audit_ok": False,
            "ob_object_audit_error": f"{type(exc).__name__}: {exc}",
            "ob_object_audit_total": 0,
            "ob_object_audit_allowed": 0,
            "ob_object_audit_denied": 0,
            "ob_object_audit_by_reason": {},
            "ob_object_audit_by_object_type": {},
            "ob_object_audit_by_severity": {},
            "ob_object_audit_recent": [],
        }


try:
    _pack057_original_get_tower_status
except NameError:
    _pack057_original_get_tower_status = get_tower_status


def get_tower_status(*args, **kwargs):
    status = _pack057_original_get_tower_status(*args, **kwargs)

    if not isinstance(status, dict):
        status = {
            "ok": False,
            "tower_status_original_type": str(type(status).__name__),
            "tower_status_original_value": str(status),
        }

    try:
        status.update(_pack057_get_object_audit_status_fields())
    except Exception as exc:
        status["ob_object_audit_ok"] = False
        status["ob_object_audit_error"] = str(exc)

    return status



# ================================================================================
# PACK059_OBJECT_SECURITY_INBOX_STATUS_WRAPPER
# ================================================================================
# Adds OB object security inbox totals to get_tower_status().
# ================================================================================

def _pack059_get_object_security_inbox_status_fields():
    try:
        from tower.ob_object_audit_capsules import summarize_ob_object_security_inbox

        summary = summarize_ob_object_security_inbox(limit=8)
        return {
            "ob_object_security_inbox_ok": bool(summary.get("ok")),
            "ob_object_security_inbox_total": int(summary.get("total", 0) or 0),
            "ob_object_security_inbox_open": int(summary.get("open", 0) or 0),
            "ob_object_security_inbox_by_status": summary.get("by_status", {}),
            "ob_object_security_inbox_by_reason": summary.get("by_reason", {}),
            "ob_object_security_inbox_by_severity": summary.get("by_severity", {}),
            "ob_object_security_inbox_by_object_type": summary.get("by_object_type", {}),
            "ob_object_security_inbox_recent": summary.get("recent", []),
            "ob_object_security_inbox_human_reason": summary.get("human_reason", ""),
            "ob_object_security_inbox_soulaana": summary.get("soulaana_translation", ""),
        }
    except Exception as exc:
        return {
            "ob_object_security_inbox_ok": False,
            "ob_object_security_inbox_error": f"{type(exc).__name__}: {exc}",
            "ob_object_security_inbox_total": 0,
            "ob_object_security_inbox_open": 0,
            "ob_object_security_inbox_by_status": {},
            "ob_object_security_inbox_by_reason": {},
            "ob_object_security_inbox_by_severity": {},
            "ob_object_security_inbox_by_object_type": {},
            "ob_object_security_inbox_recent": [],
        }


try:
    _pack059_original_get_tower_status
except NameError:
    _pack059_original_get_tower_status = get_tower_status


def get_tower_status(*args, **kwargs):
    status = _pack059_original_get_tower_status(*args, **kwargs)

    if not isinstance(status, dict):
        status = {
            "ok": False,
            "tower_status_original_type": str(type(status).__name__),
            "tower_status_original_value": str(status),
        }

    try:
        status.update(_pack059_get_object_security_inbox_status_fields())
    except Exception as exc:
        status["ob_object_security_inbox_ok"] = False
        status["ob_object_security_inbox_error"] = str(exc)

    return status



# ================================================================================
# PACK074_ARCHIVE_VAULT_HANDOFF_STATUS_WRAPPER
# ================================================================================
# Adds Archive Vault handoff queue summary fields to Tower status.
# ================================================================================

try:
    _pack074_original_get_tower_status
except NameError:
    _pack074_original_get_tower_status = get_tower_status


def get_tower_status():
    payload = _pack074_original_get_tower_status()
    if not isinstance(payload, dict):
        payload = {}

    try:
        from tower.archive_vault_handoff import summarize_archive_vault_handoffs

        summary = summarize_archive_vault_handoffs(limit=8)

        payload["archive_vault_handoff_ok"] = summary.get("ok") is True
        payload["archive_vault_handoff_total"] = summary.get("total", 0)
        payload["archive_vault_handoff_queued"] = summary.get("queued", 0)
        payload["archive_vault_handoff_by_status"] = summary.get("by_status", {})
        payload["archive_vault_handoff_by_source_type"] = summary.get("by_source_type", {})
        payload["archive_vault_handoff_by_severity"] = summary.get("by_severity", {})
        payload["archive_vault_handoff_recent"] = summary.get("recent", [])
        payload["archive_vault_handoff_human_reason"] = summary.get("human_reason")
        payload["archive_vault_handoff_soulaana_translation"] = summary.get("soulaana_translation")

    except Exception as exc:
        payload["archive_vault_handoff_ok"] = False
        payload["archive_vault_handoff_error"] = f"{type(exc).__name__}: {exc}"

    return payload



# ================================================================================
# PACK077_UI_ACTION_AUDIT_STATUS_WRAPPER
# ================================================================================
# Adds UI action audit receipt summary fields to Tower status.
# ================================================================================

try:
    _pack077_original_get_tower_status
except NameError:
    _pack077_original_get_tower_status = get_tower_status


def get_tower_status():
    payload = _pack077_original_get_tower_status()
    if not isinstance(payload, dict):
        payload = {}

    try:
        from tower.ui_action_audit import summarize_ui_action_audit_receipts

        summary = summarize_ui_action_audit_receipts(limit=8)

        payload["ui_action_audit_ok"] = summary.get("ok") is True
        payload["ui_action_audit_total"] = summary.get("total", 0)
        payload["ui_action_audit_action_ok"] = summary.get("action_ok", 0)
        payload["ui_action_audit_action_failed"] = summary.get("action_failed", 0)
        payload["ui_action_audit_by_action"] = summary.get("by_action", {})
        payload["ui_action_audit_by_reason"] = summary.get("by_reason", {})
        payload["ui_action_audit_by_severity"] = summary.get("by_severity", {})
        payload["ui_action_audit_by_status_code"] = summary.get("by_status_code", {})
        payload["ui_action_audit_recent"] = summary.get("recent", [])
        payload["ui_action_audit_human_reason"] = summary.get("human_reason")
        payload["ui_action_audit_soulaana_translation"] = summary.get("soulaana_translation")

    except Exception as exc:
        payload["ui_action_audit_ok"] = False
        payload["ui_action_audit_error"] = f"{type(exc).__name__}: {exc}"

    return payload



# ================================================================================
# PACK087_EXPOSURE_MAPPING_STATUS_WRAPPER
# ================================================================================
# Adds OB exposure mapping pass summary fields to Tower status.
# ================================================================================

try:
    _pack087_original_get_tower_status
except NameError:
    _pack087_original_get_tower_status = get_tower_status


def get_tower_status():
    payload = _pack087_original_get_tower_status()
    if not isinstance(payload, dict):
        payload = {}

    try:
        from tower.ob_exposure_mapping import (
            build_ob_exposure_mapping_pass,
            summarize_ob_exposure_mapping_pass,
        )

        # Rebuild before summarizing so the panel reflects current Flask/routes.
        mapping = build_ob_exposure_mapping_pass()
        summary = summarize_ob_exposure_mapping_pass(limit=12)

        payload["ob_exposure_mapping_ok"] = summary.get("ok") is True
        payload["ob_exposure_mapping_total"] = summary.get("total", 0)
        payload["ob_exposure_mapping_counts"] = summary.get("counts", {})
        payload["ob_exposure_mapping_reason_counts"] = summary.get("reason_counts", {})
        payload["ob_exposure_mapping_priority_counts"] = summary.get("priority_counts", {})
        payload["ob_exposure_mapping_top_next"] = summary.get("top_next", [])
        payload["ob_exposure_mapping_retire_or_redirect"] = summary.get("retire_or_redirect", [])
        payload["ob_exposure_mapping_later_review"] = summary.get("later_review", [])
        payload["ob_exposure_mapping_readiness_label"] = summary.get("readiness_label")
        payload["ob_exposure_mapping_readiness_score"] = summary.get("readiness_score")
        payload["ob_exposure_mapping_human_reason"] = summary.get("human_reason")
        payload["ob_exposure_mapping_soulaana_translation"] = summary.get("soulaana_translation")
        payload["ob_exposure_mapping_file_path"] = mapping.get("path")

    except Exception as exc:
        payload["ob_exposure_mapping_ok"] = False
        payload["ob_exposure_mapping_error"] = f"{type(exc).__name__}: {exc}"

    return payload



# ================================================================================
# PACK088B_FINAL_REPLACEMENT_EXPOSURE_STATUS_WRAPPER
# ================================================================================
# Guarantees final Tower status includes BOTH:
# - deny-path replacement receipt summary
# - OB exposure mapping summary
# regardless of earlier wrapper order.
# ================================================================================

try:
    _pack088b_original_get_tower_status
except NameError:
    _pack088b_original_get_tower_status = get_tower_status


def get_tower_status():
    payload = _pack088b_original_get_tower_status()
    if not isinstance(payload, dict):
        payload = {}

    # Deny-path replacement receipt fields.
    try:
        from tower.deny_path_replacement_audit import summarize_deny_path_replacement_receipts

        deny_summary = summarize_deny_path_replacement_receipts(limit=8)

        payload["deny_path_replacement_ok"] = deny_summary.get("ok") is True
        payload["deny_path_replacement_total"] = deny_summary.get("total", 0)
        payload["deny_path_replacement_verified"] = deny_summary.get("verified", 0)
        payload["deny_path_replacement_needs_review"] = deny_summary.get("needs_review", 0)
        payload["deny_path_replacement_by_status"] = deny_summary.get("by_status", {})
        payload["deny_path_replacement_by_route"] = deny_summary.get("by_route", {})
        payload["deny_path_replacement_by_type"] = deny_summary.get("by_replacement_type", {})
        payload["deny_path_replacement_by_severity"] = deny_summary.get("by_severity", {})
        payload["deny_path_replacement_recent"] = deny_summary.get("recent", [])
        payload["deny_path_replacement_human_reason"] = deny_summary.get("human_reason")
        payload["deny_path_replacement_soulaana_translation"] = deny_summary.get("soulaana_translation")
    except Exception as exc:
        payload["deny_path_replacement_ok"] = False
        payload["deny_path_replacement_error"] = f"{type(exc).__name__}: {exc}"

    # OB exposure mapping fields.
    try:
        from tower.ob_exposure_mapping import (
            build_ob_exposure_mapping_pass,
            summarize_ob_exposure_mapping_pass,
        )

        mapping = build_ob_exposure_mapping_pass()
        exposure_summary = summarize_ob_exposure_mapping_pass(limit=12)

        payload["ob_exposure_mapping_ok"] = exposure_summary.get("ok") is True
        payload["ob_exposure_mapping_total"] = exposure_summary.get("total", 0)
        payload["ob_exposure_mapping_counts"] = exposure_summary.get("counts", {})
        payload["ob_exposure_mapping_reason_counts"] = exposure_summary.get("reason_counts", {})
        payload["ob_exposure_mapping_priority_counts"] = exposure_summary.get("priority_counts", {})
        payload["ob_exposure_mapping_top_next"] = exposure_summary.get("top_next", [])
        payload["ob_exposure_mapping_retire_or_redirect"] = exposure_summary.get("retire_or_redirect", [])
        payload["ob_exposure_mapping_later_review"] = exposure_summary.get("later_review", [])
        payload["ob_exposure_mapping_readiness_label"] = exposure_summary.get("readiness_label")
        payload["ob_exposure_mapping_readiness_score"] = exposure_summary.get("readiness_score")
        payload["ob_exposure_mapping_human_reason"] = exposure_summary.get("human_reason")
        payload["ob_exposure_mapping_soulaana_translation"] = exposure_summary.get("soulaana_translation")
        payload["ob_exposure_mapping_file_path"] = mapping.get("path")
    except Exception as exc:
        payload["ob_exposure_mapping_ok"] = False
        payload["ob_exposure_mapping_error"] = f"{type(exc).__name__}: {exc}"

    return payload



# ================================================================================
# PACK112_OBJECT_PERMISSION_VISIBILITY_STATUS_BRIDGE
# ================================================================================

def pack112_object_permission_visibility_status_bridge():
    try:
        from tower.ob_object_permission_visibility import object_permission_visibility_status_card
        return object_permission_visibility_status_card()
    except Exception as exc:
        return {
            "ok": False,
            "pack": "112",
            "title": "OB Object Permissions",
            "reason_code": "object_permission_visibility_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Object permission visibility status could not be loaded.",
        }

# ================================================================================
# END PACK112_OBJECT_PERMISSION_VISIBILITY_STATUS_BRIDGE
# ================================================================================



# ================================================================================
# PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_STATUS_BRIDGE
# ================================================================================

def pack115_security_command_navigation_links_status_bridge():
    try:
        from tower.security_command_navigation_links import security_command_navigation_links_status_card
        return security_command_navigation_links_status_card()
    except Exception as exc:
        return {
            "ok": False,
            "pack": "115",
            "title": "Security Command Links",
            "reason_code": "security_command_navigation_links_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Security Command navigation links could not be loaded.",
        }

# ================================================================================
# END PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_STATUS_BRIDGE
# ================================================================================



# ================================================================================
# PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_STATUS_BRIDGE
# ================================================================================

def pack117_security_command_preferred_destination_status_bridge():
    try:
        from tower.security_command_preferred_destination import security_command_preferred_destination_status_card
        return security_command_preferred_destination_status_card()
    except Exception as exc:
        return {
            "ok": False,
            "pack": "117",
            "title": "Preferred Security Command",
            "reason_code": "preferred_security_command_destination_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Preferred Security Command destination status could not be loaded.",
        }

# ================================================================================
# END PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_STATUS_BRIDGE
# ================================================================================



# ================================================================================
# PACK119_OWNER_QUICK_ACTIONS_STATUS_BRIDGE
# ================================================================================

def pack119_owner_quick_actions_status_bridge():
    try:
        from tower.security_command_owner_quick_actions import owner_quick_actions_status_card
        return owner_quick_actions_status_card()
    except Exception as exc:
        return {
            "ok": False,
            "pack": "119",
            "title": "Owner Quick Actions",
            "reason_code": "owner_quick_actions_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Owner quick actions could not be loaded.",
        }

# ================================================================================
# END PACK119_OWNER_QUICK_ACTIONS_STATUS_BRIDGE
# ================================================================================



# ================================================================================
# PACK123_SECURITY_INBOX_UI_STATUS_BRIDGES
# ================================================================================

def pack123_security_inbox_owner_queue_status_bridge():
    try:
        from tower.security_inbox_owner_queue import security_inbox_owner_queue_status_card
        return security_inbox_owner_queue_status_card()
    except Exception as exc:
        return {
            "ok": False,
            "pack": "123",
            "title": "Tower Security Inbox",
            "reason_code": "security_inbox_owner_queue_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Tower Security Inbox could not be loaded.",
        }


def pack123_security_inbox_review_status_bridge():
    try:
        from tower.security_inbox_review_actions import security_inbox_review_status_card
        return security_inbox_review_status_card()
    except Exception as exc:
        return {
            "ok": False,
            "pack": "123",
            "title": "Security Inbox Review",
            "reason_code": "security_inbox_review_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Security Inbox review status could not be loaded.",
        }

# ================================================================================
# END PACK123_SECURITY_INBOX_UI_STATUS_BRIDGES
# ================================================================================



# ================================================================================
# PACK125_SECURITY_INBOX_FILTERS_STATUS_BRIDGE
# ================================================================================

def pack125_security_inbox_filters_priorities_status_bridge():
    try:
        from tower.security_inbox_filters_priorities import security_inbox_filters_priorities_status_card
        return security_inbox_filters_priorities_status_card()
    except Exception as exc:
        return {
            "ok": False,
            "pack": "125",
            "title": "Security Inbox Filters & Priorities",
            "reason_code": "security_inbox_filters_priorities_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Security Inbox filters/priorities could not be loaded.",
        }

# ================================================================================
# END PACK125_SECURITY_INBOX_FILTERS_STATUS_BRIDGE
# ================================================================================



# ================================================================================
# PACK127_SECURITY_INCIDENT_DESK_STATUS_BRIDGE
# ================================================================================

def pack127_security_incident_desk_status_bridge():
    try:
        from tower.security_incident_desk import security_incident_desk_status_card
        return security_incident_desk_status_card()
    except Exception as exc:
        return {
            "ok": False,
            "pack": "127",
            "title": "Tower Incident Desk",
            "reason_code": "security_incident_desk_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Tower Incident Desk could not be loaded.",
        }

# ================================================================================
# END PACK127_SECURITY_INCIDENT_DESK_STATUS_BRIDGE
# ================================================================================



# ================================================================================
# PACK129_SECURITY_INCIDENT_FILTERS_STATUS_BRIDGE
# ================================================================================

def pack129_security_incident_filters_escalation_status_bridge():
    try:
        from tower.security_incident_filters_escalation import security_incident_filters_escalation_status_card
        return security_incident_filters_escalation_status_card()
    except Exception as exc:
        return {
            "ok": False,
            "pack": "129",
            "title": "Incident Filters & Escalation",
            "reason_code": "security_incident_filters_escalation_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Incident filters/escalation status could not be loaded.",
        }

# ================================================================================
# END PACK129_SECURITY_INCIDENT_FILTERS_STATUS_BRIDGE
# ================================================================================



# ================================================================================
# PACK132_SECURITY_WATCH_STATUS_BRIDGE
# ================================================================================

def pack132_security_watch_owner_posture_status_bridge():
    try:
        from tower.security_watch_owner_posture import security_watch_owner_posture_status_card
        return security_watch_owner_posture_status_card()
    except Exception as exc:
        return {
            "ok": False,
            "pack": "132",
            "title": "Tower Security Watch",
            "reason_code": "security_watch_owner_posture_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Tower Security Watch could not be loaded.",
        }

# ================================================================================
# END PACK132_SECURITY_WATCH_STATUS_BRIDGE
# ================================================================================



# ================================================================================
# PACK134_SECURITY_WATCH_CHECKPOINT_STATUS_BRIDGE
# ================================================================================

def pack134_security_watch_checkpoint_status_bridge():
    try:
        from tower.security_watch_checkpoint import security_watch_checkpoint_status_card
        return security_watch_checkpoint_status_card()
    except Exception as exc:
        return {
            "ok": False,
            "pack": "134",
            "title": "Security Watch Checkpoint",
            "reason_code": "security_watch_checkpoint_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Security Watch checkpoint could not be loaded.",
        }

# ================================================================================
# END PACK134_SECURITY_WATCH_CHECKPOINT_STATUS_BRIDGE
# ================================================================================



# ================================================================================
# PACK136_OWNER_ACTION_CENTER_STATUS_BRIDGE
# ================================================================================

def pack136_owner_action_center_status_bridge():
    try:
        from tower.owner_action_center import owner_action_center_status_card
        return owner_action_center_status_card()
    except Exception as exc:
        return {
            "ok": False,
            "pack": "136",
            "title": "Owner Action Center",
            "reason_code": "owner_action_center_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Owner Action Center could not be loaded.",
        }

# ================================================================================
# END PACK136_OWNER_ACTION_CENTER_STATUS_BRIDGE
# ================================================================================



# ================================================================================
# PACK137_OWNER_ACTION_CENTER_LANE_STATUS_BRIDGE
# ================================================================================

def pack137_owner_action_center_lane_status_bridge():
    try:
        from tower.owner_action_center import (
            build_owner_action_center_quick_metadata,
            build_owner_action_center_lane_summary,
            load_owner_action_center_status,
        )
        status = load_owner_action_center_status()
        return {
            "ok": True,
            "pack": "137",
            "quick_metadata": build_owner_action_center_quick_metadata(status),
            "lane_summary": build_owner_action_center_lane_summary(status),
            "human_reason": "Owner Action Center lane status bridge loaded.",
        }
    except Exception as exc:
        return {
            "ok": False,
            "pack": "137",
            "title": "Owner Action Center Lane Summary",
            "reason_code": "owner_action_center_lane_summary_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Owner Action Center lane summary could not be loaded.",
        }

# ================================================================================
# END PACK137_OWNER_ACTION_CENTER_LANE_STATUS_BRIDGE
# ================================================================================



# ================================================================================
# PACK138_OWNER_ACTION_FILTERS_STATUS_BRIDGE
# ================================================================================

def pack138_owner_action_filters_status_bridge():
    try:
        from tower.owner_action_center import build_owner_action_filters_status
        return build_owner_action_filters_status(write_panel=True)
    except Exception as exc:
        return {
            "ok": False,
            "pack": "138",
            "title": "Owner Action Filters",
            "reason_code": "owner_action_filters_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Owner Action Filters could not be loaded.",
        }

# ================================================================================
# END PACK138_OWNER_ACTION_FILTERS_STATUS_BRIDGE
# ================================================================================



# ================================================================================
# PACK139_OWNER_ACTION_DETAIL_STATUS_BRIDGE
# ================================================================================

def pack139_owner_action_detail_status_bridge(action_id: str = ""):
    try:
        from tower.owner_action_center import build_owner_action_detail_status
        return build_owner_action_detail_status(action_id=action_id, write_panel=True)
    except Exception as exc:
        return {
            "ok": False,
            "pack": "139",
            "title": "Owner Action Detail",
            "reason_code": "owner_action_detail_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Owner Action Detail could not be loaded.",
        }

# ================================================================================
# END PACK139_OWNER_ACTION_DETAIL_STATUS_BRIDGE
# ================================================================================



# ================================================================================
# PACK146_OWNER_ACTION_REVIEW_CHECKPOINT_STATUS_BRIDGE
# ================================================================================

def pack146_owner_action_review_checkpoint_status_bridge():
    try:
        from tower.owner_action_review_checkpoint import owner_action_review_checkpoint_status_card
        return owner_action_review_checkpoint_status_card()
    except Exception as exc:
        return {
            "ok": False,
            "pack": "146",
            "title": "Owner Action Review Checkpoint",
            "reason_code": "owner_action_review_checkpoint_card_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Owner Action Review Checkpoint status card could not be loaded.",
        }

# ================================================================================
# END PACK146_OWNER_ACTION_REVIEW_CHECKPOINT_STATUS_BRIDGE
# ================================================================================



# ================================================================================
# PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_STATUS_BRIDGE
# ================================================================================

def pack148_owner_action_review_compact_card_status_bridge():
    try:
        from tower.owner_action_review_compact_card import owner_action_review_compact_card_status_card
        return owner_action_review_compact_card_status_card()
    except Exception as exc:
        return {
            "ok": False,
            "pack": "148",
            "title": "Compact Owner Action Review Card",
            "reason_code": "owner_action_review_compact_card_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Compact Owner Action Review Card status card could not be loaded.",
        }

# ================================================================================
# END PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_STATUS_BRIDGE
# ================================================================================



# ================================================================================
# PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_STATUS_BRIDGE
# ================================================================================

def pack149_owner_action_review_focus_lanes_status_bridge():
    try:
        from tower.owner_action_review_focus_lanes import owner_action_review_focus_lanes_status_card
        return owner_action_review_focus_lanes_status_card()
    except Exception as exc:
        return {
            "ok": False,
            "pack": "149",
            "title": "Owner Action Review Focus Lanes",
            "reason_code": "owner_action_review_focus_lanes_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Owner Action Review Focus Lanes status card could not be loaded.",
        }

# ================================================================================
# END PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_STATUS_BRIDGE
# ================================================================================



# ================================================================================
# PACK150_OWNER_ACTION_REVIEW_READINESS_STATUS_BRIDGE
# ================================================================================

def pack150_owner_action_review_readiness_status_bridge():
    try:
        from tower.owner_action_review_readiness_checkpoint import owner_action_review_readiness_status_card
        return owner_action_review_readiness_status_card()
    except Exception as exc:
        return {
            "ok": False,
            "pack": "150",
            "title": "Final Owner Action Review Readiness",
            "reason_code": "owner_action_review_readiness_unavailable",
            "error_type": type(exc).__name__,
            "human_reason": "Final Owner Action Review Readiness status card could not be loaded.",
        }

# ================================================================================
# END PACK150_OWNER_ACTION_REVIEW_READINESS_STATUS_BRIDGE
# ================================================================================

