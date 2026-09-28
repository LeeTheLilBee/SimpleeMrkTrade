"""All-room protected Observatory UX integration on the exact Tower branch.

These tests assert what templates and assets will be served; authenticated owner
browser acceptance must still occur after an explicit guarded release.
"""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/"web/templates"
STATIC=ROOT/"web/static/ob"

ROOMS={
  "market_map.html": ("data-ob-room=\"market-map\"","marketMapSky","marketMapFocus","ob_market_map.js"),
  "symbol_page.html": ("data-ob-room=\"symbol\"","obSymbolRoom","symbolSoulaanaSees","ob_symbol_page.js"),
  "trade_center.html": ("data-ob-room=\"trade-center\"","obtc-workspace","obtc-soulaana-drawer","ob_trade_center.js"),
  "review_center.html": ("data-ob-room=\"review-center\"","reviewSummary","reviewHero","ob_review_center.js"),
  "owner_console.html": ("data-ob-room=\"owner-console\"","oboc-health-grid","oboc-source-drawer","ob_owner_console.js"),
  "owner_dashboard.html": ("data-ob-room=\"owner-dashboard\"","ob_owner_dashboard.js","ob_owner_dashboard_contract.js","ob_owner_dashboard_soulaana.js"),
}

def content(name):
    return (WEB/name).read_text(encoding="utf-8")

def test_modern_room_templates_and_cohesive_theme():
    for name, expected in ROOMS.items():
        s=content(name)
        for marker in expected: assert marker in s,(name,marker)
        assert "ob_interchangeable_themes.css" in s,name
        assert "ob_theme_switcher.js" in s,name
        assert "ob_global_session_shell.js" in s,name
        assert "ob_beta_surface_cleanup.js" in s,name
        assert "data-ob-room=" in s,name
        assert "data-ob-atmosphere-version" in s or name=="owner_dashboard.html"

def test_living_market_sky_is_source_bound_and_original():
    s=content("market_map.html")
    for x in ('data-ob-living-sky="obux096-110"','id="marketMapSky"',
              'id="marketMapFocus"','id="marketMapReset"'):
        assert x in s
    js=(STATIC/"ob_market_map.js").read_text()
    assert "function spotlightSymbol" in js
    assert "marketMapContract()" in js
    assert "obEngineFeedAdapterUpdated" in js
    assert "fetch(" not in js
    assert "placeOrder(" not in js
    css=(STATIC/"ob_market_map.css").read_text()
    assert "--sky-void:" in css
    assert "prefers-reduced-motion" in css
    assert "forced-colors" in css
    assert "adobestock" not in css.lower()

def test_trade_and_review_show_product_first_while_legacy_stays_hidden():
    for name, primary, hidden in (
        ("trade_center.html","obtc-workspace","obtc-proof-compatibility"),
        ("review_center.html","reviewHero",None),
        ("owner_console.html","oboc-health-grid","oboc-compatibility"),
    ):
        s=content(name)
        assert primary in s
        if hidden:
            idx=s.find('id="'+hidden+'"')
            assert idx!=-1
            assert "hidden" in s[idx:idx+220],name

def test_owner_access_separate_from_normal_dashboard():
    normal=content("dashboard.html")
    owner=content("owner_dashboard.html")
    assert 'data-ob-dashboard-role="normal"' in normal
    assert 'data-ob-owner-dashboard="false"' in normal
    assert "ob_owner_dashboard.js" not in normal
    assert "ob_owner_dashboard.js" in owner
    assert 'data-ob-owner-dashboard-role="owner-only-active"' in owner

def test_referenced_static_room_assets_are_present():
    for name in ROOMS:
        source=content(name)
        files=set(re.findall(r"(?:filename='ob/|/static/ob/)([A-Za-z0-9_.-]+\.(?:css|js))",source))
        assert files,(name,"none")
        for file in files:
            assert (STATIC/file).is_file(),(name,file)
    for name in ("ob_trade_center_modes.js","ob_trade_center.css",
                 "ob_review_center_projection.js","ob_review_center_obux.css",
                 "ob_owner_console_projection.js","ob_owner_console_obux.css"):
        assert (STATIC/name).is_file(),name


def test_current_owner_cockpit_is_source_guarded_and_does_not_grant_execution():
    contract=(STATIC/"ob_owner_dashboard_contract.js").read_text(encoding="utf-8")
    for marker in ("owner_only:", "capital_lanes_owner_dashboard_only:",
                   "non_owner_capital_lane_delivery:", "sourceLooksVerified",
                   "actual_capital_known:", "verified_snapshot:",
                   "broker_api_enabled:", "broker_order_submission_enabled:",
                   "real_capital_movement_enabled:", "auto_execution_enabled:",
                   "live_auto_locked:"):
        assert marker in contract
    for exact in ("non_owner_capital_lane_delivery:\n        false",
                  "broker_api_enabled:\n        false",
                  "broker_order_submission_enabled:\n        false",
                  "real_capital_movement_enabled:\n        false",
                  "auto_execution_enabled:\n        false",
                  "live_auto_locked:\n        true"):
        assert exact in contract


def test_old_v18_and_v27_chrome_purged_in_owner_console_not_owner_dashboard():
    cleanup=(STATIC/"ob_beta_surface_cleanup.js").read_text(encoding="utf-8")
    assert 'currentRoom() === "Owner Console"' in cleanup
    assert "function shouldPurgeLegacyChrome()" in cleanup
    assert "!shouldPurgeLegacyChrome()" in cleanup
    assert '"#obMissionBar"' in cleanup
    assert '"#obRoomDataPolishPanel"' in cleanup
    assert "isBetaProductSurface() || currentRoom()" in cleanup
    owner=content("owner_dashboard.html")
    assert "ob_owner_dashboard.js" in owner
    assert "ob_mission_accounts.js" not in owner
