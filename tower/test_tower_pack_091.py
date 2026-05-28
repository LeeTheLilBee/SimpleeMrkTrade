
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

from tower.tamper_evident_audit_chain import (
    CHAINED_SOURCE_FILES,
    TAMPER_CHAIN_PATH,
    build_tamper_evident_audit_chain,
    simulate_tamper_detection,
    summarize_tamper_evident_audit_chain,
    verify_tamper_evident_audit_chain,
)


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    built = build_tamper_evident_audit_chain()

    _print("TAMPER-EVIDENT AUDIT CHAIN BUILD", {
        "ok": built.get("ok"),
        "before_count": built.get("before_count"),
        "after_count": built.get("after_count"),
        "created_count": built.get("created_count"),
        "total_entries": built.get("total_entries"),
        "source_count": built.get("source_count"),
        "latest_hash": built.get("latest_hash"),
        "readiness_score": built.get("readiness_score"),
        "readiness_label": built.get("readiness_label"),
    })

    assert built.get("ok") is True
    assert built.get("readiness_score") == 100
    assert built.get("readiness_label") == "Tamper-evident audit chain ready"
    assert built.get("source_count") == len(CHAINED_SOURCE_FILES)
    assert built.get("total_entries", 0) >= 1
    assert TAMPER_CHAIN_PATH.exists()

    verification = verify_tamper_evident_audit_chain()
    _print("TAMPER-EVIDENT AUDIT CHAIN VERIFY", verification)

    assert verification.get("ok") is True
    assert verification.get("total_entries", 0) >= 1
    assert verification.get("latest_hash")
    assert not verification.get("failures")

    summary = summarize_tamper_evident_audit_chain(limit=20)
    _print("TAMPER-EVIDENT AUDIT CHAIN SUMMARY", summary)

    assert summary.get("ok") is True
    assert summary.get("total_entries", 0) >= 1
    assert summary.get("readiness_score") == 100
    assert isinstance(summary.get("by_source"), dict)
    assert isinstance(summary.get("by_event_type"), dict)
    assert summary.get("verification", {}).get("ok") is True

    entries = summary.get("recent", [])
    assert entries
    for entry in entries:
        assert entry.get("previous_hash")
        assert entry.get("current_hash")
        assert entry.get("sequence", 0) >= 1
        assert entry.get("source_hash")
        assert entry.get("source_name")

    tamper = simulate_tamper_detection()
    _print("TAMPER SIMULATION", tamper)

    assert tamper.get("ok") is True
    assert tamper.get("tamper_detected") is True
    assert tamper.get("verification", {}).get("ok") is False
    assert tamper.get("verification", {}).get("failures")

    serialized = json.dumps([built, verification, summary, tamper], sort_keys=True, default=str)
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    # The tamper detector should prove the mismatch without needing to echo the tampered content.
    tamper_failures = tamper.get("verification", {}).get("failures", [])
    assert any(failure.get("failure") == "current_hash_mismatch" for failure in tamper_failures)
    assert "Tamper simulation was detected" in serialized
    assert "current_hash_mismatch" in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "091",
        "status": "passed",
        "human_reason": "Tamper-evident audit chain created, verified, and proven to detect simulated tampering.",
    }
    _print("PACK 091 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
