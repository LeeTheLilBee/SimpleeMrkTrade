"""GRD022 — Soulaana explanations grounded in authorized Grounds/Teller projections.

Read-only, deterministic owner/resident helper. This layer never grants access,
queries OB, performs financial actions, decides applications, or bypasses rules.
It takes a GroundsOperations instance to enforce the normal scoped read.
"""
from __future__ import annotations

from typing import Mapping

from .access import TowerScope, AccessDenied
from .operations import GroundsOperations

_WORK_MESSAGES = {
    "submitted": ("Your request has been received in Grounds.","Management review"),
    "received": ("The property desk has received this request.","Triage and review"),
    "under_review": ("The property desk is reviewing the issue and scope.","Scheduling decision"),
    "scheduled": ("This work is scheduled; assignment is the next staff step.","Technician assignment"),
    "assigned": ("The assigned technician can see the scoped job.","Technician start"),
    "in_progress": ("The assigned technician has marked the job in progress.","Work update or completion"),
    "waiting": ("Work is paused pending a follow-up or reassignment.","Resume or reschedule"),
    "completed": ("The technician marked work complete; management must review it.","Manager review"),
    "confirmation": ("The property desk is awaiting confirmation or closure.","Confirm, close or reopen"),
    "closed": ("This maintenance record has been closed and its history remains available.","Reopen if unresolved"),
    "reopened": ("This request was reopened and needs new management review.","Return to review"),
}

def explain_work_order(actor: TowerScope, operations: GroundsOperations, *, work_ref: str) -> dict:
    if not isinstance(operations, GroundsOperations):
        raise TypeError("GroundsOperations required")
    row = operations.get_work_order(actor,work_ref=work_ref)
    message,next_action = _WORK_MESSAGES[row["state"]]
    if row["emergency_flag"] and row["state"] not in ("completed","closed"):
        message += " The resident selected an urgency flag; this is not emergency dispatch confirmation."
    return {
        "speaker":"Soulaana", "source":"grounds", "work_ref":work_ref,
        "source_revision":row["revision"], "source_state":row["state"],
        "message":message, "next_useful_action":next_action,
        "action_executed":False, "permissions_granted":False, "external_ai_called":False,
    }

def explain_apartment_readiness(actor: TowerScope, projection: Mapping) -> dict:
    actor.require_role("owner","property_manager")
    if (not isinstance(projection,Mapping) or projection.get("source")!="teller"
        or projection.get("mode")!="verified_projection"
        or projection.get("property_ref") not in actor.property_refs
        or projection.get("money_movement_enabled") is not False):
        raise AccessDenied("verified Teller readiness projection required")
    lanes=projection.get("lanes")
    if not isinstance(lanes,Mapping):
        raise AccessDenied("readiness lane data unavailable")
    weak=[name for name,view in lanes.items() if isinstance(view,Mapping)
          and view.get("status") in ("weak","blocked","unknown")]
    message = (
        "The Teller indicates additional review is needed for: "+", ".join(weak)+
        ". Protected amounts are not spendable and these results do not authorize acquisition."
        if weak else
        "This is a Teller-sourced readiness view, not a funding approval. Verify the current deal terms, reserves and authorized next action."
    )
    return {
        "speaker":"Soulaana","source":"teller","source_terms_digest":projection.get("terms_digest"),
        "message":message,"next_useful_action":"Open Teller readiness details",
        "money_moved":False,"acquisition_approved":False,"ob_queried":False,
    }
