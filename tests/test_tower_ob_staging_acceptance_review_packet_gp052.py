from ob_owner_experience.tower_ob_staging_acceptance_review_packet import (
    FALSE_FLAGS,
    REVIEW_ITEMS,
    TRUE_FLAGS,
    build_tower_ob_staging_acceptance_review_packet,
    build_tower_ob_staging_acceptance_review_packet_bundle,
    build_tower_ob_staging_acceptance_review_packet_handoff,
    build_tower_ob_staging_acceptance_review_status,
)


def test_gp052_review_packet():
    packet = build_tower_ob_staging_acceptance_review_packet()
    assert packet["gp051_handoff_ready"] is True
    assert packet["staging_ready"] is True
    assert packet["acceptance_review_packet_ready"] is True
    assert packet["review_items"] == list(REVIEW_ITEMS)
    assert packet["review_items_present"] is True
    assert packet["tower_acceptance_required"] is True
    assert packet["tower_acceptance_decision_recorded"] is False
    assert packet["private_beta_access_opened"] is False
    assert packet["tester_credentials_issued"] is False


def test_gp052_status_bundle_handoff():
    status = build_tower_ob_staging_acceptance_review_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_tower_ob_staging_acceptance_review_packet_bundle()
    assert bundle["package"] == "ob_tower_ob_staging_acceptance_review_packet_gp052"
    assert bundle["acceptance_review_packet_ready"] is True
    assert bundle["source_dependency"] == "GP051"
    assert bundle["recommendation"] == "GO_FOR_TOWER_STAGING_ACCEPTANCE_DECISION_GATE"
    assert bundle["release_boundary"]["staging_ready"] is True
    assert bundle["release_boundary"]["tower_acceptance_decision_recorded"] is False

    handoff = build_tower_ob_staging_acceptance_review_packet_handoff()
    assert "Tower acceptance decision is not recorded in this package." in handoff["next_builder_notes"]
