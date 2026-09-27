"""OBSIM071–075: two-host inventory must not be a host election or owner grant."""
import pytest

from scripts.ob_anonymous_two_host_inventory import (
    CANONICAL, SECONDARY, classify,
)

REVISION = "7199a702a9ed9169c155ff24d4014a764a542ab4"


def result(state, *, revision=REVISION):
    return {
        "status": state, "reason": "PROBE_READ_ONLY",
        "observed": {
            "health_http": 200,
            "manifest_http": 200,
            "published_revision": revision,
            "anonymous_owner_page_http": 302,
            "anonymous_owner_status_http": 403,
            "secret": "not-displayable",
        },
        "owner_id": "not-displayable",
    }


def test_obsim071_secondary_pass_does_not_select_a_different_owner_site():
    called = []
    def fake(origin, revision):
        called.append((origin, revision))
        return result(
            "HOLD" if origin == CANONICAL else "PASS_ANONYMOUS_PREFLIGHT_ONLY",
            revision="old-canonical" if origin == CANONICAL else REVISION,
        )
    value = classify(CANONICAL, SECONDARY, REVISION, probe_function=fake)
    assert called == [(CANONICAL, REVISION), (SECONDARY, REVISION)]
    assert value["release_status"].startswith("HOLD_")
    assert value["observations"]["documented_canonical_candidate"]["status"] == "HOLD"
    assert value["observations"]["separate_secondary_candidate"]["status"] == "PASS_ANONYMOUS_PREFLIGHT_ONLY"
    assert value["secondary_pass_substitutes_for_canonical"] is False
    assert value["canonical_owner_url_confirmed_by_owner"] is False
    assert "secret" not in str(value) and "not-displayable" not in str(value)


def test_obsim072_even_both_passing_cannot_claim_owner_login_or_activation():
    value = classify(CANONICAL, SECONDARY, REVISION, probe_function=lambda *_: result(
        "PASS_ANONYMOUS_PREFLIGHT_ONLY",
    ))
    assert value["release_status"] == "HOLD_OWNER_SITE_AND_AUTHENTICATED_WALKTHROUGH"
    for field in (
        "anonymous_probe_is_owner_login",
        "hosted_rehearsal_feature_enabled_by_probe",
        "manual_live_authorized", "broker_submission",
        "capital_movement", "paid_service_created",
        "render_service_settings_changed", "credentials_sent",
    ):
        assert value[field] is False


def test_obsim073_refuse_off_inventory_url_port_query_wrong_revision():
    for wrong in (
        ("https://attacker.example", SECONDARY, REVISION),
        (CANONICAL, CANONICAL, REVISION),
        (CANONICAL, SECONDARY + "?x=y", REVISION),
        (CANONICAL, SECONDARY + ":443", REVISION),
        (CANONICAL, SECONDARY, "latest"),
    ):
        with pytest.raises(ValueError):
            classify(*wrong, probe_function=lambda *_: result("HOLD"))


def test_obsim074_probe_failure_and_extra_fields_remain_redacted_hold():
    def fake(origin, revision):
        if origin == CANONICAL:
            raise OSError("source secret must never be repeated")
        return {"status": "READY", "reason": "unexpected", "private_token": "BAD"}
    value = classify(CANONICAL, SECONDARY, REVISION, probe_function=fake)
    assert value["observations"]["documented_canonical_candidate"]["reason"] == "HOST_UNAVAILABLE_OR_INVALID"
    assert value["observations"]["separate_secondary_candidate"]["status"] == "HOLD"
    assert "private_token" not in str(value) and "source secret" not in str(value)


def test_obsim075_consumer_must_not_treat_inventory_exit_code_as_clearance():
    from pathlib import Path
    source = (Path(__file__).resolve().parents[1] /
              "scripts/ob_anonymous_two_host_inventory.py").read_text()
    assert 'release_status": "HOLD_OWNER_SITE_AND_AUTHENTICATED_WALKTHROUGH"' in source
    assert "secondary_pass_substitutes_for_canonical" in source
    assert "return 0" in source
    assert "render_service_settings_changed" in source
