from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


ROOMS = {
    "web/templates/dashboard.html":
        "dashboard",

    "web/templates/owner_dashboard.html":
        "owner-dashboard",

    "web/templates/market_map.html":
        "market-map",

    "web/templates/symbol_page.html":
        "symbol",

    "web/templates/trade_center.html":
        "trade-center",

    "web/templates/review_center.html":
        "review-center",

    "web/templates/owner_console.html":
        "owner-console",
}


def test_obux028_every_real_room_loads_shared_atmosphere():
    for relative, room in ROOMS.items():
        text = (
            ROOT
            / relative
        ).read_text(
            encoding="utf-8"
        )

        assert "ob/ob_atmosphere.css" in text
        assert f'data-ob-room="{room}"' in text
        assert 'class="ob-sky"' in text
        assert 'data-ob-atmosphere-version="OBUX026-OBUX030"' in text


def test_obux028_room_specific_templates_remain_room_specific():
    assert "dashboardMount" in (
        ROOT
        / "web/templates/dashboard.html"
    ).read_text(
        encoding="utf-8"
    )

    assert "ownerDashboardMount" in (
        ROOT
        / "web/templates/owner_dashboard.html"
    ).read_text(
        encoding="utf-8"
    )

    assert "skyField" in (
        ROOT
        / "web/templates/market_map.html"
    ).read_text(
        encoding="utf-8"
    )

    assert "symbolRoomMount" in (
        ROOT
        / "web/templates/symbol_page.html"
    ).read_text(
        encoding="utf-8"
    )

    assert "tradeCenterMount" in (
        ROOT
        / "web/templates/trade_center.html"
    ).read_text(
        encoding="utf-8"
    )

    assert "reviewCenterMount" in (
        ROOT
        / "web/templates/review_center.html"
    ).read_text(
        encoding="utf-8"
    )

    assert "ownerConsoleMount" in (
        ROOT
        / "web/templates/owner_console.html"
    ).read_text(
        encoding="utf-8"
    )
