from tower.tower_ir_cert_p2411 import (
    build_protected_launch_evidence_bundle,
)
from tower.tower_ir_cert_p2412 import PINNED_VERSIONS
from tower.tower_ir_cert_p2413 import (
    build_six_room_certification_matrix,
)
from tower.tower_ir_cert_p2415 import (
    create_safety_boundary_attestation,
)
from tower.tower_ir_cert_p2416 import (
    build_owner_acceptance_decision_draft,
)
from tower.tower_ir_cert_p2417 import (
    create_owner_acceptance_receipt,
)
from tower.tower_ir_cert_p2418 import (
    create_certification_seal,
    verify_certification_seal,
)


def test_pack_2418_certification_seal():
    draft = build_owner_acceptance_decision_draft()

    acceptance = create_owner_acceptance_receipt(
        owner_id="owner_1",
        decision_draft=draft,
        owner_decision="accept_preview_contract",
        decided_at="2026-07-14T14:00:00+00:00",
    )

    seal = create_certification_seal(
        evidence_bundle=(
            build_protected_launch_evidence_bundle()
        ),
        contract_versions=dict(PINNED_VERSIONS),
        certification_matrix=(
            build_six_room_certification_matrix()
        ),
        safety_attestation=(
            create_safety_boundary_attestation()
        ),
        owner_acceptance_receipt=acceptance,
    )

    verification = verify_certification_seal(seal)

    assert seal["seal_valid"] is True
    assert verification["valid"] is True
