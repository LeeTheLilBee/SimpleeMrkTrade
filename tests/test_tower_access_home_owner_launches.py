
from tower.access_home_owner_launches import (
    access_home_owner_launch_summary,
    access_home_owner_launches,
    inject_owner_launch_dock,
)


def test_access_home_owner_shortcuts_expose_only_owner_headquarters():
    launches = access_home_owner_launches()

    assert len(launches) == 1

    launch = launches[0]

    assert launch["launch_id"] == "tower-owner-headquarters"
    assert launch["title"] == "Owner Headquarters"
    assert launch["href"] == "/tower/owner-dashboard"
    assert launch["owner_only"] is True
    assert launch["danger_action"] is False


def test_security_map_is_not_a_primary_access_home_shortcut():
    routes = {
        launch["href"]
        for launch in access_home_owner_launches()
    }

    assert "/tower/owner-dashboard" in routes
    assert "/tower/security-map" not in routes


def test_access_home_owner_summary_is_truthful():
    summary = access_home_owner_launch_summary()

    assert (
        summary["status"]
        == "tower_access_home_owner_launches_truthful"
    )

    assert summary["launch_count"] == 1
    assert summary["all_owner_only"] is True
    assert summary["danger_actions_enabled"] is False
    assert summary["people_authority_state"] == "NOT_CONFIGURED"

    assert summary["live_auto"] == "LOCKED"
    assert summary["broker_execution"] is False
    assert summary["capital_action"] is False


def test_inject_owner_launch_dock_before_body():
    html = (
        "<html><body><main>"
        "Access Home"
        "</main></body></html>"
    )

    enhanced = inject_owner_launch_dock(
        html
    )

    assert "Access Home" in enhanced
    assert "tower-owner-launch-dock" in enhanced
    assert "Owner Headquarters" in enhanced
    assert "/tower/owner-dashboard" in enhanced
    assert "/tower/security-map" not in enhanced

    assert (
        enhanced.index("tower-owner-launch-dock")
        < enhanced.index("</body>")
    )


def test_inject_owner_launch_dock_is_idempotent():
    html = (
        "<html><body><main>"
        "Access Home"
        "</main></body></html>"
    )

    once = inject_owner_launch_dock(
        html
    )

    twice = inject_owner_launch_dock(
        once
    )

    assert once == twice
