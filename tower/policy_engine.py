# =============================================================================
# THE TOWER — POLICY ENGINE
# FILE: tower/policy_engine.py
# =============================================================================

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


POLICY_VERSION = "tower_policy_v0.1.0"


# =============================================================================
# POLICY DECISION CONSTANTS
# =============================================================================

POLICY_ALLOW = "allow"
POLICY_DENY = "deny"
POLICY_STEP_UP = "step_up"
POLICY_QUARANTINE = "quarantine"
POLICY_LOCKDOWN = "lockdown"
POLICY_NOT_APPLICABLE = "not_applicable"


@dataclass
class PolicyRuleResult:
    rule_id: str
    passed: bool
    decision: str
    reason_code: str
    human_reason: str
    severity: str = "info"
    required_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "passed": self.passed,
            "decision": self.decision,
            "reason_code": self.reason_code,
            "human_reason": self.human_reason,
            "severity": self.severity,
            "required_actions": self.required_actions,
            "metadata": self.metadata,
        }


@dataclass
class PolicyDecision:
    allowed: bool
    decision: str
    reason_code: str
    human_reason: str
    policy_version: str = POLICY_VERSION
    risk_score: int = 0
    risk_state: str = "clear"
    required_actions: List[str] = field(default_factory=list)
    rule_results: List[PolicyRuleResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "decision": self.decision,
            "reason_code": self.reason_code,
            "human_reason": self.human_reason,
            "policy_version": self.policy_version,
            "risk_score": self.risk_score,
            "risk_state": self.risk_state,
            "required_actions": self.required_actions,
            "rule_results": [item.to_dict() for item in self.rule_results],
            "metadata": self.metadata,
        }


# =============================================================================
# SMALL HELPERS
# =============================================================================

def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _has_app_access(user: Dict[str, Any], app_name: str) -> bool:
    app_access = user.get("app_access", {}) or {}
    return app_access.get(app_name) == "allowed"


def _has_consent(user: Dict[str, Any], consent_key: str) -> bool:
    consents = user.get("consents", {}) or {}
    return consents.get(consent_key) is True


def _is_owner_or_internal(user: Dict[str, Any]) -> bool:
    return user.get("account_type") in {"owner", "internal", "trust"}


def _is_admin_or_owner(user: Dict[str, Any]) -> bool:
    return user.get("role") in {"owner", "admin"}


def _session_score(context: Dict[str, Any]) -> int:
    session_risk = context.get("session_risk") or {}
    return int(session_risk.get("risk_score") or 0)


def _session_state(context: Dict[str, Any]) -> str:
    session_risk = context.get("session_risk") or {}
    return session_risk.get("risk_state") or "clear"


# =============================================================================
# POLICY RULES
# =============================================================================

def rule_user_status_active(payload: Dict[str, Any]) -> PolicyRuleResult:
    user = payload.get("user") or {}
    status = user.get("status", "locked")

    if status in {"locked", "revoked"}:
        return PolicyRuleResult(
            rule_id="user.status.active",
            passed=False,
            decision=POLICY_DENY,
            reason_code="policy_user_locked_or_revoked",
            human_reason="User is locked or revoked.",
            severity="critical",
            required_actions=["owner_review_required"],
            metadata={"status": status},
        )

    if status == "quarantined":
        return PolicyRuleResult(
            rule_id="user.status.active",
            passed=False,
            decision=POLICY_QUARANTINE,
            reason_code="policy_user_quarantined",
            human_reason="User is quarantined.",
            severity="high",
            required_actions=["security_review_required"],
            metadata={"status": status},
        )

    return PolicyRuleResult(
        rule_id="user.status.active",
        passed=True,
        decision=POLICY_ALLOW,
        reason_code="policy_user_status_ok",
        human_reason="User status is active.",
        metadata={"status": status},
    )


