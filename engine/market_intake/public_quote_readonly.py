"""Optional read-only Public account quote transport: SOURCE ONLY; disabled by default.

The Public API documents a no-call-fee marketdata endpoint. An API key is not
a market-data/display/non-display/AI license. This does NOT authenticate using
an account secret, create orders, attach Tower, enable a feed or claim OPRA/SIP.
A vetted backend may inject an already short-lived bearer after separate review.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import json
import re
from typing import Callable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler

from .contracts import OCC, clean_symbol

DOCS = "https://public.com/api/docs/resources/market-data/get-quotes"
OPTION_EXPIRATIONS_DOCS = "https://public.com/api/docs/resources/market-data/get-option-expirations"
OPTION_CHAIN_DOCS = "https://public.com/api/docs/resources/market-data/get-option-chain"
_HOST = "https://api.public.com"
_ACCOUNT = re.compile(r"^[A-Za-z0-9_-]{5,128}$")
_OPTION = re.compile(r"^([A-Z0-9./-]{1,6})(\d{6})([CP])(\d{8})$")
_MAX_RESPONSE_BYTES = 500_000
_MAX_CHAIN_RESPONSE_BYTES = 2_000_000
_MAX_QUOTE_BATCH = 8
_MAX_CHAIN_SIDE = 8


class PublicQuoteHold(ValueError):
    """Redacted failure; do not expose source response, token or account ID."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _http(request: Request, timeout: int):
    return build_opener(_NoRedirect()).open(request, timeout=timeout)


@dataclass(frozen=True)
class PublicReadPolicy:
    account_scope_reviewed: bool = False
    non_display_use_reviewed: bool = False
    owner_display_reviewed: bool = False
    marketdata_scope_verified: bool = False
    equity_entitled: bool = False
    option_entitled: bool = False

    def permits(self, kinds: set[str]) -> bool:
        return (self.account_scope_reviewed is True
                and self.non_display_use_reviewed is True
                and self.owner_display_reviewed is True
                and self.marketdata_scope_verified is True
                and all(self.equity_entitled is True if k == "EQUITY"
                        else self.option_entitled is True if k == "OPTION" else False
                        for k in kinds))


@dataclass(frozen=True)
class QuoteRequest:
    symbol: str
    kind: str

    def __post_init__(self):
        if self.kind not in {"EQUITY", "OPTION"}:
            raise ValueError("only equity and option research quotes supported")
        if not isinstance(self.symbol, str) or self.symbol != self.symbol.upper():
            raise ValueError("exact uppercase symbol required")
        if self.kind == "EQUITY":
            clean_symbol(self.symbol)
        elif not _OPTION.fullmatch(self.symbol):
            raise ValueError("exact compact OSI option symbol required")


@dataclass(frozen=True)
class PublicSourceQuote:
    """Gateway-shaped mapping, but neither license nor freshness gate is granted."""
    kind: str
    normalized: Mapping[str, object]
    last_timestamp: datetime
    bid_timestamp: datetime
    ask_timestamp: datetime
    retrieved_at: datetime
    source_reference: str = DOCS
    quote_verified_live: bool = False
    gateway_installed: bool = False
    broker_execution_authorized: bool = False

    def gateway_fields(self) -> dict[str, object]:
        """Only for separate, entitled UniversalMarketGateway.ingest().
        Source ID and upstream market-data family MUST come from SourceRights,
        never from this vendor payload.
        """
        return dict(self.normalized)


def _timestamp(value: object, received_at: datetime) -> datetime:
    if not isinstance(value, str):
        raise PublicQuoteHold("PUBLIC_TIMESTAMP_MISSING")
    try:
        found = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise PublicQuoteHold("PUBLIC_TIMESTAMP_INVALID") from None
    if found.tzinfo is None or found.utcoffset() is None:
        raise PublicQuoteHold("PUBLIC_TIMESTAMP_INVALID")
    if found > received_at + timedelta(seconds=2):
        raise PublicQuoteHold("PUBLIC_TIMESTAMP_FUTURE")
    return found.astimezone(timezone.utc)


