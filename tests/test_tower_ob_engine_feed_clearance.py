from tower.ob_clearance_bridge import evaluate_ob_route_clearance
from tower.ob_route_guard import evaluate_ob_request_guard, match_ob_guard_policy


def test_engine_feed_has_owner_view_clearance():
    path = "/ob/engine-feed-snapshot.json"
    match = match_ob_guard_policy(path)
    assert match["match_type"] == "exact"
    assert match["policy"]["route_key"] == "engine_feed_source_status"
    assert match["policy"]["action"] == "view"

    owner = evaluate_ob_request_guard(
        path=path,
        user_id="simplee_owner",
        role="owner",
        user_clearance_level="critical",
    )
    assert owner["allowed"] is True, owner
    assert owner["reason_code"] == "ob_route_clearance_allowed"


def test_engine_feed_clearance_is_read_only_and_owner_scoped():
    for action in ("edit", "execute", "trade", "approve"):
        denied = evaluate_ob_route_clearance(
            user_id="simplee_owner",
            role="owner",
            user_clearance_level="critical",
            route_key="engine_feed_source_status",
            action=action,
        )
        assert denied["allowed"] is False
        assert denied["reason_code"] == "ob_action_not_allowed_for_route"

    visitor = evaluate_ob_route_clearance(
        user_id="visitor",
        role="beta",
        user_clearance_level="internal",
        route_key="engine_feed_source_status",
        action="view",
    )
    assert visitor["allowed"] is False
    assert visitor["reason_code"] == "ob_clearance_level_too_low"
