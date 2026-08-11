from __future__ import annotations

from tower.tower_ir_cert_p2574 import tower_ir_cert_p2574


def test_tower_ir_cert_p2574_issue_intake():
    cert = tower_ir_cert_p2574()

    assert cert["pack"] == 2574
    assert cert["title"] == "Owner-session issue submission schema"
    assert cert["status"] == "passed"
    assert cert["requires_owner_session"] is True
    assert cert["persistence_mode"] == "append_only_jsonl"
    assert cert["dangerous_controls_locked"] is True

    routes = cert["routes"]
    assert routes["list_or_submit_issues"] == "/tower/owner-beta/issues.json"
    assert routes["review_receipts"] == "/tower/owner-beta/review-receipts.json"

    controls = cert["dangerous_controls"]
    assert controls["production_deployment"] is False
    assert controls["broker_submission"] is False
    assert controls["capital_movement"] is False
    assert controls["manual_live_authorized"] is False
    assert controls["live_auto_authorized"] is False
    assert controls["direct_vault_write"] is False
    assert controls["destructive_action_unlocked"] is False
    assert controls["public_launch_authorized"] is False
