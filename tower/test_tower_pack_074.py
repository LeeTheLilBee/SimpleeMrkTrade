
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

from tower.archive_vault_handoff import (
    build_archive_vault_handoff_record,
    queue_archive_vault_handoff,
    summarize_archive_vault_handoffs,
)
from tower.tower_status import get_tower_status
from tower.security_command_page import generate_security_command_dashboard


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    before = summarize_archive_vault_handoffs(limit=5)
    _print("BEFORE ARCHIVE HANDOFF SUMMARY", before)

    record = build_archive_vault_handoff_record(
        source_type="pack074_test",
        source_id="archive_074",
        title="Pack 074 Archive Handoff Test",
        summary="Testing Archive Vault handoff status and UI surfacing.",
        severity="medium",
        user_id="owner_solice",
        related_object={
            "object_type": "export",
            "object_id": "export_074",
        },
        source_payload={
            "safe": "yes",
            "raw_token": "SHOULD_NOT_SURVIVE",
            "tower_keycard": "SHOULD_NOT_SURVIVE",
        },
        owner_note="Pack 074 test handoff.",
    )

    queued = queue_archive_vault_handoff(record)
    _print("QUEUED PACK 074 HANDOFF", queued)
    assert queued.get("ok") is True

    after = summarize_archive_vault_handoffs(limit=8)
    _print("AFTER ARCHIVE HANDOFF SUMMARY", after)

    assert after.get("ok") is True
    assert after.get("total", 0) >= before.get("total", 0) + 1
    assert after.get("queued", 0) >= 1
    assert "pack074_test" in after.get("by_source_type", {})

    status = get_tower_status()
    _print("TOWER STATUS ARCHIVE FIELDS", {
        "archive_vault_handoff_ok": status.get("archive_vault_handoff_ok"),
        "archive_vault_handoff_total": status.get("archive_vault_handoff_total"),
        "archive_vault_handoff_queued": status.get("archive_vault_handoff_queued"),
        "archive_vault_handoff_by_status": status.get("archive_vault_handoff_by_status"),
        "archive_vault_handoff_by_source_type": status.get("archive_vault_handoff_by_source_type"),
        "archive_vault_handoff_by_severity": status.get("archive_vault_handoff_by_severity"),
    })

    assert status.get("archive_vault_handoff_ok") is True
    assert status.get("archive_vault_handoff_total", 0) >= after.get("total", 0)
    assert status.get("archive_vault_handoff_queued", 0) >= 1
    assert "pack074_test" in status.get("archive_vault_handoff_by_source_type", {})

    dashboard = generate_security_command_dashboard()
    _print("SECURITY COMMAND DASHBOARD ARCHIVE FIELDS", {
        "ok": dashboard.get("ok"),
        "path": dashboard.get("path"),
        "bytes": dashboard.get("bytes"),
        "archive_vault_handoff_ok": dashboard.get("archive_vault_handoff_ok"),
        "archive_vault_handoff_total": dashboard.get("archive_vault_handoff_total"),
        "archive_vault_handoff_queued": dashboard.get("archive_vault_handoff_queued"),
    })

    assert dashboard.get("ok") is True
    assert dashboard.get("archive_vault_handoff_ok") is True
    assert dashboard.get("archive_vault_handoff_total", 0) >= after.get("total", 0)

    html_path = Path(dashboard.get("path", ""))
    assert html_path.exists()
    html = html_path.read_text(encoding="utf-8", errors="replace")

    assert "ARCHIVE VAULT HANDOFFS" in html
    assert "Evidence Bundle Queue" in html
    assert 'data-pack="074"' in html
    assert "Pack 074 Archive Handoff Test" in html or "Archive Vault handoff" in html
    assert "pack074_test" in html or "archive_074" in html

    serialized = json.dumps([after, status, dashboard], sort_keys=True, default=str) + html
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "074",
        "status": "passed",
        "human_reason": "Archive Vault handoff summary now appears in Tower status and Security Command UI.",
    }
    _print("PACK 074 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