def rule_app_access_allowed(payload: Dict[str, Any]) -> PolicyRuleResult:
    user = payload.get("user") or {}
    app_name = payload.get("app_name")

    if not app_name:
        return PolicyRuleResult(
            rule_id="app.access.allowed",
            passed=False,
            decision=POLICY_DENY,
            reason_code="policy_app_missing",
            human_reason="No app name was provided.",
            severity="medium",
            required_actions=["provide_app_name"],
        )

    if not _has_app_access(user, app_name):
        return PolicyRuleResult(
            rule_id="app.access.allowed",
            passed=False,
            decision=POLICY_DENY,
            reason_code="policy_missing_app_access",
            human_reason=f"User does not have app clearance for {app_name}.",
            severity="high",
            required_actions=["grant_app_access"],
            metadata={"app_name": app_name},
        )

    return PolicyRuleResult(
        rule_id="app.access.allowed",
        passed=True,
        decision=POLICY_ALLOW,
        reason_code="policy_app_access_ok",
        human_reason=f"User has app clearance for {app_name}.",
        metadata={"app_name": app_name},
    )


def rule_tower_admin_requires_admin(payload: Dict[str, Any]) -> PolicyRuleResult:
    user = payload.get("user") or {}
    app_name = payload.get("app_name")
    action = payload.get("action")

    if app_name != "tower_admin" and action != "enter_admin":
        return PolicyRuleResult(
            rule_id="admin.requires.role",
            passed=True,
            decision=POLICY_NOT_APPLICABLE,
            reason_code="policy_admin_rule_not_applicable",
            human_reason="Admin role rule is not applicable.",
        )

    if not _is_admin_or_owner(user):
        return PolicyRuleResult(
            rule_id="admin.requires.role",
            passed=False,
            decision=POLICY_DENY,
            reason_code="policy_admin_role_required",
            human_reason="Tower admin access requires owner/admin role.",
            severity="high",
            required_actions=["admin_approval_required"],
        )

    return PolicyRuleResult(
        rule_id="admin.requires.role",
        passed=True,
        decision=POLICY_ALLOW,
        reason_code="policy_admin_role_ok",
        human_reason="User has owner/admin role.",
    )


def rule_session_risk(payload: Dict[str, Any]) -> PolicyRuleResult:
    context = payload.get("context") or {}
    score = _session_score(context)
    state = _session_state(context)

    if state == "quarantine_recommended" or score >= 90:
        return PolicyRuleResult(
            rule_id="session.risk.threshold",
            passed=False,
            decision=POLICY_QUARANTINE,
            reason_code="policy_session_quarantine_required",
            human_reason="Session risk is high enough to require quarantine review.",
            severity="critical",
            required_actions=["security_review_required", "step_up_required"],
            metadata={"risk_score": score, "risk_state": state, "session_risk": context.get("session_risk")},
        )

    if state == "step_up_required" or score >= 70:
        return PolicyRuleResult(
            rule_id="session.risk.threshold",
            passed=False,
            decision=POLICY_STEP_UP,
            reason_code="policy_session_step_up_required",
            human_reason="Session risk requires step-up authorization.",
            severity="high",
            required_actions=["complete_step_up"],
            metadata={"risk_score": score, "risk_state": state, "session_risk": context.get("session_risk")},
        )

    if score >= 40:
        return PolicyRuleResult(
            rule_id="session.risk.threshold",
            passed=True,
            decision=POLICY_ALLOW,
            reason_code="policy_session_watch",
            human_reason="Session is watch-level but not blocked.",
            severity="medium",
            metadata={"risk_score": score, "risk_state": state, "session_risk": context.get("session_risk")},
        )

    return PolicyRuleResult(
        rule_id="session.risk.threshold",
        passed=True,
        decision=POLICY_ALLOW,
        reason_code="policy_session_risk_ok",
        human_reason="Session risk is acceptable.",
        metadata={"risk_score": score, "risk_state": state},
    )


