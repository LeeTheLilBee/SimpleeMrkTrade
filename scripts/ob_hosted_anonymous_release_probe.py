"""OBSIM066–070: passive unauthenticated hosted Tower/OB release preflight.

Run only with the exact chosen existing HTTPS owner origin and an exact expected
commit SHA. This makes anonymous GET requests; it cannot log in, activate beta,
certify hosted owner acceptance, mutate any service, or reveal secrets. A PASS
means the published revision/health and anonymous denial are compatible only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler, Request, build_opener, HTTPSHandler,
)

REVISION = re.compile(r"^[0-9a-f]{40}$")
MAX_RESPONSE = 65536
PATHS = (
    "/tower/healthz",
    "/tower/runtime-manifest.json",
    "/ob/owner-rehearsal",
    "/ob/owner-rehearsal/status.json",
    "/ob/owner-rehearsal/evidence.json",
)
DENIED_STATUSES = frozenset((301, 302, 303, 307, 308, 401, 403, 404, 409, 410, 503))


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def strict_origin(raw: str) -> str:
    if not isinstance(raw, str) or raw != raw.strip() or len(raw) > 250:
        raise ValueError("exact HTTPS owner origin required")
    parsed = urlsplit(raw)
    if (
        parsed.scheme != "https" or not parsed.hostname
        or not parsed.netloc or parsed.username or parsed.password
        or parsed.path not in ("", "/") or parsed.query or parsed.fragment
        or parsed.netloc != parsed.netloc.lower()
        or "\\" in raw or any(ord(ch) < 32 for ch in raw)
    ):
        raise ValueError("exact HTTPS owner origin required")
    return "https://" + parsed.netloc


def _get(origin: str, path: str, *, timeout: float = 10) -> dict[str, object]:
    """Perform a single anonymous direct GET, with redirects deliberately disabled."""
    if path not in PATHS:
        raise ValueError("probe may only request a fixed known read-only route")
    opener = build_opener(HTTPSHandler(), _NoRedirect())
    request = Request(
        origin + path,
        headers={"Accept": "application/json", "User-Agent": "OB-Anonymous-Release-Preflight/1"},
        method="GET",
    )
    try:
        response = opener.open(request, timeout=timeout)
    except HTTPError as exc:
        response = exc
    with response:
        body = response.read(MAX_RESPONSE + 1)
        if len(body) > MAX_RESPONSE:
            raise ValueError("hosted preflight response too large")
        return {
            "status": response.status if hasattr(response, "status") else response.code,
            "revision_header": response.headers.get("X-Simplee-Revision", ""),
            "body": body,
        }


def probe(origin: str, expected_revision: str) -> dict[str, object]:
    """Fail closed if published revision, health or public owner denial is uncertain."""
    origin = strict_origin(origin)
    if not isinstance(expected_revision, str) or REVISION.fullmatch(expected_revision) is None:
        raise ValueError("exact 40-character source revision required")
    outcome: dict[str, object] = {
        "contract": "OBSIM_ANONYMOUS_HOSTED_RELEASE_PREFLIGHT_V1",
        "origin": origin, "expected_revision": expected_revision,
        "status": "HOLD", "hosted_owner_walkthrough_verified": False,
        "manual_live_authorized": False, "broker_submission": False,
        "capital_movement": False, "authenticated_request_made": False,
        "render_service_settings_changed": False, "paid_service_created": False,
    }
    results = {}
    try:
        for path in PATHS:
            results[path] = _get(origin, path)
    except (OSError, ValueError, URLError, TimeoutError):
        outcome["reason"] = "HOST_UNAVAILABLE_OR_RESPONSE_INVALID"
        return outcome

    def payload(path: str) -> dict[str, object] | None:
        try:
            parsed = json.loads(results[path]["body"].decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None
        return parsed if type(parsed) is dict else None

    health = results["/tower/healthz"]
    manifest_status = results["/tower/runtime-manifest.json"]["status"]
    manifest = payload("/tower/runtime-manifest.json")
    anon = results["/ob/owner-rehearsal"]["status"]
    anon_api = results["/ob/owner-rehearsal/status.json"]["status"]
    anon_evidence = results["/ob/owner-rehearsal/evidence.json"]["status"]
    outcome["observed"] = {
        "health_http": health["status"],
        "manifest_http": manifest_status,
        "published_revision": manifest.get("revision", "") if manifest else "UNKNOWN",
        "anonymous_owner_page_http": anon,
        "anonymous_owner_status_http": anon_api,
        "anonymous_final_evidence_http": anon_evidence,
    }
    # Source configuration observation ONLY. A public manifest never provides
    # authenticated owner walkthrough, hosted archive or production permission.
    rehearsal = manifest.get("owner_rehearsal") if manifest else None
    rehearsal = rehearsal if type(rehearsal) is dict else {}

    def observed_bool(key: str) -> bool | None:
        value = rehearsal.get(key)
        return value if type(value) is bool else None

    source_flags = {
        field: observed_bool(field) for field in (
            "exact_source_routes_registered", "explicit_feature_enabled",
            "exact_https_origin_configured",
            "source_runtime_activation_preconditions_met",
        )
    }
    outcome["observed"]["owner_rehearsal_source"] = source_flags
    outcome["hosted_owner_walkthrough_verified"] = False
    outcome["durable_hosted_report_archive_verified"] = False

    if health["status"] != 200:
        outcome["reason"] = "TOWER_HEALTH_NOT_VERIFIED"
        return outcome
    if manifest_status != 200 or manifest is None:
        outcome["reason"] = "RUNTIME_MANIFEST_NOT_VERIFIED"
        return outcome
    if (
        manifest.get("revision") != expected_revision
        or manifest.get("revision_source") in (None, "", "unavailable")
    ):
        outcome["reason"] = "PUBLISHED_REVISION_MISMATCH_OR_UNKNOWN"
        return outcome
    if manifest.get("broker_submission") is not False or any(
        manifest.get(key) is not False for key in (
            "capital_movement", "manual_live_authorized", "live_auto_authorized"
        )
    ):
        outcome["reason"] = "HOSTED_SAFETY_HOLD_NOT_CONFIRMED"
        return outcome
    if any(results[path]["revision_header"] not in ("", expected_revision) for path in PATHS):
        outcome["reason"] = "INCONSISTENT_PUBLISHED_REVISION_HEADERS"
        return outcome
    # A source manifest with internally conflicting activation flags or a
    # claim of owner/durability/trading acceptance is not safe to pass through.
    all_configured = all(
        source_flags[field] is True for field in (
            "exact_source_routes_registered", "explicit_feature_enabled",
            "exact_https_origin_configured",
        )
    )
    preconditions = source_flags["source_runtime_activation_preconditions_met"]
    if preconditions is True and not all_configured:
        outcome["reason"] = "INCONSISTENT_HOSTED_REHEARSAL_SOURCE_FLAGS"
        return outcome
    if all_configured and preconditions is False:
        outcome["reason"] = "INCONSISTENT_HOSTED_REHEARSAL_SOURCE_FLAGS"
        return outcome
    if any(rehearsal.get(flag) is not False for flag in (
        "actual_owner_login_walkthrough_verified", "durable_report_archive",
        "restart_recovery", "manual_live_clearance", "broker_submission",
        "capital_movement",
    )) and rehearsal:
        outcome["reason"] = "UNSAFE_HOSTED_REHEARSAL_AUTHORITY_CLAIM"
        return outcome

    if any(status not in DENIED_STATUSES for status in (anon, anon_api, anon_evidence)):
        outcome["reason"] = "ANONYMOUS_OWNER_REHEARSAL_DISCLOSURE"
        return outcome
    # Passive compatibility only. Anonymous denial is not an owner login test;
    # a 404/503 can equally mean that a feature is still disabled.
    outcome["status"] = "PASS_ANONYMOUS_PREFLIGHT_ONLY"
    outcome["reason"] = "OWNER_LOGIN_AND_HOSTED_FEATURE_STILL_REQUIRE_SEPARATE_VERIFICATION"
    return outcome


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin", required=True, help="Exact existing HTTPS owner origin")
    parser.add_argument("--expected-revision", required=True, help="Exact Git commit SHA")
    args = parser.parse_args(argv)
    try:
        result = probe(args.origin, args.expected_revision)
    except ValueError:
        print(json.dumps({"status": "HOLD", "reason": "INVALID_PREFLIGHT_INPUT"}))
        return 2
    # Only redacted fixed route statuses, origin and source revision are printed.
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS_ANONYMOUS_PREFLIGHT_ONLY" else 1


if __name__ == "__main__":
    sys.exit(main())
