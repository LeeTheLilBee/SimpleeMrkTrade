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

        assert f'data-ob-room="{room}"' in text
        if room in ("dashboard", "owner-dashboard"):
            # Modern Dashboard owns the newer celestial theme; V27 stays historical.
            assert "ob_interchangeable_themes.css" in text
            if room == "dashboard":
                assert 'class="ob-sky ob-user-sky"' in text
            else:
                assert 'class="ob-sky"' in text
            assert "ob_atmosphere.css" not in text
        else:
            assert "ob/ob_atmosphere.css" in text
            assert 'class="ob-sky"' in text
            assert "data-ob-atmosphere-version=" in text


def test_obux028_room_specific_templates_remain_room_specific():
    assert 'id="obArrivalRoot"' in (
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

    assert "marketMapSky" in (
        ROOT
        / "web/templates/market_map.html"
    ).read_text(
        encoding="utf-8"
    )

    assert "obSymbolRoom" in (
        ROOT
        / "web/templates/symbol_page.html"
    ).read_text(
        encoding="utf-8"
    )

    assert 'id="obtc-workspace"' in (
        ROOT
        / "web/templates/trade_center.html"
    ).read_text(
        encoding="utf-8"
    )

    assert 'id="reviewHero"' in (
        ROOT
        / "web/templates/review_center.html"
    ).read_text(
        encoding="utf-8"
    )

    assert 'id="oboc-health-grid"' in (
        ROOT
        / "web/templates/owner_console.html"
    ).read_text(
        encoding="utf-8"
    )
