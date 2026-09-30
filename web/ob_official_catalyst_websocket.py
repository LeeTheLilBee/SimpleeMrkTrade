"""Exact Tower-authenticated ASGI WebSocket for snapshot invalidation ONLY.

The authoritative content remains the protected Flask GET. Socket messages
cannot ask the server to fetch, approve rights, place orders or run an LLM.
A signed Tower session, current step-up, consumed OB handoff and same-origin
browser context are checked before handshake and periodically afterwards.
"""
from __future__ import annotations

import asyncio
import json
import os
from urllib.parse import parse_qs, urlsplit

PATH = "/ob/research/catalysts/stream"
SCHEMA = "OB_CATALYST_STREAM_EVENT_V1"
CLOSE_DENIED = 4403
CLOSE_INPUT = 4400
CLOSE_CAPACITY = 4429


def _headers(scope):
    headers = {}
    for raw_key, raw_value in scope.get("headers", []):
        key = raw_key.decode("ascii", "ignore").lower()
        if key in headers and key in {"cookie", "host", "origin"}:
            return {}
        headers[key] = raw_value.decode("latin-1", "ignore")
    return headers


def _safe_origin(scope, headers):
    host = headers.get("host", "")
    origin = headers.get("origin", "")
    if not (host and origin and len(host) <= 255 and len(origin) <= 400):
        return False
    try:
        parsed = urlsplit(origin)
        if (parsed.scheme != "https" or parsed.netloc.lower() != host.lower() or
                parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment):
            return False
    except ValueError:
        return False
    return True


def _cursor(scope):
    raw = scope.get("query_string", b"")
    if not isinstance(raw, bytes) or len(raw) > 120:
        raise ValueError("cursor query held")
    try:
        query = parse_qs(raw.decode("ascii"), keep_blank_values=True, strict_parsing=True)
        if set(query) != {"epoch", "cursor"} or any(len(v) != 1 for v in query.values()):
            raise ValueError("cursor query held")
        epoch, cursor = query["epoch"][0], query["cursor"][0]
        if (len(epoch) != 24 or not all(ch in "0123456789abcdef" for ch in epoch) or
                len(cursor) > 15 or not cursor.isascii() or not cursor.isdecimal()):
            raise ValueError("cursor query held")
        return epoch, int(cursor)
    except (UnicodeError, ValueError):
        raise ValueError("cursor query held") from None


def _authorize_owner(flask_app, cookie):
    # Never trust socket query strings, role labels, unsigned browser hints or
    # a bare session claim. Flask verifies its signed cookie. The canonical
    # Tower checks independently validate actual owner, step-up and consumed
    # OB operational launch receipt in that verified request context.
    from flask import session
    from tower.ob_market_data_desk_integration import _tower_authorize_data_desk
    from tower.tower_human_login_ob_launch import SESSION_ID
    if not cookie or len(cookie) > 8192 or "\r" in cookie or "\n" in cookie:
        return False
    with flask_app.test_request_context(
            "/ob/research/catalysts.json",
            method="GET", headers={"Cookie": cookie}):
        if _tower_authorize_data_desk() is not True:
            return False
        hub = flask_app.extensions.get("ob_official_catalyst_event_hub")
        tower_session_id = session.get(SESSION_ID)
        return (hub is not None and isinstance(tower_session_id, str)
                and bool(tower_session_id)
                and not hub.session_revoked(tower_session_id))


async def _emit(send, packet):
    # Exact small server-authored metadata, not user/provider text.
    raw = json.dumps(packet, sort_keys=True, separators=(",", ":"))
    if len(raw) > 1024:
        raise ValueError("notification size exceeded")
    await send({"type": "websocket.send", "text": raw})


async def official_catalyst_websocket(scope, receive, send, *, flask_app):
    if scope.get("type") != "websocket" or scope.get("path") != PATH:
        await send({"type": "websocket.close", "code": CLOSE_DENIED})
        return
    if os.environ.get("OB_CATALYST_WS_ASGI_ENABLED") != "1":
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
    hub = flask_app.extensions.get("ob_official_catalyst_event_hub")
    if hub is None:
        await send({"type": "websocket.close", "code": CLOSE_DENIED})
        return
    try:
        first = await receive()
        if first.get("type") != "websocket.connect":
            await send({"type": "websocket.close", "code": CLOSE_INPUT})
            return
        key, queue, replay, hint = hub.subscribe(
            epoch=epoch, cursor=cursor, loop=asyncio.get_running_loop())
    except ValueError:
        await send({"type": "websocket.close", "code": CLOSE_CAPACITY})
        return
    except Exception:
        await send({"type": "websocket.close", "code": CLOSE_DENIED})
        return
    try:
        # Re-check authorization immediately before accept, not just when the
        # first async await may have yielded the loop.
        if not _authorize_owner(flask_app, cookie):
            await send({"type": "websocket.close", "code": CLOSE_DENIED})
            return
        await send({"type": "websocket.accept"})
        await _emit(send, {
            "schema": SCHEMA, "type": "stream_ready",
            "epoch": hint["epoch"], "cursor": hint["cursor"],
            "source_only": True, "needs_authenticated_snapshot": False,
            "live_market_feed": False, "candidate_admitted": False,
            "execution_authorized": False,
        })
        for item in replay:
            if not _authorize_owner(flask_app, cookie):
                await send({"type": "websocket.close", "code": CLOSE_DENIED})
                return
            await _emit(send, item)
        while True:
            # No client command protocol. Read only to detect closure and reject
            # attempts to mutate behavior via socket messages.
            pending_event = asyncio.create_task(queue.get())
            pending_recv = asyncio.create_task(receive())
            done, pending = await asyncio.wait(
                {pending_event, pending_recv}, timeout=15,
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
                # No user-driven fetch, subject changes, subscription grants,
                # source-rights changes or trading commands on this channel.
                await send({"type": "websocket.close", "code": CLOSE_INPUT})
                return
            if pending_event in done:
                await _emit(send, pending_event.result())
            else:
                await _emit(send, {
                    "schema": SCHEMA, "type": "heartbeat",
                    "epoch": hint["epoch"], "cursor": hub.hint()["cursor"],
                    "source_only": True, "needs_authenticated_snapshot": False,
                    "live_market_feed": False, "candidate_admitted": False,
                    "execution_authorized": False,
                })
    except (OSError, RuntimeError, ConnectionError, asyncio.CancelledError):
        return
    finally:
        hub.unsubscribe(key)
