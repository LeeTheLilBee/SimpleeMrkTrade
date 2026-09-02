"""
Tower hosted candidate parity gate / TWR086–TWR090.

This module consumes the safe runtime identity surface created by
TWR081–TWR085 and answers one question:

    Is the hosted staging runtime serving the exact candidate
    revision we intended, with the expected Tower contract and all
    safety flags still closed?

Safety boundary:
- no deployment
- no authentication credentials
- no cookies
- no broker submission
- no capital movement
- no Manual Live authorization
- no Live Auto authorization
- no STAGING_READY mutation
"""

from __future__ import annotations

import json
from typing import Any, Mapping
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


EXPECTED_ENTRYPOINT = (
    "web.managed_staging:app"
)

PROBE_PATHS = (
    "/tower/healthz",
    "/tower/runtime-manifest.json",
    "/tower/login",
)

SAFETY_FALSE_FIELDS = (
    "production_deployment",
    "broker_submission",
    "capital_movement",
    "manual_live_authorized",
    "live_auto_authorized",
    "staging_ready",
)


def _clean_revision(
    value: Any,
) -> str:
    return str(
        value
        or ""
    ).strip().lower()


def normalize_base_url(
    base_url: str,
    *,
    allow_http: bool = False,
) -> str:
    """
    Validate and normalize a hosted base URL.

    HTTPS is mandatory unless allow_http=True is explicitly used
    for local development/tests.

    Embedded credentials, query strings, fragments, and path
    prefixes are rejected.
    """

    value = str(
        base_url
        or ""
    ).strip()

    parsed = urlsplit(
        value
    )

    allowed_schemes = (
        {"https", "http"}
        if allow_http
        else {"https"}
    )

    if (
        parsed.scheme.lower()
        not in allowed_schemes
    ):
        raise ValueError(
            "Hosted parity base URL "
            "must use HTTPS."
        )

    if not parsed.hostname:
        raise ValueError(
            "Hosted parity base URL "
            "must include a hostname."
        )

    if (
        parsed.username
        or parsed.password
    ):
        raise ValueError(
            "Credentials must not be "
            "embedded in the base URL."
        )

    if (
        parsed.query
        or parsed.fragment
    ):
        raise ValueError(
            "Base URL must not contain "
            "query strings or fragments."
        )

    path = (
        parsed.path
        or ""
    ).rstrip("/")

    if path:
        raise ValueError(
            "Base URL must point to the "
            "host root, not a path prefix."
        )

    return (
        f"{parsed.scheme.lower()}://"
        f"{parsed.netloc}"
    ).rstrip("/")


def _response_status(
    response,
) -> int:
    status = getattr(
        response,
        "status",
        None,
    )

    if status is None:
        status = (
            response.getcode()
        )

    return int(
        status
    )


def _response_headers(
    response,
) -> dict[str, str]:
    headers = getattr(
        response,
        "headers",
        {},
    )

    try:
        items = headers.items()
    except Exception:
        items = []

    return {
        str(key): str(value)
        for key, value
        in items
    }


def _fetch_probe(
    *,
    base_url: str,
    path: str,
    timeout: float,
    opener,
) -> dict[str, Any]:
    """
    Perform an unauthenticated GET probe.

    No Authorization header.
    No Cookie header.
    No secret-bearing query parameters.
    """

    request = Request(
        base_url + path,
        method="GET",
        headers={
            "Accept": (
                "application/json,"
                "text/html;q=0.9,*/*;q=0.8"
            ),
            "User-Agent": (
                "Simplee-Tower-Hosted-Parity/1.0"
            ),
        },
    )

    try:
        response = opener(
            request,
            timeout=timeout,
        )

        with response:
            body = response.read()

            return {
                "path": path,
                "status": (
                    _response_status(
                        response
                    )
                ),
                "headers": (
                    _response_headers(
                        response
                    )
                ),
                "body": (
                    body.decode(
                        "utf-8",
                        errors="replace",
                    )
                ),
                "error": None,
            }

    except HTTPError as exc:
        try:
            body = exc.read()
        except Exception:
            body = b""

        return {
            "path": path,
            "status": int(
                exc.code
            ),
            "headers": (
                {
                    str(key): str(value)
                    for key, value
                    in (
                        exc.headers.items()
                        if exc.headers
                        else []
                    )
                }
            ),
            "body": (
                body.decode(
                    "utf-8",
                    errors="replace",
                )
            ),
            "error": (
                "HTTPError"
            ),
        }


