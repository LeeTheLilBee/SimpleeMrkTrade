"""Private engine snapshot is both a real hosted Flask route and a guarded source.

Source diagnostic prints only the repository's view function source, never
request bodies, environment, credentials, tokens, or account data.
"""
from __future__ import annotations

import inspect

from tower.ob_web_route_enforcement import (
    PROTECTED_EXACT_OB_ROUTES, OWNER_ONLY_OB_ROUTES,
    is_approved_ob_web_room,
)

FEED="/ob/engine-feed-snapshot.json"


def test_canonical_feed_route_scope():
    assert FEED in PROTECTED_EXACT_OB_ROUTES
    assert FEED not in OWNER_ONLY_OB_ROUTES
    assert is_approved_ob_web_room(FEED) is True
    assert is_approved_ob_web_room(FEED + "/anything") is False
    assert is_approved_ob_web_room("/ob/another-feed.json") is False


def test_existing_hosted_backend_endpoint_is_registered_and_read_only():
    from web.hosted_tower import app
    rules=[rule for rule in app.url_map.iter_rules() if rule.rule == FEED]
    assert len(rules)==1,"Frontend's canonical engine snapshot has no server route"
    rule=rules[0]
    assert "GET" in rule.methods
    assert "POST" not in rule.methods
    view=app.view_functions[rule.endpoint]
    assert callable(view)
    src=inspect.getsource(view)
    print("CANONICAL_FEED_HANDLER",view.__module__,view.__name__)
    print("CANONICAL_FEED_SOURCE_BEGIN")
    print(src[:7500])
    print("CANONICAL_FEED_SOURCE_END")
