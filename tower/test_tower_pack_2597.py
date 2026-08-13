from __future__ import annotations

from tower.tower_ir_cert_p2597 import tower_ir_cert_p2597


def test_tower_ir_cert_p2597_ob_real_surface_route_map():
    cert = tower_ir_cert_p2597()

    assert cert["pack"] == 2597
    assert cert["title"] == "Trade Center route mapping"
    assert cert["status"] == "passed"
    assert cert["route_map_ready"] is True
    assert cert["market_map_allowed"] is True
    assert cert["symbol_amd_allowed"] is True
    assert cert["random_unmapped_denied"] is True
    assert cert["default_deny_preserved"] is True
    assert cert["requires_owner_session"] is True
    assert cert["requires_tower_handoff"] is True
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
