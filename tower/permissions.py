# =============================================================================
# THE TOWER — PERMISSIONS BRAIN
# FILE: tower/permissions.py
# =============================================================================

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


# =============================================================================
# APPS
# =============================================================================

APP_OBSERVATORY = "observatory"
APP_ARCHIVE_VAULT = "archive_vault"
APP_SIMPLEEPAY = "simpleepay"
APP_TOWER_ADMIN = "tower_admin"


# =============================================================================
# OBSERVATORY MODES
# =============================================================================

MODE_SURVEY = "survey"
MODE_PAPER = "paper"
MODE_LIVE_MANUAL = "live_manual"
MODE_LIVE_HYBRID = "live_hybrid"
MODE_LIVE_AUTOMATED = "live_automated"
MODE_INTERNAL_TRUST_AUTOMATED = "internal_trust_automated"


# =============================================================================
# USER STATES
# =============================================================================

STATUS_ACTIVE = "active"
STATUS_LOCKED = "locked"
STATUS_QUARANTINED = "quarantined"
STATUS_REVOKED = "revoked"


# =============================================================================
# DECISIONS
# =============================================================================

DECISION_ALLOW = "allow"
DECISION_DENY = "deny"
DECISION_STEP_UP = "step_up"
DECISION_QUARANTINE = "quarantine"
DECISION_LOCKDOWN = "lockdown"


# =============================================================================
# CLEARANCE RESPONSE OBJECT
# =============================================================================

@dataclass
class ClearanceDecision:
    allowed: bool
    decision: str
    reason_code: str
    human_reason: str
    risk_score: int = 0
    risk_state: str = "clear"
    required_actions: List[str] = field(default_factory=list)
    audit_required: bool = True
    expires_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "decision": self.decision,
            "reason_code": self.reason_code,
            "human_reason": self.human_reason,
            "risk_score": self.risk_score,
            "risk_state": self.risk_state,
            "required_actions": self.required_actions,
            "audit_required": self.audit_required,
            "expires_at": self.expires_at,
            "metadata": self.metadata,
        }


# =============================================================================
# SMALL HELPER FUNCTIONS
# =============================================================================

def _has_app_access(user: Dict[str, Any], app_name: str) -> bool:
    app_access = user.get("app_access", {})
    return bool(app_access.get(app_name) == "allowed")


def _has_consent(user: Dict[str, Any], consent_key: str) -> bool:
    consents = user.get("consents", {})
    return bool(consents.get(consent_key) is True)


def _is_owner_or_internal(user: Dict[str, Any]) -> bool:
    return user.get("account_type") in {"owner", "internal", "trust"}


def _is_admin(user: Dict[str, Any]) -> bool:
    return user.get("role") in {"owner", "admin"}


def _expires(minutes: int = 15) -> str:
    return (datetime.utcnow() + timedelta(minutes=minutes)).isoformat() + "Z"


# =============================================================================
# THE MAIN TOWER BRAIN
# =============================================================================