def _number(value: object, *, allow_zero: bool = False) -> float:
    if not isinstance(value, str):
        raise PublicQuoteHold("PUBLIC_PRICE_INVALID")
    try:
        decimal = Decimal(value)
    except InvalidOperation:
        raise PublicQuoteHold("PUBLIC_PRICE_INVALID") from None
    if not decimal.is_finite() or (decimal < 0 if allow_zero else decimal <= 0):
        raise PublicQuoteHold("PUBLIC_PRICE_INVALID")
    try:
        numeric = float(decimal)
    except (ValueError, OverflowError):
        raise PublicQuoteHold("PUBLIC_PRICE_INVALID") from None
    if (not numeric < float("inf") or (numeric < 0 if allow_zero else numeric <= 0)):
        raise PublicQuoteHold("PUBLIC_PRICE_INVALID")
    return numeric


def _count(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or type(value) is not int or value < 0:
        raise PublicQuoteHold("PUBLIC_COUNT_INVALID")
    return value


def _option_parts(symbol: str):
    match = _OPTION.fullmatch(symbol)
    if match is None:
        raise PublicQuoteHold("PUBLIC_OPTION_ID_INVALID")
    root, yymmdd, right, strike_raw = match.groups()
    try:
        expiry = datetime.strptime(yymmdd, "%y%m%d").date().isoformat()
    except ValueError:
        raise PublicQuoteHold("PUBLIC_OPTION_EXPIRY_INVALID") from None
    underlying = clean_symbol(root)
    occ = f"{root:<6}{yymmdd}{right}{strike_raw}"
    if not OCC.fullmatch(occ):
        raise PublicQuoteHold("PUBLIC_OPTION_ID_INVALID")
    return underlying, occ, expiry, "call" if right == "C" else "put", int(strike_raw) / 1000


def normalize_public_quotes(payload: object, requests: Sequence[QuoteRequest], *,
                            received_at: datetime) -> tuple[PublicSourceQuote, ...]:
    """Strictly match every returned requested instrument; any ambiguity HOLDs batch.

    Separate last/bid/ask timestamps are preserved. The oldest event timestamp
    determines the gateway observation; a fresh bid cannot conceal stale last.
    """
    if received_at.tzinfo is None or received_at.utcoffset() is None:
        raise ValueError("received_at must have timezone")
    if not isinstance(payload, dict) or not isinstance(payload.get("quotes"), list):
        raise PublicQuoteHold("PUBLIC_RESPONSE_SHAPE_HOLD")
    rows = payload["quotes"]
    if not requests or len(requests) > _MAX_QUOTE_BATCH or len(rows) != len(requests):
        raise PublicQuoteHold("PUBLIC_BATCH_MISMATCH")
    expected = {(q.kind, q.symbol) for q in requests}
    if len(expected) != len(requests):
        raise PublicQuoteHold("PUBLIC_DUPLICATE_REQUEST")
    seen = set()
    output = []
    for row in rows:
        if not isinstance(row, dict) or row.get("outcome") != "SUCCESS":
            raise PublicQuoteHold("PUBLIC_QUOTE_UNAVAILABLE")
        instrument = row.get("instrument")
        if not isinstance(instrument, dict):
            raise PublicQuoteHold("PUBLIC_INSTRUMENT_MISSING")
        kind, symbol = instrument.get("type"), instrument.get("symbol")
        if (kind, symbol) not in expected or (kind, symbol) in seen:
            raise PublicQuoteHold("PUBLIC_INSTRUMENT_MISMATCH")
        seen.add((kind, symbol))
        last_stamp = _timestamp(row.get("lastTimestamp"), received_at)
        bid_stamp = _timestamp(row.get("bidTimestamp"), received_at)
        ask_stamp = _timestamp(row.get("askTimestamp"), received_at)
        last = _number(row.get("last"))
        bid = _number(row.get("bid"), allow_zero=kind == "OPTION")
        ask = _number(row.get("ask"))
        if bid > ask:
            raise PublicQuoteHold("PUBLIC_CROSSED_QUOTE")
        # Do not use receipt time as event time; this intentionally preserves
        # the oldest source-reported leg, so gateway temporal gates can HOLD.
        oldest = min(last_stamp, bid_stamp, ask_stamp)
        normalized = {
            "observation_id": f"public:{kind}:{symbol}:{oldest.isoformat()}",
            "observed_at": oldest.isoformat(),
            "provenance_reference": DOCS,
            "bid": bid, "ask": ask,
        }
        if kind == "EQUITY":
            normalized.update(symbol=symbol, last=last)
            previous = row.get("previousClose")
            if previous is not None:
                normalized["previous_close"] = _number(previous)
            volume = _count(row.get("volume"))
            if volume is not None:
                normalized["volume"] = volume
        else:
            root, occ, expiry, side, strike = _option_parts(symbol)
            details = row.get("optionDetails")
            if isinstance(details, dict) and details.get("strikePrice") is not None:
                if abs(_number(details["strikePrice"]) - strike) > 0.000001:
                    raise PublicQuoteHold("PUBLIC_OPTION_STRIKE_CONFLICT")
            normalized.update(underlying=root, occ_symbol=occ, expiry=expiry,
                              right=side, strike=strike)
            for original, target in (("volume", "volume"), ("openInterest", "open_interest")):
                count = _count(row.get(original))
                if count is not None:
                    normalized[target] = count
        output.append(PublicSourceQuote(kind, normalized, last_stamp, bid_stamp,
                                        ask_stamp, received_at))
    if seen != expected:
        raise PublicQuoteHold("PUBLIC_INSTRUMENT_MISMATCH")
    return tuple(output)


class PublicReadOnlyQuoteClient:
    """Never runs in Tower page render; no auth or order endpoints are available."""

    def __init__(self, policy: PublicReadPolicy, *, opener: Callable | None = None):
        if not isinstance(policy, PublicReadPolicy):
            raise TypeError("explicit exact use-and-scope policy required")
        self.policy = policy
        self._open = opener or _http

    def fetch_once(self, *, backend_account_id: str, backend_access_token: str,
                   requests: Sequence[QuoteRequest]) -> tuple[PublicSourceQuote, ...]:
        if (not requests or len(requests) > _MAX_QUOTE_BATCH
                or any(not isinstance(q, QuoteRequest) for q in requests)
                or len({(q.kind, q.symbol) for q in requests}) != len(requests)):
            raise PublicQuoteHold("PUBLIC_REQUEST_INVALID")
        if not self.policy.permits({q.kind for q in requests}):
            raise PublicQuoteHold("PUBLIC_SCOPE_RIGHTS_HOLD")
        if not isinstance(backend_account_id, str) or not _ACCOUNT.fullmatch(backend_account_id):
            raise PublicQuoteHold("PUBLIC_ACCOUNT_NOT_CONFIGURED")
        if (not isinstance(backend_access_token, str) or
                not re.fullmatch(r"[A-Za-z0-9._~+/=-]{20,4096}", backend_access_token)):
            raise PublicQuoteHold("PUBLIC_BACKEND_TOKEN_NOT_CONFIGURED")
        request = Request(
            f"{_HOST}/userapigateway/marketdata/{backend_account_id}/quotes",
            data=json.dumps({"instruments": [
                {"symbol": q.symbol, "type": q.kind} for q in requests]}).encode(),
            headers={"Content-Type": "application/json", "Accept": "application/json",
                     "Authorization": "Bearer " + backend_access_token}, method="POST")
        try:
            with self._open(request, timeout=8) as response:
                raw = response.read(_MAX_RESPONSE_BYTES + 1)
            if len(raw) > _MAX_RESPONSE_BYTES:
                raise PublicQuoteHold("PUBLIC_RESPONSE_TOO_LARGE")
            payload = json.loads(raw)
        except (HTTPError, URLError, OSError, TimeoutError):
            raise PublicQuoteHold("PUBLIC_TRANSPORT_HOLD") from None
        except (UnicodeError, json.JSONDecodeError):
            raise PublicQuoteHold("PUBLIC_RESPONSE_SHAPE_HOLD") from None
        received = datetime.now(timezone.utc)
        return normalize_public_quotes(payload, requests, received_at=received)


@dataclass(frozen=True)
class PublicOptionChainSnapshot:
    underlying: str
    expiration: str
    underlying_midpoint: float
    contracts: tuple[Mapping[str, object], ...]
    retrieved_at: datetime
    source_reference: str = OPTION_CHAIN_DOCS
    personal_owner_only: bool = True
    broker_execution_authorized: bool = False


def _signed_number(value: object, *, allow_zero: bool = True) -> float:
    if not isinstance(value, str):
        raise PublicQuoteHold("PUBLIC_OPTION_NUMBER_INVALID")
    try:
        decimal = Decimal(value)
    except InvalidOperation:
        raise PublicQuoteHold("PUBLIC_OPTION_NUMBER_INVALID") from None
    if not decimal.is_finite() or (not allow_zero and decimal == 0):
        raise PublicQuoteHold("PUBLIC_OPTION_NUMBER_INVALID")
    try:
        numeric = float(decimal)
    except (ValueError, OverflowError):
        raise PublicQuoteHold("PUBLIC_OPTION_NUMBER_INVALID") from None
    if not (-float("inf") < numeric < float("inf")):
        raise PublicQuoteHold("PUBLIC_OPTION_NUMBER_INVALID")
    return numeric


def _read_json_response(opener: Callable, request: Request, *, max_bytes: int) -> object:
    try:
        with opener(request, timeout=8) as response:
            raw = response.read(max_bytes + 1)
        if len(raw) > max_bytes:
            raise PublicQuoteHold("PUBLIC_RESPONSE_TOO_LARGE")
        return json.loads(raw)
    except (HTTPError, URLError, OSError, TimeoutError):
        raise PublicQuoteHold("PUBLIC_TRANSPORT_HOLD") from None
    except (UnicodeError, json.JSONDecodeError):
        raise PublicQuoteHold("PUBLIC_RESPONSE_SHAPE_HOLD") from None


def _option_chain_row(row: object, *, right: str, expiration: str,
                      underlying_midpoint: float, received_at: datetime
                      ) -> Mapping[str, object] | None:
    if not isinstance(row, dict) or row.get("outcome") != "SUCCESS":
        return None
    instrument = row.get("instrument")
    if not isinstance(instrument, dict):
        return None
    symbol = instrument.get("symbol")
    if not isinstance(symbol, str):
        return None
    symbol = symbol.upper()
    match = _OPTION.fullmatch(symbol)
    if match is None:
        return None
    underlying, occ, parsed_expiry, parsed_right, strike = _option_parts(symbol)
    if parsed_expiry != expiration or parsed_right != right:
        return None

    details = row.get("optionDetails")
    if not isinstance(details, dict):
        return None
    try:
        stated_strike = _number(details.get("strikePrice"))
        if abs(stated_strike - strike) > 0.000001:
            return None
        bid = _number(row.get("bid"), allow_zero=True)
        ask = _number(row.get("ask"))
        if bid > ask:
            return None
        mid = _number(details.get("midPrice"), allow_zero=True)
        last_raw = row.get("last")
        last = _number(last_raw, allow_zero=True) if last_raw is not None else None
        volume = _count(row.get("volume"))
        open_interest = _count(row.get("openInterest"))
        observed = min(
            _timestamp(row.get("lastTimestamp"), received_at),
            _timestamp(row.get("bidTimestamp"), received_at),
            _timestamp(row.get("askTimestamp"), received_at),
        )
    except PublicQuoteHold:
        return None

    greeks_raw = details.get("greeks")
    greeks = {}
    if isinstance(greeks_raw, dict):
        for source, target in (
            ("delta", "delta"), ("gamma", "gamma"), ("theta", "theta"),
            ("vega", "vega"), ("rho", "rho"),
            ("impliedVolatility", "implied_volatility"),
        ):
            value = greeks_raw.get(source)
            if value is None:
                continue
            try:
                parsed = _signed_number(value)
            except PublicQuoteHold:
                continue
            if target == "implied_volatility" and parsed < 0:
                continue
            greeks[target] = parsed

    return {
        "occ_symbol": occ.replace(" ", ""),
        "provider_symbol": symbol,
        "underlying": underlying,
        "right": right,
        "expiration": expiration,
        "strike": strike,
        "bid": bid,
        "ask": ask,
        "mid": mid,
        "last": last,
        "volume": volume,
        "open_interest": open_interest,
        "greeks": greeks,
        "observed_at": observed.isoformat(),
        "distance_from_underlying": abs(strike - underlying_midpoint),
    }


class PublicReadOnlyOptionChainClient:
    """Bounded owner-only option-chain research; never an order client."""

    def __init__(self, policy: PublicReadPolicy, *, opener: Callable | None = None):
        if not isinstance(policy, PublicReadPolicy):
            raise TypeError("explicit exact use-and-scope policy required")
        self.policy = policy
        self._open = opener or _http

    def _post(self, *, backend_account_id: str, backend_access_token: str,
              suffix: str, body: Mapping[str, object], max_bytes: int) -> object:
        if not self.policy.permits({"EQUITY", "OPTION"}):
            raise PublicQuoteHold("PUBLIC_SCOPE_RIGHTS_HOLD")
        if not isinstance(backend_account_id, str) or not _ACCOUNT.fullmatch(backend_account_id):
            raise PublicQuoteHold("PUBLIC_ACCOUNT_NOT_CONFIGURED")
        if (not isinstance(backend_access_token, str) or
                not re.fullmatch(r"[A-Za-z0-9._~+/=-]{20,4096}", backend_access_token)):
            raise PublicQuoteHold("PUBLIC_BACKEND_TOKEN_NOT_CONFIGURED")
        request = Request(
            f"{_HOST}/userapigateway/marketdata/{backend_account_id}/{suffix}",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "Accept": "application/json",
                     "Authorization": "Bearer " + backend_access_token},
            method="POST",
        )
        return _read_json_response(self._open, request, max_bytes=max_bytes)

    def fetch_nearest(self, *, backend_account_id: str, backend_access_token: str,
                      symbol: str) -> PublicOptionChainSnapshot:
        symbol = clean_symbol(str(symbol or "").strip().upper())
        expirations_payload = self._post(
            backend_account_id=backend_account_id,
            backend_access_token=backend_access_token,
            suffix="option-expirations",
            body={"instrument": {"symbol": symbol, "type": "EQUITY"}},
            max_bytes=_MAX_RESPONSE_BYTES,
        )
        if (not isinstance(expirations_payload, dict)
                or expirations_payload.get("baseSymbol") != symbol
                or not isinstance(expirations_payload.get("expirations"), list)):
            raise PublicQuoteHold("PUBLIC_OPTION_EXPIRATIONS_SHAPE_HOLD")

        today = datetime.now(timezone.utc).date()
        expirations = []
        for value in expirations_payload["expirations"]:
            if not isinstance(value, str):
                continue
            try:
                parsed = datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                continue
            if parsed >= today:
                expirations.append(parsed)
        if not expirations:
            raise PublicQuoteHold("PUBLIC_OPTION_EXPIRATIONS_EMPTY")
        expiration = min(expirations).isoformat()

        equity = PublicReadOnlyQuoteClient(self.policy, opener=self._open).fetch_once(
            backend_account_id=backend_account_id,
            backend_access_token=backend_access_token,
            requests=[QuoteRequest(symbol=symbol, kind="EQUITY")],
        )[0]
        bid = float(equity.normalized["bid"])
        ask = float(equity.normalized["ask"])
        midpoint = round((bid + ask) / 2.0, 6)

        chain_payload = self._post(
            backend_account_id=backend_account_id,
            backend_access_token=backend_access_token,
            suffix="option-chain",
            body={
                "instrument": {"symbol": symbol, "type": "EQUITY"},
                "expirationDate": expiration,
            },
            max_bytes=_MAX_CHAIN_RESPONSE_BYTES,
        )
        if (not isinstance(chain_payload, dict)
                or chain_payload.get("baseSymbol") != symbol
                or not isinstance(chain_payload.get("calls"), list)
                or not isinstance(chain_payload.get("puts"), list)):
            raise PublicQuoteHold("PUBLIC_OPTION_CHAIN_SHAPE_HOLD")

        received = datetime.now(timezone.utc)
        selected = []
        for right, rows in (("call", chain_payload["calls"]), ("put", chain_payload["puts"])):
            parsed = [
                item for item in (
                    _option_chain_row(
                        row, right=right, expiration=expiration,
                        underlying_midpoint=midpoint, received_at=received,
                    )
                    for row in rows
                )
                if item is not None
            ]
            parsed.sort(key=lambda item: (
                float(item["distance_from_underlying"]),
                -int(item["open_interest"] or 0),
                -int(item["volume"] or 0),
            ))
            selected.extend(parsed[:_MAX_CHAIN_SIDE])

        if not selected:
            raise PublicQuoteHold("PUBLIC_OPTION_CHAIN_EMPTY")

        selected.sort(key=lambda item: (
            item["right"], float(item["strike"]), str(item["provider_symbol"])
        ))
        return PublicOptionChainSnapshot(
            underlying=symbol,
            expiration=expiration,
            underlying_midpoint=midpoint,
            contracts=tuple(selected),
            retrieved_at=received,
        )
