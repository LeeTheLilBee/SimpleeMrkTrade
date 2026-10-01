"""BBX047–051 — real, registry-driven owner diligence workbench.

The workbench derives current document requirements from the seven versioned
vertical manifests and actually saved evidence. It never generates fake seller
documents, marks evidence verified, sends messages or completes owner tasks.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date
from .registry import get_vertical
from .dealroom import new_task, current_tasks

SUPPORTED_STATES = frozenset({"DOCUMENT_SUPPORTED", "THIRD_PARTY_VERIFIED"})
WORKSTREAM = "EVIDENCE_DILIGENCE"


class DiligenceError(ValueError):
    pass


def _latest_evidence(op, kind):
    matching = [(i, e) for i, e in enumerate(op.get("evidence", []))
                if isinstance(e, dict) and e.get("kind") == kind
                and e.get("status") != "SUPERSEDED"]
    if not matching:
        return None
    # The recorded timestamp is a provenance indicator. Equal timestamps
    # resolve by append order, not by guessing which source is more truthful.
    return max(matching, key=lambda pair: (pair[1].get("observed_at") or "",
                                           pair[0]))[1]


def diligence_snapshot(op):
    """A current owner checklist, not authorization or archival certification."""
    manifest = get_vertical(op["vertical"])
    active = current_tasks(op)
    rows = []
    for requirement in manifest["evidence"]:
        kind = requirement["kind"]
        evidence = _latest_evidence(op, kind)
        state = evidence.get("status", "MISSING") if evidence else "MISSING"
        tasks = [t for t in active if t.get("workstream") == WORKSTREAM
                 and t.get("evidence_kind") == kind]
        pending = [t for t in tasks if t["status"] in ("OPEN", "WAITING")]
        rows.append({
            "kind": kind,
            "critical": bool(requirement["critical"]),
            "weight": requirement["weight"],
            "recorded_state": state,
            "documentary_supported": state in SUPPORTED_STATES,
            "evidence_id": evidence.get("id") if evidence else None,
            "source_reference": evidence.get("reference") if evidence else None,
            "source_party": evidence.get("source") if evidence else None,
            "artifact_id": evidence.get("artifact_id") if evidence else None,
            "open_tasks": deepcopy(pending),
            "task_count": len(tasks),
        })
    return {
        "opportunity_id": op["id"], "opportunity_revision": op.get("version"),
        "vertical": op["vertical"], "manifest_version": manifest["version"],
        "requirements": rows, "total_requirements": len(rows),
        "documentary_supported_count": sum(r["documentary_supported"] for r in rows),
        "critical_outstanding": sum(r["critical"] and not r["documentary_supported"]
                                     for r in rows),
        "open_owner_tasks": sum(len(r["open_tasks"]) for r in rows),
        "actual_source_count": sum(r["evidence_id"] is not None for r in rows),
        "fully_verified_or_authorized": False,
        "seller_contact_sent": False, "teller_readiness": "UNKNOWN",
        "vault_archive_claimed": False,
    }


def create_diligence_task(op, *, evidence_kind, due_date, owner_actor, notes=""):
    """Owner elects an actual deadline; never auto-sends a seller request.

    One pending task per requirement avoids duplicate generated reminders.
    Completing a task does not change evidence, and receiving evidence does not
    silently complete or reschedule the task.
    """
    manifest = get_vertical(op["vertical"])
    if evidence_kind not in {r["kind"] for r in manifest["evidence"]}:
        raise DiligenceError("UNREGISTERED_EVIDENCE_REQUIREMENT")
    if not isinstance(owner_actor, str) or not owner_actor.strip():
        raise DiligenceError("VERIFIED_OWNER_REFERENCE_REQUIRED")
    if not isinstance(notes, str) or len(notes) > 1000:
        raise DiligenceError("INVALID_OWNER_NOTES")
    snapshot = diligence_snapshot(op)
    record = next(r for r in snapshot["requirements"] if r["kind"] == evidence_kind)
    if record["documentary_supported"]:
        raise DiligenceError("REQUIREMENT_ALREADY_DOCUMENT_SUPPORTED")
    if record["open_tasks"]:
        raise DiligenceError("EXISTING_OPEN_DILIGENCE_TASK")
    try:
        day = date.fromisoformat(due_date)
        if day.isoformat() != due_date:
            raise ValueError
    except (TypeError, ValueError):
        raise DiligenceError("OWNER_DEADLINE_REQUIRED") from None
    title = "Request/review " + evidence_kind.replace("_", " ") + " for " + op["name"]
    if len(title) > 180:
        title = title[:177].rstrip() + "..."
    revised, task = new_task(
        op, title=title, due_date=due_date, owner=owner_actor,
        source_reference="REGISTRY_REQUIREMENT:" + evidence_kind,
        notes=notes,
    )
    task.update({
        "workstream": WORKSTREAM,
        "evidence_kind": evidence_kind,
        "requirement_registry_version": manifest["version"],
        "created_against_opportunity_revision": op["version"],
        "source_evidence_id_at_creation": record["evidence_id"],
        "does_not_contact_seller": True,
        "does_not_verify_evidence": True,
        "does_not_authorize_purchase": True,
    })
    return revised, deepcopy(task)
