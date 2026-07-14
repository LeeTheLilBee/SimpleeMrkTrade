from tower.tower_ir_cert_p2416 import (
    build_owner_acceptance_decision_draft,
)


def test_pack_2416_owner_decision_draft():
    draft = build_owner_acceptance_decision_draft()

    assert draft["acceptable"] is True
    assert draft["decision"] == (
        "ACCEPT_PREVIEW_CONTRACT"
    )
    assert all(draft["checks"].values())
    assert draft["owner_acceptance_applied"] is False
    assert draft["production_authorization_granted"] is False
