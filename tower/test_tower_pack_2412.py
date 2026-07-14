from tower.tower_ir_cert_p2412 import (
    PINNED_VERSIONS,
    evaluate_contract_compatibility,
)


def test_pack_2412_compatible_versions():
    result = evaluate_contract_compatibility(
        dict(PINNED_VERSIONS)
    )

    assert result["compatible"] is True
    assert result["mismatches"] == []


def test_pack_2412_version_mismatch_default_denied():
    observed = dict(PINNED_VERSIONS)
    observed["room_contract_version"] = "bad-version"

    result = evaluate_contract_compatibility(observed)

    assert result["compatible"] is False
    assert result["reason_code"] == (
        "ob_contract_version_mismatch"
    )
    assert result["default_deny_on_mismatch"] is True
