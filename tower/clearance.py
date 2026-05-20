# =============================================================================
# THE TOWER — CLEARANCE WRAPPER
# FILE: tower/clearance.py
# =============================================================================

from typing import Any, Dict, Optional

from tower.audit import write_audit_event
from tower.permissions import evaluate_clearance


def request_clearance(
    user: Dict[str, Any],
    app_name: str,
    action: str = "enter_app",
    mode_name: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    write_audit: bool = True,
) -> Dict[str, Any]:
    """
    This is the nice wrapper around The Tower brain.

    Baby version:
    1. Ask permissions.py if the user is allowed.
    2. Write a receipt in audit.py.
    3. Return the answer.
    """

    decision = evaluate_clearance(
        user=user,
        app_name=app_name,
        action=action,
        mode_name=mode_name,
        object_type=object_type,
        object_id=object_id,
        context=context,
    )

    decision_dict = decision.to_dict()

    if write_audit and decision.audit_required:
        write_audit_event(
            actor_user_id=str(user.get("user_id", "unknown")),
            target_user_id=str(user.get("user_id", "unknown")),
            action=action,
            app_name=app_name,
            object_type=object_type,
            object_id=object_id,
            result=decision.decision,
            reason_code=decision.reason_code,
            human_reason=decision.human_reason,
            risk_score=decision.risk_score,
            risk_state=decision.risk_state,
            metadata={
                "mode_name": mode_name,
                "required_actions": decision.required_actions,
                "decision_metadata": decision.metadata,
            },
        )

    return decision_dict
