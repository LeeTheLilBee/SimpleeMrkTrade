from pathlib import Path


def test_clouds_rebuild_is_blank_and_ready():
    clouds_root = Path(__file__).resolve().parents[1]

    inherited_services = [
        "clouds_service.py",
        "clouds_app_registry_service.py",
        "clouds_owner_focus_service.py",
        "clouds_app_lane_status_service.py",
        "clouds_today_service.py",
        "clouds_mission_lane_service.py",
    ]

    inherited_tests = [
        f"test_clouds_giant_pack_{pack:03d}.py"
        for pack in range(1, 7)
    ]

    for filename in inherited_services:
        assert not (clouds_root / filename).exists()

    for filename in inherited_tests:
        assert not (clouds_root / filename).exists()

    assert (clouds_root / "__init__.py").exists()
    assert (clouds_root / "README.md").exists()