def evaluate_clearance(
    user: Dict[str, Any],
    app_name: str,
    action: str = "enter_app",
    mode_name: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> ClearanceDecision:
    """
    The Tower's main yes/no brain.

    Baby version:
    This function is the guard at the door.

    It checks:
    - Is this account locked?
    - Is this account quarantined?
    - Is this user allowed into this app?
    - Is this user allowed to use this mode?
    - Does this action need extra approval?
    """

    context = context or {}

    user_id = user.get("user_id", "unknown")
    status = user.get("status", STATUS_LOCKED)

    # -------------------------------------------------------------------------
    # Rule 1: locked or revoked users go nowhere.
    # -------------------------------------------------------------------------
    if status in {STATUS_LOCKED, STATUS_REVOKED}:
        return ClearanceDecision(
            allowed=False,
            decision=DECISION_DENY,
            reason_code="user_locked_or_revoked",
            human_reason="This account is locked or revoked. Access is denied.",
            risk_score=100,
            risk_state="locked",
            required_actions=["owner_review_required"],
            metadata={"user_id": user_id, "app_name": app_name, "action": action},
        )

    # -------------------------------------------------------------------------
    # Rule 2: quarantined users are blocked from sensitive movement.
    # -------------------------------------------------------------------------
    if status == STATUS_QUARANTINED:
        return ClearanceDecision(
            allowed=False,
            decision=DECISION_QUARANTINE,
            reason_code="user_quarantined",
            human_reason="This account is in quarantine. Sensitive access is paused.",
            risk_score=90,
            risk_state="quarantined",
            required_actions=["security_review_required"],
            metadata={"user_id": user_id, "app_name": app_name, "action": action},
        )

    # -------------------------------------------------------------------------
    # Rule 3: app access is deny-by-default.
    # -------------------------------------------------------------------------
    if not _has_app_access(user, app_name):
        return ClearanceDecision(
            allowed=False,
            decision=DECISION_DENY,
            reason_code="missing_app_access",
            human_reason=f"This user does not have clearance for {app_name}.",
            risk_score=50,
            risk_state="restricted",
            required_actions=["grant_app_access"],
            metadata={"user_id": user_id, "app_name": app_name, "action": action},
        )

    # -------------------------------------------------------------------------
    # Rule 4: Tower admin requires owner/admin role.
    # -------------------------------------------------------------------------
    if app_name == APP_TOWER_ADMIN and not _is_admin(user):
        return ClearanceDecision(
            allowed=False,
            decision=DECISION_DENY,
            reason_code="admin_role_required",
            human_reason="Tower admin access requires an admin or owner role.",
            risk_score=80,
            risk_state="restricted",
            required_actions=["admin_approval_required"],
            metadata={"user_id": user_id, "app_name": app_name, "action": action},
        )

    # -------------------------------------------------------------------------
    # Rule 5: Observatory mode checks.
    # -------------------------------------------------------------------------
    if app_name == APP_OBSERVATORY and mode_name:
        return evaluate_observatory_mode(
            user=user,
            mode_name=mode_name,
            context=context,
        )

    # -------------------------------------------------------------------------
    # Rule 6: exports need special permission and step-up.
    # -------------------------------------------------------------------------
    if action == "export":
        if user.get("can_export") is not True:
            return ClearanceDecision(
                allowed=False,
                decision=DECISION_DENY,
                reason_code="export_permission_required",
                human_reason="Export access is locked. This user does not have export clearance.",
                risk_score=75,
                risk_state="restricted",
                required_actions=["export_approval_required"],
                metadata={
                    "user_id": user_id,
                    "app_name": app_name,
                    "object_type": object_type,
                    "object_id": object_id,
                    "action": action,
                },
            )

        return ClearanceDecision(
            allowed=False,
            decision=DECISION_STEP_UP,
            reason_code="export_step_up_required",
            human_reason="Export access requires step-up confirmation before continuing.",
            risk_score=60,
            risk_state="step_up_required",
            required_actions=["complete_step_up"],
            metadata={
                "user_id": user_id,
                "app_name": app_name,
                "object_type": object_type,
                "object_id": object_id,
                "action": action,
            },
        )

    # -------------------------------------------------------------------------
    # Default allow after checks.
    # -------------------------------------------------------------------------
    return ClearanceDecision(
        allowed=True,
        decision=DECISION_ALLOW,
        reason_code="clearance_granted",
        human_reason="Tower clearance granted.",
        risk_score=10,
        risk_state="clear",
        expires_at=_expires(15),
        metadata={"user_id": user_id, "app_name": app_name, "action": action},
    )


# =============================================================================
# OBSERVATORY MODE RULES
# =============================================================================

def evaluate_observatory_mode(
    user: Dict[str, Any],
    mode_name: str,
    context: Optional[Dict[str, Any]] = None,
) -> ClearanceDecision:
    """
    Checks whether a user can enter a specific Observatory mode.

    Baby version:
    Survey is easy.
    Paper needs paper disclosure.
    Live is dangerous, so it gets locked or step-up.
    Automated is the big scary door.
    """

    context = context or {}
    user_id = user.get("user_id", "unknown")

    # Survey Mode: easiest approved mode.
    if mode_name == MODE_SURVEY:
        return ClearanceDecision(
            allowed=True,
            decision=DECISION_ALLOW,
            reason_code="survey_mode_allowed",
            human_reason="Survey Mode clearance granted.",
            risk_score=10,
            risk_state="clear",
            expires_at=_expires(15),
            metadata={"user_id": user_id, "mode_name": mode_name},
        )

    # Paper Mode: requires simulated trading disclosure.
    if mode_name == MODE_PAPER:
        if not _has_consent(user, "paper_trading_disclosure"):
            return ClearanceDecision(
                allowed=False,
                decision=DECISION_DENY,
                reason_code="paper_disclosure_required",
                human_reason="Paper Mode requires the simulated trading disclosure first.",
                risk_score=40,
                risk_state="restricted",
                required_actions=["accept_paper_trading_disclosure"],
                metadata={"user_id": user_id, "mode_name": mode_name},
            )

        return ClearanceDecision(
            allowed=True,
            decision=DECISION_ALLOW,
            reason_code="paper_mode_allowed",
            human_reason="Paper Mode clearance granted.",
            risk_score=15,
            risk_state="clear",
            expires_at=_expires(15),
            metadata={"user_id": user_id, "mode_name": mode_name},
        )

    # Live Manual: requires live trading consent and step-up.
    if mode_name == MODE_LIVE_MANUAL:
        if not _has_consent(user, "live_trading_consent"):
            return ClearanceDecision(
                allowed=False,
                decision=DECISION_DENY,
                reason_code="live_consent_required",
                human_reason="Live Manual requires live trading consent first.",
                risk_score=70,
                risk_state="restricted",
                required_actions=["accept_live_trading_consent"],
                metadata={"user_id": user_id, "mode_name": mode_name},
            )

        return ClearanceDecision(
            allowed=False,
            decision=DECISION_STEP_UP,
            reason_code="live_manual_step_up_required",
            human_reason="Live Manual requires step-up confirmation before entry.",
            risk_score=70,
            risk_state="step_up_required",
            required_actions=["complete_step_up"],
            metadata={"user_id": user_id, "mode_name": mode_name},
        )

    # Live Hybrid: locked until stronger approvals exist.
    if mode_name == MODE_LIVE_HYBRID:
        return ClearanceDecision(
            allowed=False,
            decision=DECISION_DENY,
            reason_code="live_hybrid_locked",
            human_reason="Live Hybrid is locked until owner/legal/control approval is complete.",
            risk_score=85,
            risk_state="locked",
            required_actions=[
                "owner_approval_required",
                "legal_review_required",
                "broker_permission_check_required",
            ],
            metadata={"user_id": user_id, "mode_name": mode_name},
        )

    # Live Automated: hard blocked for public and beta users.
    if mode_name == MODE_LIVE_AUTOMATED:
        return ClearanceDecision(
            allowed=False,
            decision=DECISION_DENY,
            reason_code="public_live_automated_blocked",
            human_reason="Live Automated is blocked for public and beta users.",
            risk_score=95,
            risk_state="locked",
            required_actions=[
                "internal_trust_account_required",
                "owner_approval_required",
                "legal_review_required",
                "control_tower_approval_required",
            ],
            metadata={"user_id": user_id, "mode_name": mode_name},
        )

    # Internal/trust automated: only owner/internal/trust accounts.
    if mode_name == MODE_INTERNAL_TRUST_AUTOMATED:
        if not _is_owner_or_internal(user):
            return ClearanceDecision(
                allowed=False,
                decision=DECISION_DENY,
                reason_code="internal_trust_required",
                human_reason="Internal Trust Automated access requires an owner, internal, or trust account.",
                risk_score=95,
                risk_state="locked",
                required_actions=["owner_or_trust_account_required"],
                metadata={"user_id": user_id, "mode_name": mode_name},
            )

        if not _has_consent(user, "automated_trading_consent"):
            return ClearanceDecision(
                allowed=False,
                decision=DECISION_DENY,
                reason_code="automated_consent_required",
                human_reason="Automated access requires automated trading consent first.",
                risk_score=90,
                risk_state="restricted",
                required_actions=["accept_automated_trading_consent"],
                metadata={"user_id": user_id, "mode_name": mode_name},
            )

        return ClearanceDecision(
            allowed=False,
            decision=DECISION_STEP_UP,
            reason_code="internal_trust_automated_step_up_required",
            human_reason="Internal Trust Automated access requires step-up confirmation.",
            risk_score=90,
            risk_state="step_up_required",
            required_actions=["complete_step_up", "verify_kill_switch_active"],
            metadata={"user_id": user_id, "mode_name": mode_name},
        )

    # Unknown mode: deny.
    return ClearanceDecision(
        allowed=False,
        decision=DECISION_DENY,
        reason_code="unknown_mode",
        human_reason="Unknown mode requested. Access denied.",
        risk_score=60,
        risk_state="restricted",
        required_actions=["check_mode_name"],
        metadata={"user_id": user_id, "mode_name": mode_name},
    )
