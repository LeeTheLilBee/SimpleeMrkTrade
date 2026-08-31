
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tower.app_truth_projection import (
    app_truth_by_id,
    future_registered_apps,
    registered_app_truth_projection,
)
from tower.truth_contract import (
    AUTHORITATIVE,
    AVAILABLE,
    AUTHORIZED,
    CAPABILITY_STATES,
    CACHED,
    CONFIGURED,
    DERIVED,
    ENABLED,
    ENTITLED,
    EVIDENCE_ONLY,
    HISTORICAL,
    LOCKED,
    NOT_CONFIGURED,
    PRODUCT_FORBIDDEN_SOURCE_CLASSES,
    PUBLISHED,
    REGISTERED,
    SOURCE_CLASSES,
    STALE,
    TEST_ONLY,
    UNAVAILABLE,
    UNAVAILABLE_SOURCE,
    UNKNOWN,
    UNVERIFIED,
    VERIFIED,
    VERIFICATION_STATES,
    TowerTruthContractError,
    capability_truth_contract,
    count_truth,
    not_configured_truth,
    product_display_projection,
    read_mapping_truth,
    require_verified_value,
    truth_envelope,
    unavailable_truth,
    unknown_truth,
    verified_truth,
)
from tower.truth_surface_audit import (
    DEFAULT_PRODUCT_SURFACES,
    audit_product_surfaces,
    findings_for_file,
    findings_for_rule,
)


def test_twr121_source_classification_is_exact_and_explicit():

    assert SOURCE_CLASSES == {
        AUTHORITATIVE,
        DERIVED,
        CACHED,
        HISTORICAL,
        EVIDENCE_ONLY,
        TEST_ONLY,
        UNAVAILABLE_SOURCE,
    }

    assert PRODUCT_FORBIDDEN_SOURCE_CLASSES == {
        EVIDENCE_ONLY,
        TEST_ONLY,
    }


def test_twr121_verification_states_are_not_status_theater():

    assert VERIFICATION_STATES == {
        VERIFIED,
        UNVERIFIED,
        UNKNOWN,
        UNAVAILABLE,
        NOT_CONFIGURED,
        STALE,
    }


def test_twr121_test_only_truth_cannot_feed_product_surface():

    with pytest.raises(TowerTruthContractError):
        verified_truth(
            value="fake",
            source_id="tests.fixture",
            source_class=TEST_ONLY,
            product_visible=True,
        )


def test_twr121_evidence_only_truth_cannot_feed_product_surface():

    with pytest.raises(TowerTruthContractError):
        verified_truth(
            value="certification-proof",
            source_id="evidence.receipt",
            source_class=EVIDENCE_ONLY,
            product_visible=True,
        )


def test_twr121_evidence_can_exist_backstage_when_not_product_visible():

    envelope = verified_truth(
        value="certification-proof",
        source_id="evidence.receipt",
        source_class=EVIDENCE_ONLY,
        product_visible=False,
    )

    assert envelope.value == "certification-proof"
    assert envelope.product_visible is False


def test_twr122_verified_truth_has_provenance():

    envelope = verified_truth(
        value=14,
        source_id="tower.identity_store",
        source_class=AUTHORITATIVE,
        observed_at_utc="2026-08-31T10:00:00+00:00",
        fresh_until_utc="2026-08-31T10:05:00+00:00",
        reason="identity_store_count",
    )

    assert envelope.value == 14
    assert envelope.source_id == "tower.identity_store"
    assert envelope.source_class == AUTHORITATIVE
    assert envelope.verification_state == VERIFIED
    assert envelope.reason == "identity_store_count"


def test_twr122_timestamp_must_be_timezone_aware():

    with pytest.raises(TowerTruthContractError):
        verified_truth(
            value=True,
            source_id="tower.runtime",
            observed_at_utc="2026-08-31T10:00:00",
        )


