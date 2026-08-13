from __future__ import annotations

from web.app import app
from tower.tower_ob_real_surface_route_map import tower_ob_real_surface_route_allowed


APPROVED_OB_ROUTES = [
    "/ob/dashboard",
    "/ob/market-map",
    "/ob/symbol/AMD",
    "/ob/trade-center",
    "/ob/review-center",
    "/ob/owner-console",
]

DENIED_OB_ROUTES = [
    "/ob/not-real",
    "/ob/symbol/",
    "/ob/symbol/../../secrets",
    "/ob/admin/root",
    "/ob/random/unmapped/page",
]


def test_approved_route_contract_allows_walkthrough_surfaces():
    for route in APPROVED_OB_ROUTES:
        assert tower_ob_real_surface_route_allowed(route) is True


def test_unmapped_route_contract_denies_unknown_ob_routes():
    for route in DENIED_OB_ROUTES:
        assert tower_ob_real_surface_route_allowed(route) is False


def test_market_map_and_symbol_amd_do_not_hit_unmapped_default_deny_with_owner_session():
    app.config["TESTING"] = True
    client = app.test_client()

    with client.session_transaction() as session:
        session["owner_id"] = "owner_solice"
        session["role"] = "owner"
        session["tower_owner_authenticated"] = True
        session["tower_ob_handoff_authorized"] = True
        session["tower_ob_clearance"] = "owner"

    for route in ["/ob/market-map", "/ob/symbol/AMD"]:
        response = client.get(route, follow_redirects=False)
        body = response.get_data(as_text=True)

        assert "ob_route_unmapped_default_deny" not in body
        assert response.status_code not in {403, 404}


def test_random_unmapped_ob_route_still_fails_closed_with_owner_session():
    app.config["TESTING"] = True
    client = app.test_client()

    with client.session_transaction() as session:
        session["owner_id"] = "owner_solice"
        session["role"] = "owner"
        session["tower_owner_authenticated"] = True
        session["tower_ob_handoff_authorized"] = True
        session["tower_ob_clearance"] = "owner"

    response = client.get("/ob/random/unmapped/page", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert response.status_code in {401, 403, 404}
    assert (
        "ob_route_unmapped_default_deny" in body
        or "denied" in body.lower()
        or "not found" in body.lower()
    )