def _header(
    probe: Mapping[str, Any],
    name: str,
) -> str:
    headers = (
        probe.get(
            "headers",
            {}
        )
        or {}
    )

    wanted = name.lower()

    for key, value in headers.items():
        if (
            str(key).lower()
            == wanted
        ):
            return str(
                value
                or ""
            ).strip()

    return ""


def evaluate_hosted_runtime_parity(
    *,
    expected_revision: str,
    probes: Mapping[
        str,
        Mapping[str, Any],
    ],
    manifest: Mapping[
        str,
        Any,
    ],
) -> dict[str, Any]:
    """
    Fail-closed parity evaluation.

    PASS means:
    - exact revision equality
    - expected managed-staging entrypoint
    - consistent runtime headers
    - all critical routes present
    - every safety flag remains False

    PASS does NOT authorize deployment or STAGING_READY.
    """

    checks: dict[
        str,
        bool,
    ] = {}

    failures: list[
        str
    ] = []


    def check(
        name: str,
        condition: bool,
        failure: str,
    ):
        result = bool(
            condition
        )

        checks[
            name
        ] = result

        if not result:
            failures.append(
                failure
            )


    expected = (
        _clean_revision(
            expected_revision
        )
    )

    check(
        "expected_revision_valid",
        bool(
            expected
            and expected
            not in {
                "unknown",
                "unavailable",
                "none",
                "null",
            }
        ),
        "Expected candidate revision "
        "is missing or unknown.",
    )


    health = (
        probes.get(
            "/tower/healthz",
            {}
        )
        or {}
    )

    runtime_manifest_probe = (
        probes.get(
            "/tower/runtime-manifest.json",
            {}
        )
        or {}
    )

    login = (
        probes.get(
            "/tower/login",
            {}
        )
        or {}
    )


    check(
        "health_http_200",
        health.get(
            "status"
        )
        == 200,
        "Hosted /tower/healthz "
        "did not return HTTP 200.",
    )

    check(
        "manifest_http_200",
        runtime_manifest_probe.get(
            "status"
        )
        == 200,
        "Hosted runtime manifest "
        "did not return HTTP 200.",
    )

    login_status = (
        login.get(
            "status"
        )
    )

    check(
        "login_route_reachable",
        (
            isinstance(
                login_status,
                int,
            )
            and 200
            <= login_status
            < 400
        ),
        "Hosted /tower/login "
        "was not reachable.",
    )


    manifest_entrypoint = str(
        manifest.get(
            "entrypoint",
            ""
        )
        or ""
    ).strip()

    check(
        "manifest_entrypoint",
        (
            manifest_entrypoint
            == EXPECTED_ENTRYPOINT
        ),
        "Runtime manifest entrypoint "
        "does not match "
        "web.managed_staging:app.",
    )


    header_entrypoints = [
        _header(
            probe,
            "X-Simplee-Entrypoint",
        )
        for probe
        in (
            health,
            runtime_manifest_probe,
            login,
        )
    ]

    check(
        "entrypoint_headers_present",
        all(
            header_entrypoints
        ),
        "One or more hosted routes "
        "is missing X-Simplee-Entrypoint.",
    )

    check(
        "entrypoint_headers_exact",
        all(
            value
            == EXPECTED_ENTRYPOINT
            for value
            in header_entrypoints
        ),
        "Hosted entrypoint headers "
        "do not all identify "
        "web.managed_staging:app.",
    )


    actual_revision = (
        _clean_revision(
            manifest.get(
                "revision"
            )
        )
    )

    check(
        "manifest_revision_present",
        bool(
            actual_revision
            and actual_revision
            not in {
                "unknown",
                "unavailable",
                "none",
                "null",
            }
        ),
        "Runtime manifest revision "
        "is missing or unknown.",
    )


    header_revisions = [
        _clean_revision(
            _header(
                probe,
                "X-Simplee-Revision",
            )
        )
        for probe
        in (
            health,
            runtime_manifest_probe,
            login,
        )
    ]

    check(
        "revision_headers_present",
        all(
            value
            and value
            not in {
                "unknown",
                "unavailable",
                "none",
                "null",
            }
            for value
            in header_revisions
        ),
        "One or more hosted routes "
        "is missing a usable "
        "X-Simplee-Revision.",
    )

    check(
        "revision_headers_consistent",
        (
            bool(
                header_revisions
            )
            and len(
                set(
                    header_revisions
                )
            )
            == 1
        ),
        "Hosted revision headers "
        "are inconsistent across routes.",
    )

    check(
        "headers_match_manifest_revision",
        (
            bool(
                actual_revision
            )
            and all(
                value
                == actual_revision
                for value
                in header_revisions
            )
        ),
        "Hosted revision headers "
        "do not match the runtime "
        "manifest revision.",
    )

    check(
        "exact_candidate_revision_match",
        (
            bool(
                expected
            )
            and actual_revision
            == expected
        ),
        "Hosted runtime revision "
        "does not equal the exact "
        "expected candidate revision.",
    )


    manifest_revision_source = str(
        manifest.get(
            "revision_source",
            ""
        )
        or ""
    ).strip()

    header_revision_sources = [
        _header(
            probe,
            "X-Simplee-Revision-Source",
        )
        for probe
        in (
            health,
            runtime_manifest_probe,
            login,
        )
    ]

    check(
        "revision_source_present",
        bool(
            manifest_revision_source
        )
        and all(
            header_revision_sources
        ),
        "Revision source metadata "
        "is missing.",
    )

    check(
        "revision_source_consistent",
        (
            bool(
                manifest_revision_source
            )
            and all(
                value
                == manifest_revision_source
                for value
                in header_revision_sources
            )
        ),
        "Revision source metadata "
        "is inconsistent across "
        "manifest and headers.",
    )


    critical_routes = (
        manifest.get(
            "critical_routes",
            {}
        )
        or {}
    )

    check(
        "critical_route_manifest_present",
        (
            isinstance(
                critical_routes,
                Mapping,
            )
            and bool(
                critical_routes
            )
        ),
        "Critical-route manifest "
        "is missing.",
    )

    check(
        "all_critical_routes_present",
        (
            isinstance(
                critical_routes,
                Mapping,
            )
            and bool(
                critical_routes
            )
            and all(
                value is True
                for value
                in critical_routes.values()
            )
        ),
        "One or more critical Tower, "
        "Archive Vault, or OB routes "
        "is missing.",
    )

    check(
        "critical_routes_present_flag",
        (
            manifest.get(
                "critical_routes_present"
            )
            is True
        ),
        "Runtime manifest does not "
        "assert all critical routes present.",
    )


    for field in SAFETY_FALSE_FIELDS:
        check(
            f"safety_{field}_false",
            (
                manifest.get(
                    field
                )
                is False
            ),
            (
                "Safety boundary opened: "
                + field
                + " is not False."
            ),
        )


    parity_pass = (
        not failures
    )

    return {
        "status": (
            "tower_hosted_candidate_parity_pass"
            if parity_pass
            else "tower_hosted_candidate_parity_fail"
        ),
        "parity_pass": parity_pass,
        "expected_revision": expected,
        "actual_revision": actual_revision,
        "entrypoint": manifest_entrypoint,
        "critical_route_count": (
            len(
                critical_routes
            )
            if isinstance(
                critical_routes,
                Mapping,
            )
            else 0
        ),
        "checks": checks,
        "failures": failures,
        "deployment_authorized": False,
        "production_promotion_authorized": False,
        "broker_submission_authorized": False,
        "capital_movement_authorized": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
        "staging_ready_changed": False,
    }


