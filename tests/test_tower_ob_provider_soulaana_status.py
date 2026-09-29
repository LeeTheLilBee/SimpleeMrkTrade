"""Seven-provider owner-session status → Soulaana, with no raw source/AI authority."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import pytest

from tower.ob_provider_soulaana_status import build_soulaana_provider_status
from web.ob_connection_truth_route import connection_status_projection

ROOT = Path(__file__).resolve().parents[1]
SID = "tower_session_fictional_owner_source_status_1234"
SECRET = "FICTIONAL-TEST-SECRET-DO-NOT-EXPOSE"
ACCOUNT = "fictional-private-account-1234"
PROVIDERS = ("public", "finnhub", "alpha_vantage", "sec", "bls", "treasury", "openfigi")


def keys(_sid):
    assert _sid == SID
    return (
        {"id": "finnhub", "present": True, "probe": "READ_ONLY_CHECK_PASSED",
         "secret": SECRET, "expires_at": "2030-01-01T00:00:00Z"},
        {"id": "alpha_vantage", "present": False, "probe": "NOT_CONFIGURED",
         "secret": SECRET},
    )


def public(_sid):
    assert _sid == SID
    return {
        "authentication_temporarily_present": True,
        "account_linked": False, "owner_selection_required": False,
        "access_token": SECRET, "account_id": ACCOUNT,
    }


def projection(monkeypatch):
    for key in ("OB_KEYLESS_RESEARCH_ENABLED", "OB_SEC_PUBLIC_RESEARCH_ENABLED"):
        monkeypatch.delenv(key, raising=False)
    return connection_status_projection(
        sid=SID, key_reader=keys, public_reader=public,
    )


def test_all_provider_statuses_reach_soulaana_without_credentials_or_vendor_data(monkeypatch):
    result = projection(monkeypatch)
    brief = result["soulaana_provider_status"]
    assert brief["schema"] == "OB_SOULAANA_PROVIDER_CONNECTION_STATUS_V1"
    assert brief["channel"] == "SOULAANA_CONNECTION_STATUS_ONLY"
    assert [r["provider"] for r in brief["provider_register"]] == list(PROVIDERS)
    assert {r["provider"]: r["state"] for r in brief["provider_register"]}["public"] == "TEMPORARY_AUTH_ONLY"
    assert {r["provider"]: r["state"] for r in brief["provider_register"]}["finnhub"] == "READ_ONLY_CHECK_PASSED"
    assert all(r["meaning"] for r in brief["provider_register"])
    for forbidden in (SECRET, ACCOUNT, "expires_at", "access_token", "account_id"):
        assert forbidden not in json.dumps(result)
        assert forbidden not in json.dumps(brief)
    for flag in (
        "raw_provider_values_included", "account_identifiers_included",
        "credentials_included", "source_content_ai_authorized", "quote_verified",
        "broker_execution_authorized", "capital_authorized",
    ):
        assert brief[flag] is False
    assert result["live_feed_count_verified"] is None
    assert result["may_authorize_order"] is False


@pytest.mark.parametrize("field,value", [
    ("prices_attached", True), ("positions_attached", True),
    ("may_authorize_order", True), ("may_authorize_capital", True),
    ("may_change_trading_mode", True), ("live_feed_count_verified", 1),
    ("owner_session_checked", False), ("no_browser_provider_credentials", False),
    ("dissemination_contract", "SOURCE_CONTENT_AI_APPROVED"),
])
def test_authority_promotion_or_contract_change_is_rejected(monkeypatch, field, value):
    packet = projection(monkeypatch)
    packet[field] = value
    with pytest.raises(ValueError, match="SOULAANA_PROVIDER_CONNECTION_HOLD"):
        build_soulaana_provider_status(packet)


@pytest.mark.parametrize("provider,field,value", [
    ("public", "state", "TEMPORARY_ACCOUNT_LINK_VERIFIED"),
    ("finnhub", "state", "LIVE_MARKET_DATA"),
    ("finnhub", "state", []),
    ("alpha_vantage", "quote_feed_activated", True),
    ("sec", "provider_request_made", True),
    ("bls", "ai_use_authorized", True),
    ("treasury", "reference_only", False),
    ("openfigi", "current_data_accepted", True),
])
def test_provider_state_tampering_or_unreviewed_ai_does_not_reach_soulaana(
        monkeypatch, provider, field, value):
    packet = projection(monkeypatch)
    for row in packet["provider_status"]:
        if row["provider"] == provider:
            row[field] = value
            break
    with pytest.raises(ValueError, match="SOULAANA_PROVIDER_CONNECTION_HOLD"):
        build_soulaana_provider_status(packet)


def test_default_off_and_revocation_status_are_truthful(monkeypatch):
    packet = projection(monkeypatch)
    states = {row["provider"]: row["state"]
              for row in packet["soulaana_provider_status"]["provider_register"]}
    assert all(states[k] == "RIGHTS_REVIEW_HOLD" for k in ("sec", "bls", "treasury", "openfigi"))
    monkeypatch.setenv("OB_KEYLESS_RESEARCH_ENABLED", "1")
    monkeypatch.setenv("OB_KEYLESS_BLS_USE_REVIEWED", "1")
    monkeypatch.setenv("OB_KEYLESS_BLS_OWNER_DISPLAY_REVIEWED", "1")
    granted = connection_status_projection(sid=SID, key_reader=keys, public_reader=public)
    bls = next(x for x in granted["soulaana_provider_status"]["provider_register"] if x["provider"] == "bls")
    assert bls["state"] == "USE_AND_OWNER_DISPLAY_CONFIGURED"
    assert "No actual data was requested" in bls["meaning"]
    monkeypatch.delenv("OB_KEYLESS_BLS_OWNER_DISPLAY_REVIEWED")
    again = connection_status_projection(sid=SID, key_reader=keys, public_reader=public)
    assert next(x for x in again["soulaana_provider_status"]["provider_register"]
                if x["provider"] == "bls")["state"] == "RIGHTS_REVIEW_HOLD"


def test_public_owner_selection_cannot_outlive_temporary_session_auth():
    def invalid(_sid):
        return {"authentication_temporarily_present": False, "account_linked": False,
                "owner_selection_required": True}
    with pytest.raises(ValueError, match="Public owner account choice"):
        connection_status_projection(sid=SID, key_reader=keys, public_reader=invalid)


def test_soulaana_displays_provider_status_in_all_eight_protected_rooms():
    rail = (ROOT / "web/static/ob/ob_keyless_context.js").read_text()
    for expected in (
        '"/ob/data-desk/connections.json"',
        '"OB_SOULAANA_PROVIDER_CONNECTION_STATUS_V1"',
        'readProviderSoulaana()',
        'credentials: "same-origin"',
        'providerSoulaana.replaceChildren',
        'item.meaning',
    ):
        assert expected in rail
    assert "innerHTML" not in rail
    assert "api.public.com" not in rail and "finnhub.io/api" not in rail
    for page in (
        "market_data_desk", "dashboard", "market_map", "symbol_page",
        "trade_center", "review_center", "owner_dashboard", "owner_console"
    ):
        html = (ROOT / "web/templates" / (page + ".html")).read_text()
        assert 'id="obKeylessContextRoot"' in html
        assert "/static/ob/ob_keyless_context.js" in html
