
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

from tower.ob_privacy_wall_checkpoint import build_ob_privacy_wall_checkpoint

def run_tests():
    checkpoint = build_ob_privacy_wall_checkpoint()
    print(json.dumps(checkpoint, indent=2, sort_keys=True, default=str))
    assert checkpoint.get("ok") is True
    assert checkpoint.get("readiness_score", 0) >= 90
    assert checkpoint.get("smoke_ok") is True
    built = json.dumps(checkpoint.get("built_packs", []), sort_keys=True)
    for pack in ["045", "046", "047", "048", "049", "050", "051", "052", "053", "054"]:
        assert pack in built
    assert "Soulaana:" in checkpoint.get("soulaana_translation", "")
    print("\nPACK 055 PASSED")

if __name__ == "__main__":
    run_tests()
