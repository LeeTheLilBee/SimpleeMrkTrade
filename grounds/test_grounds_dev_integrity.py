"""GRD062: synthetic SQLite invariant and local backup/restore checks."""
import tempfile
import unittest
from pathlib import Path

from grounds.dev_integrity import (
    LocalIntegrityError, inspect_local_store, make_local_fixture_backup,
)
from grounds.maintenance import MaintenanceIntake
from grounds.operations import GroundsOperations
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope


class LocalIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.store=GroundsStore(Path(self.temp.name)/"fictional.sqlite3")
        self.store.initialize()
        self.ops=GroundsOperations(self.store)
        self.owner=fixture_scope("owner","owner",("p1",))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.resident=fixture_scope("resident","resident",("p1",),("u1",))
        self.ops.record_closed_property(
            self.owner,property_ref="p1",name="Local fake property",
            close_evidence={"status":"verified_closed","property_ref":"p1",
                            "proof_ref":"fixture-closed","owned_on":"2026-09-26"},
            close_verifier=lambda x:x, # TEST ONLY
        )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",unit_ref="u1",label="101")
        self.ops.activate_lease(
            self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",
            resident_ref="resident",start_on="2026-09-26",end_on="2027-09-25",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_report_is_counts_only_and_healthy_for_fixture(self):
        report=inspect_local_store(self.store)
        self.assertTrue(report["healthy"])
        self.assertEqual(report["foreign_key_violations"],0)
        self.assertFalse(report["contains_raw_row_data"])
        self.assertFalse(report["production_restore_certified"])
        self.assertNotIn("Local fake property",repr(report))
        self.assertTrue(all(x==0 for x in report["domain_issue_counts"].values()))

    def test_copy_new_fixture_restore_preserves_records_without_cloud_upload(self):
        self.ops.submit_maintenance(
            self.resident,work_ref="w1",
            intake=MaintenanceIntake("p1","u1","plumbing","Example leak",False,"contact_first"),
        )
        dest=Path(self.temp.name)/"fixture-backup.sqlite3"
        info=make_local_fixture_backup(self.store,dest)
        self.assertTrue(info["unencrypted_local_copy"])
        self.assertFalse(info["production_backup_enabled"])
        self.assertFalse(info["cloud_upload_occurred"])
        copy=GroundsStore(dest)
        self.assertTrue(inspect_local_store(copy)["healthy"])
        with copy.transaction() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM work_orders").fetchone()[0],1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM work_events").fetchone()[0],1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM lease_members").fetchone()[0],1)
        with self.assertRaises(LocalIntegrityError):
            make_local_fixture_backup(self.store,dest) # must never overwrite
        self.ops.publish_notice(
            self.manager,property_ref="p1",notice_ref="n1",
            headline="Example",body="Only the source changed",
        )
        with copy.transaction() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM property_notices").fetchone()[0],0)

    def test_detects_domain_corruption_and_refuses_to_backup(self):
        with self.store.transaction(write=True) as db:
            db.execute("UPDATE units SET lifecycle='ready' WHERE unit_ref='u1'")
        report=inspect_local_store(self.store)
        self.assertFalse(report["healthy"])
        self.assertEqual(report["domain_issue_counts"]["active_lease_unit_not_occupied"],1)
        self.assertEqual(report["foreign_key_violations"],0)
        target=Path(self.temp.name)/"unhealthy-backup.sqlite3"
        with self.assertRaises(LocalIntegrityError):
            make_local_fixture_backup(self.store,target)
        self.assertFalse(target.exists())

    def test_unknown_or_damaged_file_denied_without_exposing_user_content(self):
        with self.assertRaises(LocalIntegrityError):
            inspect_local_store(GroundsStore(Path(self.temp.name)/"missing.sqlite3"))
        broken=Path(self.temp.name)/"bad.sqlite3"
        broken.write_bytes(b"not a sqlite file")
        with self.assertRaises(LocalIntegrityError):
            inspect_local_store(GroundsStore(broken))
        with self.assertRaises(LocalIntegrityError):
            make_local_fixture_backup(self.store,self.store.path)


if __name__=="__main__":
    unittest.main()