def rule_observatory_mode(payload: Dict[str, Any]) -> PolicyRuleResult:
    user = payload.get("user") or {}
    app_name = payload.get("app_name")
    mode_name = payload.get("mode_name")

    if app_name != "observatory" or not mode_name:
        return PolicyRuleResult(
            rule_id="observatory.mode.allowed",
            passed=True,
            decision=POLICY_NOT_APPLICABLE,
            reason_code="policy_ob_mode_rule_not_applicable",
            human_reason="Observatory mode rule is not applicable.",
        )

    if mode_name == "survey":
        return PolicyRuleResult(
            rule_id="observatory.mode.allowed",
            passed=True,
            decision=POLICY_ALLOW,
            reason_code="policy_survey_mode_ok",
            human_reason="Survey Mode is allowed after app clearance.",
            metadata={"mode_name": mode_name},
        )

    if mode_name == "paper":
        if not _has_consent(user, "paper_trading_disclosure"):
            return PolicyRuleResult(
                rule_id="observatory.mode.allowed",
                passed=False,
                decision=POLICY_DENY,
                reason_code="policy_paper_disclosure_required",
                human_reason="Paper Mode requires simulated trading disclosure.",
                severity="medium",
                required_actions=["accept_paper_trading_disclosure"],
                metadata={"mode_name": mode_name},
            )

        return PolicyRuleResult(
            rule_id="observatory.mode.allowed",
            passed=True,
            decision=POLICY_ALLOW,
            reason_code="policy_paper_mode_ok",
            human_reason="Paper Mode requirements are satisfied.",
            metadata={"mode_name": mode_name},
        )

    if mode_name == "live_manual":
        if not _has_consent(user, "live_trading_consent"):
            return PolicyRuleResult(
                rule_id="observatory.mode.allowed",
                passed=False,
                decision=POLICY_DENY,
                reason_code="policy_live_consent_required",
                human_reason="Live Manual requires live trading consent.",
                severity="high",
                required_actions=["accept_live_trading_consent"],
                metadata={"mode_name": mode_name},
            )

        return PolicyRuleResult(
            rule_id="observatory.mode.allowed",
            passed=False,
            decision=POLICY_STEP_UP,
            reason_code="policy_live_manual_step_up_required",
            human_reason="Live Manual requires step-up.",
            severity="high",
            required_actions=["complete_step_up"],
            metadata={"mode_name": mode_name},
        )

    if mode_name in {"live_hybrid", "live_automated"}:
        return PolicyRuleResult(
            rule_id="observatory.mode.allowed",
            passed=False,
            decision=POLICY_DENY,
            reason_code="policy_public_live_advanced_locked",
            human_reason="Advanced Live modes are locked until legal/control approval.",
            severity="critical",
            required_actions=[
                "owner_approval_required",
                "legal_review_required",
                "broker_permission_check_required",
                "control_tower_approval_required",
            ],
            metadata={"mode_name": mode_name},
        )

    if mode_name == "internal_trust_automated":
        if not _is_owner_or_internal(user):
            return PolicyRuleResult(
                rule_id="observatory.mode.allowed",
                passed=False,
                decision=POLICY_DENY,
                reason_code="policy_internal_trust_required",
                human_reason="Internal Trust Automated requires owner/internal/trust account.",
                severity="critical",
                required_actions=["internal_trust_account_required"],
                metadata={"mode_name": mode_name},
            )

        return PolicyRuleResult(
            rule_id="observatory.mode.allowed",
            passed=False,
            decision=POLICY_STEP_UP,
            reason_code="policy_internal_trust_automated_step_up_required",
            human_reason="Internal Trust Automated requires step-up.",
            severity="critical",
            required_actions=["complete_step_up", "verify_kill_switch_active"],
            metadata={"mode_name": mode_name},
        )

    return PolicyRuleResult(
        rule_id="observatory.mode.allowed",
        passed=False,
        decision=POLICY_DENY,
        reason_code="policy_unknown_mode",
        human_reason="Unknown mode requested.",
        severity="medium",
        required_actions=["check_mode_name"],
        metadata={"mode_name": mode_name},
    )


