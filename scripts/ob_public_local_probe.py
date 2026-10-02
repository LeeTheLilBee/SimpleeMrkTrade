"""Owner-operated one-time Public business API proof, run ONLY on owner's machine.

No secret/token/account ID in argv, env, git, logs or output. No file writes.
Explicit allowlist: documented short-lived token POST, account-list GET, and
(optional, rights-reviewed) read-only single-equity quote POST. Never orders.
Public's docs name the token route 'personal'; confirm it applies to the
approved business account before using this script.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from getpass import getpass
import json
import re
import sys
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request

from engine.market_intake.public_quote_readonly import (
    PublicQuoteHold, PublicReadOnlyQuoteClient, PublicReadPolicy,
    QuoteRequest, _http,
)

_HOST = "https://api.public.com"
_AUTH = _HOST + "/userapiauthservice/personal/access-tokens"
_ACCOUNTS = _HOST + "/userapigateway/trading/account"
_LIMIT = 128_000
_SYMBOL = re.compile(r"^[A-Z][A-Z0-9.-]{0,13}$")


class ProbeHold(ValueError):
    """Sanitized outcome: never expose a response body or credentials."""


def _request_json(opener: Callable, request: Request, *, max_bytes: int = _LIMIT) -> object:
    if request.full_url not in {_AUTH, _ACCOUNTS}:
        raise ProbeHold("PROBE_ENDPOINT_NOT_ALLOWED")
    if (request.full_url == _AUTH and request.get_method() != "POST" or
        request.full_url == _ACCOUNTS and request.get_method() != "GET"):
        raise ProbeHold("PROBE_METHOD_NOT_ALLOWED")
    try:
        with opener(request, timeout=8) as response:
            payload = response.read(max_bytes + 1)
        if len(payload) > max_bytes:
            raise ProbeHold("PROBE_RESPONSE_TOO_LARGE")
        return json.loads(payload)
    except (HTTPError, URLError, TimeoutError, OSError):
        raise ProbeHold("PROBE_NETWORK_OR_AUTH_HOLD") from None
    except (UnicodeError, json.JSONDecodeError):
        raise ProbeHold("PROBE_INVALID_RESPONSE") from None


def get_short_token(secret: str, opener: Callable = _http) -> str:
    """Public-documented 15-minute token exchange; never printed or persisted."""
    if not isinstance(secret, str) or len(secret.strip()) < 10:
        raise ProbeHold("SECRET_NOT_CONFIGURED")
    request = Request(_AUTH, method="POST",
                      data=json.dumps({"validityInMinutes": 15, "secret": secret}).encode(),
                      headers={"Content-Type": "application/json", "Accept": "application/json"})
    payload = _request_json(opener, request)
    if (not isinstance(payload, dict)
        or not isinstance(payload.get("accessToken"), str)
        or len(payload["accessToken"]) < 20):
        raise ProbeHold("ACCESS_TOKEN_NOT_RETURNED")
    return payload["accessToken"]


def select_account(access_token: str, opener: Callable = _http, *,
                   choose_index: Callable[[int], int]) -> str:
    """Display only ordinal/type, never account ID, cash, holdings or key."""
    request = Request(_ACCOUNTS, method="GET",
                      headers={"Authorization": "Bearer " + access_token,
                               "Accept": "application/json",
                               "Content-Type": "application/json"})
    payload = _request_json(opener, request)
    if (not isinstance(payload, dict) or not isinstance(payload.get("accounts"), list)
        or not payload["accounts"] or len(payload["accounts"]) > 20):
        raise ProbeHold("ACCOUNT_DISCOVERY_HOLD")
    ids = set()
    accounts = []
    for row in payload["accounts"]:
        if not isinstance(row, dict):
            raise ProbeHold("ACCOUNT_DISCOVERY_HOLD")
        account_id = row.get("accountId")
        if (not isinstance(account_id, str)
            or not re.fullmatch(r"[A-Za-z0-9_-]{5,128}", account_id)
            or account_id in ids):
            raise ProbeHold("ACCOUNT_DISCOVERY_HOLD")
        ids.add(account_id)
        accounts.append((account_id, row.get("accountType")))
    print(f"Account discovery: {len(accounts)} account(s) accessible.")
    for i, (_, kind) in enumerate(accounts, 1):
        print(f"  {i}. API type: {kind if kind in {'BROKERAGE', 'RETIREMENT', 'HIGH_YIELD_CASH'} else 'OTHER'}")
    selected = choose_index(len(accounts))
    if type(selected) is not int or not 1 <= selected <= len(accounts):
        raise ProbeHold("ACCOUNT_SELECTION_HOLD")
    return accounts[selected - 1][0]


def run_probe(*, equity: str | None = None,
              terms_confirmed: bool = False,
              quote_rights_confirmed: bool = False,
              opener: Callable = _http,
              secret_reader: Callable[[str], str] = getpass,
              account_chooser: Callable[[int], int] | None = None) -> dict[str, object]:
    """Return only a non-secret completion report; never claim a deployed feed.

    Terms confirmation is a human action, not a substitute for provider's rights.
    """
    if terms_confirmed is not True:
        raise ProbeHold("BUSINESS_AUTH_TERMS_CONFIRMATION_REQUIRED")
    if equity is not None and (not _SYMBOL.fullmatch(equity)
                               or quote_rights_confirmed is not True):
        raise ProbeHold("EQUITY_QUOTE_RIGHTS_HOLD")
    secret = secret_reader("Paste Public secret key (hidden, never saved): ")
    token = get_short_token(secret, opener)
    del secret
    chooser = account_chooser
    if chooser is None:
        def chooser(count: int) -> int:
            try:
                return int(input(f"Select the confirmed business brokerage account (1-{count}): "))
            except (ValueError, EOFError):
                raise ProbeHold("ACCOUNT_SELECTION_HOLD") from None
    account_id = select_account(token, opener, choose_index=chooser)
    report: dict[str, object] = {
        "auth": "ACCESS_TOKEN_AND_ACCOUNT_LOOKUP_OK",
        "quote": "NOT_REQUESTED",
        "source_only": True,
        "market_feed_connected": False,
        "trading_authorized": False,
        "account_id_printed": False,
        "credentials_persisted": False,
    }
    if equity is not None:
        # Only source-only confirmation: self-reported quote permissions do NOT
        # install a feed, assert venue/SIP/OPRA or authorize AI/redistribution.
        policy = PublicReadPolicy(True, True, True, True, True, False)
        client = PublicReadOnlyQuoteClient(policy, opener=opener)
        observations = client.fetch_once(
            backend_account_id=account_id,
            backend_access_token=token,
            requests=[QuoteRequest(equity, "EQUITY")])
        observed = observations[0].normalized["observed_at"]
        event = datetime.fromisoformat(str(observed))
        report["quote"] = "SOURCE_RESPONSE_VALIDATED"
        report["quote_event_age_seconds"] = round(
            (observations[0].retrieved_at - event).total_seconds(), 2)
        report["live_quote_entitlement_verified"] = False
    del token, account_id
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="One-time, no-write Public account check.")
    parser.add_argument("--business-auth-confirmed", action="store_true",
                        help="Confirm Public business account may use documented token exchange")
    parser.add_argument("--equity", metavar="SYMBOL",
                        help="Optional single equity quote; authentication check is the default")
    parser.add_argument("--quote-rights-confirmed", action="store_true",
                        help="Confirm actual account's internal/owner marketdata permission")
    args = parser.parse_args(argv)
    if not args.business_auth_confirmed:
        print("HOLD: confirm Public's documented token flow applies to your business key.")
        print("No key requested. No network call made.")
        return 2
    if args.equity and not args.quote_rights_confirmed:
        print("HOLD: explicit account marketdata owner/non-display rights required.")
        print("No key requested. No network call made.")
        return 2
    try:
        report = run_probe(
            equity=args.equity, terms_confirmed=True,
            quote_rights_confirmed=args.quote_rights_confirmed)
    except (ProbeHold, PublicQuoteHold) as exc:
        # These exceptions intentionally contain only redacted enums.
        print(f"HOLD: {exc}")
        return 2
    print(json.dumps(report, sort_keys=True))
    print("No trades, persistence, browser credentials or runtime feed activation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
