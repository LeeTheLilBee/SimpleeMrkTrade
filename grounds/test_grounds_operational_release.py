"""GRD138–139 isolated future-production release wrapper tests; fictional only."""
from __future__ import annotations

import io
import json
import unittest

from grounds.operational_release import (
    GroundsOperationalReleaseGate,GroundsOperationalReleaseUnavailable,
)


class FictionalGuard:
    def __init__(self):
        self.healthy=False
        self.admit=False
        self.calls=0
        self.fail_health=False
        self.fail_admission=False
    def health_check(self):
        if self.fail_health:
            raise RuntimeError("private provider diagnostics")
        return self.healthy
    def __call__(self,environ):
        self.calls+=1
        if self.fail_admission:
            raise RuntimeError("private release receipt")
        return self.admit


class ReleaseGuardTests(unittest.TestCase):
    def setUp(self):
        self.guard=FictionalGuard()
        self.app_calls=0
        def private_app(environ,start_response):
            self.app_calls+=1
            payload=b'{"ready":true}' if environ.get("PATH_INFO")=="/grounds/health/ready" else b'{"private":"fictional"}'
            start_response("200 OK",[("Content-Type","application/json"),
                                      ("Content-Length",str(len(payload)))])
            return [payload]
        self.app=GroundsOperationalReleaseGate(private_app,self.guard)

    def call(self,path="/grounds/api/me",method="GET"):
        result={}
        def start(status,headers):
            result["status"]=status
            result["headers"]=dict(headers)
        raw=b"".join(self.app({
            "PATH_INFO":path,"REQUEST_METHOD":method,
            "wsgi.input":io.BytesIO(b""),
        },start))
        result["json"]=json.loads(raw)
        return result

    def test_missing_or_self_reported_inert_authority_fails_configuration(self):
        with self.assertRaises(GroundsOperationalReleaseUnavailable):
            GroundsOperationalReleaseGate(lambda e,s:[],None)
        with self.assertRaises(GroundsOperationalReleaseUnavailable):
            GroundsOperationalReleaseGate(lambda e,s:[],lambda e:True)
        with self.assertRaises(GroundsOperationalReleaseUnavailable):
            GroundsOperationalReleaseGate(None,self.guard)

    def test_no_private_request_without_independent_health_and_admission(self):
        denied=self.call()
        self.assertEqual(denied["status"],"503 Service Unavailable")
        self.assertEqual(denied["json"],{"error":"service_unavailable"})
        self.assertEqual(self.app_calls,0)
        self.assertEqual(self.guard.calls,0)
        self.assertEqual(denied["headers"]["Cache-Control"],"no-store, private, max-age=0")
        self.assertEqual(self.call("/grounds/health/ready")["json"],{"ready":False})
        self.assertEqual(self.call("/grounds/health/live")["status"],"200 OK")
        self.assertEqual(self.app_calls,1)  # liveness only

        self.guard.healthy=True
        self.assertEqual(self.call("/grounds/health/ready")["json"],{"ready":True})
        # Infrastructure/provider-health readiness alone still does not admit
        # private tenants or even static JS until the independent current
        # release authority admits each request.
        self.assertEqual(self.call("/grounds/api/me")["status"],"503 Service Unavailable")
        self.assertEqual(self.call("/grounds/app.js")["status"],"503 Service Unavailable")
        self.assertEqual(self.guard.calls,2)

        self.guard.admit=True
        self.assertEqual(self.call("/grounds/api/me")["status"],"200 OK")
        self.guard.admit=False  # current release revoked between two requests
        self.assertEqual(self.call("/grounds/api/me")["status"],"503 Service Unavailable")

    def test_only_literal_true_and_private_failures_never_leak(self):
        self.guard.healthy=1  # bool coercion must not silently accept integer
        self.guard.admit=True
        self.assertEqual(self.call()["status"],"503 Service Unavailable")
        self.guard.healthy=True
        self.guard.admit=1
        self.assertEqual(self.call()["status"],"503 Service Unavailable")
        self.guard.fail_admission=True
        denied=self.call()
        self.assertEqual(denied["json"],{"error":"service_unavailable"})
        self.assertNotIn("private",str(denied))
        self.guard.fail_health=True
        denied=self.call("/grounds/health/ready")
        self.assertEqual(denied["json"],{"ready":False})
        self.assertNotIn("provider",str(denied))


if __name__=="__main__":
    unittest.main()
