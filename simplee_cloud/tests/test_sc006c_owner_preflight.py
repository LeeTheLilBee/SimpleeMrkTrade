"""No-live owner preflight renderer regression tests."""
import json
import subprocess
import sys

from simplee_cloud.owner_preflight import (
    owner_preflight_json, owner_preflight_markdown,
)
from simplee_cloud.readiness import GATE_IDS


def test_markdown_compact_owner_report_is_explicit_hold_and_scannable():
    report = owner_preflight_markdown()
    assert report.startswith("# Simplee Sovereign Cloud — Owner Release Preflight")
    assert "SOURCE ONLY · NO GO · NO HOSTED RECEIVER" in report
    assert report.count("**State:** Review pending; not independently certified.") == 10
    assert "**Owner:** Tower" in report
    assert "**Owner:** Archive Vault" in report
    assert "**Owner:** Owner" in report
    assert "issue #99" in report
    assert "cannot and does not authorize production" in report
    assert "password" not in report.lower()
    assert "private_key" not in report.lower()


def test_json_representation_keeps_release_controls_closed():
    doc = json.loads(owner_preflight_json())
    assert doc["status"] == "SOURCE_ONLY_NO_GO"
    assert doc["production_authorized"] is False
    assert doc["hosted_receiver_enabled"] is False
    assert doc["independent_certifications"] == 0
    assert doc["release_decision_recorded"] is False
    assert doc["gate_count"] == len(GATE_IDS)
    assert not any(gate["independently_certified"] for gate in doc["gates"])


def test_cli_has_no_external_dependency_or_release_toggle():
    markdown = subprocess.run(
        [sys.executable, "-m", "simplee_cloud.owner_preflight"],
        text=True, capture_output=True, check=True,
    )
    json_result = subprocess.run(
        [sys.executable, "-m", "simplee_cloud.owner_preflight", "--format", "json"],
        text=True, capture_output=True, check=True,
    )
    assert "NO HOSTED RECEIVER" in markdown.stdout
    assert not markdown.stderr
    assert json.loads(json_result.stdout)["production_authorized"] is False
    assert not json_result.stderr
