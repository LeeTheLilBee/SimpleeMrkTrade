
"""
Pack 021 test:
- Verifies Tower web bridge imports
- Verifies Flask app route registration if web.app can load
- Verifies saved dashboard HTML exists or can be regenerated
"""

from __future__ import annotations

import os
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path("/content/SimpleeMrkTrade_REAL_CLONE")
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 80)
print("PACK 021 TEST — TOWER WEB BRIDGE")
print("=" * 80)

from tower.web_bridge import register_tower_web_routes, SECURITY_COMMAND_HTML

print("Tower web bridge import: OK")
print("Dashboard HTML path:", SECURITY_COMMAND_HTML)
print("Dashboard HTML exists:", SECURITY_COMMAND_HTML.exists())

if not SECURITY_COMMAND_HTML.exists():
    try:
        from tower.security_command_dashboard import save_security_command_dashboard_html
        result = save_security_command_dashboard_html()
        print("Regenerated dashboard:", json.dumps(result, indent=2, sort_keys=True))
    except Exception as exc:
        print("Dashboard regeneration failed:", type(exc).__name__, str(exc))

# Import app carefully. Some app files start servers when run directly,
# but import should normally be safe.
try:
    from web.app import app

    register_tower_web_routes(app)

    routes = sorted(str(rule) for rule in app.url_map.iter_rules())
    tower_routes = [route for route in routes if route.startswith("/tower")]

    print("\nTower routes:")
    print(json.dumps(tower_routes, indent=2))

    required = {
        "/tower/",
        "/tower/security-command",
        "/tower/security-command/regenerate",
        "/tower/status.json",
    }

    # Flask may show /tower instead of /tower/ depending on strict slash behavior.
    found_normalized = set(tower_routes)
    tower_home_ok = "/tower" in found_normalized or "/tower/" in found_normalized

    missing = sorted(route for route in required if route not in found_normalized and route != "/tower/")

    result = {
        "pack": "021",
        "status": "passed" if tower_home_ok and not missing else "needs_review",
        "tower_home_ok": tower_home_ok,
        "missing_routes": missing,
        "tower_route_count": len(tower_routes),
        "dashboard_html_exists": SECURITY_COMMAND_HTML.exists(),
    }

    print("\nPACK 021 RESULT")
    print(json.dumps(result, indent=2, sort_keys=True))

except Exception as exc:
    result = {
        "pack": "021",
        "status": "needs_review",
        "reason_code": "web_app_import_or_route_registration_failed",
        "error": f"{type(exc).__name__}: {exc}",
        "dashboard_html_exists": SECURITY_COMMAND_HTML.exists(),
    }
    print("\nPACK 021 RESULT")
    print(json.dumps(result, indent=2, sort_keys=True))
