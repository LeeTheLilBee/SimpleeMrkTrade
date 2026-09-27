"""OBSIM051–055: landing source does not create any hosted simulator authority."""
import ast
from pathlib import Path

from tower.app_registry import route_by_path
from tower.ob_web_route_enforcement import is_approved_ob_web_room

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / "web/ob_local_owner_rehearsal_ui.py"


def test_obsim051_importing_source_only_does_not_export_a_hosted_app():
    tree = ast.parse(LOCAL.read_text())
    top_level_assigns = [
        target.id for node in tree.body
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        for target in (node.targets if isinstance(node, ast.Assign) else (node.target,))
        if isinstance(target, ast.Name)
    ]
    assert "app" not in top_level_assigns
    assert "create_local_owner_rehearsal_app" in LOCAL.read_text()


def test_obsim052_canonical_tower_route_registry_still_denies_unapproved_rehearsal():
    assert not is_approved_ob_web_room("/ob/owner-rehearsal")
    assert route_by_path("/ob/owner-rehearsal") is None
    assert is_approved_ob_web_room("/ob/owner-dashboard")


def test_obsim053_no_existing_hosted_entrypoint_auto_imports_loopback_app():
    # Main has a managed-staging entrypoint; dedicated hosted Tower has
    # web.hosted_tower instead. Require isolation for whichever app exists.
    for path in ("web/app.py", "web/managed_staging.py", "web/hosted_tower.py"):
        candidate = ROOT / path
        if not candidate.exists():
            continue
        body = candidate.read_text(encoding="utf-8")
        assert "ob_local_owner_rehearsal_ui" not in body
        assert "ob_local_owner_rehearsal_web" not in body
    assert "ob_local_owner_rehearsal" not in (
        ROOT / "web/templates/owner_dashboard.html"
    ).read_text()
    assert "ob_local_owner_rehearsal" not in (
        ROOT / "tower/ob_web_route_enforcement.py"
    ).read_text()


def test_obsim054_local_runner_is_bound_to_loopback_and_never_debug():
    runner = (ROOT / "scripts/ob_local_owner_rehearsal_web.py").read_text()
    assert 'app.run(host="127.0.0.1", port=args.port, threaded=False, debug=False, use_reloader=False)' in runner
    assert "0.0.0.0" not in runner
    assert 'SourceKind(args.source_kind)' in runner


def test_obsim055_source_is_not_production_or_broker_release():
    ui = LOCAL.read_text()
    doc = (ROOT / "docs/owner_experience/OBSIM046_050_LOOPBACK_OWNER_WEB_ACCEPTANCE.md").read_text()
    for marker in (
        '"real_manual_live_ready": False',
        '"tower_owner_authenticated_here": False',
        '"source_provider_authenticated": False',
        '"broker_submission": False',
        '"capital_movement": False',
        '"unattended_tick_scheduled": False',
        '"proof_demo_only": True',
    ):
        assert marker in ui
    assert "not hosted Observatory/Tower deployment" in doc
