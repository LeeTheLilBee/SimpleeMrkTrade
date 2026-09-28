"""SC015: one regular full Vault/Cloud PR gate, specialist checks opt-in by path.

The check is pure source text, no PyYAML dependency, no network or billing.
It guards against reintroducing dozens of duplicate full-package PR jobs.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
CONSOLIDATED = WORKFLOWS / "vault-cloud-consolidated-source.yml"


def specialist_workflows():
    return sorted(
        p for p in WORKFLOWS.glob("*.yml")
        if p.name.startswith(("simplee-cloud-", "simplee-sovereign-cloud-"))
    )


def test_historical_specialists_are_still_present_and_self_scoped():
    files = specialist_workflows()
    assert len(files) >= 18
    for path in files:
        content = path.read_text(encoding="utf-8")
        assert "  pull_request:\n    paths:\n" in content, path
        assert "      - 'simplee_cloud/**'" not in content, path
        assert "      - '.github/workflows/" + path.name + "'" in content, path
        assert "    runs-on: ubuntu-latest" in content, path


def test_consolidated_runs_all_current_cloud_and_vault_corridors_and_owner_hold():
    content = CONSOLIDATED.read_text(encoding="utf-8")
    assert content.count("      - 'simplee_cloud/**'") == 2  # PR and vault-dev push
    assert "      - vault-dev\n" in content
    assert "source-only-all-corridors:" in content
    assert "vault/test_canonical_evidence_registry_cloud_ref.py" in content
    assert "vault/test_archival_transaction_journal.py" in content
    assert "vault/test_real_operations_encrypted_storage.py" in content
    assert "tower/test_buybox_evidence_handoff.py" in content
    assert "simplee_cloud/tests" in content
    assert "if: always()" in content
    assert 'python -m simplee_cloud.owner_preflight >> "$GITHUB_STEP_SUMMARY"' in content
    assert "cancel-in-progress: true" in content
    assert "AWS_EC2_METADATA_DISABLED: 'true'" in content


def test_no_broad_cloud_pr_trigger_outside_single_consolidated_gate():
    broad = []
    for path in WORKFLOWS.glob("*.yml"):
        content = path.read_text(encoding="utf-8")
        if "      - 'simplee_cloud/**'" in content:
            broad.append(path.name)
    assert broad == ["vault-cloud-consolidated-source.yml"]


def test_no_production_unlock_in_consolidated_source_workflow():
    content = CONSOLIDATED.read_text(encoding="utf-8")
    for dangerous in (
        "deploy-service", "aws configure", "render deploy", "kubectl apply",
        "secrets.", "workflow_run:", "pull_request_target:",
    ):
        assert dangerous not in content.lower()
    assert "persist-credentials: false" in content
