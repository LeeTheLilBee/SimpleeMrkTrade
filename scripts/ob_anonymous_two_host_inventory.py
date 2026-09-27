"""OBSIM071–075: noncredentialed inventory of the two existing Tower HTTPS origins.

A release classification is ALWAYS HOLD until separately reviewed service
ownership, authenticated owner walkthrough, host configuration and voluntary
ephemeral storage acceptance. A successful second service cannot stand in for
the original documented canonical owner entrance. No Render mutation.
"""
from __future__ import annotations

import argparse
import json

from scripts.ob_hosted_anonymous_release_probe import REVISION, probe, strict_origin

SCHEMA = "OBSIM_TWO_HOST_ANONYMOUS_CANDIDATE_CHECK_V1"
CANONICAL = "https://simplee-tower-ob.onrender.com"
SECONDARY = "https://simplee-tower-ob-tunv.onrender.com"


def classify(canonical_origin: str, secondary_origin: str, exact_revision: str,
             *, probe_function=probe) -> dict[str, object]:
    if (strict_origin(canonical_origin) != CANONICAL
            or strict_origin(secondary_origin) != SECONDARY
            or not isinstance(exact_revision, str)
            or REVISION.fullmatch(exact_revision) is None):
        raise ValueError("exact documented origin inventory and revision required")
    observations = {}
    for label, origin in (("documented_canonical_candidate", CANONICAL),
                          ("separate_secondary_candidate", SECONDARY)):
        try:
            value = probe_function(origin, exact_revision)
            if not isinstance(value, dict):
                raise ValueError("probe payload invalid")
            # Tight allowlist: do not repeat accidental future secret/identity fields.
            observed = value.get("observed")
            observed = observed if type(observed) is dict else {}
            observations[label] = {
                "origin": origin,
                "status": value.get("status") if value.get("status") in (
                    "PASS_ANONYMOUS_PREFLIGHT_ONLY", "HOLD"
                ) else "HOLD",
                "reason": value.get("reason") if isinstance(value.get("reason"), str) else "UNKNOWN",
                "observed": {
                    field: observed.get(field) for field in (
                        "health_http", "manifest_http", "published_revision",
                        "anonymous_owner_page_http", "anonymous_owner_status_http",
                    "anonymous_final_evidence_http",
                    )
                },
            }
        except (OSError, ValueError, TimeoutError):
            observations[label] = {
                "origin": origin, "status": "HOLD",
                "reason": "HOST_UNAVAILABLE_OR_INVALID",
                "observed": {},
            }
    return {
        "contract": SCHEMA, "expected_tower_revision": exact_revision,
        "observations": observations,
        "release_status": "HOLD_OWNER_SITE_AND_AUTHENTICATED_WALKTHROUGH",
        "canonical_owner_url_confirmed_by_owner": False,
        "secondary_pass_substitutes_for_canonical": False,
        "anonymous_probe_is_owner_login": False,
        "hosted_rehearsal_feature_enabled_by_probe": False,
        "manual_live_authorized": False, "broker_submission": False,
        "capital_movement": False, "paid_service_created": False,
        "render_service_settings_changed": False,
        "credentials_sent": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical-origin", required=True)
    parser.add_argument("--secondary-origin", required=True)
    parser.add_argument("--expected-revision", required=True)
    args = parser.parse_args(argv)
    try:
        result = classify(args.canonical_origin, args.secondary_origin, args.expected_revision)
    except ValueError:
        print(json.dumps({"status": "HOLD", "reason": "INVALID_ORIGIN_INVENTORY"}))
        return 2
    print(json.dumps(result, sort_keys=True))
    # This exits 0 only to confirm a read-only, redacted *inventory was run*.
    # Consumers MUST read release_status, never infer permission from exit 0.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
