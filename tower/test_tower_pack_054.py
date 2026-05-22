
from __future__ import annotations
import json, os, sys
from pathlib import Path

PROJECT_ROOT = Path("/content/SimpleeMrkTrade_REAL_CLONE")
os.chdir(PROJECT_ROOT)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

for name in list(sys.modules.keys()):
    if name == "tower" or name.startswith("tower.") or name == "web.app":
        sys.modules.pop(name, None)

from tower.ob_privacy_wall_smoke import run_ob_privacy_wall_smoke

def run_tests():
    result = run_ob_privacy_wall_smoke()
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    assert result.get("ok") is True
    assert not result.get("failures")
    for key in [
        "route_guard_allows_owner_blocks_beta_default_denies",
        "object_guard_symbols_trades_exports",
        "mode_guard_survey_paper_live_auto",
        "flask_routes_lock_private_surfaces",
        "exposure_report_loads",
        "no_raw_keycard_leakage",
    ]:
        assert key in result.get("checks", {})
        assert result["checks"][key]["ok"] is True
    print("\nPACK 054 PASSED")

if __name__ == "__main__":
    run_tests()
