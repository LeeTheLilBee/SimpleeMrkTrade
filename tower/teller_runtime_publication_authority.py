"""
TWR191 — Dedicated runtime publication authority for The Teller.

This provider is deliberately separate from the shared Tower app
publication file used by Observatory and other applications.

It activates only when all explicit Teller deployment receipt
configuration is present.

Runtime truth requires:
- HTTPS Teller URL,
- explicit Render deploy SHA,
- explicit Render deploy receipt ID,
- fresh HTTP request,
- HTTP 200,
- expected Teller HTML markers.

It does NOT create:
- request authorization,
- employee/manager access,
- payroll execution,
- bank authority,
- capital authority,
- broker authority,
- Manual Live,
- Live Auto.
"""

from __future__ import annotations

import os
import re

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from typing import Any

from urllib.error import (
    HTTPError,
    URLError,
)

from urllib.parse import (
    urlsplit,
)

from urllib.request import (
    Request,
    urlopen,
)

from tower.truth_contract import (
    AUTHORITATIVE,
    TowerTruthEnvelope,
    verified_truth,
)


TOWER_TELLER_WEB_URL_ENV = (
    "TOWER_TELLER_WEB_URL"
)

TOWER_TELLER_DEPLOY_SHA_ENV = (
    "TOWER_TELLER_DEPLOY_SHA"
)

TOWER_TELLER_DEPLOY_ID_ENV = (
    "TOWER_TELLER_DEPLOY_ID"
)

TOWER_TELLER_HEALTH_TIMEOUT_SECONDS_ENV = (
    "TOWER_TELLER_HEALTH_TIMEOUT_SECONDS"
)

TOWER_TELLER_HEALTH_FRESH_SECONDS_ENV = (
    "TOWER_TELLER_HEALTH_FRESH_SECONDS"
)


DEFAULT_TIMEOUT_SECONDS = 5.0

DEFAULT_FRESH_SECONDS = 60

MAX_RESPONSE_BYTES = 256 * 1024


_SHA_RE = re.compile(
    r"^[0-9a-f]{40}$"
)


def _clean(
    value: Any,
) -> str:

    return str(
        value
        if value is not None
        else ""
    ).strip()


def _configured_web_url() -> str:

    return _clean(
        os.environ.get(
            TOWER_TELLER_WEB_URL_ENV
        )
    )


def _configured_deploy_sha() -> str:

    return _clean(
        os.environ.get(
            TOWER_TELLER_DEPLOY_SHA_ENV
        )
    ).lower()


def _configured_deploy_id() -> str:

    return _clean(
        os.environ.get(
            TOWER_TELLER_DEPLOY_ID_ENV
        )
    )


def _timeout_seconds() -> float:

    raw = _clean(
        os.environ.get(
            TOWER_TELLER_HEALTH_TIMEOUT_SECONDS_ENV
        )
    )

    if not raw:
        return DEFAULT_TIMEOUT_SECONDS

    try:
        value = float(
            raw
        )

    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS

    return max(
        1.0,
        min(
            value,
            10.0,
        ),
    )


def _fresh_seconds() -> int:

    raw = _clean(
        os.environ.get(
            TOWER_TELLER_HEALTH_FRESH_SECONDS_ENV
        )
    )

    if not raw:
        return DEFAULT_FRESH_SECONDS

    try:
        value = int(
            raw
        )

    except ValueError:
        return DEFAULT_FRESH_SECONDS

    return max(
        15,
        min(
            value,
            300,
        ),
    )