def probe_hosted_runtime(
    *,
    base_url: str,
    expected_revision: str,
    timeout: float = 10.0,
    allow_http: bool = False,
    opener=urlopen,
) -> dict[str, Any]:
    """
    Probe the three safe runtime identity surfaces and evaluate
    exact candidate parity.
    """

    normalized = (
        normalize_base_url(
            base_url,
            allow_http=allow_http,
        )
    )

    probes: dict[
        str,
        dict[str, Any],
    ] = {}


    for path in PROBE_PATHS:
        try:
            probes[
                path
            ] = _fetch_probe(
                base_url=normalized,
                path=path,
                timeout=timeout,
                opener=opener,
            )

        except Exception as exc:
            probes[
                path
            ] = {
                "path": path,
                "status": 0,
                "headers": {},
                "body": "",
                "error": (
                    exc.__class__.__name__
                ),
            }


    manifest: dict[
        str,
        Any,
    ] = {}

    manifest_probe = (
        probes.get(
            "/tower/runtime-manifest.json",
            {}
        )
    )

    try:
        decoded = json.loads(
            manifest_probe.get(
                "body",
                ""
            )
            or "{}"
        )

        if isinstance(
            decoded,
            dict,
        ):
            manifest = decoded

    except Exception:
        manifest = {}


    return (
        evaluate_hosted_runtime_parity(
            expected_revision=expected_revision,
            probes=probes,
            manifest=manifest,
        )
    )
