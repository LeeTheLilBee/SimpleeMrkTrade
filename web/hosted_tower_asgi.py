"""Opt-in ASGI wrapper around the SAME canonical Tower Flask WSGI app.

All existing HTTP paths continue through Flask/its Tower before_request
policies. Only the exact Catalyst Radar WebSocket is intercepted here. No new
identity or provider connection is created by an ASGI import. The deployed
WSGI start stays default unless explicitly opted in and release tested.
"""
from __future__ import annotations

from asgiref.wsgi import WsgiToAsgi

from web.hosted_tower import app as flask_app
from web.ob_official_catalyst_websocket import (
    PATH, official_catalyst_websocket,
)

http_app = WsgiToAsgi(flask_app)


async def application(scope, receive, send):
    if scope["type"] == "websocket":
        if scope.get("path") != PATH:
            await send({"type": "websocket.close", "code": 4403})
            return
        await official_catalyst_websocket(
            scope, receive, send, flask_app=flask_app,
        )
        return
    await http_app(scope, receive, send)
