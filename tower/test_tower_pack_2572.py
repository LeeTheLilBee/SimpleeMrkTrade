from __future__ import annotations

from tower.tower_ir_cert_p2572 import tower_ir_cert_p2572


def test_tower_ir_cert_p2572_owner_beta_route_gate():
    cert = tower_ir_cert_p2572()

    assert cert["pack"] == 2572
    assert cert["title"] == "Merge and deploy readiness cert"
    assert cert["status"] == "passed"
    assert cert["requires_owner_session"] is True
    assert cert["requires_tower_boundary"] is True
    assert cert["route"] == "/tower/owner-beta"
    assert cert["json_route"] == "/tower/owner-beta.json"
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
