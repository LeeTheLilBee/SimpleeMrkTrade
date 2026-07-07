
from pathlib import Path

from vault.owner_share_access_lock_prep_layer_service import (
    LOCKS,
    get_owner_share_access_lock_prep_home,
    get_owner_share_access_lock_prep_readiness_checkpoint,
    get_owner_share_approval_lock_board,
    get_share_eligibility_policy_board,
    get_share_expiration_policy_board,
    get_share_receipt_draft_ledger,
    get_share_recipient_policy_board,
    get_share_route_payload_draft_builder,
    get_share_safety_blocker_board,
    get_share_scope_contract,
    validate_owner_share_access_lock_prep_layer,
)


def test_gp371_380_readiness_checkpoint_passes():
    result = validate_owner_share_access_lock_prep_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Owner share access lock prep layer" in result["readiness_label"]


def test_gp371_380_share_eligibility_candidates_are_owner_only_and_locked():
    board = get_share_eligibility_policy_board()

    assert board["ready"] is True
    assert board["candidate_count"] >= 2
    assert board["all_candidates_owner_only"] is True
    assert board["all_owner_approval_required"] is True
    assert board["no_share_execution_allowed"] is True
    assert board["no_share_links_created"] is True
    assert board["no_external_recipients_granted"] is True

    for item in board["candidates"]:
        assert item["owner_only"] == 1
        assert item["owner_approval_required"] == 1
        assert item["share_execution_allowed"] == 0
        assert item["share_link_created"] == 0
        assert item["external_recipient_granted"] == 0
        assert item["eligibility_state"] == "share_policy_candidate_owner_approval_required_locked"
        assert len(item["packet_hash"]) == 64


def test_gp371_380_share_scope_contract_keeps_execution_locked():
    contract = get_share_scope_contract()

    assert contract["ready"] is True
    assert contract["scope"]["owner_only_share_prep"] is True
    assert contract["scope"]["owner_approval_required"] is True
    assert contract["scope"]["tower_identity_required_for_future_recipient"] is True
    assert contract["scope"]["share_execution_allowed"] is False
    assert contract["scope"]["share_link_creation_allowed"] is False
    assert contract["scope"]["share_token_creation_allowed"] is False
    assert contract["scope"]["external_recipient_grant_allowed"] is False
    assert contract["scope"]["public_access_allowed"] is False
    assert contract["scope"]["beta_access_allowed"] is False
    assert contract["scope"]["download_link_sharing_allowed"] is False
    assert contract["scope"]["raw_file_bytes_returned_by_json"] is False


def test_gp371_380_share_recipient_policy_requires_tower_identity_and_locks_grants():
    board = get_share_recipient_policy_board()

    assert board["ready"] is True
    assert board["recipient_policy_count"] >= 2
    assert board["all_tower_identity_required"] is True
    assert board["all_external_email_locked"] is True
    assert board["all_recipient_grants_locked"] is True
    assert board["all_public_access_locked"] is True
    assert board["all_beta_access_locked"] is True

    for item in board["recipient_policies"]:
        assert item["recipient_policy_state"] == "recipient_policy_draft_locked_tower_identity_required"
        assert item["allowed_recipient_type"] == "future_tower_identity_subject_only"
        assert item["external_email_allowed"] == 0
        assert item["tower_identity_required"] == 1
        assert item["recipient_grant_allowed"] == 0
        assert item["public_access_allowed"] == 0
        assert item["beta_access_allowed"] == 0


def test_gp371_380_owner_share_approval_locks_are_closed():
    board = get_owner_share_approval_lock_board()

    assert board["ready"] is True
    assert board["approval_lock_count"] >= 2
    assert board["all_owner_approval_required"] is True
    assert board["all_approval_recording_locked"] is True
    assert board["all_share_execution_locked"] is True

    for item in board["approval_locks"]:
        assert item["approval_state"] == "owner_share_approval_required_locked"
        assert item["owner_approval_required"] == 1
        assert item["approval_recording_allowed"] == 0
        assert item["share_execution_allowed"] == 0


def test_gp371_380_share_expiration_policy_is_prepared_but_token_locked():
    board = get_share_expiration_policy_board()

    assert board["ready"] is True
    assert board["expiration_policy_count"] >= 2
    assert board["all_one_time_access_required"] is True
    assert board["all_expiration_enforced"] is True
    assert board["all_share_token_creation_locked"] is True
    assert board["all_share_execution_locked"] is True

    for item in board["expiration_policies"]:
        assert item["ttl_seconds"] == 3600
        assert item["max_ttl_seconds"] == 86400
        assert item["one_time_access_required"] == 1
        assert item["expiration_enforced"] == 1
        assert item["share_token_creation_allowed"] == 0
        assert item["share_execution_allowed"] == 0


def test_gp371_380_share_payload_drafts_exclude_link_token_recipient_public_and_body():
    builder = get_share_route_payload_draft_builder()

    assert builder["ready"] is True
    assert builder["payload_draft_count"] >= 2
    assert builder["metadata_only"] is True
    assert builder["share_link_included"] is False
    assert builder["share_token_included"] is False
    assert builder["recipient_access_included"] is False
    assert builder["public_url_included"] is False
    assert builder["file_body_included"] is False

    for payload in builder["payload_drafts"]:
        assert payload["metadata_only"] is True
        assert payload["display"]["share_link"] == "LOCKED"
        assert payload["display"]["share_token"] == "LOCKED"
        assert payload["display"]["recipient_access"] == "LOCKED"
        assert payload["display"]["public_url"] == "LOCKED"
        assert payload["display"]["file_body"] == "LOCKED"
        assert payload["locks"]["share_link_included"] is False
        assert payload["locks"]["share_token_included"] is False
        assert payload["locks"]["recipient_access_included"] is False
        assert payload["locks"]["public_url_included"] is False
        assert payload["locks"]["file_body_included"] is False
        assert len(payload["payload_hash"]) == 64


