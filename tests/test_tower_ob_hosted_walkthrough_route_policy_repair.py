from __future__ import annotations

import pytest

from tower.ob_clearance_bridge import (
    OB_ROUTE_CLEARANCE_CATALOG,
    evaluate_ob_route_clearance,
)
from tower.ob_route_guard import (
    match_ob_guard_policy,
    should_block_ob_request,
)


EXACT_ROUTES = {
    "/market-map": ("market_map", "confidential"),
    "/ob/trade-center": ("trade_center", "restricted"),
    "/ob/review-center": ("review_center", "restricted"),
    "/ob/owner-console": ("owner_console", "critical"),
}

SYMBOL_ROUTES = (
    "/ob/symbol/AMD",
    "/symbol/AAPL",
)


@pytest.mark.parametrize("path,expected", EXACT_ROUTES.items())
def test_walkthrough_exact_route_policy_is_mapped(path, expected):
    route_key, sensitivity = expected
    matched = match_ob_guard_policy(path)
    assert matched["matched"] is True
    assert matched["match_type"] == "exact"
    assert matched["policy"]["route_key"] == route_key
    assert matched["policy"]["sensitivity"] == sensitivity
    assert matched["policy"]["public_allowed"] is False


@pytest.mark.parametrize("path", SYMBOL_ROUTES)
def test_walkthrough_symbol_route_policy_is_mapped(path):
    matched = match_ob_guard_policy(path)
    assert matched["matched"] is True
    assert matched["match_type"] == "dynamic_ob_symbol"
    assert matched["policy"]["route_key"] == "symbol_detail"
    assert matched["object_id"] in {"AMD", "AAPL"}


@pytest.mark.parametrize(
    "path",
    tuple(EXACT_ROUTES) + SYMBOL_ROUTES + ("/dashboard",),
)
def test_critical_owner_is_allowed_through_every_walkthrough_surface(path):
    decision = should_block_ob_request(
        path=path,
        user_id="tower-owner-solice-001",
        role="owner",
        user_clearance_level="critical",
        current_risk_score=0,
    )
    assert decision["block"] is False
    assert decision["allowed"] is True
    assert decision["reason_code"] == "ob_route_clearance_allowed"


@pytest.mark.parametrize(
    "path",
    tuple(EXACT_ROUTES) + SYMBOL_ROUTES,
)
def test_anonymous_user_remains_denied(path):
    decision = should_block_ob_request(
        path=path,
        user_id="anonymous",
        role="",
        user_clearance_level="",
        current_risk_score=0,
    )
    assert decision["block"] is True
    assert decision["allowed"] is False


@pytest.mark.parametrize(
    "route_key,required_level",
    (
        ("market_map", "confidential"),
        ("trade_center", "restricted"),
        ("review_center", "restricted"),
        ("owner_console", "critical"),
    ),
)
def test_clearance_catalog_contains_walkthrough_rooms(route_key, required_level):
    policy = OB_ROUTE_CLEARANCE_CATALOG[route_key]
    assert policy["required_clearance_level"] == required_level
    assert policy["allowed_actions"] == ["view"]


def test_owner_console_requires_critical_clearance():
    denied = evaluate_ob_route_clearance(
        user_id="admin-1",
        route_key="owner_console",
        action="view",
        role="admin",
        user_clearance_level="restricted",
    )
    assert denied["allowed"] is False
    assert denied["reason_code"] == "ob_clearance_level_too_low"

    allowed = evaluate_ob_route_clearance(
        user_id="tower-owner-solice-001",
        route_key="owner_console",
        action="view",
        role="owner",
        user_clearance_level="critical",
    )
    assert allowed["allowed"] is True


def test_unknown_private_route_still_defaults_deny():
    matched = match_ob_guard_policy("/private-route-not-in-map")
    assert matched["matched"] is False
    assert matched["match_type"] == "unmapped_default_deny"

    decision = should_block_ob_request(
        path="/private-route-not-in-map",
        user_id="tower-owner-solice-001",
        role="owner",
        user_clearance_level="critical",
    )
    assert decision["block"] is True
    assert decision["reason_code"] == "ob_route_unmapped_default_deny"
