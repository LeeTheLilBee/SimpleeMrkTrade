from __future__ import annotations

from web.managed_staging import app


def test_managed_staging_health_route_is_registered():
    routes = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/healthz" in routes


def test_managed_staging_health_get_is_anonymous_and_minimal():
    client = app.test_client()
    response = client.get("/tower/healthz")

    assert response.status_code == 200
    assert response.get_json() == {"ok": True}
    assert response.headers.get("Cache-Control") == "no-store"


def test_managed_staging_health_head_is_healthy():
    client = app.test_client()
    response = client.head("/tower/healthz")

    assert response.status_code == 200
    assert response.data == b""


def test_managed_staging_health_post_is_not_bypassed():
    client = app.test_client()
    response = client.post("/tower/healthz")

    assert response.status_code not in {200, 201, 202, 204, 301, 302, 307, 308}


def test_protected_tower_surface_remains_fail_closed_anonymously():
    client = app.test_client()
    response = client.get("/tower/status.json", follow_redirects=False)

    assert response.status_code in {401, 403}