def rule_export_permission(payload: Dict[str, Any]) -> PolicyRuleResult:
    user = payload.get("user") or {}
    action = payload.get("action")

    if action != "export":
        return PolicyRuleResult(
            rule_id="export.permission.allowed",
            passed=True,
            decision=POLICY_NOT_APPLICABLE,
            reason_code="policy_export_rule_not_applicable",
            human_reason="Export permission rule is not applicable.",
        )

    if user.get("can_export") is not True:
        return PolicyRuleResult(
            rule_id="export.permission.allowed",
            passed=False,
            decision=POLICY_DENY,
            reason_code="policy_export_permission_required",
            human_reason="User does not have export permission.",
            severity="high",
            required_actions=["export_approval_required"],
        )

    return PolicyRuleResult(
        rule_id="export.permission.allowed",
        passed=True,
        decision=POLICY_ALLOW,
        reason_code="policy_export_permission_ok",
        human_reason="User has export permission.",
    )


# =============================================================================
# MAIN POLICY EVALUATOR
# =============================================================================

DEFAULT_RULES: List[Callable[[Dict[str, Any]], PolicyRuleResult]] = [
    rule_user_status_active,
    rule_session_risk,
    rule_app_access_allowed,
    rule_tower_admin_requires_admin,
    rule_observatory_mode,
    rule_export_permission,
]


def evaluate_policy(
    user: Dict[str, Any],
    app_name: str,
    action: str = "enter_app",
    mode_name: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> PolicyDecision:
    """
    Main policy engine.

    Baby version:
    This runs the official rulebook and explains what happened.
    """

    context = context or {}
    extra = extra or {}

    payload = {
        "user": user,
        "app_name": app_name,
        "action": action,
        "mode_name": mode_name,
        "object_type": object_type,
        "object_id": object_id,
        "context": context,
        "extra": extra,
    }

    results: List[PolicyRuleResult] = []

    for rule in DEFAULT_RULES:
        try:
            results.append(rule(payload))
        except Exception as exc:
            results.append(
                PolicyRuleResult(
                    rule_id=getattr(rule, "__name__", "unknown_rule"),
                    passed=False,
                    decision=POLICY_DENY,
                    reason_code="policy_rule_error",
                    human_reason=f"A policy rule failed with an error: {exc}",
                    severity="critical",
                    required_actions=["developer_review_required"],
                    metadata={"error": str(exc)},
                )
            )

    # Highest severity/strongest decision wins.
    for decision_kind in [POLICY_LOCKDOWN, POLICY_QUARANTINE, POLICY_DENY, POLICY_STEP_UP]:
        blockers = [
            item for item in results
            if item.decision == decision_kind and item.passed is False
        ]

        if blockers:
            first = blockers[0]

            risk_score = 50
            risk_state = "restricted"

            if decision_kind == POLICY_QUARANTINE:
                risk_score = 95
                risk_state = "quarantined"
            elif decision_kind == POLICY_LOCKDOWN:
                risk_score = 100
                risk_state = "locked"
            elif decision_kind == POLICY_STEP_UP:
                risk_score = 70
                risk_state = "step_up_required"
            elif decision_kind == POLICY_DENY:
                risk_score = 75
                risk_state = "restricted"

            required_actions = []
            for item in blockers:
                required_actions.extend(item.required_actions)

            return PolicyDecision(
                allowed=False,
                decision=decision_kind,
                reason_code=first.reason_code,
                human_reason=first.human_reason,
                risk_score=risk_score,
                risk_state=risk_state,
                required_actions=sorted(set(required_actions)),
                rule_results=results,
                metadata={
                    "policy_version": POLICY_VERSION,
                    "evaluated_at": _now(),
                    "app_name": app_name,
                    "action": action,
                    "mode_name": mode_name,
                    "object_type": object_type,
                    "object_id": object_id,
                    "blocking_rule_id": first.rule_id,
                },
            )

    return PolicyDecision(
        allowed=True,
        decision=POLICY_ALLOW,
        reason_code="policy_clearance_allowed",
        human_reason="Policy engine allowed this request.",
        risk_score=10,
        risk_state="clear",
        required_actions=[],
        rule_results=results,
        metadata={
            "policy_version": POLICY_VERSION,
            "evaluated_at": _now(),
            "app_name": app_name,
            "action": action,
            "mode_name": mode_name,
            "object_type": object_type,
            "object_id": object_id,
        },
    )
