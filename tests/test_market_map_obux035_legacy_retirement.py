import ast
from pathlib import Path

from web.app import app


ROOT = Path(__file__).resolve().parents[1]

APP = (
    ROOT / "web/app.py"
).read_text(encoding="utf-8")

TEMPLATE = (
    ROOT / "web/templates/market_map.html"
).read_text(encoding="utf-8")


def function_source(name):
    tree = ast.parse(APP)

    matches = [
        node
        for node in tree.body
        if (
            isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            )
            and
            node.name == name
        )
    ]

    assert len(matches) == 1

    return ast.get_source_segment(
        APP,
        matches[0],
    )


def test_obux035_old_market_map_files_are_deleted():
    assert not (
        ROOT / "web/templates/market_map_v10.html"
    ).exists()

    assert not (
        ROOT / "web/static/ob/ob_market_map_symbol_page.js"
    ).exists()


def test_obux035_bare_market_map_is_redirect_only():
    body = function_source(
        "market_map_page"
    )

    assert '302' in body
    assert '"/ob/market-map"' in body

    assert "render_template" not in body
    assert "get_v2_market_map" not in body
    assert "get_v2_market_map_interactions" not in body
    assert "get_v2_map_layers" not in body


def test_obux035_v10_routes_are_redirect_only():
    body = function_source(
        "ob_market_map_v10"
    )

    assert '302' in body
    assert '"/ob/market-map"' in body

    assert "render_template" not in body
    assert "market_map_v10.html" not in body


def test_obux035_route_aliases_and_canonical_room_coexist():
    rules = {
        rule.rule
        for rule in app.url_map.iter_rules()
    }

    assert "/market-map" in rules
    assert "/market-map-v10" in rules
    assert "/ob/market-map-v10" in rules

    assert "/ob/market-map" in rules


def test_obux035_legacy_aliases_do_not_render_market_map_directly():
    app.config.update(
        TESTING=True,
    )

    client = app.test_client()

    for route in [
        "/market-map",
        "/market-map-v10",
        "/ob/market-map-v10",
    ]:
        response = client.get(
            route,
            follow_redirects=False,
        )

        # Depending on Tower's global route enforcement, a legacy
        # path may be default-denied before its compatibility redirect
        # executes. Either state is safe; direct room rendering is not.
        assert response.status_code in {
            301,
            302,
            303,
            307,
            308,
            401,
            403,
        }

        assert b"Source-backed constellations" not in response.data
        assert b"What the sky means" not in response.data


def test_obux035_canonical_market_map_remains_tower_protected():
    app.config.update(
        TESTING=True,
    )

    response = app.test_client().get(
        "/ob/market-map",
        follow_redirects=False,
    )

    assert response.status_code in {
        301,
        302,
        303,
        307,
        308,
        401,
        403,
    }


def test_obux035_canonical_template_contains_no_legacy_market_fixture():
    assert "Tower Clear" not in TEMPLATE
    assert "ob_market_map_symbol_page.js" not in TEMPLATE
    assert "ob_market_data.js" not in TEMPLATE


def test_obux035_tower_inventory_snapshots_are_preserved():
    inventory_files = [
        ROOT / "tower/data/ob_exposure_mapping_pass.json",
        ROOT / "tower/data/ob_route_coverage_report.json",
        ROOT / "tower/data/security_command_dashboard.json",
    ]

    for path in inventory_files:
        text = path.read_text(
            encoding="utf-8"
        )

        assert "market_map_page" in text
        assert "/market-map" in text
