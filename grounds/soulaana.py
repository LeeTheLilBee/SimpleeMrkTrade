"""GRD022 — Soulaana explanations grounded in authorized Grounds/Teller projections.

Read-only, deterministic owner/resident helper. This layer never grants access,
queries OB, performs financial actions, decides applications, or bypasses rules.
It takes a GroundsOperations instance to enforce the normal scoped read.
"""
from __future__ import annotations

from typing import Callable, Mapping

from .access import TowerScope, AccessDenied
from .operations import GroundsOperations
from .communications import GroundsCommunications
from .capital import verified_apartment_readiness
from .leasing import GroundsLeasing
from .stewardship import GroundsStewardship
from .teller import resident_rent_projection

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


# Only deterministic, source-limited explanations are supported in this pack.
# A live conversational/voice model is NOT integrated and cannot be substituted
# for access control, emergency service or an actual payment/dispatch service.

def explain_resident_lease(actor: TowerScope, operations: GroundsOperations, *,
                           property_ref: str, unit_ref: str) -> dict:
    """Use the current active membership-verified resident Home, never caller data."""
    home=operations.resident_home(actor,property_ref=property_ref,unit_ref=unit_ref)
    lease=home["lease"]
    return {
        "speaker":"Soulaana","source":"grounds","property_ref":property_ref,
        "unit_ref":unit_ref,"lease_ref":lease["lease_ref"],
        "source_revision":lease["revision"],
        "message":"Your current Grounds lease context runs from "+
                  lease["start_on"]+" through "+lease["end_on"]+
                  ". Document access and any renewal terms require the certified Tower/Vault workflow.",
        "next_useful_action":"Review your lease record or contact the property desk",
        "actual_lease_document_loaded":False,"renewal_approved":False,
        "payment_executed":False,
    }


def explain_verified_resident_rent(
    actor:TowerScope,operations:GroundsOperations, signed_message:object,*,
    property_ref:str,unit_ref:str,teller_verifier:Callable[[object],Mapping],
    now:int|None=None,
)->dict:
    """The service obtains Grounds membership and verifies fresh Teller truth itself."""
    home=operations.resident_home(actor,property_ref=property_ref,unit_ref=unit_ref)
    rent=resident_rent_projection(actor,home,signed_message,
                                  teller_verifier=teller_verifier,now=now)
    state=rent["invoice_status"]
    explain={
        "due":"Teller currently reports an amount due.",
        "partial":"Teller reports a partially paid invoice; the remaining amount comes from Teller.",
        "paid":"Teller reports this invoice as paid.",
        "overdue":"Teller reports this invoice as overdue; ask the property desk or Teller for options.",
        "credit":"Teller reports a credit status; Grounds does not determine a refund.",
        "pending":"Teller reports a pending transaction; do not assume it has settled.",
    }
    return {
        "speaker":"Soulaana","source":"teller",
        "property_ref":property_ref,"unit_ref":unit_ref,
        "lease_ref":home["lease"]["lease_ref"],
        "invoice_status":state,"amount_due_cents":rent["amount_due_cents"],
        "due_on":rent["due_on"],"observed_at":rent["observed_at"],
        "expires_at":rent["expires_at"],
        "message":explain[state]+" Grounding is limited to this fresh, scoped projection.",
        "next_useful_action":("Request Tower-mediated Teller checkout"
                              if rent["teller_handoff_ref"] else
                              "Check Teller or contact the property desk"),
        "checkout_url":None,"checkout_executed":False,
        "autopay_modified":False,"funds_transferred":False,
    }


def explain_verified_apartment_readiness(
    actor:TowerScope,signed_snapshot:object,*,property_ref:str,
    mission_ref:str,terms_digest:str,
    teller_verifier:Callable[[object],Mapping],now:int|None=None,
)->dict:
    """Only this verification-first entrypoint accepts untrusted external snapshots."""
    projection=verified_apartment_readiness(
        actor,signed_snapshot,property_ref=property_ref,mission_ref=mission_ref,
        terms_digest=terms_digest,teller_verifier=teller_verifier,now=now,
    )
    result=explain_apartment_readiness(actor,projection)
    result["observed_at"]=projection["observed_at"]
    result["expires_at"]=projection["expires_at"]
    return result


def explain_appointment(actor:TowerScope,communications:GroundsCommunications,*,
                        appointment_ref:str)->dict:
    item=communications.appointment(actor,appointment_ref=appointment_ref)
    details={
        "requested":"You proposed a window. The property desk has not confirmed a slot.",
        "proposed":"The property desk proposed a window. The requester can accept or cancel.",
        "accepted":"The requester accepted this proposed window in Grounds.",
        "cancelled":"This in-app appointment was cancelled.",
    }
    return {
        "speaker":"Soulaana","source":"grounds","appointment_ref":appointment_ref,
        "work_ref":item["work_ref"],"source_revision":item["revision"],
        "source_state":item["state"],"window_start":item["start_at"],
        "window_end":item["end_at"],"message":details[item["state"]]+
          " This is not proof of entry consent, legal notice, external dispatch or message delivery.",
        "next_useful_action":"Verify entry permission and actual staff confirmation through Grounds",
        "entry_consent_granted":False,"calendar_synced":False,"notice_delivered":False,
        "action_executed":False,
    }


