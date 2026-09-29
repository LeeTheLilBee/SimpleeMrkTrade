"""Regress the exact missing Tower clearance map for Public connection.

The route's presence in OB_ROUTE_GUARD_MAP alone is insufficient: the separate
OB_ROUTE_CLEARANCE_CATALOG must recognize its route_key, and deny nonowners.
"""
from tower.ob_clearance_bridge import evaluate_ob_route_clearance
from tower.ob_route_guard import evaluate_ob_request_guard, match_ob_guard_policy
from tower.ob_web_route_enforcement import PROTECTED_EXACT_OB_ROUTES


def test_both_market_data_desk_paths_have_owner_view_clearance():
    for path in ("/ob/data-desk", "/ob/data-desk/public"):
        match = match_ob_guard_policy(path)
        assert match["match_type"] == "exact"
        assert match["policy"]["route_key"] == "data_desk"
        assert match["policy"]["action"] == "view"
        assert path in PROTECTED_EXACT_OB_ROUTES

        owner = evaluate_ob_request_guard(path=path, user_id="simplee_owner", role="owner")
        assert owner["allowed"] is True, owner
        assert owner["reason_code"] == "ob_route_clearance_allowed"

        visitor = evaluate_ob_request_guard(path=path, user_id="visitor", role="beta")
        assert visitor["allowed"] is False
        assert visitor["reason_code"] == "ob_clearance_level_too_low"


def test_no_public_credential_action_or_unmapped_route_grant():
    for action in ("connect", "edit", "approve", "execute", "trade"):
        denied = evaluate_ob_route_clearance(
            user_id="simplee_owner", role="owner",
            route_key="data_desk", action=action,
        )
        assert denied["allowed"] is False
        assert denied["reason_code"] == "ob_action_not_allowed_for_route"

    for path in ("/ob/data-desk/public/other", "/ob/data-desk/connect", "/ob/data-desk/public/trade"):
        match = match_ob_guard_policy(path)
        assert match["match_type"] == "unmapped_default_deny"
        denied = evaluate_ob_request_guard(path=path, role="owner", user_id="simplee_owner")
        assert denied["allowed"] is False
        assert denied["reason_code"] == "ob_route_unmapped_default_deny"
