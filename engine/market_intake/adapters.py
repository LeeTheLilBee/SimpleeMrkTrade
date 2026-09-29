"""OBSCAN provider ingress: explicitly mapped, licensed payloads; no HTTP or SDK coupling.

A vendor's JSON is untrusted. Adapters are installed only after rights verification.
A live quote is never dated with receipt time when the upstream timestamp is absent.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Mapping

from .contracts import (EquityQuote, Observation, OptionQuote, SourceRights,
                        clean_symbol)


def _stamp(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("provider event timestamp must be an ISO string with UTC offset")
    try:
        found = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid provider timestamp") from exc
    if found.tzinfo is None or found.utcoffset() is None:
        raise ValueError("naive provider event timestamp may not assert freshness")
    return found


def _field(raw: Mapping[str, object], mapping: Mapping[str, str], name: str) -> object:
    key = mapping.get(name)
    if not key or key not in raw or raw[key] is None:
        raise ValueError(f"provider field mapping missing {name}")
    return raw[key]


def _count(value: object, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer, not a boolean")
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be integer numeric") from exc
    if not isfinite(numeric) or numeric < 0 or not numeric.is_integer():
        raise ValueError(f"{name} must be a nonnegative integer")
    return int(numeric)


@dataclass(frozen=True)
class FeedAdapter:
    source: SourceRights
    fields: Mapping[str, str]
    feed_label: str = "unknown"
    instrument: str = "equity"

    def __post_init__(self) -> None:
        if self.instrument not in {"equity", "option"}:
            raise ValueError("feed adapter must identify quote instrument")
        if self.feed_label not in {"realtime", "delayed", "historical", "unknown"}:
            raise ValueError("explicit feed label required")
        if not self.source.reviewed_for_scan():
            raise ValueError("no unreviewed source may be installed as a live research adapter")
        if self.instrument not in self.source.entitled_instruments:
            raise ValueError("instrument-specific entitlement is required for adapter installation")
        if self.feed_label == "realtime" and not self.source.real_time_entitled:
            raise ValueError("unknown or delayed entitlement cannot declare live ingress")

    def normalize(self, raw: Mapping[str, object], *, received_at: datetime) -> EquityQuote | OptionQuote:
        if not isinstance(raw, Mapping):
            raise ValueError("provider payload must be a mapping")
        f = lambda name: _field(raw, self.fields, name)
        observed = _stamp(f("observed_at"))
        # Source ID, lineage and entitlements come from the installed registry,
        # never from arbitrary response keys.
        identity = Observation(str(f("observation_id")), self.source.source_id,
            self.source.upstream_family, clean_symbol(str(f("underlying" if self.instrument=="option" else "symbol"))),
            observed, received_at, str(f("provenance_reference")), self.feed_label, self.instrument)
        if self.instrument == "equity":
            return EquityQuote(identity, float(f("last")), float(f("bid")), float(f("ask")),
                float(f("previous_close")) if self.fields.get("previous_close") in raw and
                raw.get(self.fields["previous_close"]) is not None else None,
                _count(f("volume"), "volume") if self.fields.get("volume") in raw and
                raw.get(self.fields["volume"]) is not None else None,
                float(f("average_volume")) if self.fields.get("average_volume") in raw and
                raw.get(self.fields["average_volume"]) is not None else None)
        return OptionQuote(identity,str(f("underlying")),str(f("occ_symbol")),
            float(f("bid")),float(f("ask")),float(f("strike")),str(f("expiry")),str(f("right")),
            _count(f("open_interest"), "open_interest") if self.fields.get("open_interest") in raw and
            raw.get(self.fields["open_interest"]) is not None else None,
            int(f("volume")) if self.fields.get("volume") in raw and
            raw.get(self.fields["volume"]) is not None else None)


class IngressRegistry:
    """A provider cannot set its own entitlement flags by submitting a JSON payload."""
    def __init__(self) -> None:
        self._adapters: dict[tuple[str, str], FeedAdapter] = {}

    def register(self, adapter: FeedAdapter) -> None:
        key=(adapter.source.source_id,adapter.instrument)
        if key in self._adapters:
            raise ValueError("duplicate feed adapter requires explicit replacement review")
        self._adapters[key]=adapter

    def normalize(self, source_id: str, instrument: str, raw: Mapping[str, object], *,
                  received_at: datetime) -> EquityQuote | OptionQuote:
        return self._adapters[(source_id,instrument)].normalize(raw,received_at=received_at)

    def capability_snapshot(self) -> dict[str, object]:
        return {"providers":sorted(set(key[0] for key in self._adapters)),
            "adapted_lanes":sorted(f"{a}:{b}" for a,b in self._adapters),
            "network_enabled":False,"order_transport_enabled":False,
            "provider_claims_cannot_override_registry_rights":True}
