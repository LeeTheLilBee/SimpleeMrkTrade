
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

from tower.visibility_policy_transition_checkpoint import (
    build_visibility_policy_transition_checkpoint,
    load_visibility_policy_transition_checkpoint,
)


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    checkpoint = build_visibility_policy_transition_checkpoint()

    _print("VISIBILITY + POLICY TRANSITION CHECKPOINT", {
        "ok": checkpoint.get("ok"),
        "readiness_score": checkpoint.get("readiness_score"),
        "readiness_label": checkpoint.get("readiness_label"),
        "proof": checkpoint.get("proof"),
        "deny_path_replacement_summary": checkpoint.get("deny_path_replacement_summary"),
        "exposure_mapping_summary": checkpoint.get("exposure_mapping_summary"),
        "route_replacement_policy_summary": checkpoint.get("route_replacement_policy_summary"),
        "next_block": checkpoint.get("next_block"),
        "current_boundary": checkpoint.get("current_boundary"),
    })

    assert checkpoint.get("ok") is True
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("readiness_label") == "Ready for tamper-evident audit chain"

    proof = checkpoint.get("proof", {})
    for key, value in proof.items():
        assert value is True, key

    deny = checkpoint.get("deny_path_replacement_summary", {})
    assert deny.get("ok") is True
    assert deny.get("total", 0) >= 1
    assert deny.get("verified", 0) >= 1
    assert deny.get("by_route", {}).get("/no-access", 0) >= 1

    exposure = checkpoint.get("exposure_mapping_summary", {})
    assert exposure.get("ok") is True
    assert exposure.get("total", 0) >= 1
    assert exposure.get("readiness_score") == 100

    policy = checkpoint.get("route_replacement_policy_summary", {})
    assert policy.get("ok") is True
    assert policy.get("total") == exposure.get("total")
    assert policy.get("counts", {}).get("approved_to_replace", 0) >= 1
    assert policy.get("counts", {}).get("needs_owner_review", 0) >= 1
    assert policy.get("counts", {}).get("retire_or_redirect", 0) >= 1
    assert policy.get("counts", {}).get("Tower_only", 0) >= 1
    assert policy.get("counts", {}).get("OB_protected", 0) >= 1

    lookup = checkpoint.get("policy_lookup_proof", {})
    assert lookup.get("no_access", {}).get("policy_decision") == "approved_to_replace"
    assert lookup.get("observatory_private", {}).get("policy_decision") == "approved_to_replace"
    assert lookup.get("admin", {}).get("policy_decision") == "retire_or_redirect"
    assert lookup.get("signals", {}).get("policy_decision") == "OB_protected"
    assert lookup.get("signals_symbol", {}).get("policy_decision") == "needs_owner_review"
    assert lookup.get("unknown", {}).get("policy_decision") == "needs_owner_review"

    built = json.dumps(checkpoint.get("built_packs", []), sort_keys=True)
    for pack in ["086", "087", "088", "089", "090"]:
        assert pack in built

    next_block = json.dumps(checkpoint.get("next_block", []), sort_keys=True)
    for pack in ["091", "092", "093", "094", "095"]:
        assert pack in next_block
    assert "Tamper-evident audit chain" in next_block

    boundary = json.dumps(checkpoint.get("current_boundary", {}), sort_keys=True)
    assert "Route policy decisions do not yet have owner action buttons" in boundary
    assert "Step-up authentication is not active yet" in boundary
    assert "The Tower now has visibility" in boundary

    loaded = load_visibility_policy_transition_checkpoint()
    _print("LOADED VISIBILITY + POLICY TRANSITION CHECKPOINT", {
        "ok": loaded.get("ok"),
        "readiness_score": loaded.get("readiness_score"),
        "path": loaded.get("path"),
    })

    assert loaded.get("ok") is True
    assert loaded.get("readiness_score") == 100

    serialized = json.dumps([checkpoint, loaded], sort_keys=True, default=str)
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in checkpoint.get("soulaana_translation", "")

    final = {
        "pack": "090",
        "status": "passed",
        "human_reason": "Visibility and route replacement policy block is checkpointed and ready for tamper-evident audit chains.",
    }
    _print("PACK 090 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
