"""Opt-in ASGI wrapper around the SAME canonical Tower Flask WSGI app.

Every HTTP path still runs through the canonical Flask/Tower boundary. Only the
exact, separately feature-gated Observatory WebSocket paths are intercepted.
Neither socket creates provider entitlement, identity, quote or trading rights.
"""
from __future__ import annotations

from asgiref.wsgi import WsgiToAsgi

from web.hosted_tower import app as flask_app
from web.ob_official_catalyst_websocket import (
    PATH as CATALYST_PATH,
    official_catalyst_websocket,
)
from web.ob_market_websocket import (
    PATH as MARKET_PATH,
    market_stream_websocket,
)

http_app = WsgiToAsgi(flask_app)


async def application(scope, receive, send):
    if scope["type"] == "websocket":
        path = scope.get("path")
        if path == CATALYST_PATH:
            await official_catalyst_websocket(
                scope, receive, send, flask_app=flask_app,
            )
            return
        if path == MARKET_PATH:
            await market_stream_websocket(
                scope, receive, send, flask_app=flask_app,
            )
            return
        await send({"type": "websocket.close", "code": 4403})
        return
    await http_app(scope, receive, send)
