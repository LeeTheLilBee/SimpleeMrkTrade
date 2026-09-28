"""OBSIM091–095: source routes, activation and real owner acceptance are distinct.

These tests operate on the existing hosted Tower app's redacted public manifest,
not on a fabricated positive Tower login or any real Render configuration.
"""
from __future__ import annotations

import web.hosted_tower as runtime
from tower.ob_hosted_owner_rehearsal import EXACT_PATHS


def _rehearsal():
    return runtime.hosted_tower_runtime_manifest()["owner_rehearsal"]


def test_091_exact_source_routes_are_enumerated_without_marking_live_permission():
    data = _rehearsal()
    assert all(path in {r.rule for r in runtime.app.url_map.iter_rules()} for path in EXACT_PATHS)
    assert data["exact_source_routes_registered"] is True
    for key in (
        "actual_owner_login_walkthrough_verified", "durable_report_archive",
        "restart_recovery", "manual_live_clearance", "broker_submission",
        "capital_movement",
    ):
        assert data[key] is False


def test_092_registration_and_default_off_are_not_a_positive_hosted_release(monkeypatch):
    monkeypatch.setitem(runtime.app.extensions, "ob_hosted_owner_rehearsal_registered", {
        "enabled": False, "canonical_origin_configured": False,
    })
    data = _rehearsal()
    assert data["exact_source_routes_registered"] is True
    assert data["explicit_feature_enabled"] is False
    assert data["exact_https_origin_configured"] is False
    assert data["source_runtime_activation_preconditions_met"] is False
    assert data["actual_owner_login_walkthrough_verified"] is False


def test_093_partial_or_missing_config_never_promotes_source_to_activation(monkeypatch):
    for flags in (
        {},
        {"enabled": True},
        {"canonical_origin_configured": True},
        {"enabled": "true", "canonical_origin_configured": True},
        {"enabled": True, "canonical_origin_configured": "yes"},
    ):
        monkeypatch.setitem(runtime.app.extensions, "ob_hosted_owner_rehearsal_registered", flags)
        assert _rehearsal()["source_runtime_activation_preconditions_met"] is False
    monkeypatch.delitem(runtime.app.extensions, "ob_hosted_owner_rehearsal_registered")
    data = _rehearsal()
    assert data["source_runtime_activation_preconditions_met"] is False
    assert data["explicit_feature_enabled"] is False


def test_094_even_server_flag_and_origin_are_not_owner_login_or_archive_proof(monkeypatch):
    monkeypatch.setitem(runtime.app.extensions, "ob_hosted_owner_rehearsal_registered", {
        "enabled": True, "canonical_origin_configured": True,
        "durable_archive": True, "manual_live_grant": True,
        "actual_owner_login_walkthrough_verified": True,
    })
    data = _rehearsal()
    assert data["source_runtime_activation_preconditions_met"] is True
    assert data["actual_owner_login_walkthrough_verified"] is False
    assert data["durable_report_archive"] is False
    assert data["manual_live_clearance"] is False
    assert runtime.hosted_tower_runtime_manifest()["manual_live_authorized"] is False


def test_095_public_manifest_contains_only_redacted_booleans_not_host_or_secret(monkeypatch):
    monkeypatch.setitem(runtime.app.extensions, "ob_hosted_owner_rehearsal_registered", {
        "enabled": True, "canonical_origin_configured": True,
        "canonical_origin": "https://not-for-display.example",
        "csrf_token": "not-for-display-token",
        "tower_owner_id": "not-for-display-owner",
    })
    response = runtime.app.test_client().get("/tower/runtime-manifest.json")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data["owner_rehearsal"], dict)
    assert "not-for-display" not in response.get_data(as_text=True)
    assert "source_runtime_activation_preconditions_met" in data["owner_rehearsal"]
    assert data["owner_rehearsal"]["actual_owner_login_walkthrough_verified"] is False
    assert data["capital_movement"] is False