def test_twr122_stale_truth_does_not_keep_displaying_as_verified():

    now = datetime.now(timezone.utc)

    envelope = verified_truth(
        value="reachable",
        source_id="tower.runtime.health",
        observed_at_utc=(
            now - timedelta(minutes=10)
        ).isoformat(),
        fresh_until_utc=(
            now - timedelta(minutes=5)
        ).isoformat(),
    )

    projection = product_display_projection(
        envelope,
        now_utc=now.isoformat(),
    )

    assert projection["display_value"] is None
    assert projection["display_state"] == STALE


def test_twr122_fresh_verified_truth_can_be_used():

    now = datetime.now(timezone.utc)

    envelope = verified_truth(
        value="reachable",
        source_id="tower.runtime.health",
        observed_at_utc=now.isoformat(),
        fresh_until_utc=(
            now + timedelta(minutes=5)
        ).isoformat(),
    )

    assert (
        require_verified_value(
            envelope,
            now_utc=now.isoformat(),
        )
        == "reachable"
    )


def test_twr123_missing_mapping_does_not_become_zero():

    envelope = read_mapping_truth(
        None,
        "count",
        source_id="tower.people",
    )

    assert envelope.value is None
    assert envelope.verification_state == UNKNOWN

    display = product_display_projection(
        envelope
    )

    assert display["display_value"] is None
    assert display["display_value"] != 0


def test_twr123_missing_key_does_not_become_ready():

    envelope = read_mapping_truth(
        {},
        "status",
        source_id="tower.runtime",
    )

    assert envelope.value is None
    assert envelope.verification_state == UNKNOWN

    assert (
        product_display_projection(
            envelope
        )["display_value"]
        is None
    )


def test_twr123_none_collection_does_not_mean_zero():

    envelope = count_truth(
        None,
        source_id="tower.identity_store",
    )

    assert envelope.value is None
    assert envelope.verification_state == UNKNOWN


def test_twr123_present_empty_collection_can_truthfully_mean_zero():

    envelope = count_truth(
        [],
        source_id="tower.identity_store",
    )

    assert envelope.value == 0
    assert envelope.verification_state == VERIFIED


def test_twr123_unknown_state_cannot_carry_plausible_value():

    with pytest.raises(TowerTruthContractError):
        truth_envelope(
            value="Healthy",
            source_id="tower.runtime",
            source_class=UNAVAILABLE_SOURCE,
            verification_state=UNKNOWN,
        )


def test_twr123_unavailable_state_has_no_fake_value():

    envelope = unavailable_truth(
        source_id="tower.runtime.health"
    )

    assert envelope.value is None
    assert envelope.verification_state == UNAVAILABLE


def test_twr123_not_configured_state_has_no_fake_value():

    envelope = not_configured_truth(
        source_id="tower.invitation_delivery"
    )

    assert envelope.value is None
    assert envelope.verification_state == NOT_CONFIGURED


def test_twr124_capability_vocabulary_is_exact():

    assert CAPABILITY_STATES == (
        REGISTERED,
        CONFIGURED,
        PUBLISHED,
        ENTITLED,
        AUTHORIZED,
        AVAILABLE,
        ENABLED,
        LOCKED,
    )

    contract = capability_truth_contract()

    assert (
        "REGISTERED_DOES_NOT_IMPLY_CONFIGURED"
        in contract["non_implications"]
    )

    assert (
        "PUBLISHED_DOES_NOT_IMPLY_ENTITLED"
        in contract["non_implications"]
    )

    assert (
        "AUTHORIZED_DOES_NOT_IMPLY_AVAILABLE"
        in contract["non_implications"]
    )


def test_twr124_all_registered_apps_receive_truth_projection():

    projections = registered_app_truth_projection()

    assert len(projections) == 5

    assert {
        projection["app_id"]
        for projection in projections
    } == {
        "observatory",
        "teller",
        "vault",
        "clouds",
        "grounds",
    }