def teller_runtime_publication_configured(
) -> bool:

    url = _configured_web_url()

    deploy_sha = (
        _configured_deploy_sha()
    )

    deploy_id = (
        _configured_deploy_id()
    )

    if not (
        url
        and deploy_sha
        and deploy_id
    ):
        return False

    parsed = urlsplit(
        url
    )

    if (
        parsed.scheme
        != "https"
        or not parsed.netloc
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        return False

    if not _SHA_RE.fullmatch(
        deploy_sha
    ):
        return False

    if not deploy_id.startswith(
        "dep-"
    ):
        return False

    return True


def _http_health_check(
    url: str,
) -> dict[str, Any]:

    request = Request(
        url,
        method="GET",
        headers={
            "User-Agent":
                "Simplee-Tower-Teller-Health/TWR191",

            "Accept":
                "text/html,application/xhtml+xml",
        },
    )

    try:

        with urlopen(
            request,
            timeout=_timeout_seconds(),
        ) as response:

            status = int(
                getattr(
                    response,
                    "status",
                    0,
                )
                or 0
            )

            final_url = str(
                response.geturl()
                or ""
            )

            body = response.read(
                MAX_RESPONSE_BYTES
            )

    except (
        HTTPError,
        URLError,
        TimeoutError,
        OSError,
    ):
        return {
            "reachable":
                False,

            "healthy":
                False,

            "status":
                None,

            "final_url":
                "",

            "markers_verified":
                False,
        }

    final = urlsplit(
        final_url
    )

    expected = urlsplit(
        url
    )

    same_origin = (
        final.scheme
        == expected.scheme
        and final.netloc
        == expected.netloc
    )

    try:

        html = body.decode(
            "utf-8"
        )

    except UnicodeDecodeError:

        html = body.decode(
            "utf-8",
            errors="replace",
        )

    markers_verified = all((
        "<title>The Teller</title>"
        in html,

        'id="root"'
        in html,
    ))

    reachable = (
        status == 200
        and same_origin
    )

    healthy = (
        reachable
        and markers_verified
    )

    return {
        "reachable":
            reachable,

        "healthy":
            healthy,

        "status":
            status,

        "final_url":
            final_url,

        "markers_verified":
            markers_verified,
    }


def _runtime_truth(
    value: bool,
    *,
    dimension: str,
    deploy_sha: str,
    deploy_id: str,
    observed_at: datetime,
    fresh_until: datetime,
) -> TowerTruthEnvelope:

    return verified_truth(
        value=value,

        source_id=(
            "tower.teller_runtime_publication_authority:"
            f"{dimension}:"
            f"{deploy_id}:"
            f"{deploy_sha}"
        ),

        source_class=
            AUTHORITATIVE,

        observed_at_utc=
            observed_at.isoformat(),

        fresh_until_utc=
            fresh_until.isoformat(),

        reason=(
            "verified_teller_render_deployment_"
            f"{dimension}"
        ),
    )


def teller_runtime_publication_truth_bundle(
) -> dict[str, TowerTruthEnvelope] | None:

    if not teller_runtime_publication_configured():
        return None

    url = (
        _configured_web_url()
    )

    deploy_sha = (
        _configured_deploy_sha()
    )

    deploy_id = (
        _configured_deploy_id()
    )

    observed = datetime.now(
        timezone.utc
    )

    fresh_until = (
        observed
        + timedelta(
            seconds=
                _fresh_seconds()
        )
    )

    health = (
        _http_health_check(
            url
        )
    )

    # The explicit Render deploy receipt proves which sealed
    # build was published. The live HTTPS request proves current
    # environment reachability and current Teller response health.

    return {
        "configured":
            _runtime_truth(
                True,
                dimension="configured",
                deploy_sha=deploy_sha,
                deploy_id=deploy_id,
                observed_at=observed,
                fresh_until=fresh_until,
            ),

        "implemented":
            _runtime_truth(
                True,
                dimension="implemented",
                deploy_sha=deploy_sha,
                deploy_id=deploy_id,
                observed_at=observed,
                fresh_until=fresh_until,
            ),

        "published":
            _runtime_truth(
                True,
                dimension="published",
                deploy_sha=deploy_sha,
                deploy_id=deploy_id,
                observed_at=observed,
                fresh_until=fresh_until,
            ),

        "environment_available":
            _runtime_truth(
                bool(
                    health[
                        "reachable"
                    ]
                ),
                dimension="environment_available",
                deploy_sha=deploy_sha,
                deploy_id=deploy_id,
                observed_at=observed,
                fresh_until=fresh_until,
            ),

        "health_verified":
            _runtime_truth(
                bool(
                    health[
                        "healthy"
                    ]
                ),
                dimension="health_verified",
                deploy_sha=deploy_sha,
                deploy_id=deploy_id,
                observed_at=observed,
                fresh_until=fresh_until,
            ),
    }


def teller_runtime_publication_status(
) -> dict[str, Any]:

    configured = (
        teller_runtime_publication_configured()
    )

    return {
        "configured":
            configured,

        "provider":
            "teller_render_runtime_https",

        "deploy_sha_present":
            bool(
                _configured_deploy_sha()
            ),

        "deploy_id_present":
            bool(
                _configured_deploy_id()
            ),

        "web_url_present":
            bool(
                _configured_web_url()
            ),

        "credentials_exposed":
            False,

        "secrets_required":
            False,

        "request_authorization":
            False,

        "payroll_execution_authority":
            False,

        "bank_authority":
            False,

        "capital_authority":
            False,

        "broker_authority":
            False,

        "manual_live_authorized":
            False,

        "live_auto_authorized":
            False,
    }
