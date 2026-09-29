"""Synthetic, offline, credential-redacted Public one-shot auth checks."""
from datetime import datetime, timedelta, timezone
import json

import pytest

from scripts.ob_public_local_probe import (
    ProbeHold, _AUTH, _ACCOUNTS, get_short_token, select_account, run_probe,
    main,
)


SECRET = "syntheticSecretDoNotUse_123456789"
TOKEN = "syntheticBearerTokenDoNotUse_123456789"
ACCOUNT_ID = "synthetic-business-account-1"


class Response:
    def __init__(self, body):
        self.body = json.dumps(body).encode()
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, size):
        return self.body[:size]


class Recorder:
    def __init__(self):
        self.calls = []
    def __call__(self, request, timeout):
        self.calls.append((request, timeout))
        if request.full_url == _AUTH:
            assert request.get_method() == "POST"
            body = json.loads(request.data)
            assert body == {"secret": SECRET, "validityInMinutes": 15}
            return Response({"accessToken": TOKEN})
        if request.full_url == _ACCOUNTS:
            assert request.get_method() == "GET"
            assert request.get_header("Authorization") == "Bearer " + TOKEN
            # Keep account lookup aligned with Public's documented quickstart.
            assert request.get_header("Content-type") == "application/json"
            return Response({"accounts": [
                {"accountId": ACCOUNT_ID, "accountType": "BROKERAGE"},
                {"accountId": "another-valid-account-22", "accountType": "RETIREMENT"},
            ]})
        if request.full_url.endswith("/quotes"):
            assert request.get_method() == "POST"
            assert request.full_url.endswith(ACCOUNT_ID + "/quotes")
            assert json.loads(request.data) == {
                "instruments": [{"symbol": "AAPL", "type": "EQUITY"}]}
            stamp = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
            return Response({"quotes": [{
                "instrument": {"symbol": "AAPL", "type": "EQUITY"},
                "outcome": "SUCCESS",
                "last": "101.00", "bid": "100.90", "ask": "101.10",
                "lastTimestamp": stamp, "bidTimestamp": stamp, "askTimestamp": stamp,
                "previousClose": "99.00", "volume": 100,
            }]})
        raise AssertionError("Unapproved network endpoint")


def test_default_cli_never_reads_key_or_network(capsys):
    assert main([]) == 2
    assert "No network call made" in capsys.readouterr().out
    assert main(["--business-auth-confirmed", "--equity", "AAPL"]) == 2


def test_only_documented_auth_post_then_account_get_and_no_sensitive_logs(capsys):
    rec = Recorder()
    result = run_probe(terms_confirmed=True, opener=rec,
                       secret_reader=lambda prompt: SECRET,
                       account_chooser=lambda count: 1)
    assert result == {
        "auth": "ACCESS_TOKEN_AND_ACCOUNT_LOOKUP_OK",
        "quote": "NOT_REQUESTED",
        "source_only": True,
        "market_feed_connected": False,
        "trading_authorized": False,
        "account_id_printed": False,
        "credentials_persisted": False,
    }
    output = capsys.readouterr().out
    assert all(x not in output and x not in str(result)
               for x in (SECRET, TOKEN, ACCOUNT_ID, "another-valid-account-22"))
    assert [r.full_url for r, _ in rec.calls] == [_AUTH, _ACCOUNTS]
    assert [r.get_method() for r, _ in rec.calls] == ["POST", "GET"]


def test_no_secret_collection_or_calls_before_permission_gate():
    rec = Recorder()
    prompts = []
    def ask(prompt):
        prompts.append(prompt)
        return SECRET
    with pytest.raises(ProbeHold, match="BUSINESS_AUTH_TERMS"):
        run_probe(opener=rec, secret_reader=ask)
    with pytest.raises(ProbeHold, match="EQUITY_QUOTE_RIGHTS_HOLD"):
        run_probe(equity="AAPL", terms_confirmed=True, opener=rec,
                  secret_reader=ask)
    assert not prompts and not rec.calls


def test_quote_success_stays_source_only_no_trades_or_price_dump(capsys):
    rec = Recorder()
    result = run_probe(terms_confirmed=True, quote_rights_confirmed=True,
                       equity="AAPL", opener=rec, secret_reader=lambda _: SECRET,
                       account_chooser=lambda count: 1)
    assert result["quote"] == "SOURCE_RESPONSE_VALIDATED"
    assert result["market_feed_connected"] is False
    assert result["trading_authorized"] is False
    assert result["live_quote_entitlement_verified"] is False
    assert result["quote_event_age_seconds"] >= 0
    assert len(rec.calls) == 3
    output = capsys.readouterr().out
    assert not any(x in output for x in (SECRET, TOKEN, ACCOUNT_ID))
    assert all("order" not in request.full_url and "preflight" not in request.full_url
               for request, _ in rec.calls)


def test_wrong_account_selection_is_a_hold():
    rec = Recorder()
    with pytest.raises(ProbeHold, match="ACCOUNT_SELECTION_HOLD"):
        run_probe(terms_confirmed=True, opener=rec,
                  secret_reader=lambda _: SECRET,
                  account_chooser=lambda count: 3)
    assert len(rec.calls) == 2


def test_no_secret_error_reflection_and_no_account_data(capsys):
    rec = Recorder()
    assert get_short_token(SECRET, rec) == TOKEN
    assert select_account(TOKEN, rec, choose_index=lambda n: 1) == ACCOUNT_ID
    output = capsys.readouterr().out
    assert SECRET not in output and TOKEN not in output and ACCOUNT_ID not in output
