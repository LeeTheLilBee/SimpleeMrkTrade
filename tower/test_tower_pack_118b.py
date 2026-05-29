
import os
import sys
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path("/content/SimpleeMrkTrade_REAL_CLONE")
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def show(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))

from tower.security_command_unified_owner_page import (
    build_unified_owner_security_command_status,
    render_unified_owner_security_command_html,
    write_unified_owner_security_command_html,
)
from tower.ob_route_coverage_report import build_ob_route_coverage_report
from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

status = build_unified_owner_security_command_status(write_html=False)
show("PACK 118B STATUS", {
    "ok": status.get("ok"),
    "status": status.get("status"),
    "readiness_score": status.get("readiness_score"),
    "failed_checks": status.get("failed_checks"),
})

html = render_unified_owner_security_command_html(status)
show("PACK 118B HTML", {
    "html_length": len(html),
    "has_pack116": "PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE" in html,
    "has_pack118": "PACK118_UNIFIED_OWNER_PAGE_INCLUDES_PREFERRED_DESTINATION" in html,
    "has_pack118b": "PACK118B_SAFE_NON_RECURSIVE_RENDERER" in html,
    "has_pack117": "PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_SECTION" in html,
    "has_pack115": "PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_SECTION" in html,
    "has_pack113": "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in html,
})

assert status.get("ok") is True
assert status.get("status") == "passed"
assert status.get("readiness_score") == 100
assert "PACK118B_SAFE_NON_RECURSIVE_RENDERER" in html
assert "PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_SECTION" in html
assert "PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_SECTION" in html
assert "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in html
assert "SHOULD_NOT_SURVIVE" not in html
assert "tower_keycard=" not in html

write_result = write_unified_owner_security_command_html(status)
show("PACK 118B WRITE", write_result)
assert write_result.get("ok") is True

route_report = build_ob_route_coverage_report(write_panel=True)
checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

show("PACK 118B FINAL HEALTH", {
    "route_coverage_pct": route_report.get("coverage_pct"),
    "unguarded_needed_count": route_report.get("unguarded_needed_count"),
    "unguarded_high_risk_count": route_report.get("unguarded_high_risk_count"),
    "checkpoint_status": checkpoint.get("status"),
    "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
})

assert route_report.get("coverage_pct") == 100
assert route_report.get("unguarded_needed_count") == 0
assert route_report.get("unguarded_high_risk_count") == 0
assert checkpoint.get("status") == "passed"
assert checkpoint.get("helper_wrapped_count") == 0

for path in [
    PROJECT_ROOT / "tower/security_command_unified_owner_page.py",
    PROJECT_ROOT / "tower/test_tower_pack_118b.py",
    PROJECT_ROOT / "web/app.py",
]:
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(path)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    show("PY_COMPILE " + str(path), {"returncode": result.returncode, "stderr": result.stderr})
    assert result.returncode == 0

show("PACK 118B RESULT", {
    "pack": "118B",
    "status": "passed",
    "readiness_score": status.get("readiness_score"),
    "route_coverage_pct": route_report.get("coverage_pct"),
    "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
})
