"""Exact Tower-protected data route and honest provider status on hosted beta."""
from tower.ob_web_route_enforcement import (
    PROTECTED_EXACT_OB_ROUTES, OWNER_ONLY_OB_ROUTES, is_approved_ob_web_room,
)
from tower.ob_market_source_status import (
    FEED_PATH, FEED_ENDPOINT, VERSION, pending_provider_document,
)


def test_canonical_feed_route_scope():
    assert FEED_PATH in PROTECTED_EXACT_OB_ROUTES
    assert FEED_PATH not in OWNER_ONLY_OB_ROUTES
    assert is_approved_ob_web_room(FEED_PATH) is True
    assert is_approved_ob_web_room(FEED_PATH + "/anything") is False
    assert is_approved_ob_web_room("/ob/another-feed.json") is False


def test_existing_hosted_backend_endpoint_is_registered_and_safe():
    from web.hosted_tower import app
    rules=[rule for rule in app.url_map.iter_rules() if rule.rule == FEED_PATH]
    assert len(rules)==1,"Frontend's canonical engine snapshot has no server route"
    rule=rules[0]
    assert rule.endpoint == FEED_ENDPOINT
    assert "GET" in rule.methods and "POST" not in rule.methods
    view=app.view_functions[rule.endpoint]
    assert callable(view)
    assert view.__module__ == "tower.ob_market_source_status"
    assert view.__name__ == "hosted_source_status"
    assert app.extensions["_tower_ob_provider_pending_status_registered"] is True
    previous=app.extensions["ob_old_seed_only_feed_handler_preserved_for_audit"]
    assert callable(previous) and previous is not view
    with app.test_request_context(FEED_PATH):
        response=view()
        assert response.status_code == 200
        assert response.is_json
        assert response.headers["Cache-Control"] == "private, no-store"
        assert response.headers["X-OB-Market-Source-State"] == "provider-not-configured"
        assert response.get_json() == pending_provider_document()


def test_no_seeded_candidate_position_score_or_manual_live_claim_exposed():
    doc=pending_provider_document()
    assert doc["version"] == VERSION
    assert doc["market_data_state"] == "provider_not_configured"
    assert doc["source"] is None and doc["as_of"] is None
    assert doc["current_eligible"] is False and doc["display_eligible"] is False
    assert doc["market_health"] == {}
    assert doc["options_projection"] == {}
    for key in (
        "sectors","symbols","signals","options","research_contracts","ranked_contracts",
        "positions","positions_preview","candidates","candidates_preview",
        "manual_live_queue",
    ):
        assert doc[key] == [], key
    assert doc["provider_boundary"]["authorized_feed_connected"] is False
    assert doc["tower_boundaries"]["no_broker_api"] is True
    assert doc["tower_boundaries"]["no_order_submission"] is True
    assert doc["tower_boundaries"]["no_capital_movement"] is True
    assert doc["tower_boundaries"]["no_auto_execution"] is True
    assert doc["tower_boundaries"]["live_auto_locked"] is True


def test_actual_anonymous_hosted_market_data_is_not_exposed():
    from web.hosted_tower import app
    response=app.test_client().get(FEED_PATH, follow_redirects=False)
    assert response.status_code in (301,302,303,307,308,401,403)
    assert b"provider_not_configured" not in response.data
