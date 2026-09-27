"""GRD074 — read-only, role-scoped Grounds workspace projections for future UI.

Never accept a caller-supplied role or property grant. Every projection consumes
an already verified TowerScope and rechecks the corresponding Grounds domain
service. This file is NOT a Tower receiver, HTTP API, entitlement, payment
processor, resident screen, or live Soulaana model.
"""
from __future__ import annotations

from .access import AccessDenied, TowerScope
from .contract import ROOMS
from .leasing import GroundsLeasing
from .operations import GroundsOperations
from .owner_status import owner_operating_snapshot
from .soulaana import (
    explain_property_pulse, explain_resident_lease, explain_work_order,
)


def _work_card(item:dict, *, resident:bool=False)->dict:
    """Whitelist UI fields rather than passing an entire row to other roles."""
    fields=("work_ref","category","state","emergency_flag","updated_at")
    result={name:item[name] for name in fields}
    if not resident:
        result["revision"]=item["revision"]
        result["unit_ref"]=item["unit_ref"]
        result["entry_preference_is_not_legal_consent"]=True
    return result


def build_workspace(actor:TowerScope, operations:GroundsOperations, *,
                    property_ref:str, unit_ref:str|None=None)->dict:
    if not isinstance(operations,GroundsOperations):
        raise TypeError("GroundsOperations required")
    actor=operations._scope(actor)
    actor.require_property(property_ref)
    if actor.role not in ROOMS:
        raise AccessDenied("role unavailable")
    frame={
        "source":"grounds","source_mode":"local_domain_read_only",
        "role":actor.role,"property_ref":property_ref,
        "authenticated_by_tower_receiver":False,
        "payment_execution_enabled":False,
        "notification_delivery_enabled":False,
        "soulaana_action_enabled":False,
    }
    if actor.role=="resident":
        if not isinstance(unit_ref,str) or not unit_ref.strip():
            raise AccessDenied("current authorized resident unit required")
        home=operations.resident_home(actor,property_ref=property_ref,unit_ref=unit_ref)
        lease=home["lease"]
        explanation=explain_resident_lease(
            actor,operations,property_ref=property_ref,unit_ref=unit_ref,
        )
        return {**frame,
            "room":"resident_home","unit_ref":unit_ref,"unit_label":home["unit_label"],
            "lease":{"lease_ref":lease["lease_ref"],"start_on":lease["start_on"],
                     "end_on":lease["end_on"],"revision":lease["revision"]},
            "work_orders":[_work_card(x,resident=True) for x in home["maintenance"]],
            "notices":[{key:x[key] for key in
                        ("notice_ref","headline","body","published_at","read_in_app")}
                       for x in home["notices"]],
            "rent":{"source":"teller","status":"awaiting_verified_projection",
                    "amount_due_cents":None,"checkout_url":None},
            "soulaana":{"source":explanation["source"],
                        "message":explanation["message"],
                        "next_useful_action":explanation["next_useful_action"]},
        }
    if actor.role in ("maintenance_technician","property_manager","maintenance_supervisor"):
        jobs=operations.list_work_orders(actor,property_ref=property_ref)
        cards=[_work_card(x) for x in jobs]
        first=(explain_work_order(actor,operations,work_ref=jobs[0]["work_ref"])
               if jobs else None)
        projection={**frame,"room":"assigned_work" if actor.role=="maintenance_technician"
                    else "property_service_desk",
                    "work_orders":cards,
                    "soulaana":({"source":first["source"],"message":first["message"],
                                  "next_useful_action":first["next_useful_action"]}
                                 if first else None)}
        if actor.role=="property_manager":
            projection["property_pulse"]=operations.property_pulse(
                actor,property_ref=property_ref,
            )
        elif actor.role=="maintenance_supervisor":
            # A supervisor's work queue must not silently grant owner/manager
            # property intelligence or Teller financial administration.
            projection["open_assigned_property_work_count"]=sum(
                item["state"]!="closed" for item in cards
            )
        return projection
    if actor.role=="leasing_agent":
        leasing=GroundsLeasing(operations.store)
        units=leasing.availability(actor,property_ref=property_ref)
        return {**frame,"room":"leasing_office","units":units,
                "application_decisions_enabled":False,
                "actual_advertised_rent":None,
                "soulaana":{"source":"grounds","message":
                    "Availability reflects current recorded unit lifecycle only. "
                    "Applications, rent offers and approvals require certified sources.",
                    "next_useful_action":"Review authorized inventory and real evidence"}}
    if actor.role=="regional_manager":
        pulse=operations.property_pulse(actor,property_ref=property_ref)
        return {**frame,"room":"regional_property_summary",
                "property_pulse":{
                    key:pulse[key] for key in (
                        "units","occupied_units","open_work_orders",
                        "untriaged_urgent_work","open_turnovers",
                        "unresolved_serious_inspection_findings","source_observed_at",
                    )
                },"resident_details_included":False}
    if actor.role=="owner":
        pulse=owner_operating_snapshot(actor,operations,property_ref=property_ref)
        explanation=explain_property_pulse(actor,operations,property_ref=property_ref)
        return {**frame,"room":"owner_overview",
                "operating_snapshot":pulse,
                "soulaana":{"source":explanation["source"],
                            "message":explanation["message"],
                            "next_useful_action":explanation["next_useful_action"]}}
    # Assignments require distinct Tower grants not present in internal v1
    # TowerScope (e.g. inspection_ref, temporary vendor task, cleaning/project).
    return {**frame,"room":"assignment_certification_required",
            "locked":True,"record_count":None,
            "reason":"Tower task-specific entitlement and Grounds receiver not certified"}