def test_gp371_380_share_receipts_are_draft_locked():
    ledger = get_share_receipt_draft_ledger()

    assert ledger["ready"] is True
    assert ledger["receipt_draft_count"] >= 2
    assert ledger["all_receipts_draft_locked"] is True
    assert ledger["receipt_finalization_allowed"] is False

    for item in ledger["receipt_drafts"]:
        assert item["receipt_state"] == "share_receipt_draft_locked"
        assert item["finalized"] == 0
        assert item["finalization_allowed"] == 0
        assert len(item["receipt_hash"]) == 64


def test_gp371_380_share_safety_blockers_keep_danger_actions_locked():
    board = get_share_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "share_execution" in blocked_actions
    assert "share_link_creation" in blocked_actions
    assert "share_token_creation" in blocked_actions
    assert "external_recipient_grant" in blocked_actions
    assert "public_access" in blocked_actions
    assert "beta_access" in blocked_actions
    assert "download_link_sharing" in blocked_actions
    assert "raw_file_bytes_json" in blocked_actions
    assert "raw_share_token_exposure" in blocked_actions
    assert "file_delete" in blocked_actions
    assert "file_restore" in blocked_actions
    assert "quarantine_release" in blocked_actions
    assert "external_sync" in blocked_actions


def test_gp371_380_home_exposes_packs_and_locks():
    home = get_owner_share_access_lock_prep_home()

    assert home["ready"] is True
    assert len(home["packs"]) == 10
    assert home["locks"]["share_eligibility_metadata_allowed"] is True
    assert home["locks"]["share_scope_policy_allowed"] is True
    assert home["locks"]["share_recipient_policy_allowed"] is True
    assert home["locks"]["share_execution_allowed"] is False
    assert home["locks"]["share_link_creation_allowed"] is False
    assert home["locks"]["external_recipient_grant_allowed"] is False
    assert home["locks"]["file_share_unlocked"] is False


def test_gp371_380_readiness_declares_next_layer():
    checkpoint = get_owner_share_access_lock_prep_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_controlled_owner_download_ready"] is True
    assert checkpoint["checks"]["share_eligibility_ready"] is True
    assert checkpoint["checks"]["share_execution_locked_on_candidates"] is True
    assert checkpoint["checks"]["share_links_not_created"] is True
    assert checkpoint["checks"]["external_recipients_not_granted"] is True
    assert checkpoint["checks"]["recipient_policy_ready"] is True
    assert checkpoint["checks"]["recipient_grants_locked"] is True
    assert checkpoint["checks"]["share_payloads_metadata_only"] is True
    assert checkpoint["checks"]["share_receipt_drafts_locked"] is True
    assert checkpoint["checks"]["share_execution_still_locked"] is True
    assert checkpoint["checks"]["share_link_creation_still_locked"] is True
    assert checkpoint["checks"]["external_recipient_grant_still_locked"] is True
    assert "CONTROLLED SHARE GRANT EXECUTION" in checkpoint["next_recommended_layer"]


def test_gp371_380_allowed_features_are_share_prep_only():
    assert LOCKS["share_eligibility_metadata_allowed"] is True
    assert LOCKS["share_scope_policy_allowed"] is True
    assert LOCKS["share_recipient_policy_allowed"] is True
    assert LOCKS["owner_share_approval_lock_allowed"] is True
    assert LOCKS["share_expiration_policy_allowed"] is True
    assert LOCKS["share_route_payload_draft_allowed"] is True
    assert LOCKS["share_receipt_draft_allowed"] is True

    assert LOCKS["share_execution_allowed"] is False
    assert LOCKS["share_link_creation_allowed"] is False
    assert LOCKS["share_token_creation_allowed"] is False
    assert LOCKS["external_recipient_grant_allowed"] is False
    assert LOCKS["public_access_unlocked"] is False
    assert LOCKS["beta_access_unlocked"] is False
    assert LOCKS["download_link_sharing_allowed"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_share_token_exposed"] is False
    assert LOCKS["public_url_created"] is False
    assert LOCKS["file_share_unlocked"] is False
    assert LOCKS["file_delete_unlocked"] is False
    assert LOCKS["file_restore_unlocked"] is False
    assert LOCKS["quarantine_release_allowed"] is False
    assert LOCKS["quarantine_object_move_allowed"] is False
    assert LOCKS["public_upload_unlocked"] is False
    assert LOCKS["beta_upload_unlocked"] is False
    assert LOCKS["provider_upload_unlocked"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["external_sync_unlocked"] is False


def test_gp371_380_routes_are_registered_in_web_app_text():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/owner-share-access-lock-prep-layer",
        "/vault/owner-share-access-lock-prep-layer.json",
        "/vault/owner-share-access-lock-prep-shell.json",
        "/vault/share-eligibility-policy-board.json",
        "/vault/share-scope-contract.json",
        "/vault/share-recipient-policy-board.json",
        "/vault/owner-share-approval-lock-board.json",
        "/vault/share-expiration-policy-board.json",
        "/vault/share-route-payload-draft-builder.json",
        "/vault/share-receipt-draft-ledger.json",
        "/vault/share-safety-blocker-board.json",
        "/vault/owner-share-access-lock-prep-readiness-checkpoint.json",
        "/vault/gp371-status.json",
        "/vault/gp380-status.json",
    ]

    for route in required_routes:
        assert route in app_text
