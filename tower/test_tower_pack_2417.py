from tower.tower_ir_cert_p2416 import (
    build_owner_acceptance_decision_draft,
)
from tower.tower_ir_cert_p2417 import (
    create_owner_acceptance_receipt,
)


def test_pack_2417_preview_acceptance_receipt():
    draft = build_owner_acceptance_decision_draft()

    receipt = create_owner_acceptance_receipt(
        owner_id="owner_1",
        decision_draft=draft,
        owner_decision="accept_preview_contract",
        decided_at="2026-07-14T14:00:00+00:00",
    )

    assert receipt["decision_valid"] is True
    assert receipt["preview_contract_accepted"] is True
    assert receipt["production_authorization_granted"] is False
    assert receipt["manual_live_authorization_granted"] is False
    assert receipt["live_auto_authorization_granted"] is False
