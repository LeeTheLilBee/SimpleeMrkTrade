"""BBX032–036: synthetic real encrypted-original/local-snapshot evidence check."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from cryptography.fernet import Fernet

from buybox.core import new_opportunity, add_evidence
from buybox.documents import PrivateDocumentStore
from buybox.store import connect, save
from buybox.tower_evidence import (
    freeze_local_evidence_snapshot, HandoffPreparationError,
)
from buybox.vault_local_original_preflight import (
    LocalVaultOriginalPreflightError, verify_latest_local_original_unsent,
)

PDF = b"%PDF-1.7\n% Fictional evidence only\n%%EOF\n"
CSV = b"month,value\n2026-01,10\n"


class LocalOriginalPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        private = root / "originals"
        private.mkdir(mode=0o700)
        self.docstore = PrivateDocumentStore(private, Fernet.generate_key())
        self.db = connect(str(root / "synthetic.sqlite3"))
        self.op = new_opportunity("atm", "Fictional local document")
        self.artifact = self.docstore.ingest(
            contents=PDF, filename="fictional.pdf", mime="application/pdf",
            source_party="Synthetic seller",
        )
        self.op["artifacts"] = [self.artifact]
        self.evidence = add_evidence(
            self.op, "ownership_documents", status="RECEIVED",
            reference=self.artifact["id"], source="Synthetic seller",
        )
        self.evidence["artifact_id"] = self.artifact["id"]
        self.saved = save(self.db, self.op, event_type="FictionalEvidenceAdded")
        self.frozen, self.snapshot = freeze_local_evidence_snapshot(
            self.saved, evidence_id=self.evidence["id"],
            artifact_id=self.artifact["id"], actor_reference="local-owner",
        )

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def persist_freeze(self, frozen=None):
        return save(
            self.db, self.frozen if frozen is None else frozen,
            event_type="LocalProofFrozen", expected_revision=1,
        )

    def check(self):
        return verify_latest_local_original_unsent(
            self.db, self.docstore,
            opportunity_id=self.op["id"],
            evidence_id=self.evidence["id"],
            artifact_id=self.artifact["id"],
            snapshot_id=self.snapshot["snapshot_id"],
        )

    def test_actual_decrypted_original_and_saved_snapshot_only_unsubmitted(self):
        self.persist_freeze()
        result = self.check()
        self.assertEqual(result["state"], "LOCAL_ORIGINAL_VERIFIED_UNSENT")
        self.assertEqual(result["opportunity_revision"], 2)
        self.assertEqual(result["original_sha256"], self.artifact["sha256"])
        self.assertEqual(result["snapshot_sha256"], self.snapshot["snapshot_sha256"])
        self.assertEqual(result["mime_type"], "application/pdf")
        self.assertEqual(result["size_bytes"], len(PDF))
        for key in (
            "tower_identity_verified", "tower_owner_approval_verified",
            "malware_scan_verified", "vault_issuer_receipt_present",
            "vault_archived", "original_transferred", "external_request_made",
            "authorizes_download", "authorizes_acquisition",
        ):
            self.assertIs(result[key], False)
        encoded = json.dumps(result)
        self.assertNotIn(self.artifact["storage_reference"], encoded)
        self.assertNotIn(str(self.docstore.root), encoded)
        self.assertNotIn("Fictional evidence only", encoded)

    def test_snapshot_must_really_be_saved_not_only_in_memory(self):
        with self.assertRaisesRegex(LocalVaultOriginalPreflightError, "EXACT_SAVED"):
            self.check()

    def test_following_opportunity_revision_stales_previous_freeze(self):
        saved = self.persist_freeze()
        changed = dict(saved, name="A later seller revision")
        save(self.db, changed, event_type="DealTermsChanged", expected_revision=2)
        with self.assertRaisesRegex(LocalVaultOriginalPreflightError, "LATEST_PERSISTED"):
            self.check()

    def test_tampered_frozen_snapshot_hash_fails(self):
        changed = copy.deepcopy(self.frozen)
        changed["snapshots"][-1]["snapshot_sha256"] = "0" * 64
        self.persist_freeze(changed)
        with self.assertRaisesRegex(LocalVaultOriginalPreflightError, "FROZEN_SNAPSHOT_DIGEST_MISMATCH"):
            self.check()

    def test_frozen_claim_and_saved_evidence_mismatch_fail(self):
        changed = copy.deepcopy(self.frozen)
        changed["snapshots"][-1]["evidence_versions"][0]["evidence_state"] = "THIRD_PARTY_VERIFIED"
        # Even a recalculated valid snapshot digest cannot fabricate an actual
        # matching local evidence state.
        import hashlib
        material = {key: value for key, value in changed["snapshots"][-1].items()
                    if key != "snapshot_sha256"}
        changed["snapshots"][-1]["snapshot_sha256"] = hashlib.sha256(
            json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        self.persist_freeze(changed)
        with self.assertRaisesRegex(LocalVaultOriginalPreflightError, "FROZEN_DOCUMENT_LINEAGE_MISMATCH"):
            self.check()

    def test_corrupted_or_unavailable_ciphertext_fails_not_archive(self):
        self.persist_freeze()
        target = self.docstore.root / self.artifact["storage_reference"]
        target.write_bytes(b"not encrypted evidence")
        with self.assertRaisesRegex(LocalVaultOriginalPreflightError, "LOCAL_ORIGINAL_UNAVAILABLE_OR_INVALID"):
            self.check()

    def test_vault_v1_does_not_accept_csv_even_when_buybox_intake_does(self):
        descriptor = self.docstore.ingest(
            contents=CSV, filename="fictional.csv", mime="text/csv",
            source_party="Synthetic seller",
        )
        op = new_opportunity("atm", "Fictional CSV")
        op["artifacts"] = [descriptor]
        claim = add_evidence(
            op, "processor_statements", status="RECEIVED",
            reference=descriptor["id"], source="Synthetic seller",
        )
        claim["artifact_id"] = descriptor["id"]
        with self.assertRaisesRegex(HandoffPreparationError, "MIME_NOT_IN_CANONICAL_CONTRACT"):
            freeze_local_evidence_snapshot(
                op, evidence_id=claim["id"], artifact_id=descriptor["id"],
                actor_reference="local-owner",
            )

    def test_corrupt_persisted_revision_fails_closed(self):
        self.persist_freeze()
        self.db.execute(
            "UPDATE revisions SET digest=? WHERE opportunity_id=? AND revision=2",
            ("0" * 64, self.op["id"]),
        )
        self.db.commit()
        with self.assertRaisesRegex(LocalVaultOriginalPreflightError, "CURRENT_SOURCE_NOT_VERIFIED"):
            self.check()

    def test_no_vault_import_or_network_provider_in_preflight(self):
        from buybox import vault_local_original_preflight as module
        source = Path(module.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "from vault.", "requests.post(", "@app.route(",
            "TELLER_TOWER_TOKEN_SECRET", "from observatory.",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
