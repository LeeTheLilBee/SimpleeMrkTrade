"""Owner-beta Observatory publication observer for the hosted Tower process.

This is a separate local HTTP observer, NOT a self-reported registry flag,
production release certificate, or financial/trading readiness grant.
It only publishes short-lived evidence of a specific Render service/revision,
the canonical renderer's successful startup registration, and a protected
unauthenticated OB route response. A failed probe removes its receipt.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

from tower.app_publication_authority import publication_document

EXPECTED_BRANCH = "tower-hosted-runtime-identity-twr081-085"
EXPECTED_REPOSITORY = "LeeTheLilBee/SimpleeMrkTrade"
PUBLICATION_PATH = Path("/tmp/tower-owner-beta-ob-publication.json")
REQUIRED_ROUTES = (
    "ob_dashboard", "ob_market_map", "ob_trade_center",
    "ob_review_center", "ob_owner_console",
)
RECEIPT_SECONDS = 180
POLL_SECONDS = 60


class _DoNotFollowRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


# One opener per observer process. Rebuilding urllib opener/handler stacks for
# every probe created unnecessary churn on the 512 MiB owner-beta service.
_PROBE_OPENER = build_opener(_DoNotFollowRedirects())


def metadata_from_environment(env=None):
    env = os.environ if env is None else env
    commit = str(env.get("RENDER_GIT_COMMIT", "")).strip()
    service_id = str(env.get("RENDER_SERVICE_ID", "")).strip()
    required_service = str(
        env.get("TOWER_OWNER_BETA_OB_PUBLICATION_SERVICE_ID", "")
    ).strip()
    hostname = str(env.get("RENDER_EXTERNAL_HOSTNAME", "")).strip()
    port = str(env.get("PORT", "10000")).strip()
    if (
        env.get("TOWER_OWNER_BETA_OB_PUBLICATION_ENABLED") != "1"
        or env.get("RENDER") != "true"
        or env.get("IS_PULL_REQUEST") != "false"
        or env.get("RENDER_GIT_BRANCH") != EXPECTED_BRANCH
        or env.get("RENDER_GIT_REPO_SLUG") != EXPECTED_REPOSITORY
        or not re.fullmatch(r"[a-fA-F0-9]{40}", commit)
        or not re.fullmatch(r"srv-[a-zA-Z0-9]+", service_id)
        or service_id != required_service
        or not re.fullmatch(r"[a-z0-9-]+\.onrender\.com", hostname)
        or not port.isdecimal()
        or not 1 <= int(port) <= 65535
    ):
        return None
    return {
        "commit": commit.lower(),
        "service_id": service_id,
        "hostname": hostname,
        "port": int(port),
    }


def _fetch(path, metadata):
    """Probe only the currently running local service; never follow redirects."""
    opener = _PROBE_OPENER
    request = Request(
        "http://127.0.0.1:" + str(metadata["port"]) + path,
        headers={"Host": metadata["hostname"], "User-Agent": "tower-ob-publication-observer/1"},
        method="GET",
    )
    try:
        with opener.open(request, timeout=3) as response:
            return response.status, dict(response.headers), response.read(65537)
    except HTTPError as error:
        try:
            return error.code, dict(error.headers), error.read(65537)
        finally:
            error.close()


def _get_header(headers, key):
    return next(
        (str(value) for name, value in headers.items() if name.lower() == key.lower()),
        "",
    )


def observe(probe, metadata, now=None):
    """Construct evidence only from actual responses of this exact revision."""
    now = datetime.now(timezone.utc) if now is None else now
    if now.tzinfo is None:
        raise ValueError("Observer time must be timezone-aware")
    commit = metadata["commit"]
    # The liveness response alone is insufficient to prove OB readiness.
    status, headers, body = probe("/tower/healthz", metadata)
    if (
        status != 200 or body.strip() != b'{"ok":true}'
        or _get_header(headers, "X-Simplee-Entrypoint") != "web.hosted_tower:app"
        or _get_header(headers, "X-Simplee-Revision").lower() != commit
    ):
        return None

    status, headers, body = probe("/tower/runtime-manifest.json", metadata)
    if (
        status != 200
        or _get_header(headers, "X-Simplee-Revision").lower() != commit
        or len(body) > 65536
    ):
        return None
    try:
        manifest = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return None
    routes = manifest.get("critical_routes", {})
    if (
        manifest.get("entrypoint") != "web.hosted_tower:app"
        or str(manifest.get("revision", "")).lower() != commit
        or manifest.get("ob_product_renderer_verified") is not True
        or not isinstance(routes, dict)
        or not all(routes.get(route) is True for route in REQUIRED_ROUTES)
    ):
        return None

    # The anonymous dashboard MUST remain guarded. This probe never obtains
    # credentials or a handoff; authenticated owner acceptance is a separate test.
    status, headers, body = probe("/ob/dashboard", metadata)
    if _get_header(headers, "X-Simplee-Revision").lower() != commit:
        return None
    if status in (302, 303):
        target = _get_header(headers, "Location")
        parsed = urlsplit(target)
        if (
            (parsed.netloc and parsed.netloc != metadata["hostname"])
            or parsed.path not in (
                "/tower/login", "/tower/start", "/tower/access-home",
                "/tower/step-up/observatory",
            )
        ):
            return None
    elif status not in (401, 403):
        return None

    observed = now.astimezone(timezone.utc).isoformat()
    fresh_until = (now + timedelta(seconds=RECEIPT_SECONDS)).astimezone(
        timezone.utc
    ).isoformat()
    # Receipts identify an observed revision and this exact probe; they do not
    # assert production acceptance or allow trading/financial execution.
    receipt_seed = (
        metadata["service_id"] + ":" + commit + ":" + observed
    )
    receipt = hashlib.sha256(receipt_seed.encode("utf-8")).hexdigest()[:24]
    return publication_document({
        "observatory": {
            "app_id": "observatory",
            "implemented": {
                "value": True,
                "evidence_id": "owner-beta-renderer-startup:" + commit,
            },
            "published": {
                "value": True,
                "evidence_id": "render-service-revision:" + metadata["service_id"] + ":" + commit,
            },
            "environment_available": {
                "value": True,
                "receipt_id": "owner-beta-runtime-ob-guard:" + receipt,
                "observed_at_utc": observed,
                "fresh_until_utc": fresh_until,
            },
            "health_verified": {
                "value": True,
                "receipt_id": "owner-beta-runtime-ob-health:" + receipt,
                "observed_at_utc": observed,
                "fresh_until_utc": fresh_until,
            },
        },
    })


def _publish_atomic(document, path=PUBLICATION_PATH):
    # Do not trust a pre-existing symlink or leave a partial receipt readable.
    if path.is_symlink():
        raise ValueError("publication destination is a symlink")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".new")
    fd = os.open(str(temporary), os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(document, handle, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def main():
    metadata = metadata_from_environment()
    if metadata is None:
        print("Tower OB observer disabled: exact owner-beta Render configuration not verified", flush=True)
        return 2
    path = PUBLICATION_PATH
    path.unlink(missing_ok=True)
    while True:
        try:
            document = observe(_fetch, metadata)
            if document is None:
                path.unlink(missing_ok=True)
                print("Tower OB owner-beta publication: probe unavailable; launch closed", flush=True)
            else:
                _publish_atomic(document, path)
                print("Tower OB owner-beta publication: runtime probe verified (not owner acceptance)", flush=True)
        except Exception:
            path.unlink(missing_ok=True)
            print("Tower OB owner-beta publication: observer failed closed", flush=True)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    sys.exit(main())
