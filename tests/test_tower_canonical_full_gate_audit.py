"""TWR-RELEASE001–005: source audit invariants for the canonical Tower branch.

This is a source gate, NOT observed authenticated Render owner acceptance.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FULL = (ROOT / ".github/workflows/tower-ob-obsim-source-compat.yml").read_text()
SYNTAX = (ROOT / ".github/workflows/tower-py311-syntax-seal-twrtest006-010.yml").read_text()
HOSTED = (ROOT / "tower/ob_hosted_owner_rehearsal.py").read_text()
MANIFEST = (ROOT / "web/hosted_tower.py").read_text()


def test_release_001_canonical_push_must_run_blocking_full_suite():
    assert "  push:\n    branches:\n      - tower-hosted-runtime-identity-twr081-085" in FULL
    assert "Full Tower test suite (blocking)" in FULL
    assert "run: python -m pytest -q tests" in FULL
    assert "continue-on-error" not in FULL
    assert "|| true" not in FULL
    assert "source-parity-and-guard:" in FULL


def test_release_002_full_gate_pins_required_independent_sources():
    for path in (
        "receiver-source", "grounds-source", "obai-source",
        "obml-request-source", "source-buybox-pinned",
        "pinned-obml-phase-source",
    ):
        assert f"path: {path}" in FULL
    assert "pip install -r source-buybox-pinned/buybox/requirements.txt" in FULL


def test_release_003_syntax_gate_runs_on_canonical_push():
    assert "  push:\n    branches:" in SYNTAX
    assert "      - tower-hosted-runtime-identity-twr081-085" in SYNTAX
    assert "python -m compileall -q tower web" in SYNTAX


def test_release_004_hosted_owner_rehearsal_stays_explicitly_disabled_by_default():
    assert 'os.environ.get("OB_OWNER_REHEARSAL_HOSTED_ENABLED") == "1"' in HOSTED
    assert 'canonical_origin=os.environ.get("OB_OWNER_REHEARSAL_ORIGIN", "")' in HOSTED
    assert 'source_kind=SourceKind.SYNTHETIC' in HOSTED
    assert '"durable_archive": False' in HOSTED
    assert '"manual_live_grant": False' in HOSTED
    assert '"broker_submission": False' in HOSTED
    assert '"capital_movement": False' in HOSTED


def test_release_005_source_manifest_does_not_certify_owner_walkthrough():
    assert '"actual_owner_login_walkthrough_verified": False' in MANIFEST
    assert '"durable_report_archive": False' in MANIFEST
    assert '"manual_live_clearance": False' in MANIFEST
    assert '"source_runtime_activation_preconditions_met"' in MANIFEST
