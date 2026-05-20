# =============================================================================
# THE TOWER — STATUS SUMMARY
# FILE: tower/tower_status.py
# =============================================================================

from typing import Any, Dict

from tower.audit import get_audit_summary, verify_audit_chain
from tower.security_events import get_security_summary
from tower.user_store import list_users
from tower.evidence_capsules import get_evidence_summary


def get_tower_status() -> Dict[str, Any]:
    """
    Gives The Tower dashboard-friendly numbers.

    Baby version:
    This counts users, locked users, open security alerts, and audit health.
    """

    users = list_users()
    audit = get_audit_summary()
    security = get_security_summary()
    evidence = get_evidence_summary()
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
        "apps_seen_in_audit": audit.get("apps", {}),
        "risk_states_seen_in_audit": audit.get("risk_states", {}),
    }
