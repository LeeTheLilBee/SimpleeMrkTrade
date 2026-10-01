"""BBX042-046: saved searches observe actual persisted local records only."""
import tempfile
import unittest
from pathlib import Path

from buybox.core import new_opportunity
from buybox.saved_search import (
    SavedSearchError, normalize_filters, create_saved_search,
    get_saved_search, saved_searches, run_saved_search, latest_check,
    archive_saved_search,
)
from buybox.store import connect, save


def filters(**kwargs):
    args={"vertical":"atm","query":"","max_price":"100000.00"}
    args.update(kwargs)
    return args


class SavedSearchTests(unittest.TestCase):
    def setUp(self):
        self.db=connect()
        self.atm=save(self.db,new_opportunity("atm","Owner's real route",95000),
                      event_type="OpportunityCreated")

    def tearDown(self):
        self.db.close()

    def create(self, **changes):
        return create_saved_search(self.db,name="Owner route discovery",
               filters=filters(**changes),actor_reference="local_owner")

    def test_new_saved_search_is_only_definition_not_fake_notification(self):
        saved=self.create()
        self.assertEqual(saved["filters"]["max_price"],"100000.00")
        self.assertIsNone(latest_check(self.db,saved["id"]))
        first=run_saved_search(self.db,saved["id"])
        self.assertTrue(first["result"]["delta"]["first_baseline"])
        self.assertEqual(first["result"]["match_count"],1)
        self.assertEqual(first["result"]["delta"]["newly_matching"],[])
        self.assertFalse(first["result"]["external_listing_feed_connected"])
        self.assertFalse(first["result"]["automated_notification_sent"])
        self.assertFalse(first["result"]["claims_new_marketplace_listings"])
        self.assertFalse(first["result"]["authorizes_acquisition"])
        self.assertEqual(first["current_snapshot"][self.atm["id"]]["revision"],1)
        again=run_saved_search(self.db,saved["id"])
        self.assertFalse(again["result"]["delta"]["first_baseline"])
        self.assertEqual(again["result"]["delta"]["revised"],[])
        self.assertEqual(again["result"]["delta"]["newly_matching"],[])
        self.assertEqual(again["result"]["delta"]["no_longer_matching"],[])

    def test_newly_matching_and_revised_then_no_longer_matching(self):
        saved=self.create()
        run_saved_search(self.db,saved["id"])
        second=save(self.db,new_opportunity("atm","Second actual route",85000),
                    event_type="OpportunityCreated")
        added=run_saved_search(self.db,saved["id"])
        self.assertEqual(added["result"]["delta"]["newly_matching"],[second["id"]])
        changed={**self.atm,"name":"Owner route after document review"}
        changed=save(self.db,changed,expected_revision=1)
        updated=run_saved_search(self.db,saved["id"])
        revisions=updated["result"]["delta"]["revised"]
        self.assertEqual(len(revisions),1)
        self.assertEqual(revisions[0]["id"],self.atm["id"])
        self.assertEqual(revisions[0]["previous_revision"],1)
        self.assertEqual(revisions[0]["current_revision"],2)
        expensive={**second,"asking_price":"145000.00"}
        save(self.db,expensive,expected_revision=1)
        gone=run_saved_search(self.db,saved["id"])
        self.assertEqual(gone["result"]["delta"]["no_longer_matching"],[second["id"]])
        self.assertEqual(gone["result"]["match_count"],1)

    def test_category_query_price_and_unknown_asking_are_honored(self):
        save(self.db,new_opportunity("multifamily","Owner's apartments",95000),
             event_type="OpportunityCreated")
        save(self.db,new_opportunity("atm","No asking price",None),
             event_type="OpportunityCreated")
        saved=self.create(query="route")
        result=run_saved_search(self.db,saved["id"])
        self.assertEqual(result["result"]["match_ids"],[self.atm["id"]])
        all_verticals=self.create(vertical=None,query="",max_price=None)
        all_result=run_saved_search(self.db,all_verticals["id"])
        self.assertEqual(all_result["result"]["match_count"],3)
        self.assertIsNone(all_verticals["filters"]["vertical"])
        self.assertIsNone(all_verticals["filters"]["max_price"])

    def test_cannot_forge_filters_or_pretend_external_updates(self):
        for inputs in (
            {"vertical":"unknown","query":"","max_price":None},
            {"vertical":"atm","query":"","max_price":"-1"},
            {"vertical":"atm","query":"","max_price":"$99"},
            {"vertical":"atm","query":"","max_price":"1e6"},
            {"vertical":"atm","query":"x"*121,"max_price":None},
            {"vertical":"atm","query":"","max_price":True},
        ):
            with self.subTest(inputs=inputs),self.assertRaises(SavedSearchError):
                normalize_filters(**inputs)
        with self.assertRaisesRegex(SavedSearchError,"EXACT_FILTERS_REQUIRED"):
            create_saved_search(self.db,name="Malformed",
                filters={"vertical":"atm","query":"","max_price":None,
                         "live_external_feed":True})

    def test_archive_is_traced_and_preserves_old_checks(self):
        saved=self.create()
        before=run_saved_search(self.db,saved["id"])
        self.assertTrue(archive_saved_search(self.db,saved["id"],
                                             actor_reference="local_owner")["archived"])
        record=get_saved_search(self.db,saved["id"])
        self.assertIsNotNone(record["archived_at"])
        self.assertEqual(record["archived_by"],"local_owner")
        self.assertEqual(latest_check(self.db,saved["id"])["check_id"],before["check_id"])
        with self.assertRaisesRegex(SavedSearchError,"SAVED_SEARCH_ARCHIVED"):
            run_saved_search(self.db,saved["id"])
        with self.assertRaisesRegex(SavedSearchError,"SEARCH_NOT_FOUND_OR_ALREADY_ARCHIVED"):
            archive_saved_search(self.db,saved["id"])

    def test_corrupt_source_digest_fails_without_new_saved_check(self):
        saved=self.create()
        first=run_saved_search(self.db,saved["id"])
        self.db.execute("UPDATE revisions SET digest=? WHERE opportunity_id=?",
                        ("0"*64,self.atm["id"]))
        self.db.commit()
        with self.assertRaisesRegex(SavedSearchError,"CURRENT_OPPORTUNITY_SOURCE_NOT_VERIFIED"):
            run_saved_search(self.db,saved["id"])
        self.assertEqual(latest_check(self.db,saved["id"])["check_id"],first["check_id"])

    def test_checks_are_append_only_and_rechecked_from_persistent_database(self):
        with tempfile.TemporaryDirectory() as folder:
            path=str(Path(folder)/"radar.sqlite3")
            a=connect(path)
            b=connect(path)
            try:
                opp=save(a,new_opportunity("atm","Actual persisted route",74000),
                         event_type="OpportunityCreated")
                saved=create_saved_search(a,name="Persisted",
                    filters=filters(),actor_reference="local_owner")
                run_saved_search(a,saved["id"])
                changed={**opp,"name":"Updated saved deal title"}
                save(b,changed,expected_revision=1)
                delta=run_saved_search(b,saved["id"])
                self.assertEqual(delta["result"]["delta"]["revised"][0]["id"],opp["id"])
                self.assertEqual(run_saved_search(a,saved["id"])["result"]["delta"]["revised"],[])
                count=a.execute("SELECT count(*) FROM buybox_saved_search_checks").fetchone()[0]
                self.assertEqual(count,3)
            finally:
                a.close()
                b.close()


if __name__=="__main__":
    unittest.main()
