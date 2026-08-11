from __future__ import annotations

from tower.tower_ir_cert_p2557 import tower_ir_cert_p2557


def test_tower_ir_cert_p2557_owner_beta_control_room():
    cert = tower_ir_cert_p2557()

    assert cert["pack"] == 2557
    assert cert["title"] == "Beta blocker tracker"
    assert cert["status"] == "passed"
    assert cert["owner_beta_control_room_ready"] is True
    assert cert["staging_ready_for_owner_beta_walkthrough"] is True
    assert cert["dangerous_controls_locked"] is True

    controls = cert["dangerous_controls"]
    assert controls["production_deployment"] is False
    assert controls["broker_submission"] is False
    assert controls["capital_movement"] is False
    assert controls["manual_live_authorized"] is False
    assert controls["live_auto_authorized"] is False
    assert controls["direct_vault_write"] is False
    assert controls["destructive_action_unlocked"] is False
    assert controls["public_launch_authorized"] is False
