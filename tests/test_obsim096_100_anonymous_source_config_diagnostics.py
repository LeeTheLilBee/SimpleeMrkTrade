"""OBSIM096–100: public source configuration != owner acceptance or durability."""
import json

import pytest

import test_obsim066_070_anonymous_release_probe as base
from scripts import ob_hosted_anonymous_release_probe as probe
from scripts.ob_anonymous_two_host_inventory import CANONICAL, SECONDARY, classify


def _manifest_case(monkeypatch, flags):
    cases, _ = base._case()
    code, raw = cases["/tower/runtime-manifest.json"]
    manifest = json.loads(raw)
    manifest["owner_rehearsal"] = flags
    cases["/tower/runtime-manifest.json"] = (code, json.dumps(manifest).encode())
    base._inject(monkeypatch, cases, headers=base.REVISION)


def _flags(routes=False, enabled=False, origin=False, ready=False, **extra):
    return {
        "exact_source_routes_registered": routes,
        "explicit_feature_enabled": enabled,
        "exact_https_origin_configured": origin,
        "source_runtime_activation_preconditions_met": ready,
        "actual_owner_login_walkthrough_verified": False,
        "durable_report_archive": False,
        "restart_recovery": False,
        "manual_live_clearance": False,
        "broker_submission": False,
        "capital_movement": False,
        **extra,
    }


def test_096_default_off_manifest_does_not_claim_source_activation_or_owner(monkeypatch):
    _manifest_case(monkeypatch, _flags(routes=True))
    got = probe.probe(base.HOST, base.REVISION)
    assert got["status"] == "PASS_ANONYMOUS_PREFLIGHT_ONLY"
    assert got["observed"]["owner_rehearsal_source"] == {
        "exact_source_routes_registered": True,
        "explicit_feature_enabled": False,
        "exact_https_origin_configured": False,
        "source_runtime_activation_preconditions_met": False,
    }
    assert got["hosted_owner_walkthrough_verified"] is False
    assert got["durable_hosted_report_archive_verified"] is False
    assert got["authenticated_request_made"] is False


def test_097_even_all_source_flags_true_anon_probe_cannot_certify_real_owner(monkeypatch):
    _manifest_case(monkeypatch, _flags(routes=True, enabled=True, origin=True, ready=True))
    got = probe.probe(base.HOST, base.REVISION)
    assert got["status"] == "PASS_ANONYMOUS_PREFLIGHT_ONLY"
    assert got["observed"]["owner_rehearsal_source"]["source_runtime_activation_preconditions_met"] is True
    assert got["hosted_owner_walkthrough_verified"] is False
    assert got["durable_hosted_report_archive_verified"] is False
    assert got["manual_live_authorized"] is False
    assert got["reason"] == "OWNER_LOGIN_AND_HOSTED_FEATURE_STILL_REQUIRE_SEPARATE_VERIFICATION"


@pytest.mark.parametrize("flags", [
    _flags(routes=True, enabled=False, origin=False, ready=True),
    _flags(routes=False, enabled=True, origin=True, ready=True),
    _flags(routes=True, enabled=True, origin=True, ready=False),
    _flags(routes=True, enabled=True, origin=False, ready=True),
])
def test_098_manifest_conflicts_hold_even_with_correct_revision_and_anonymous_denial(monkeypatch, flags):
    _manifest_case(monkeypatch, flags)
    got = probe.probe(base.HOST, base.REVISION)
    assert got["status"] == "HOLD"
    assert got["reason"] == "INCONSISTENT_HOSTED_REHEARSAL_SOURCE_FLAGS"


@pytest.mark.parametrize("flag", [
    "actual_owner_login_walkthrough_verified", "durable_report_archive",
    "restart_recovery", "manual_live_clearance", "broker_submission",
    "capital_movement",
])
def test_099_source_must_not_self_certify_independent_authority(monkeypatch, flag):
    _manifest_case(monkeypatch, _flags(routes=True, **{flag: True}))
    got = probe.probe(base.HOST, base.REVISION)
    assert got["status"] == "HOLD"
    assert got["reason"] == "UNSAFE_HOSTED_REHEARSAL_AUTHORITY_CLAIM"
    assert got["hosted_owner_walkthrough_verified"] is False


def test_100_two_host_inventory_is_redacted_and_never_elects_newer_site():
    names = {
        "exact_source_routes_registered", "explicit_feature_enabled",
        "exact_https_origin_configured", "source_runtime_activation_preconditions_met",
    }

    def fake(origin, revision):
        assert revision == base.REVISION
        return {
            "status": "PASS_ANONYMOUS_PREFLIGHT_ONLY",
            "reason": "ANONYMOUS_ONLY",
            "observed": {
                "health_http": 200, "published_revision": revision,
                "owner_rehearsal_source": {
                    **{name: True for name in names},
                    "secret": "do-not-display",
                    "exact_https_origin_configured": "fake-positive"
                    if origin == CANONICAL else True,
                },
                "private_owner_token": "do-not-display",
            },
        }

    got = classify(CANONICAL, SECONDARY, base.REVISION, probe_function=fake)
    assert got["release_status"] == "HOLD_OWNER_SITE_AND_AUTHENTICATED_WALKTHROUGH"
    assert got["canonical_owner_url_confirmed_by_owner"] is False
    assert got["secondary_pass_substitutes_for_canonical"] is False
    for row in got["observations"].values():
        assert set(row["owner_rehearsal_source"]) == names
        assert row["owner_login_verified"] is False
        assert row["durable_archive_verified"] is False
    assert got["observations"]["documented_canonical_candidate"]["owner_rehearsal_source"]["exact_https_origin_configured"] is None
    assert got["observations"]["separate_secondary_candidate"]["owner_rehearsal_source"]["exact_https_origin_configured"] is True
    assert "do-not-display" not in repr(got)
