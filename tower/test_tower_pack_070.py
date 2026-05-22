
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

from tower.locked_state_transition_checkpoint import build_locked_state_transition_checkpoint


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    checkpoint = build_locked_state_transition_checkpoint()

    _print("LOCKED-STATE TRANSITION CHECKPOINT", {
        "ok": checkpoint.get("ok"),
        "readiness_score": checkpoint.get("readiness_score"),
        "readiness_label": checkpoint.get("readiness_label"),
        "locked_page_proof": checkpoint.get("locked_page_proof"),
        "next_block": checkpoint.get("next_block"),
        "current_boundary": checkpoint.get("current_boundary"),
    })

    assert checkpoint.get("ok") is True
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("readiness_label") == "Ready for UI endpoint wiring"
    assert checkpoint.get("smoke_ok") is True
    assert checkpoint.get("privacy_checkpoint_ok") is True

    proof = checkpoint.get("locked_page_proof", {})
    for key in [
        "has_tower",
        "has_clearance_gate",
        "has_soulaana",
        "has_route_variant",
        "has_object_variant",
        "has_mode_variant",
        "has_export_variant",
        "has_unmapped_variant",
        "no_keycard_query",
        "no_raw_token_assignment",
        "no_test_secret",
    ]:
        assert proof.get(key) is True

    for key in [
        "route_status",
        "object_status",
        "mode_status",
        "export_status",
        "unmapped_status",
        "helper_status",
        "preview_status",
    ]:
        assert proof.get(key) == 403

    built = json.dumps(checkpoint.get("built_packs", []), sort_keys=True)
    for pack in ["066", "067", "068", "069", "070"]:
        assert pack in built

    next_block = json.dumps(checkpoint.get("next_block", []), sort_keys=True)
    for pack in ["071", "072", "073", "074", "075"]:
        assert pack in next_block

    serialized = json.dumps(checkpoint, sort_keys=True, default=str)
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Soulaana:" in checkpoint.get("soulaana_translation", "")

    final = {
        "pack": "070",
        "status": "passed",
        "human_reason": "Locked-state transition checkpoint is ready before UI endpoint wiring.",
    }
    _print("PACK 070 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