def test_twr124_future_registration_does_not_mean_published_or_available():

    future = future_registered_apps()

    assert {
        projection["app_id"]
        for projection in future
    } == {
        "teller",
        "vault",
        "clouds",
        "grounds",
    }

    for projection in future:

        states = projection["states"]

        assert states[REGISTERED]["value"] is True
        assert states[REGISTERED]["verification_state"] == VERIFIED

        assert states[PUBLISHED]["value"] is False
        assert states[PUBLISHED]["verification_state"] == VERIFIED

        assert states[AVAILABLE]["value"] is None
        assert states[AVAILABLE]["verification_state"] == UNKNOWN

        assert projection["launchable"] is False


def test_twr124_ob_registry_does_not_fake_current_runtime_availability():

    ob = app_truth_by_id(
        "observatory"
    )

    assert ob is not None

    states = ob["states"]

    assert states[REGISTERED]["value"] is True
    assert states[PUBLISHED]["value"] is True

    assert states[ENTITLED]["value"] is None
    assert states[ENTITLED]["verification_state"] == UNKNOWN

    assert states[AUTHORIZED]["value"] is None
    assert states[AUTHORIZED]["verification_state"] == UNKNOWN

    assert states[AVAILABLE]["value"] is None
    assert states[AVAILABLE]["verification_state"] == UNKNOWN

    assert states[ENABLED]["value"] is None
    assert states[ENABLED]["verification_state"] == UNKNOWN

    assert states[LOCKED]["value"] is True

    assert ob["launchable"] is False


def test_twr124_execution_locks_are_real_truth_not_fake_product_state():

    ob = app_truth_by_id(
        "observatory"
    )

    assert ob["safety"][
        "live_auto_locked"
    ]["value"] is True

    assert ob["safety"][
        "broker_execution_enabled"
    ]["value"] is False

    assert ob["safety"][
        "capital_action_enabled"
    ]["value"] is False


def test_twr125_default_audit_scope_excludes_tests_and_evidence():

    assert DEFAULT_PRODUCT_SURFACES

    assert all(
        not path.startswith("tests/")
        for path in DEFAULT_PRODUCT_SURFACES
    )

    assert all(
        not path.startswith("ob_evidence/")
        for path in DEFAULT_PRODUCT_SURFACES
    )


def test_twr125_retired_people_surface_no_longer_reports_identity_theater():

    report = audit_product_surfaces(
        "/content/SimpleeMrkTrade"
    )

    findings = findings_for_file(
        report,
        "tower/owner_people_registry.py",
    )

    assert findings == []


def test_twr125_retired_owner_dashboard_service_no_longer_reports_control_theater():

    report = audit_product_surfaces(
        "/content/SimpleeMrkTrade"
    )

    findings = findings_for_file(
        report,
        "tower/owner_dashboard_service.py",
    )

    assert findings == []


def test_twr125_retired_access_home_shortcuts_no_longer_report_ready_or_draft_debt():

    report = audit_product_surfaces(
        "/content/SimpleeMrkTrade"
    )

    findings = findings_for_file(
        report,
        "tower/access_home_owner_launches.py",
    )

    assert findings == []


def test_twr125_future_apps_are_flagged_as_registry_not_product_availability():

    report = audit_product_surfaces(
        "/content/SimpleeMrkTrade"
    )

    findings = findings_for_rule(
        report,
        "future_app_registry",
    )

    assert findings

    assert all(
        finding["severity"]
        == "KEEP_REGISTRY_HIDE_PRODUCT"
        for finding in findings
    )


def test_twr125_walkthrough_routes_are_inventory_debt_for_next_cutover():

    report = audit_product_surfaces(
        "/content/SimpleeMrkTrade"
    )

    findings = findings_for_rule(
        report,
        "walkthrough_route",
    )

    assert findings


def test_twr125_audit_is_inventory_not_fake_success():

    report = audit_product_surfaces(
        "/content/SimpleeMrkTrade"
    )

    assert (
        report["status"]
        == "tower_truth_debt_audit_complete"
    )

    assert report["finding_count"] > 0

    assert report["tests_scanned_as_product"] is False
    assert report["evidence_scanned_as_product"] is False
