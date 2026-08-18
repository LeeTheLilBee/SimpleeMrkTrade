from tower.access_home_owner_launches import (
    access_home_owner_launch_summary,
    access_home_owner_launches,
    inject_owner_launch_dock,
)


def test_access_home_owner_launches_include_owner_dashboard_and_security_map():
    launches = access_home_owner_launches()

    launch_ids = {
        launch["launch_id"]
        for launch in launches
    }

    routes = {
        launch["href"]
        for launch in launches
    }

    assert "tower-owner-dashboard-people-access-desk" in launch_ids
    assert "tower-security-map" in launch_ids

    assert "/tower/owner-dashboard" in routes
    assert "/tower/security-map" in routes


def test_access_home_owner_launches_are_owner_only_and_safe():
    launches = access_home_owner_launches()

    assert launches

    for launch in launches:
        assert launch["owner_only"] is True
        assert launch["danger_action"] is False


def test_access_home_owner_launch_summary_keeps_danger_locks_off():
    summary = access_home_owner_launch_summary()

    assert summary["status"] == "tower_access_home_owner_launches_ready"
    assert summary["launch_count"] == 2
    assert summary["all_owner_only"] is True
    assert summary["danger_actions_enabled"] is False
    assert summary["real_account_creation"] is False
    assert summary["real_invites_sent"] is False
    assert summary["real_access_granted"] is False
    assert summary["live_auto"] == "LOCKED"
    assert summary["broker_execution"] is False
    assert summary["capital_action"] is False


def test_inject_owner_launch_dock_before_body():
    html = "<html><body><main>Access Home</main></body></html>"
    enhanced = inject_owner_launch_dock(html)

    assert "Access Home" in enhanced
    assert "tower-owner-launch-dock" in enhanced
    assert "/tower/owner-dashboard" in enhanced
    assert "/tower/security-map" in enhanced
    assert enhanced.index("tower-owner-launch-dock") < enhanced.index("</body>")


def test_inject_owner_launch_dock_is_idempotent():
    html = "<html><body><main>Access Home</main></body></html>"

    once = inject_owner_launch_dock(html)
    twice = inject_owner_launch_dock(once)

    assert once == twice
    assert twice.count("tower-owner-launch-dock") >= 1
