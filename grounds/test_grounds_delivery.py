"""GRD146–149: verified provider receipt and urgent human-escalation tests."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from grounds.access import AccessDenied
from grounds.delivery import GroundsDeliveryReceipts, SCHEMA_VERSION
from grounds.maintenance import MaintenanceIntake
from grounds.operations import GroundsConflict, GroundsOperations
from grounds.safety import GroundsSafety
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope


class DeliveryReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=GroundsStore(Path(self.tmp.name)/"fiction.sqlite3")
        self.store.initialize()
        self.ops=GroundsOperations(self.store)
        self.safety=GroundsSafety(self.store)
        self.receipts=GroundsDeliveryReceipts(self.store)
        self.owner=fixture_scope("owner","owner",("p1",))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.resident=fixture_scope("resident","resident",("p1",),("u1",))
        self.ops.record_closed_property(
            self.owner,property_ref="p1",name="Fictional Property",
            close_evidence={"status":"verified_closed","property_ref":"p1",
                            "proof_ref":"close-p1","owned_on":"2026-09-28"},
            close_verifier=lambda x:x, # TEST FIXTURE ONLY
        )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",unit_ref="u1",label="101")
        self.ops.activate_lease(
            self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",
            resident_ref="resident",start_on="2026-09-28",end_on="2027-09-27",
        )
        self.ops.submit_maintenance(
            self.resident,work_ref="urgent1",
            intake=MaintenanceIntake("p1","u1","plumbing","Synthetic leak",True,"contact_first"),
        )
        events=self.safety.pending_event_intents(self.manager,property_ref="p1")
        self.work_event=next(x for x in events if x["event_kind"]=="work_changed")
        self.urgent_event=next(
            x for x in events if x["event_kind"]=="urgent_intake_requires_human_review"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def payload(self,event,*,kind="notification_delivery",state="delivered",receipt="receipt-1",
                provider="provider-1"):
        return {
            "schema_version":SCHEMA_VERSION,"source":"tower_delivery_gateway",
            "audience":"grounds","kind":kind,"receipt_ref":receipt,
            "event_ref":event["event_ref"],"property_ref":"p1",
            "event_kind":event["event_kind"],"resource_ref":event["resource_ref"],
            "source_revision":event["source_revision"],
            "provider_receipt_ref":provider,"delivery_state":state,
            "observed_at":990,"expires_at":1100,
        }

    def record(self,payload):
        return self.receipts.record(
            payload,receipt_verifier=lambda doc:doc,now=1000, # TEST FIXTURE ONLY
        )

    def test_verified_notification_receipt_is_append_only_and_idempotent(self):
        item=self.payload(self.work_event)
        first=self.record(item)
        self.assertTrue(first["recorded"])
        self.assertFalse(first["replayed"])
        self.assertFalse(first["legal_service_proven"])
        replay=self.record(item)
        self.assertTrue(replay["replayed"])
        changed=dict(item);changed["delivery_state"]="failed"
        with self.assertRaises(GroundsConflict):
            self.record(changed)
        status=self.receipts.property_status(self.manager,property_ref="p1")
        self.assertEqual(status["verified_receipt_count"],1)
        self.assertEqual(status["delivered_event_count"],1)
        self.assertEqual(status["failed_receipt_count"],0)
        self.assertFalse(status["provider_connection_currently_verified"])

    def test_urgent_human_ack_requires_exact_urgent_outbox_event(self):
        bad=self.payload(
            self.work_event,kind="urgent_human_escalation",
            state="human_acknowledged",receipt="urgent-bad",provider="urgent-provider-bad",
        )
        with self.assertRaises(AccessDenied):
            self.record(bad)
        good=self.payload(
            self.urgent_event,kind="urgent_human_escalation",
            state="human_acknowledged",receipt="urgent-good",provider="urgent-provider-good",
        )
        saved=self.record(good)
        self.assertEqual(saved["delivery_state"],"human_acknowledged")
        self.assertFalse(saved["emergency_services_contacted"])
        triage=self.safety.triage_status(self.resident,work_ref="urgent1")
        self.assertTrue(triage["human_escalation_acknowledged"])
        self.assertFalse(triage["external_dispatch_confirmed"])
        status=self.safety.delivery_status(self.manager,property_ref="p1")
        self.assertEqual(status["urgent_human_acknowledged_event_count"],1)
        self.assertFalse(status["emergency_dispatch_confirmed"])
        self.assertFalse(status["legal_service_proven"])

    def test_receipt_must_match_existing_exact_event_and_fresh_gateway_proof(self):
        wrong=self.payload(self.work_event)
        wrong["resource_ref"]="other-work"
        with self.assertRaises(AccessDenied):
            self.record(wrong)
        stale=self.payload(self.work_event,receipt="stale",provider="stale-provider")
        stale["observed_at"]=500;stale["expires_at"]=800
        with self.assertRaises(AccessDenied):
            self.record(stale)
        spoof=self.payload(self.work_event,receipt="spoof",provider="spoof-provider")
        spoof["source"]="sms-provider-direct"
        with self.assertRaises(AccessDenied):
            self.record(spoof)
        with self.assertRaises(AccessDenied):
            self.receipts.record(self.payload(self.work_event),receipt_verifier=None,now=1000)

    def test_provider_receipt_reference_cannot_be_reused_for_another_event(self):
        first=self.payload(self.work_event,receipt="receipt-a",provider="shared-provider-ref")
        self.record(first)
        second=self.payload(
            self.urgent_event,kind="urgent_human_escalation",state="queued",
            receipt="receipt-b",provider="shared-provider-ref",
        )
        with self.assertRaises(GroundsConflict):
            self.record(second)


if __name__=="__main__":
    unittest.main()
