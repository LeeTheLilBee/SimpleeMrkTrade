"""Registry-wide diligence is source-grounded and cannot verify or contact sellers."""
from __future__ import annotations

import unittest
from copy import deepcopy

from buybox.registry import VERTICALS, get_vertical
from buybox.core import add_evidence, new_opportunity
from buybox.dealroom import current_tasks, update_task
from buybox.diligence import (
    DiligenceError, WORKSTREAM, diligence_snapshot, create_diligence_task,
)
from buybox.soulaana import context


class DiligenceTests(unittest.TestCase):
    def test_every_registered_vertical_uses_its_exact_evidence_manifest(self):
        for vertical in VERTICALS:
            with self.subTest(vertical=vertical):
                op=new_opportunity(vertical,"Owner entered asset")
                work=diligence_snapshot(op)
                requirements=get_vertical(vertical)["evidence"]
                self.assertEqual(
                    [r["kind"] for r in work["requirements"]],
                    [r["kind"] for r in requirements])
                self.assertEqual(work["total_requirements"],len(requirements))
                self.assertEqual(work["critical_outstanding"],
                                 sum(bool(r["critical"]) for r in requirements))
                self.assertEqual(work["documentary_supported_count"],0)
                self.assertEqual(work["actual_source_count"],0)
                self.assertEqual(work["open_owner_tasks"],0)
                self.assertFalse(work["fully_verified_or_authorized"])
                self.assertFalse(work["seller_contact_sent"])
                self.assertFalse(work["vault_archive_claimed"])

    def test_owner_deadline_adds_actual_task_once_without_sending(self):
        op=new_opportunity("atm","Document request")
        before=deepcopy(op)
        revised,task=create_diligence_task(
            op,evidence_kind="processor_statements",
            due_date="2026-10-02",owner_actor="local_owner",
            notes="Request actual processor statement")
        self.assertEqual(op,before)
        self.assertEqual(task["workstream"],WORKSTREAM)
        self.assertEqual(task["evidence_kind"],"processor_statements")
        self.assertEqual(task["due_date"],"2026-10-02")
        self.assertEqual(task["created_against_opportunity_revision"],op["version"])
        self.assertEqual(task["owner"],"local_owner")
        self.assertFalse(task["does_not_contact_seller"] is False)
        self.assertTrue(task["does_not_verify_evidence"])
        self.assertTrue(task["does_not_authorize_purchase"])
        self.assertEqual(len(current_tasks(revised)),1)
        self.assertEqual(diligence_snapshot(revised)["open_owner_tasks"],1)
        with self.assertRaisesRegex(DiligenceError,"EXISTING_OPEN_DILIGENCE_TASK"):
            create_diligence_task(revised,evidence_kind="processor_statements",
                due_date="2026-10-03",owner_actor="local_owner")

    def test_task_status_is_not_evidence_status_and_new_task_after_completion(self):
        op=new_opportunity("multifamily","Actual property")
        op,task=create_diligence_task(
            op,evidence_kind="rent_roll",due_date="2026-10-03",
            owner_actor="tower-actor-verified-in-route")
        updated,revision=update_task(op,task_id=task["id"],status="COMPLETE",
                                     notes="Owner completed her follow-up")
        queue=diligence_snapshot(updated)
        row=next(r for r in queue["requirements"] if r["kind"]=="rent_roll")
        self.assertEqual(row["recorded_state"],"MISSING")
        self.assertEqual(row["open_tasks"],[])
        self.assertEqual(queue["documentary_supported_count"],0)
        self.assertEqual(revision["workstream"],WORKSTREAM)
        self.assertEqual(revision["evidence_kind"],"rent_roll")
        _,followup=create_diligence_task(
            updated,evidence_kind="rent_roll",due_date="2026-10-10",
            owner_actor="tower-actor-verified-in-route")
        self.assertNotEqual(followup["id"],task["id"])

    def test_received_is_not_document_supported_or_auto_task_completion(self):
        op=new_opportunity("atm","Source status")
        op,task=create_diligence_task(op,evidence_kind="machine_inventory",
            due_date="2026-10-05",owner_actor="local_owner")
        source=add_evidence(op,"machine_inventory",status="RECEIVED",
                            reference="owner-supplied-source-1",source="Seller")
        row=next(x for x in diligence_snapshot(op)["requirements"]
                 if x["kind"]=="machine_inventory")
        self.assertEqual(row["recorded_state"],"RECEIVED")
        self.assertFalse(row["documentary_supported"])
        self.assertEqual(row["evidence_id"],source["id"])
        self.assertEqual(len(row["open_tasks"]),1)
        reviewed=add_evidence(op,"machine_inventory",status="DOCUMENT_SUPPORTED",
                             reference="owner-supplied-source-2",source="Seller")
        row=next(x for x in diligence_snapshot(op)["requirements"]
                 if x["kind"]=="machine_inventory")
        self.assertEqual(row["recorded_state"],"DOCUMENT_SUPPORTED")
        self.assertTrue(row["documentary_supported"])
        self.assertEqual(row["evidence_id"],reviewed["id"])
        self.assertEqual(len(row["open_tasks"]),1)
        with self.assertRaisesRegex(DiligenceError,"ALREADY_DOCUMENT_SUPPORTED"):
            create_diligence_task(op,evidence_kind="machine_inventory",
                due_date="2026-10-06",owner_actor="local_owner")
        self.assertEqual(op["tasks"][0]["status"],"OPEN")

    def test_reject_unknown_category_invalid_date_and_empty_owner(self):
        op=new_opportunity("land_farm","Parcel")
        for change,pattern in [
            ({"evidence_kind":"fake-document"},"UNREGISTERED"),
            ({"owner_actor":""},"VERIFIED_OWNER"),
            ({"due_date":"tomorrow"},"DEADLINE"),
            ({"due_date":"20261003"},"DEADLINE"),
            ({"notes":"x"*1001},"INVALID_OWNER_NOTES"),
        ]:
            fields={"evidence_kind":"survey","due_date":"2026-10-03",
                    "owner_actor":"local_owner","notes":""}
            fields.update(change)
            with self.subTest(change=change):
                with self.assertRaisesRegex(DiligenceError,pattern):
                    create_diligence_task(op,**fields)

    def test_soulaana_diligence_uses_recorded_missing_and_real_owner_due_date(self):
        op=new_opportunity("equipment","Owned equipment lot")
        op,task=create_diligence_task(op,evidence_kind="asset_schedule",
            due_date="2026-10-07",owner_actor="local_owner")
        result=context(op,"diligence")
        self.assertEqual(result["intent"],"diligence")
        self.assertFalse(result["can_authorize"])
        self.assertFalse(result["live_ai_connected"])
        self.assertTrue(any(x["classification"]=="DILIGENCE_REQUIREMENT"
                            and x["label"]=="CRITICAL_OPEN" for x in result["entries"]))
        owner_tasks=[x for x in result["entries"]
                     if x["classification"]=="OWNER_RECORDED_TASK"]
        self.assertTrue(any(task["id"] in x["references"] and
                            "2026-10-07" in x["text"] for x in owner_tasks))
        self.assertTrue(any("does not imply independent verification" in x["text"]
                            for x in result["entries"]))

if __name__=="__main__":
    unittest.main()
