"""BBX readiness is a read-only projection, never an external authority issuer."""
from copy import deepcopy
from datetime import datetime, timezone
import unittest

from buybox.core import new_opportunity
from buybox.external_proof_gate import (
    KINDS, integration_readiness, record_verified_external_proof,
)
from buybox.store import connect, save
from buybox.tower_action_draft import stored_source_snapshot


class ReadinessStoredProofIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.db = connect()
        self.op = save(
            self.db, new_opportunity("multifamily", "Synthetic asset", 150000),
            event_type="OpportunityCreated",
        )

    def tearDown(self):
        self.db.close()

    def add(self, kind):
        source = stored_source_snapshot(self.db, self.op["id"])
        claims = {
            "authenticated": True,
            "issuer": "trusted-" + kind.lower().replace("_", "-"),
            "receipt_ref": "receipt-" + kind.lower().replace("_", "-"),
            "opportunity_id": source["opportunity_id"],
            "opportunity_revision": source["opportunity_revision"],
            "input_snapshot_digest": source["input_snapshot_digest"],
            "purpose": "acquisition-readiness",
        }
        candidate, record = record_verified_external_proof(
            self.db, self.op, kind=kind, raw_proof={"fixture": True},
            verifier=lambda _: claims,
            now_utc=datetime(2026, 9, 28, 15, tzinfo=timezone.utc),
        )
        self.op = save(self.db, candidate, expected_revision=self.op["version"],
                       event_type="ExternalProofRecorded")
        return record

    def test_genuine_persisted_verifier_records_survive_sequential_proof_only_saves(self):
        for kind in sorted(KINDS):
            self.add(kind)
        report = integration_readiness(self.op)
        self.assertTrue(report["external_proofs_complete"])
        self.assertEqual(report["missing"], [])
        self.assertFalse(report["authorizes_purchase"])
        self.assertFalse(report["authorizes_money"])
        self.assertFalse(report["can_mark_operational"])

    def test_injected_browser_shaped_record_cannot_show_verified(self):
        injected = deepcopy(self.op)
        injected["external_proofs"] = [{
            "kind": "TOWER_PROTECTED_ACTION",
            "deal_fingerprint": "not evidence",
            "receipt_ref": "browser-impostor",
            "authenticated": True,
            "ready": True,
        }]
        self.assertIn("TOWER_PROTECTED_ACTION", integration_readiness(injected)["missing"])

    def test_changed_stored_receipt_and_local_assertions_are_not_counted(self):
        record = self.add("TOWER_PROTECTED_ACTION")
        for key, value in (
            ("kind", []), ("receipt_ref", "receipt-modified"),
            ("browser_supplied_authority", True),
            ("authorizes_purchase", True), ("source_opportunity_revision", 999),
            ("authentication_scope", "BROWSER_SUBMITTED"),
            ("record_sha256", "0" * 64),
        ):
            with self.subTest(key=key):
                candidate = deepcopy(self.op)
                candidate["external_proofs"][-1][key] = value
                self.assertIn("TOWER_PROTECTED_ACTION", integration_readiness(candidate)["missing"])
        self.assertEqual(record["receipt_ref"], self.op["external_proofs"][-1]["receipt_ref"])

    def test_malformed_receipt_collection_does_not_crash_or_claim_complete(self):
        for value in (None, {}, True, "READY", [None, False, {"kind": "VAULT_CANONICAL_ARCHIVAL"}]):
            with self.subTest(value=value):
                candidate = deepcopy(self.op)
                candidate["external_proofs"] = value
                report = integration_readiness(candidate)
                self.assertFalse(report["external_proofs_complete"])
                self.assertIn("VAULT_CANONICAL_ARCHIVAL", report["missing"])

    def test_material_deal_change_invalidates_intact_receipt(self):
        self.add("TOWER_PROTECTED_ACTION")
        changed = save(
            self.db, {**self.op, "asking_price": "140000.00"},
            expected_revision=self.op["version"],
        )
        self.assertIn("TOWER_PROTECTED_ACTION", integration_readiness(changed)["missing"])


if __name__ == "__main__":
    unittest.main()
