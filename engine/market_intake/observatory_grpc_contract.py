"""Fail-closed adapter for the Observatory internal gRPC contract.

This module deliberately does not start a network server. Today the relevant OB
components still share one protected process, so a loopback gRPC server would
add failure modes without creating a real service boundary. The protobuf file is
the stable wire contract for the later process split; this adapter guarantees
that only the content-free ObservatoryEventHub envelope can cross that boundary.
"""
from __future__ import annotations

import re

from .observatory_event_stream import EVENT_SCHEMA, TRACE_STAGES

GRPC_PACKAGE = "simplee.observatory.v1"
GRPC_EVENT_SCHEMA = "SIMPLEE_OBSERVATORY_GRPC_EVENT_V1"
PROTO_PATH = "proto/observatory_event_v1.proto"

_EVENT_ID = re.compile(r"^[0-9a-f]{24}\.[1-9][0-9]*$")
_CONSUMER = re.compile(r"^[a-z0-9][a-z0-9_.:-]{0,95}$")
_ALLOWED_TYPES = frozenset({
    "research_context_changed",
    "source_status_changed",
    "market_snapshot_changed",
    "scanner_context_changed",
    "candidate_context_changed",
})
_ALLOWED_CHANNELS = frozenset({"research", "system", "market", "scanner", "candidate"})
_ALLOWED_SNAPSHOTS = frozenset({
    "/ob/research/catalysts.json",
    "/ob/research/keyless.json",
    "/ob/research/providers.json",
    "/ob/data-desk/connections.json",
    "/ob/engine-feed-snapshot.json",
})


def grpc_event_projection(event: dict) -> dict:
    """Project one EventHub notification into the protobuf field contract."""
    if not isinstance(event, dict) or event.get("schema") != EVENT_SCHEMA:
        raise ValueError("OBSERVATORY_GRPC_EVENT_HOLD")
    event_id = event.get("event_id")
    epoch = event.get("epoch")
    cursor = event.get("cursor")
    event_type = event.get("type")
    channel = event.get("channel")
    source = event.get("source")
    symbol = event.get("symbol")
    snapshot_path = event.get("snapshot_path")
    if (
        not isinstance(event_id, str) or not _EVENT_ID.fullmatch(event_id)
        or not isinstance(epoch, str) or len(epoch) != 24
        or not event_id.startswith(epoch + ".")
        or type(cursor) is not int or cursor < 1
        or event_id != f"{epoch}.{cursor}"
        or event_type not in _ALLOWED_TYPES
        or channel not in _ALLOWED_CHANNELS
        or not isinstance(source, str) or not _CONSUMER.fullmatch(source)
        or snapshot_path not in _ALLOWED_SNAPSHOTS
        or (symbol is not None and (not isinstance(symbol, str) or len(symbol) > 16))
        or event.get("needs_authenticated_snapshot") is not True
        or event.get("trace_available") is not True
        or event.get("content_attached") is not False
        or event.get("provider_payload_attached") is not False
        or event.get("provider_stream_attached") is not False
        or event.get("live_quote_payload_attached") is not False
        or event.get("current_quote_verified") is not False
        or event.get("candidate_admitted") is not False
        or event.get("execution_authorized") is not False
    ):
        raise ValueError("OBSERVATORY_GRPC_EVENT_HOLD")
    return {
        "schema": GRPC_EVENT_SCHEMA,
        "event_id": event_id,
        "type": event_type,
        "channel": channel,
        "epoch": epoch,
        "cursor": cursor,
        "source": source,
        "symbol": symbol or "",
        "has_symbol": symbol is not None,
        "snapshot_path": snapshot_path,
        "needs_authenticated_snapshot": True,
        "trace_available": True,
        "content_attached": False,
        "provider_payload_attached": False,
        "provider_stream_attached": False,
        "live_quote_payload_attached": False,
        "current_quote_verified": False,
        "candidate_admitted": False,
        "execution_authorized": False,
    }


def grpc_lifecycle_projection(*, event_id: str, stage: str, consumer: str, observed_at: str) -> dict:
    """Validate a lifecycle receipt before a future gRPC RecordLifecycle call."""
    if (
        not isinstance(event_id, str) or not _EVENT_ID.fullmatch(event_id)
        or stage not in TRACE_STAGES
        or not isinstance(consumer, str) or not _CONSUMER.fullmatch(consumer)
        or not isinstance(observed_at, str) or len(observed_at) > 64
        or "T" not in observed_at
    ):
        raise ValueError("OBSERVATORY_GRPC_LIFECYCLE_HOLD")
    return {
        "event_id": event_id,
        "stage": stage,
        "consumer": consumer,
        "observed_at": observed_at,
    }


def grpc_runtime_status() -> dict:
    """Truthful status: contract installed, network gRPC runtime not started."""
    return {
        "schema": "OB_INTERNAL_GRPC_STATUS_V1",
        "package": GRPC_PACKAGE,
        "proto_path": PROTO_PATH,
        "contract_installed": True,
        "network_server_started": False,
        "loopback_server_started": False,
        "generated_runtime_stubs_required_for_service_split": True,
        "provider_payload_transport_enabled": False,
        "broker_execution_authorized": False,
        "capital_authorized": False,
    }
