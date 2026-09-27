"""OBSIM066–070: passive release probe never substitutes for a Tower owner walkthrough."""
import json
from urllib.error import URLError

import pytest

from scripts import ob_hosted_anonymous_release_probe as check

HOST = "https://simplee-tower-ob.onrender.com"
REVISION = "a" * 40


def _case(*, health=200, revision=REVISION, route=302, api=403,
          broker=False, capital=False, manual=False, auto=False, header=""):
    data = {
        "status": "tower_hosted_tower_runtime_manifest_ready",
        "entrypoint": "web.hosted_tower:app",
        "revision": revision,
        "revision_source": "environment:RENDER_GIT_COMMIT",
        "broker_submission": broker, "capital_movement": capital,
        "manual_live_authorized": manual, "live_auto_authorized": auto,
    }
    return {
        "/tower/healthz": (health, b'{"ok":true}'),
        "/tower/runtime-manifest.json": (200, json.dumps(data).encode()),
        "/ob/owner-rehearsal": (route, b""),
        "/ob/owner-rehearsal/status.json": (api, b""),
    }, header


def _inject(monkeypatch, cases, *, headers=""):
    def fake(origin, path):
        assert origin == HOST and path in check.PATHS
        code, body = cases[path]
        return {"status": code, "body": body, "revision_header": headers}
    monkeypatch.setattr(check, "_get", fake)


@pytest.mark.parametrize("bad", [
    "", "http://simplee-tower-ob.onrender.com", "https://host.test/sneaky",
    "https://name:password@host.test", "https://host.test/?a=1",
    "https://host.test/#part", "https://host.test\\@evil.example",
    "https://HOST.TEST:443", " https://host.test ", "https://host.test\n",
])
def test_066_only_exact_ordinary_https_origin(bad):
    with pytest.raises(ValueError, match="exact HTTPS"):
        check.strict_origin(bad)


def test_067_published_exact_revision_and_anonymous_denials_are_passive(monkeypatch):
    cases, _ = _case()
    _inject(monkeypatch, cases, headers=REVISION)
    answer = check.probe(HOST, REVISION)
    assert answer["status"] == "PASS_ANONYMOUS_PREFLIGHT_ONLY"
    assert answer["hosted_owner_walkthrough_verified"] is False
    assert answer["authenticated_request_made"] is False
    assert answer["manual_live_authorized"] is False
    assert answer["paid_service_created"] is False
    assert answer["render_service_settings_changed"] is False
    assert answer["observed"]["published_revision"] == REVISION
    assert answer["reason"] == "OWNER_LOGIN_AND_HOSTED_FEATURE_STILL_REQUIRE_SEPARATE_VERIFICATION"
    assert set(cases) == set(check.PATHS)


@pytest.mark.parametrize("overrides,expected_reason", [
    ({"revision": "b" * 40}, "PUBLISHED_REVISION_MISMATCH_OR_UNKNOWN"),
    ({"health": 503}, "TOWER_HEALTH_NOT_VERIFIED"),
    ({"route": 200}, "ANONYMOUS_OWNER_REHEARSAL_DISCLOSURE"),
    ({"api": 200}, "ANONYMOUS_OWNER_REHEARSAL_DISCLOSURE"),
    ({"broker": True}, "HOSTED_SAFETY_HOLD_NOT_CONFIRMED"),
    ({"capital": True}, "HOSTED_SAFETY_HOLD_NOT_CONFIRMED"),
    ({"manual": True}, "HOSTED_SAFETY_HOLD_NOT_CONFIRMED"),
    ({"auto": True}, "HOSTED_SAFETY_HOLD_NOT_CONFIRMED"),
])
def test_068_mismatch_unsafe_flag_or_anonymous_disclosure_is_hold(
    monkeypatch, overrides, expected_reason
):
    cases, _ = _case(**overrides)
    _inject(monkeypatch, cases)
    answer = check.probe(HOST, REVISION)
    assert answer["status"] == "HOLD" and answer["reason"] == expected_reason


def test_069_malformed_unavailable_and_inconsistent_header_hold(monkeypatch):
    cases, _ = _case()
    cases["/tower/runtime-manifest.json"] = (200, b"not-json")
    _inject(monkeypatch, cases)
    assert check.probe(HOST, REVISION)["reason"] == "RUNTIME_MANIFEST_NOT_VERIFIED"

    cases, _ = _case()
    _inject(monkeypatch, cases, headers="b" * 40)
    assert check.probe(HOST, REVISION)["reason"] == "INCONSISTENT_PUBLISHED_REVISION_HEADERS"

    def unavailable(origin, path):
        raise URLError("unavailable")
    monkeypatch.setattr(check, "_get", unavailable)
    answer = check.probe(HOST, REVISION)
    assert answer["status"] == "HOLD"
    assert answer["reason"] == "HOST_UNAVAILABLE_OR_RESPONSE_INVALID"
    assert answer["hosted_owner_walkthrough_verified"] is False


def test_070_invalid_revision_and_no_redirect_following():
    for bad in ("", "example", "g" * 40, "A" * 40, "a" * 39):
        with pytest.raises(ValueError, match="40-character"):
            check.probe(HOST, bad)
    assert check._NoRedirect().redirect_request(None, None, 302, "Found", {}, HOST + "/tower/login") is None
    assert check.PATHS == (
        "/tower/healthz", "/tower/runtime-manifest.json",
        "/ob/owner-rehearsal", "/ob/owner-rehearsal/status.json",
    )
