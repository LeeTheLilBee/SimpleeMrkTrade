from pathlib import Path
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

module_path = ROOT / "tower" / "vault_authorized_view_protocol.py"
data_path = ROOT / "data" / "tower_authorized_view_protocol_gp471_480.json"

assert module_path.exists(), "Missing tower/vault_authorized_view_protocol.py"
assert data_path.exists(), "Missing data/tower_authorized_view_protocol_gp471_480.json"

spec = importlib.util.spec_from_file_location(
    "vault_authorized_view_protocol",
    module_path,
)

module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

data = json.loads(data_path.read_text(encoding="utf-8"))

assert data["pack_id"] == "GP471-GP480"
assert data["doctrine"]["key_rule"] == "Teller can ask. Tower must decide. Vault only answers Tower."
assert "download protocol" in data["not_allowed_here"]
assert "Teller direct Vault access" in data["not_allowed_here"]

gate_result = module.build_demo_gate_result(
    protocol_action="request_authorized_view_prep",
    redaction_required=True,
)

result = module.prepare_tower_authorized_view_protocol(gate_result)

assert result["decision"] == "view_prepared_redacted"
assert result["authorized_view_scope"] is not None
assert result["vault_authorized_view_request"] is not None
assert result["vault_authorized_view_request"]["source_app"] == "tower"
assert result["vault_authorized_view_request"]["target_app"] == "vault"
assert result["vault_authorized_view_request"]["view_only"] is True
assert result["vault_authorized_view_request"]["download_allowed"] is False
assert result["vault_authorized_view_request"]["raw_links_allowed"] is False
assert result["vault_authorized_view_request"]["public_links_allowed"] is False
assert result["vault_authorized_view_request"]["shared_folder_allowed"] is False
assert result["vault_authorized_view_request"]["vault_answers_tower_only"] is True
assert result["vault_authorized_view_request"]["teller_direct_vault_access_allowed"] is False
assert result["safe_return_for_teller"]["vault_direct_access_allowed"] is False
assert result["safe_return_for_teller"]["raw_files_included"] is False
assert result["safe_return_for_teller"]["raw_links_included"] is False
assert result["safe_return_for_teller"]["download_available"] is False
assert result["download_protocol_created"] is False

unredacted_gate_result = module.build_demo_gate_result(
    protocol_action="request_authorized_view_prep",
    redaction_required=False,
)

unredacted_result = module.prepare_tower_authorized_view_protocol(unredacted_gate_result)

assert unredacted_result["decision"] == "view_prepared"
assert unredacted_result["authorized_view_scope"]["redaction_required"] is False
assert unredacted_result["safe_return_for_teller"]["redaction_applied"] is False

blocked_gate_result = dict(gate_result)
blocked_gate_result["vault_protocol_request"] = None

blocked_result = module.prepare_tower_authorized_view_protocol(blocked_gate_result)

assert blocked_result["decision"] == "blocked"
assert blocked_result["vault_authorized_view_request"] is None
assert blocked_result["safe_return_for_teller"]["next_teller_action"] == "resolve_tower_requirement"

download_gate_result = module.build_demo_gate_result(
    protocol_action="request_authorized_download_prep",
    redaction_required=True,
)

download_blocked = module.prepare_tower_authorized_view_protocol(download_gate_result)

assert download_blocked["decision"] == "download_not_allowed_in_view_protocol"
assert download_blocked["vault_authorized_view_request"] is None
assert download_blocked["download_protocol_created"] is False

try:
    bad_gate_result = module.build_demo_gate_result()
    bad_gate_result["vault_protocol_request"]["download_url"] = "https://example.com/raw-download"
    module.prepare_tower_authorized_view_protocol(bad_gate_result)
    raise AssertionError("Raw Vault exposure should have been blocked.")
except ValueError:
    pass

readiness = module.get_tower_authorized_view_protocol_readiness()

assert readiness["tower_prepares_authorized_view_request"] is True
assert readiness["view_only_protocol"] is True
assert readiness["download_protocol_created"] is False
assert readiness["vault_answers_tower_only"] is True
assert readiness["teller_direct_vault_access_allowed"] is False
assert readiness["raw_vault_links_exposed_to_teller"] is False
assert readiness["raw_vault_files_exposed_to_teller"] is False
assert readiness["workflow_safe_return_only"] is True

print("GP471-GP480 SMOKE TEST PASSED")
print("Tower prepares authorized view-only request for Vault.")
print("Vault still answers Tower only.")
print("Teller receives workflow-safe status only.")
print("No raw Vault links/files are exposed.")
print("Download remains blocked for GP481-GP490.")
