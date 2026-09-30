"""Tower-authenticated Observatory market/intelligence event WebSocket.

The socket carries bounded server-authored invalidation metadata only. It cannot
request provider fetches, subscriptions, rights changes, scanner admission,
orders, capital movement or model execution. Authoritative data remains behind
the existing protected HTTP snapshots.
"""
from __future__ import annotations

import asyncio
import json
import os

from engine.market_intake.market_stream import PATH, SCHEMA
from web.ob_official_catalyst_websocket import (
    _authorize_owner,
    _cursor,
    _headers,
    _safe_origin,
)

CLOSE_DENIED = 4403
CLOSE_INPUT = 4400
CLOSE_CAPACITY = 4429


async def _emit(send, packet):
    raw = json.dumps(packet, sort_keys=True, separators=(",", ":"))
    if len(raw) > 1400:
        raise ValueError("market stream notification size exceeded")
    await send({"type": "websocket.send", "text": raw})


async def market_stream_websocket(scope, receive, send, *, flask_app):
    if scope.get("type") != "websocket" or scope.get("path") != PATH:
        await send({"type": "websocket.close", "code": CLOSE_DENIED})
        return
    if os.environ.get("OB_MARKET_WS_ASGI_ENABLED") != "1":
        await send({"type": "websocket.close", "code": CLOSE_DENIED})
        return

    headers = _headers(scope)
    if not _safe_origin(scope, headers):
        await send({"type": "websocket.close", "code": CLOSE_DENIED})
        return
    cookie = headers.get("cookie", "")
    try:
        epoch, cursor = _cursor(scope)
    except ValueError:
        await send({"type": "websocket.close", "code": CLOSE_INPUT})
        return

    if not _authorize_owner(flask_app, cookie):
        await send({"type": "websocket.close", "code": CLOSE_DENIED})
        return
    hub = flask_app.extensions.get("ob_market_stream_event_hub")
    if hub is None:
        await send({"type": "websocket.close", "code": CLOSE_DENIED})
        return

    try:
        first = await receive()
        if first.get("type") != "websocket.connect":
            await send({"type": "websocket.close", "code": CLOSE_INPUT})
            return
        key, queue, replay, hint = hub.subscribe(
            epoch=epoch, cursor=cursor, loop=asyncio.get_running_loop()
        )
    except ValueError:
        await send({"type": "websocket.close", "code": CLOSE_CAPACITY})
        return
    except Exception:
        await send({"type": "websocket.close", "code": CLOSE_DENIED})
        return

    try:
        if not _authorize_owner(flask_app, cookie):
            await send({"type": "websocket.close", "code": CLOSE_DENIED})
            return
        await send({"type": "websocket.accept"})
        await _emit(send, {
            "schema": SCHEMA,
            "type": "stream_ready",
            "channel": "system",
            "epoch": hint["epoch"],
            "cursor": hint["cursor"],
            "source": "market_stream_hub",
            "symbol": None,
            "snapshot_path": None,
            "needs_authenticated_snapshot": False,
            "content_attached": False,
            "provider_payload_attached": False,
            "provider_stream_attached": False,
            "live_quote_payload_attached": False,
            "current_quote_verified": False,
            "candidate_admitted": False,
            "execution_authorized": False,
        })
        for item in replay:
            if not _authorize_owner(flask_app, cookie):
                await send({"type": "websocket.close", "code": CLOSE_DENIED})
                return
            await _emit(send, item)

        while True:
            pending_event = asyncio.create_task(queue.get())
            pending_recv = asyncio.create_task(receive())
            done, pending = await asyncio.wait(
                {pending_event, pending_recv},
                timeout=15,
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            if pending:
                await asyncio.gather(*pending, return_exceptions=True)

            if not _authorize_owner(flask_app, cookie):
                await send({"type": "websocket.close", "code": CLOSE_DENIED})
                return

            if pending_recv in done:
                message = pending_recv.result()
                if message.get("type") == "websocket.disconnect":
                    return
                # There is deliberately no client command/subscription protocol.
                await send({"type": "websocket.close", "code": CLOSE_INPUT})
                return

            if pending_event in done:
                await _emit(send, pending_event.result())
            else:
                latest = hub.hint()
                await _emit(send, {
                    "schema": SCHEMA,
                    "type": "heartbeat",
                    "channel": "system",
                    "epoch": latest["epoch"],
                    "cursor": latest["cursor"],
                    "source": "market_stream_hub",
                    "symbol": None,
                    "snapshot_path": None,
                    "needs_authenticated_snapshot": False,
                    "content_attached": False,
                    "provider_payload_attached": False,
                    "provider_stream_attached": False,
                    "live_quote_payload_attached": False,
                    "current_quote_verified": False,
                    "candidate_admitted": False,
                    "execution_authorized": False,
                })
    except (OSError, RuntimeError, ConnectionError, asyncio.CancelledError):
        return
    finally:
        hub.unsubscribe(key)
