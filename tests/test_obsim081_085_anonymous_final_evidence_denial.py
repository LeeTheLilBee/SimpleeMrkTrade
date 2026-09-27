"""OBSIM081–085: passive public probe includes new final evidence route, never a login test."""
import pytest

import test_obsim066_070_anonymous_release_probe as base
from scripts import ob_hosted_anonymous_release_probe as check
from scripts.ob_anonymous_two_host_inventory import CANONICAL, SECONDARY, classify


def test_081_new_final_evidence_route_is_fixed_read_only_and_denied(monkeypatch):
    cases, _ = base._case()
    base._inject(monkeypatch, cases)
    value = check.probe(base.HOST, base.REVISION)
    assert value["status"] == "PASS_ANONYMOUS_PREFLIGHT_ONLY"
    assert value["observed"]["anonymous_final_evidence_http"] == 403
    assert value["authenticated_request_made"] is False
    assert value["hosted_owner_walkthrough_verified"] is False
    assert value["manual_live_authorized"] is False
    assert "/ob/owner-rehearsal/evidence.json" in check.PATHS
    assert all(route.startswith("/") for route in check.PATHS)
    for bad in ("/ob/owner-rehearsal/evidence.json?token=bad",
                "/ob/owner-rehearsal/evidence.json/raw",
                "/ob/owner-rehearsal/export-all"):
        with pytest.raises(ValueError):
            check._get(base.HOST, bad)


@pytest.mark.parametrize("status", [200, 201, 204, 206])
def test_082_any_successful_anonymous_proof_route_is_hold(monkeypatch, status):
    cases, _ = base._case(evidence=status)
    base._inject(monkeypatch, cases)
    result = check.probe(base.HOST, base.REVISION)
    assert result["status"] == "HOLD"
    assert result["reason"] == "ANONYMOUS_OWNER_REHEARSAL_DISCLOSURE"
    assert result["observed"]["anonymous_final_evidence_http"] == status
    assert result["capital_movement"] is False


@pytest.mark.parametrize("status", [302, 403, 404, 409, 503])
def test_083_anonymous_denial_is_only_passive_compatibility(monkeypatch, status):
    cases, _ = base._case(evidence=status)
    base._inject(monkeypatch, cases)
    result = check.probe(base.HOST, base.REVISION)
    assert result["status"] == "PASS_ANONYMOUS_PREFLIGHT_ONLY"
    assert result["observed"]["anonymous_final_evidence_http"] == status
    assert result["reason"] == "OWNER_LOGIN_AND_HOSTED_FEATURE_STILL_REQUIRE_SEPARATE_VERIFICATION"
    assert result["hosted_owner_walkthrough_verified"] is False


def test_084_two_distinct_hosts_cannot_elect_official_site_or_claim_export(monkeypatch):
    def fake(origin, exact_revision):
        return {
            "status": "PASS_ANONYMOUS_PREFLIGHT_ONLY",
            "reason": "OWNER_STILL_NOT_VERIFIED",
            "observed": {
                "published_revision": exact_revision,
                "anonymous_final_evidence_http": 403,
                "anonymous_owner_page_http": 302,
                "private_token": "not-for-display",
            },
        }
    result = classify(CANONICAL, SECONDARY, base.REVISION, probe_function=fake)
    assert result["release_status"] == "HOLD_OWNER_SITE_AND_AUTHENTICATED_WALKTHROUGH"
    assert result["canonical_owner_url_confirmed_by_owner"] is False
    assert result["secondary_pass_substitutes_for_canonical"] is False
    for host in result["observations"].values():
        assert host["observed"]["anonymous_final_evidence_http"] == 403
        assert "private_token" not in str(host)


def test_085_public_probe_does_not_read_proof_bytes_or_send_creds(monkeypatch):
    called = []
    def fake(origin, path):
        called.append(path)
        if path not in check.PATHS:
            raise AssertionError("unknown path")
        cases, _ = base._case()
        code, body = cases[path]
        return {"status": code, "body": body, "revision_header": base.REVISION}
    monkeypatch.setattr(check, "_get", fake)
    result = check.probe(base.HOST, base.REVISION)
    assert called == list(check.PATHS)
    assert result["status"] == "PASS_ANONYMOUS_PREFLIGHT_ONLY"
    assert "evidence" not in str(result.get("private_token", ""))
    assert result["render_service_settings_changed"] is False
    assert result["paid_service_created"] is False
    assert result["broker_submission"] is False
