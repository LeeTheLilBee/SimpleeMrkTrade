from __future__ import annotations

from tower.tower_ir_cert_p2591 import tower_ir_cert_p2591


def test_tower_ir_cert_p2591_walkthrough_closeout():
    cert = tower_ir_cert_p2591()

    assert cert["pack"] == 2591
    assert cert["title"] == "Owner decision packet"
    assert cert["status"] == "passed"
    assert cert["requires_owner_session"] is True
    assert cert["tester_entry_open"] is False
    assert cert["tester_invites_sent"] is False
    assert cert["external_accounts_created"] is False
    assert cert["dangerous_controls_locked"] is True

    routes = cert["routes"]
    assert routes["closeout"] == "/tower/owner-beta/closeout.json"
    assert routes["tester_entry_prep"] == "/tower/owner-beta/tester-entry-prep.json"

    controls = cert["dangerous_controls"]
    assert controls["production_deployment"] is False
    assert controls["broker_submission"] is False
    assert controls["capital_movement"] is False
    assert controls["manual_live_authorized"] is False
    assert controls["live_auto_authorized"] is False
    assert controls["direct_vault_write"] is False
    assert controls["destructive_action_unlocked"] is False
    assert controls["public_launch_authorized"] is False
    assert controls["tester_invites_sent"] is False
    assert controls["external_accounts_created"] is False
