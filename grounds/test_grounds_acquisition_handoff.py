"""GRD142–145: verified post-close acceptance, replay and scope regressions."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from grounds.access import AccessDenied
from grounds.acquisition_handoff import GroundsAcquisitionHandoff, SCHEMA_VERSION
from grounds.operations import GroundsConflict
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope


class AcquisitionHandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=GroundsStore(Path(self.tmp.name)/"fiction.sqlite3")
        self.store.initialize()
        self.receiver=GroundsAcquisitionHandoff(self.store)
        self.owner=fixture_scope("owner","owner",("p1","p2"))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.other_owner=fixture_scope("other","owner",("p2",))
        self.payload={
            "schema_version":SCHEMA_VERSION,
            "source":"tower","audience":"grounds","kind":"multifamily_post_close",
            "handoff_ref":"handoff-1","owner_ref":"owner",
            "property_ref":"p1","property_name":"Fictional Gardens",
            "owned_on":"2026-09-28","opportunity_id":"opp-1",
            "opportunity_revision":7,
            "input_snapshot_digest":"a"*64,
            "proposal_fingerprint":"b"*64,
            "vertical_id":"multifamily","proposed_recipient":"grounds",
            "closing_status":"completed","ownership_status":"verified_owner",
            "encumbrance_status":"verified_recorded",
            "tower_close_receipt_ref":"tower-close-1",
            "title_proof_ref":"title-proof-1",
            "encumbrance_review_ref":"encumbrance-review-1",
            "issued_at":990,"expires_at":1100,
        }

    def tearDown(self):
        self.tmp.cleanup()

    def accept(self,payload=None,actor=None,verifier=None):
        item=self.payload if payload is None else payload
        return self.receiver.accept_multifamily_close(
            self.owner if actor is None else actor,
            signed_handoff=item,
            tower_verifier=(lambda document:document) if verifier is None else verifier,
            now=1000,
        )

    def test_verified_close_creates_one_property_and_full_lineage(self):
        result=self.accept()
        self.assertTrue(result["accepted"])
        self.assertFalse(result["replayed"])
        self.assertFalse(result["money_moved"])
        self.assertFalse(result["payment_authorized"])
        with self.store.transaction() as db:
            prop=db.execute(
                "SELECT property_ref,name,owned_on,close_proof_ref FROM properties WHERE property_ref=?",
                ("p1",),
            ).fetchone()
            self.assertEqual(dict(prop),{
                "property_ref":"p1","name":"Fictional Gardens",
                "owned_on":"2026-09-28","close_proof_ref":"tower-close-1",
            })
            receipt=db.execute(
                "SELECT * FROM property_acquisition_receipts WHERE property_ref=?",("p1",),
            ).fetchone()
            self.assertEqual(receipt["opportunity_revision"],7)
            self.assertEqual(receipt["proposal_fingerprint"],"b"*64)
            self.assertEqual(receipt["title_proof_ref"],"title-proof-1")
            self.assertEqual(receipt["encumbrance_review_ref"],"encumbrance-review-1")
        view=self.receiver.accepted_receipt(self.manager,property_ref="p1")
        self.assertEqual(view["status"],"accepted_verified_close")
        self.assertFalse(view["raw_close_document_included"])
        self.assertFalse(view["money_moved"])

    def test_exact_retry_is_idempotent_but_changed_replay_fails(self):
        first=self.accept()
        repeat=self.accept()
        self.assertEqual(first["property_ref"],repeat["property_ref"])
        self.assertTrue(repeat["replayed"])
        with self.store.transaction() as db:
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM properties WHERE property_ref='p1'"
            ).fetchone()[0],1)
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM property_acquisition_receipts WHERE property_ref='p1'"
            ).fetchone()[0],1)
        changed=dict(self.payload)
        changed["property_name"]="Changed after receipt"
        with self.assertRaises(GroundsConflict):
            self.accept(changed)

    def test_local_acquired_label_or_buybox_proposal_is_never_close_authority(self):
        local={
            "state":"SOURCE_ONLY_UNSENT","locally_recorded_lifecycle":"ACQUIRED",
            "vertical_id":"multifamily","proposed_recipient":"grounds",
            "proposal_fingerprint":"b"*64,
        }
        with self.assertRaises(AccessDenied):
            self.accept(local)
        bad=dict(self.payload);bad["source"]="buybox"
        with self.assertRaises(AccessDenied):
            self.accept(bad)
        bad=dict(self.payload);bad["closing_status"]="pending"
        with self.assertRaises(AccessDenied):
            self.accept(bad)

    def test_owner_property_scope_and_current_fresh_receipt_are_required(self):
        with self.assertRaises(AccessDenied):
            self.accept(actor=self.manager)
        with self.assertRaises(AccessDenied):
            self.accept(actor=self.other_owner)
        wrong=dict(self.payload);wrong["owner_ref"]="other"
        with self.assertRaises(AccessDenied):
            self.accept(wrong)
        stale=dict(self.payload);stale["issued_at"]=600;stale["expires_at"]=900
        with self.assertRaises(AccessDenied):
            self.accept(stale)
        long_lived=dict(self.payload);long_lived["expires_at"]=1400
        with self.assertRaises(AccessDenied):
            self.accept(long_lived)
        with self.assertRaises(AccessDenied):
            self.receiver.accept_multifamily_close(
                self.owner,signed_handoff=self.payload,tower_verifier=None,now=1000,
            )

    def test_second_close_or_duplicate_external_proof_cannot_silently_replace_property(self):
        self.accept()
        other=dict(self.payload)
        other.update({
            "handoff_ref":"handoff-2","property_ref":"p2","property_name":"Other",
            "tower_close_receipt_ref":"tower-close-1",
            "title_proof_ref":"title-proof-2",
            "encumbrance_review_ref":"encumbrance-review-2",
        })
        with self.assertRaises(GroundsConflict):
            self.accept(other)
        with self.assertRaises(AccessDenied):
            self.receiver.accepted_receipt(self.other_owner,property_ref="p1")


if __name__=="__main__":
    unittest.main()
