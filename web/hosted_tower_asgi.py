"""Opt-in ASGI wrapper around the SAME canonical Tower Flask WSGI app.

Every HTTP path continues through Flask/Tower. The one exact Observatory event
WebSocket is intercepted here and remains independently feature-gated.
"""
from __future__ import annotations

from asgiref.wsgi import WsgiToAsgi

from web.hosted_tower import app as flask_app
from web.ob_event_websocket import PATH, observatory_event_websocket

http_app = WsgiToAsgi(flask_app)


async def application(scope, receive, send):
    if scope["type"] == "websocket":
        if scope.get("path") != PATH:
            await send({"type": "websocket.close", "code": 4403})
            return
        await observatory_event_websocket(
            scope,
            receive,
            send,
            flask_app=flask_app,
        )
        return
    await http_app(scope, receive, send)
