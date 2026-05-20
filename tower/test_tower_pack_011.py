# =============================================================================
# THE_TOWER_FOUNDATION_PACK_011_TEST
# FILE: tower/test_tower_pack_011.py
# =============================================================================

import json

from tower.object_access import CLASS_CONFIDENTIAL, CLASS_TRUST_INTERNAL
from tower.redaction import (
    classify_record,
    redact_and_audit,
    redact_record,
)
from tower.tower_seed import seed_tower_users
from tower.user_store import get_user


def pretty(title, payload):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    seed_tower_users()

    owner = get_user("owner_solice")
    beta = get_user("beta_001")

    sample_record = {
        "object_id": "sample_trade_001",
        "object_type": "trade_record",
        "app_name": "observatory",
        "classification": "confidential",
        "title": "Sample Trade Record",
        "symbol": "AAPL",
        "status": "paper",
        "email": "beta@example.com",
        "strategy_core": "secret internal strategy logic",
        "raw_signal_payload": {
            "internal_score": 91,
            "reason": "technical setup",
            "broker_token": "SHOULD_NOT_SHOW",
        },
        "session_id": "session_abc",
        "device_fingerprint": "device_secret",
        "admin_notes": "Admin-only review note",
        "public_summary": "This is a safe summary.",
    }

    pretty("CLASSIFY SAMPLE RECORD", classify_record(sample_record))

    beta_redacted, beta_report = redact_record(
        record=sample_record,
        user=beta,
        classification=CLASS_CONFIDENTIAL,
    )

    pretty("BETA REDACTED RECORD", beta_redacted)
    pretty("BETA REDACTION REPORT", beta_report)

    owner_redacted, owner_report = redact_record(
        record=sample_record,
        user=owner,
        classification=CLASS_CONFIDENTIAL,
    )

    pretty("OWNER REDACTED RECORD", owner_redacted)
    pretty("OWNER REDACTION REPORT", owner_report)

    trust_record = {
        "object_id": "trust_record_001",
        "object_type": "trust_record",
        "classification": "trust_internal",
        "title": "Trust Funding Note",
        "trust_notes": "Internal trust planning details",
        "owner_draw": 1000,
        "public_summary": "Trust-related record exists.",
    }

    pretty(
        "BETA TRUST RECORD REDACT_AND_AUDIT",
        redact_and_audit(
            record=trust_record,
            user=beta,
            classification=CLASS_TRUST_INTERNAL,
            actor_user_id="tower_test",
            app_name="archive_vault",
            object_type="trust_record",
            object_id="trust_record_001",
        ),
    )

    pretty(
        "OWNER TRUST RECORD REDACT_AND_AUDIT",
        redact_and_audit(
            record=trust_record,
            user=owner,
            classification=CLASS_TRUST_INTERNAL,
            actor_user_id="tower_test",
            app_name="archive_vault",
            object_type="trust_record",
            object_id="trust_record_001",
        ),
    )


if __name__ == "__main__":
    run_tests()
