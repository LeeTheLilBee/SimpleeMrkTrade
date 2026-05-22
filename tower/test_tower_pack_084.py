
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
    if name == "web.app" or name == "web" or name == "tower" or name.startswith("tower."):
        sys.modules.pop(name, None)

from tower.ob_exposure_mapping import (
    build_ob_exposure_mapping_pass,
    load_ob_exposure_mapping_pass,
    summarize_ob_exposure_mapping_pass,
)


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    mapping = build_ob_exposure_mapping_pass()

    _print("EXPOSURE MAPPING PASS", {
        "ok": mapping.get("ok"),
        "total": mapping.get("total"),
        "counts": mapping.get("counts"),
        "reason_counts": mapping.get("reason_counts"),
        "priority_counts": mapping.get("priority_counts"),
        "top_next_count": len(mapping.get("top_next", [])),
        "retire_or_redirect_count": len(mapping.get("retire_or_redirect", [])),
        "later_review_count": len(mapping.get("later_review", [])),
        "path": mapping.get("path"),
    })

    assert mapping.get("ok") is True
    assert mapping.get("total", 0) >= 1
    assert isinstance(mapping.get("items"), list)
    assert len(mapping.get("items", [])) == mapping.get("total")

    counts = mapping.get("counts", {})
    assert isinstance(counts, dict)
    assert sum(counts.values()) == mapping.get("total")

    allowed_categories = {
        "keep_protected",
        "keep_public_safe",
        "map_next",
        "retire_or_redirect",
        "later_review",
    }

    for item in mapping.get("items", []):
        assert item.get("path", "").startswith("/")
        assert item.get("category") in allowed_categories
        assert item.get("reason_code")
        assert item.get("plain")
        assert isinstance(item.get("priority"), int)

    # We should see at least the Tower routes protected or safe public routes.
    assert (
        counts.get("keep_protected", 0) >= 1
        or counts.get("keep_public_safe", 0) >= 1
        or counts.get("later_review", 0) >= 1
    )

    loaded = load_ob_exposure_mapping_pass()
    _print("LOADED EXPOSURE MAPPING PASS", {
        "ok": loaded.get("ok"),
        "total": loaded.get("total"),
        "path": loaded.get("path"),
    })
    assert loaded.get("ok") is True
    assert loaded.get("total") == mapping.get("total")

    summary = summarize_ob_exposure_mapping_pass(limit=12)
    _print("SUMMARY EXPOSURE MAPPING PASS", summary)

    assert summary.get("ok") is True
    assert summary.get("total") == mapping.get("total")
    assert isinstance(summary.get("counts"), dict)
    assert summary.get("readiness_score") == 100
    assert summary.get("readiness_label") == "Exposure mapping pass ready"

    serialized = json.dumps([mapping, loaded, summary], sort_keys=True, default=str)
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in summary.get("soulaana_translation", "")

    final = {
        "pack": "084",
        "status": "passed",
        "human_reason": "Exposure report mapping pass categorizes protected, public-safe, map-next, retire/redirect, and later-review routes.",
    }
    _print("PACK 084 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
