"""GRD116 — synthetic HTTP rent-read integration; no live Teller or payments.

The source/reviewer lambdas below exist only in the isolated test fixture.
Production must inject independently certified server-owned Tower/Teller adapters.
"""
from __future__ import annotations

import io
import json
import tempfile
import time
import unittest
from pathlib import Path
from urllib.parse import urlsplit

from grounds.operations import GroundsOperations
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope
from grounds.web import GroundsWebApp, GroundsWebConfigurationError


class RentReadWebTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=GroundsStore(Path(self.tmp.name)/"fictional.sqlite3")
        self.store.initialize()
        self.ops=GroundsOperations(self.store)
        self.owner=fixture_scope("owner","owner",("p1",))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.resident=fixture_scope("resident","resident",("p1",),("u1",))
        self.other=fixture_scope("other","resident",("p1",),("u1",))
        self.ops.record_closed_property(
            self.owner,property_ref="p1",name="Fictional property",
            close_evidence={"status":"verified_closed","property_ref":"p1",
                            "proof_ref":"fictional-close","owned_on":"2026-09-26"},
            close_verifier=lambda signed:signed, # FIXTURE ONLY
        )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",unit_ref="u1",label="101")
        self.ops.activate_lease(self.manager,property_ref="p1",unit_ref="u1",
                                lease_ref="lease-current",resident_ref="resident",
                                start_on="2026-09-26",end_on="2027-09-25")
        self.calls=[]
        self.app=self.make_app()

    def tearDown(self):
        self.tmp.cleanup()

    def snapshot(self,**override):
        now=int(time.time())
        data={
            "source":"teller","audience":"grounds","resident_ref":"resident",
            "property_ref":"p1","unit_ref":"u1","lease_ref":"lease-current",
            "observed_at":now,"expires_at":now+120,
            "amount_due_cents":125050,"currency":"USD",
            "invoice_status":"partial","due_on":"2026-10-01",
            "teller_handoff_ref":"opaque-no-checkout",
        }
        data.update(override)
        return data

    def make_app(self,source=None,verifier=None):
        return GroundsWebApp(
            self.store,tower_receiver=lambda environ:environ["fictional.actor"],
            csrf_secret=bytes(range(32)),local_fixture_only=True,
            teller_document_source=source,teller_verifier=verifier,
        )

    def get(self,actor=None,path="/grounds/api/rent?property_ref=p1&unit_ref=u1"):
        parsed=urlsplit(path)
        env={"REQUEST_METHOD":"GET","PATH_INFO":parsed.path,
             "QUERY_STRING":parsed.query,"wsgi.input":io.BytesIO(b"")}
        if actor is not None:
            env["fictional.actor"]=actor
        result={}
        def start(status,headers):
            result["status"]=status
            result["headers"]=dict(headers)
        raw=b"".join(self.app(env,start))
        result["json"]=json.loads(raw)
        return result

    def test_unconnected_teller_never_claims_zero_balance_or_checkout(self):
        reply=self.get(self.resident)
        self.assertEqual(reply["status"],"200 OK")
        self.assertEqual(reply["json"]["status"],"not_connected")
        self.assertIsNone(reply["json"]["amount_due_cents"])
        self.assertIsNone(reply["json"]["checkout_url"])
        self.assertFalse(reply["json"]["checkout_execution_enabled"])
        self.assertEqual(self.get(self.manager)["status"],"404 Not Found")
        self.assertEqual(self.get()["status"],"401 Unauthorized")

    def test_pair_of_server_owned_adapters_must_be_complete_and_callable(self):
        with self.assertRaises(GroundsWebConfigurationError):
            self.make_app(source=lambda actor,home:self.snapshot())
        with self.assertRaises(GroundsWebConfigurationError):
            self.make_app(verifier=lambda doc:doc)
        with self.assertRaises(GroundsWebConfigurationError):
            self.make_app(source=object(),verifier=lambda doc:doc)

    def test_current_exact_lease_verified_rent_is_read_only(self):
        def source(actor,home):
            self.calls.append((actor.subject_ref,home["lease"]["lease_ref"]))
            return self.snapshot()
        self.app=self.make_app(source=source,verifier=lambda doc:doc) # FIXTURE ONLY
        reply=self.get(self.resident)
        self.assertEqual(reply["status"],"200 OK")
        self.assertEqual(self.calls,[("resident","lease-current")])
        view=reply["json"]
        self.assertEqual(view["amount_due_cents"],125050)
        self.assertEqual(view["invoice_status"],"partial")
        self.assertEqual(view["status"],"verified_projection")
        self.assertIsNone(view["checkout_url"])
        self.assertFalse(view["checkout_execution_enabled"])
        self.assertEqual(reply["headers"]["Cache-Control"],"no-store, private, max-age=0")
        self.assertEqual(self.get(self.other)["status"],"404 Not Found")
        self.assertEqual(self.get(self.manager)["status"],"404 Not Found")

    def test_stale_wrong_lease_and_unverified_source_fail_closed(self):
        for changed in (
            {"lease_ref":"another-lease"},
            {"resident_ref":"other"},
            {"unit_ref":"another-unit"},
            {"source":"observatory"},
            {"expires_at":int(time.time())-1},
        ):
            with self.subTest(changed=changed):
                self.app=self.make_app(
                    source=lambda actor,home:self.snapshot(**changed),
                    verifier=lambda doc:doc, # FIXTURE ONLY
                )
                self.assertEqual(self.get(self.resident)["status"],"404 Not Found")
        self.app=self.make_app(
            source=lambda actor,home:self.snapshot(),
            verifier=lambda doc:(_ for _ in ()).throw(ValueError("invalid signature")),
        )
        self.assertEqual(self.get(self.resident)["status"],"404 Not Found")

    def test_ended_lease_is_denied_before_teller_source_called(self):
        self.app=self.make_app(
            source=lambda actor,home:self.calls.append("called") or self.snapshot(),
            verifier=lambda doc:doc, # FIXTURE ONLY
        )
        self.ops.end_lease(self.manager,property_ref="p1",
                           lease_ref="lease-current",expected_revision=1)
        self.assertEqual(self.get(self.resident)["status"],"404 Not Found")
        self.assertEqual(self.calls,[])

    def test_unexpected_query_and_other_property_cannot_reach_source(self):
        self.app=self.make_app(
            source=lambda actor,home:self.calls.append("called") or self.snapshot(),
            verifier=lambda doc:doc, # FIXTURE ONLY
        )
        self.assertEqual(self.get(self.resident,path="/grounds/api/rent?property_ref=p2&unit_ref=u1")["status"],
                         "404 Not Found")
        self.assertEqual(self.get(self.resident,path="/grounds/api/rent?property_ref=p1&unit_ref=u1&lease_ref=another")["status"],
                         "400 Bad Request")
        self.assertEqual(self.calls,[])


if __name__=="__main__":
    unittest.main()
