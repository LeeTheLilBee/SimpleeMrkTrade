
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path("/content/SimpleeMrkTrade_REAL_CLONE")
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

for name in list(sys.modules.keys()):
    if name == "tower" or name.startswith("tower.") or name == "web.app":
        sys.modules.pop(name, None)

from tower.route_replacement_policy import (
    VALID_POLICY_DECISIONS,
    build_route_replacement_policy_list,
    get_policy_for_route,
    load_route_replacement_policy_list,
    summarize_route_replacement_policy_list,
)


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    policy = build_route_replacement_policy_list()

    _print("ROUTE REPLACEMENT POLICY LIST", {
        "ok": policy.get("ok"),
        "total": policy.get("total"),
        "counts": policy.get("counts"),
        "clearance_counts": policy.get("clearance_counts"),
        "replacement_allowed_count": policy.get("replacement_allowed_count"),
        "owner_review_count": policy.get("owner_review_count"),
        "public_allowed_count": policy.get("public_allowed_count"),
        "archive_handoff_count": policy.get("archive_handoff_count"),
        "step_up_count": policy.get("step_up_count"),
        "path": policy.get("path"),
    })

    assert policy.get("ok") is True
    assert policy.get("total", 0) >= 1
    assert policy.get("readiness_score") == 100
    assert policy.get("readiness_label") == "Route replacement policy list ready"
    assert isinstance(policy.get("items"), list)
    assert len(policy.get("items", [])) == policy.get("total")

    counts = policy.get("counts", {})
    assert isinstance(counts, dict)
    assert sum(counts.values()) == policy.get("total")

    for decision in counts.keys():
        assert decision in VALID_POLICY_DECISIONS

    # Core expected categories should exist in this codebase.
    assert counts.get("approved_to_replace", 0) >= 1
    assert counts.get("needs_owner_review", 0) >= 1
    assert counts.get("retire_or_redirect", 0) >= 1
    assert counts.get("OB_protected", 0) >= 1

    for item in policy.get("items", []):
        assert item.get("route_path", "").startswith("/")
        assert item.get("policy_decision") in VALID_POLICY_DECISIONS
        assert isinstance(item.get("replacement_allowed"), bool)
        assert isinstance(item.get("route_may_be_public"), bool)
        assert isinstance(item.get("owner_review_required"), bool)
        assert item.get("required_clearance_level")
        assert item.get("policy_reason")
        assert item.get("policy_version") == "pack089.v1"

        # Nothing should be public unless explicitly public shell/static behavior.
        if item.get("route_may_be_public"):
            assert item.get("required_clearance_level") == "public_shell"

    loaded = load_route_replacement_policy_list()
    _print("LOADED ROUTE REPLACEMENT POLICY LIST", {
        "ok": loaded.get("ok"),
        "total": loaded.get("total"),
        "path": loaded.get("path"),
    })
    assert loaded.get("ok") is True
    assert loaded.get("total") == policy.get("total")

    summary = summarize_route_replacement_policy_list(limit=8)
    _print("ROUTE REPLACEMENT POLICY SUMMARY", summary)

    assert summary.get("ok") is True
    assert summary.get("total") == policy.get("total")
    assert summary.get("readiness_score") == 100
    assert summary.get("counts", {}).get("approved_to_replace", 0) >= 1
    assert summary.get("counts", {}).get("needs_owner_review", 0) >= 1
    assert summary.get("counts", {}).get("retire_or_redirect", 0) >= 1

    no_access = get_policy_for_route("/no-access")
    _print("POLICY LOOKUP /no-access", no_access)
    assert no_access.get("ok") is True
    assert no_access.get("policy_decision") == "approved_to_replace"
    assert no_access.get("replacement_allowed") is True
    assert no_access.get("route_may_be_public") is False

    admin = get_policy_for_route("/admin")
    _print("POLICY LOOKUP /admin", admin)
    assert admin.get("ok") is True
    assert admin.get("policy_decision") == "retire_or_redirect"
    assert admin.get("owner_review_required") is True
    assert admin.get("route_may_be_public") is False

    signals = get_policy_for_route("/signals")
    _print("POLICY LOOKUP /signals", signals)
    assert signals.get("ok") is True
    assert signals.get("policy_decision") in {"OB_protected", "needs_owner_review"}
    assert signals.get("route_may_be_public") is False

    symbol = get_policy_for_route("/signals/AAPL")
    _print("POLICY LOOKUP /signals/AAPL", symbol)
    assert symbol.get("ok") is True
    assert symbol.get("policy_decision") in {"needs_owner_review", "OB_protected"}
    assert symbol.get("route_may_be_public") is False

    unknown = get_policy_for_route("/brand-new-secret-door")
    _print("POLICY LOOKUP UNKNOWN", unknown)
    assert unknown.get("ok") is False
    assert unknown.get("policy_decision") == "needs_owner_review"
    assert unknown.get("owner_review_required") is True
    assert unknown.get("route_may_be_public") is False

    serialized = json.dumps([policy, loaded, summary, no_access, admin, signals, symbol, unknown], sort_keys=True, default=str)
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "089",
        "status": "passed",
        "human_reason": "Route replacement policy list now controls which mapped doors can be replaced, reviewed, protected, retired, or kept.",
    }
    _print("PACK 089 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
