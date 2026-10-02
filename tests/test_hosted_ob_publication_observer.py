"""Owner beta runtime publication: only observed same-revision protected OB truth."""
from datetime import datetime, timedelta, timezone

import pytest

from deploy.hosted_tower.ob_publication_observer import (
    EXPECTED_BRANCH,
    EXPECTED_REPOSITORY,
    POLL_SECONDS,
    RECEIPT_SECONDS,
    metadata_from_environment,
    observe,
)
from tower.app_publication_authority import validate_publication_document
from tower.truth_contract import STALE


COMMIT = "a" * 40
META = {
    "commit": COMMIT,
    "service_id": "srv-dag3gn9594qs73fnd0kg",
    "hostname": "simplee-tower-ob.onrender.com",
    "port": 10000,
}


def env(**overrides):
    result = {
        "TOWER_OWNER_BETA_OB_PUBLICATION_ENABLED": "1",
        "TOWER_OWNER_BETA_OB_PUBLICATION_SERVICE_ID": META["service_id"],
        "RENDER": "true",
        "IS_PULL_REQUEST": "false",
        "RENDER_GIT_BRANCH": EXPECTED_BRANCH,
        "RENDER_GIT_REPO_SLUG": EXPECTED_REPOSITORY,
        "RENDER_GIT_COMMIT": COMMIT,
        "RENDER_SERVICE_ID": META["service_id"],
        "RENDER_EXTERNAL_HOSTNAME": META["hostname"],
        "PORT": "10000",
    }
    result.update(overrides)
    return result


@pytest.mark.parametrize("key,value", [
    ("TOWER_OWNER_BETA_OB_PUBLICATION_ENABLED", "0"),
    ("RENDER", "false"),
    ("IS_PULL_REQUEST", "true"),
    ("RENDER_GIT_BRANCH", "main"),
    ("RENDER_GIT_REPO_SLUG", "someone/else"),
    ("RENDER_GIT_COMMIT", ""),
    ("RENDER_SERVICE_ID", "srv-wrong"),
    ("TOWER_OWNER_BETA_OB_PUBLICATION_SERVICE_ID", ""),
    ("RENDER_EXTERNAL_HOSTNAME", "evil.invalid"),
    ("PORT", "99999"),
])
def test_invalid_or_other_service_cannot_publish(key, value):
    assert metadata_from_environment(env(**{key: value})) is None


def response(path, meta):
    headers = {
        "X-Simplee-Entrypoint": "web.hosted_tower:app",
        "X-Simplee-Revision": meta["commit"],
    }
    if path == "/tower/healthz":
        return 200, headers, b'{"ok":true}\n'
    if path == "/tower/runtime-manifest.json":
        import json
        return 200, headers, json.dumps({
            "entrypoint": "web.hosted_tower:app",
            "revision": meta["commit"],
            "ob_product_renderer_verified": True,
            "critical_routes": {
                name: True for name in (
                    "ob_dashboard", "ob_market_map", "ob_trade_center",
                    "ob_review_center", "ob_owner_console",
                )
            },
        }).encode()
    if path == "/ob/dashboard":
        return 302, dict(headers, Location="/tower/login"), b""
    raise AssertionError(path)


def test_valid_observed_receipt_is_schema_and_integrity_valid_and_expires():
    now = datetime(2026, 9, 28, 14, 30, tzinfo=timezone.utc)
    doc = observe(response, META, now=now)
    assert doc is not None
    valid = validate_publication_document(doc)
    assert valid["apps"]["observatory"]["health_verified"]["value"] is True
    expiry = datetime.fromisoformat(
        valid["apps"]["observatory"]["health_verified"]["fresh_until_utc"]
    )
    assert expiry == now + timedelta(seconds=RECEIPT_SECONDS)
    assert RECEIPT_SECONDS == 180
    assert POLL_SECONDS == 60
    assert RECEIPT_SECONDS >= POLL_SECONDS * 2


@pytest.mark.parametrize("path,bad", [
    ("/tower/healthz", (503, {}, b"")),
    ("/tower/runtime-manifest.json", (200, {}, b"{}")),
    ("/ob/dashboard", (200, {"X-Simplee-Revision": COMMIT}, b"public!")),
    ("/ob/dashboard", (302, {
        "X-Simplee-Revision": COMMIT,
        "Location": "https://evil.invalid/tower/login",
    }, b"")),
    ("/ob/dashboard", (302, {
        "X-Simplee-Revision": "b" * 40,
        "Location": "/tower/login",
    }, b"")),
])
def test_no_publication_on_missing_unsafe_or_wrong_revision_probe(path, bad):
    def probe(route, meta):
        return bad if route == path else response(route, meta)
    assert observe(probe, META) is None


def test_renderer_not_verified_never_launches():
    def probe(route, meta):
        status, headers, body = response(route, meta)
        if route == "/tower/runtime-manifest.json":
            body = body.replace(
                b'"ob_product_renderer_verified": true',
                b'"ob_product_renderer_verified": false',
            )
        return status, headers, body
    assert observe(probe, META) is None
