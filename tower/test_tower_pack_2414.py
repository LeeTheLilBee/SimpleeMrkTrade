from tower.tower_ir_cert_p2414 import (
    build_reason_code_coverage,
)


def test_pack_2414_reason_code_coverage():
    coverage = build_reason_code_coverage()

    assert coverage["coverage_complete"] is True
    assert coverage["missing_allow_codes"] == []
    assert coverage["missing_deny_codes"] == []
    assert coverage["unknown_codes_default_deny"] is True
