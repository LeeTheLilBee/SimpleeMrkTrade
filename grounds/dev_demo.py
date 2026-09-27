"""GRD072 — explicit one-command, offline, *fictional* Grounds owner demonstration.

Run: python -m grounds.dev_demo --fictional-only

This imports NO live data, opens NO web port, sends NO network requests and
creates NO accounts or persistent fixtures. It executes the same domain services
as the source-only Grounds implementation against a disposable local SQLite
fixture. Every fake verifier in this module exists solely for synthetic testing.
Never import this module in a hosted service or reuse its fake validators.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import time

from .access import AccessDenied, verified_scope
from .communications import GroundsCommunications
from .dev_integrity import inspect_local_store
from .maintenance import MaintenanceIntake
from .operations import GroundsOperations, GroundsConflict
from .owner_status import owner_operating_snapshot
from .safety import GroundsSafety
from .soulaana import (
    explain_appointment, explain_property_pulse, explain_verified_resident_rent,
    explain_work_order, explain_work_resources,
)
from .storage import GroundsStore
from .work_resources import GroundsWorkResources


def _fictional_scope(subject: str, role: str, *,
                     units: tuple[str,...]=(), assignments:tuple[str,...]=()):
    stamp=int(time())
    claims={
        "issuer":"tower","audience":"grounds","subject_ref":subject,"role":role,
        "session_ref":"FAKE-NONPRODUCTION-DEMO-SESSION",
        "property_refs":["fictional-p"],"unit_refs":list(units),
        "assigned_work_refs":list(assignments),"issued_at":stamp-1,"expires_at":stamp+180,
    }
    return verified_scope(claims,verifier=lambda x:x) # FICTION-ONLY IN PROCESS


def run_fictional_demo() -> dict:
    """Use only known synthetic constants and a temporary automatically removed DB."""
    with tempfile.TemporaryDirectory(prefix="grounds_fictional_only_") as directory:
        store=GroundsStore(Path(directory)/"synthetic.sqlite3")
        store.initialize()
        ops=GroundsOperations(store)
        comm=GroundsCommunications(store)
        safety=GroundsSafety(store)
        resources=GroundsWorkResources(store)
        owner=_fictional_scope("FICTITIOUS_OWNER","owner")
        manager=_fictional_scope("FICTITIOUS_MANAGER","property_manager")
        resident=_fictional_scope("FICTITIOUS_RESIDENT","resident",units=("fictional-u",))
        other=_fictional_scope("UNAUTHORIZED_DEMO_PERSON","resident",units=("fictional-u",))
        tech=_fictional_scope("FICTITIOUS_TECH","maintenance_technician",assignments=("fictional-job",))
        ops.record_closed_property(
            owner,property_ref="fictional-p",name="Fictional Garden Property",
            close_evidence={"status":"verified_closed","property_ref":"fictional-p",
                            "proof_ref":"FAKE_CLOSE_PROOF_NOT_FOR_PRODUCTION",
                            "owned_on":"2026-09-26"},
            close_verifier=lambda x:x, # FICTION-ONLY IN PROCESS
        )
        ops.add_building(manager,property_ref="fictional-p",
                         building_ref="fictional-b",label="Demo Building")
        ops.add_unit(manager,property_ref="fictional-p",
                     building_ref="fictional-b",unit_ref="fictional-u",label="Fictional 101")
        ops.activate_lease(
            manager,property_ref="fictional-p",unit_ref="fictional-u",
            lease_ref="fictional-lease",resident_ref="FICTITIOUS_RESIDENT",
            start_on="2026-09-26",end_on="2027-09-25",
        )
        ops.publish_notice(
            manager,property_ref="fictional-p",notice_ref="fictional-notice",
            headline="Fictional maintenance update",body="Demo-only communication",
        )
        receipt=comm.mark_notice_read(
            resident,property_ref="fictional-p",unit_ref="fictional-u",
            notice_ref="fictional-notice",
        )
        intake=MaintenanceIntake(
            "fictional-p","fictional-u","plumbing","Synthetic demo faucet issue",
            True,"contact_first",
        )
        created=ops.submit_maintenance(resident,work_ref="fictional-job",intake=intake)
        blocked_untriaged=False
        try:
            ops.advance_work_order(
                manager,work_ref="fictional-job",next_state="received",expected_revision=1,
            )
        except GroundsConflict:
            blocked_untriaged=True
        triage=safety.acknowledge_urgency(
            manager,work_ref="fictional-job",assessed_urgency="priority",
        )
        revision=1
        for stage in ("received","under_review","scheduled"):
            revision=ops.advance_work_order(
                manager,work_ref="fictional-job",next_state=stage,
                expected_revision=revision,
            )["revision"]
        revision=ops.assign_work_order(
            manager,work_ref="fictional-job",technician=tech,
            expected_revision=revision,
        )["revision"]
        safety.record_entry_preference(
            resident,work_ref="fictional-job",preference="no",expected_revision=0,
        )
        blocked_entry=False
        try:
            ops.advance_work_order(
                tech,work_ref="fictional-job",next_state="in_progress",
                expected_revision=revision,
            )
        except GroundsConflict:
            blocked_entry=True
        safety.record_entry_preference(
            resident,work_ref="fictional-job",preference="contact_first",
            expected_revision=1,
        )
        revision=ops.advance_work_order(
            tech,work_ref="fictional-job",next_state="in_progress",
            expected_revision=revision,
        )["revision"]
        resources.record(
            tech,work_ref="fictional-job",resource_type="material",
            label="Demo washer",quantity=2,
        )
        resources.record(
            tech,work_ref="fictional-job",resource_type="labor",
            label="Demo visual check",quantity=25,
        )
        window=datetime.now(timezone.utc)+timedelta(days=3)
        initial=comm.request_appointment(
            resident,work_ref="fictional-job",appointment_ref="fictional-appointment",
            start_at=window.isoformat(),end_at=(window+timedelta(hours=2)).isoformat(),
        )
        proposed=comm.propose_appointment(
            manager,appointment_ref="fictional-appointment",
            start_at=window.isoformat(),end_at=(window+timedelta(hours=2)).isoformat(),
            expected_revision=initial["revision"],
        )
        accepted=comm.accept_appointment(
            resident,appointment_ref="fictional-appointment",
            expected_revision=proposed["revision"],
        )
        unauthorized_denied=False
        try:
            ops.resident_home(other,property_ref="fictional-p",unit_ref="fictional-u")
        except AccessDenied:
            unauthorized_denied=True
        now=int(time())
        faux_teller={
            "source":"teller","audience":"grounds","resident_ref":"FICTITIOUS_RESIDENT",
            "property_ref":"fictional-p","unit_ref":"fictional-u",
            "lease_ref":"fictional-lease",
            "observed_at":now,"expires_at":now+120,
            "amount_due_cents":120000,"currency":"USD","invoice_status":"due",
            "due_on":"2027-01-01","teller_handoff_ref":None,
        }
        rent=explain_verified_resident_rent(
            resident,ops,faux_teller,property_ref="fictional-p",unit_ref="fictional-u",
            teller_verifier=lambda x:x, # FICTION-ONLY IN PROCESS
        )
        integrity=inspect_local_store(store)
        pulse=owner_operating_snapshot(owner,ops,property_ref="fictional-p")
        return {
            "mode":"FICTIONAL_OFFLINE_DEVELOPER_DEMO_ONLY",
            "scenario":"Local developer walk-through, not a tenant beta",
            "property_ref":"fictional-p",
            "checks":{
                "untriaged_urgent_transition_blocked":blocked_untriaged,
                "human_triage_acknowledged":triage["human_review_recorded"],
                "explicit_no_entry_work_start_blocked":blocked_entry,
                "unlisted_same_unit_subject_denied":unauthorized_denied,
                "notice_read_is_not_delivery":not receipt["delivery_confirmed"],
                "appointment_accepted_not_entry_authorization":
                    accepted["state"]=="accepted" and not accepted["entry_consent_granted"],
                "resident_teller_explanation_did_not_execute_checkout":
                    rent["source"]=="teller" and not rent["checkout_executed"],
                "sqlite_integrity_and_invariants_passed":integrity["healthy"],
            },
            "resident_status":{
                "maintenance":created["state"],
                "appointment":accepted["state"],
                "soulaana_work":explain_work_order(
                    resident,ops,work_ref="fictional-job",
                )["message"],
                "soulaana_appointment":explain_appointment(
                    resident,comm,appointment_ref="fictional-appointment",
                )["message"],
                "rent":"fictional, test-only Teller projection; checkout unavailable",
            },
            "staff_status":{
                "resource_summary":resources.summary(manager,work_ref="fictional-job"),
                "soulaana":explain_work_resources(
                    manager,resources,work_ref="fictional-job",
                )["message"],
            },
            "owner_status":{
                "physical_counts":pulse["counts"],
                "soulaana":explain_property_pulse(
                    owner,ops,property_ref="fictional-p",
                )["message"],
            },
            "external_services_connected":False,
            "network_requests_sent":False,
            "checkout_enabled":False,
            "notification_delivery_enabled":False,
            "emergency_dispatch_enabled":False,
            "file_persisted_after_exit":False,
            "production_identity_verification_performed":False,
        }


def main(argv: list[str]|None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fictional-only",action="store_true",
                        help="I understand the scenario is fake, offline and disposable")
    args=parser.parse_args(argv)
    if not args.fictional_only:
        parser.error("explicit --fictional-only acknowledgment is required")
    result=run_fictional_demo()
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if all(result["checks"].values()) else 1


if __name__=="__main__":
    raise SystemExit(main())
