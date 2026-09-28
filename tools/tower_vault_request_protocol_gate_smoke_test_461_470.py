from pathlib import Path
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

module_path = ROOT / "tower" / "vault_request_protocol_gate.py"
data_path = ROOT / "data" / "tower_vault_request_protocol_gate_gp461_470.json"

assert module_path.exists(), "Missing tower/vault_request_protocol_gate.py"
assert data_path.exists(), "Missing data/tower_vault_request_protocol_gate_gp461_470.json"

spec = importlib.util.spec_from_file_location(
    "vault_request_protocol_gate",
    module_path,
)

module = importlib.util.module_from_spec(spec)

# Python 3.12 dataclasses require the module to be registered before exec_module.
sys.modules[spec.name] = module

spec.loader.exec_module(module)

data = json.loads(data_path.read_text(encoding="utf-8"))

assert data["pack_id"] == "GP461-GP470"
assert data["doctrine"]["key_rule"] == "Teller can ask. Tower must decide. Vault only answers Tower."
assert "raw Vault links to Teller" in data["prevented_behaviors"]

packet = module.build_demo_teller_packet(
    requested_output_type="receipt",
    sensitivity_level="sensitive",
)

actor = module.build_demo_actor_context(
    clearance_active=True,
    step_up_active=True,
    owner_approval_active=False,
    sensitive_view_allowed=False,
    role="manager",
)

result = module.evaluate_and_prepare_vault_protocol_request(packet, actor)

assert result["tower_decision"]["allowed"] is True
assert result["tower_decision"]["decision"] in {"allowed", "redacted"}
assert result["vault_protocol_request"] is not None
assert result["vault_protocol_request"]["source_app"] == "tower"
assert result["vault_protocol_request"]["target_app"] == "vault"
assert result["vault_protocol_request"]["vault_answers_tower_only"] is True
assert result["vault_protocol_request"]["teller_direct_vault_access_allowed"] is False
assert result["safe_return_for_teller"]["vault_direct_access_allowed"] is False
assert result["raw_vault_links_included"] is False
assert result["raw_vault_files_included"] is False

no_step_actor = module.build_demo_actor_context(
    clearance_active=True,
    step_up_active=False,
    owner_approval_active=False,
    role="manager",
)

step_result = module.evaluate_and_prepare_vault_protocol_request(packet, no_step_actor)

assert step_result["tower_decision"]["decision"] == "needs_step_up"
assert step_result["vault_protocol_request"] is None
assert step_result["safe_return_for_teller"]["next_teller_action"] == "resolve_tower_requirement"

expired_actor = module.build_demo_actor_context(
    clearance_active=False,
    step_up_active=True,
    owner_approval_active=False,
    role="manager",
)

expired_result = module.evaluate_and_prepare_vault_protocol_request(packet, expired_actor)

assert expired_result["tower_decision"]["decision"] == "expired_clearance"
assert expired_result["vault_protocol_request"] is None

owner_packet = module.build_demo_teller_packet(
    requested_output_type="download",
    sensitivity_level="owner_only",
)

owner_needed_result = module.evaluate_and_prepare_vault_protocol_request(owner_packet, actor)

assert owner_needed_result["tower_decision"]["decision"] == "needs_owner_approval"
assert owner_needed_result["vault_protocol_request"] is None

invalid_packet = dict(packet)
invalid_packet["vault_direct_access_allowed"] = True

invalid_result = module.evaluate_and_prepare_vault_protocol_request(invalid_packet, actor)

assert invalid_result["tower_decision"]["decision"] == "invalid_packet"
assert invalid_result["vault_protocol_request"] is None

try:
    bad_packet = dict(packet)
    bad_packet["raw_file_url"] = "https://example.com/vault/raw-file"
    module.evaluate_and_prepare_vault_protocol_request(bad_packet, actor)
    raise AssertionError("Raw Vault exposure should have been blocked.")
except ValueError:
    pass

readiness = module.get_tower_vault_protocol_gate_readiness()

assert readiness["tower_receives_teller_packets"] is True
assert readiness["tower_validates_teller_packets"] is True
assert readiness["tower_checks_clearance"] is True
assert readiness["tower_checks_step_up"] is True
assert readiness["tower_sets_redaction"] is True
assert readiness["vault_answers_tower_only"] is True
assert readiness["teller_direct_vault_access_allowed"] is False

print("GP461-GP470 SMOKE TEST PASSED")
print("Tower receives Teller packets.")
print("Tower validates identity/role/clearance/step-up/owner approval/redaction requirements.")
print("Tower creates Vault protocol request only when allowed.")
print("Vault still answers Tower only.")
print("No raw Vault links/files are returned to Teller.")