def explain_inspection(actor:TowerScope,stewardship:GroundsStewardship,*,
                       property_ref:str,inspection_ref:str)->dict:
    item=stewardship.inspection_summary(
        actor,property_ref=property_ref,inspection_ref=inspection_ref,
    )
    severe=item["unresolved_major_or_urgent"]
    message=(
        "This inspection has "+str(severe)+
        " unresolved major or urgent findings. Certified finding-specific remediation "
        "is required before it can be closed."
        if severe else
        "Inspection status is "+item["state"]+
        "; recorded findings: "+str(item["findings_count"])+
        ". This source summary is not a legal or regulatory inspection certification."
    )
    return {
        "speaker":"Soulaana","source":"grounds","inspection_ref":inspection_ref,
        "property_ref":property_ref,"source_revision":item["revision"],
        "source_state":item["state"],"unresolved_major_or_urgent":severe,
        "message":message,
        "next_useful_action":("Review severe findings and certified resolution evidence"
                              if severe else "Open scoped inspection details"),
        "inspection_closed_by_assistant":False,"notice_delivered":False,
    }


def explain_turnover(actor:TowerScope,stewardship:GroundsStewardship,*,
                     property_ref:str,turnover_ref:str)->dict:
    item=stewardship.turnover_summary(
        actor,property_ref=property_ref,turnover_ref=turnover_ref,
    )
    if item["inspection_state"]!="closed":
        message="This unit turnover still needs its own completed, linked inspection."
        next_action="Complete and review the linked turnover inspection"
    elif item["open_unit_work_orders"]:
        message="This turnover has "+str(item["open_unit_work_orders"])+" open unit work orders."
        next_action="Review outstanding work before final review"
    elif item["state"]=="final_review" and not item["final_sealed_proof_present"]:
        message="The turnover is in final review; the exact-turnover sealed proof is still missing."
        next_action="Obtain certified final Vault evidence and owner/manager review"
    elif item["state"]=="complete":
        message="Grounds records the turnover as completed; staff must independently confirm external availability."
        next_action="Review unit readiness and leasing handoff"
    else:
        message="Turnover stage is "+item["state"]+". Complete the next protected step before changing unit readiness."
        next_action="Review the next stage and requirements"
    return {
        "speaker":"Soulaana","source":"grounds","turnover_ref":turnover_ref,
        "property_ref":property_ref,"unit_ref":item["unit_ref"],
        "source_revision":item["revision"],"source_state":item["state"],
        "message":message,"next_useful_action":next_action,
        "open_work_orders":item["open_unit_work_orders"],
        "action_executed":False,"leasing_advertised":False,"payment_executed":False,
    }


def explain_leasing_unit(actor:TowerScope,leasing:GroundsLeasing,*,
                         property_ref:str,unit_ref:str)->dict:
    available=leasing.availability(actor,property_ref=property_ref)
    item=next((record for record in available if record["unit_ref"]==unit_ref),None)
    if item is None:
        raise AccessDenied("unit unavailable")
    state=item["lifecycle"]
    return {
        "speaker":"Soulaana","source":"grounds","property_ref":property_ref,
        "unit_ref":unit_ref,"lifecycle":state,
        "message":"Grounds currently records this unit as "+state+
                  ". This is an operational status, not an approved advertised rent, "
                  "application decision or certified move-in offer.",
        "next_useful_action":"Verify unit conditions, policies, and leasing approval",
        "applicant_screened":False,"rental_rate_generated":False,
    }


def explain_property_pulse(actor:TowerScope,operations:GroundsOperations,*,
                           property_ref:str)->dict:
    pulse=operations.property_pulse(actor,property_ref=property_ref)
    return {
        "speaker":"Soulaana","source":"grounds","property_ref":property_ref,
        "units":pulse["units"],"occupied_units":pulse["occupied_units"],
        "open_work_orders":pulse["open_work_orders"],
        "message":str(pulse["occupied_units"])+" of "+str(pulse["units"])+
                  " units have occupied lifecycle status, with "+
                  str(pulse["open_work_orders"])+" not-closed work records. "
                  "Actual rent collections and deployable capital are Teller-owned.",
        "next_useful_action":"Review assigned property work and verify Teller financial status",
        "rent_collections":None,"ob_queried":False,"capital_approved":False,
    }
