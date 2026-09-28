"""The view-only half must not accept a protocol request without its Tower decision."""
from __future__ import annotations

from copy import deepcopy
import pytest

from tower.vault_authorized_view_protocol import (
    build_demo_gate_result,
    prepare_tower_authorized_view_protocol,
)


@pytest.mark.parametrize("redacted", [False, True])
def test_valid_bound_tower_gate_can_prepare_only_a_view(redacted):
    result = prepare_tower_authorized_view_protocol(
        build_demo_gate_result(redaction_required=redacted)
    )
    assert result["vault_authorized_view_request"]["view_only"] is True
    assert result["vault_authorized_view_request"]["download_allowed"] is False
    assert result["teller_direct_vault_access_allowed"] is False
    assert result["download_protocol_created"] is False


@pytest.mark.parametrize("mutation", [
    lambda x: x.pop("tower_decision"),
    lambda x: x["tower_decision"].update({"allowed": False}),
    lambda x: x["tower_decision"].update({"decision": "blocked"}),
    lambda x: x["tower_decision"].update({"tower_decision_receipt_id": "other"}),
    lambda x: x["vault_protocol_request"].update({"tower_decision_receipt_id": "other"}),
    lambda x: x["tower_decision"].update({"redaction_required": False}),
    lambda x: x["safe_return_for_teller"].update({"request_id": "other"}),
    lambda x: x["safe_return_for_teller"].update({"tower_decision_receipt_id": "other"}),
])
def test_mismatched_or_forged_tower_gate_never_prepares_vault_view(mutation):
    result = deepcopy(build_demo_gate_result())
    mutation(result)
    with pytest.raises(ValueError, match="Tower gate decision and view request are not bound"):
        prepare_tower_authorized_view_protocol(result)


def test_download_still_has_no_authorized_view_or_download():
    result = prepare_tower_authorized_view_protocol(
        build_demo_gate_result(protocol_action="request_authorized_download_prep")
    )
    assert result["vault_authorized_view_request"] is None
    assert result["download_protocol_created"] is False
    assert result["safe_return_for_teller"]["download_available"] is False
