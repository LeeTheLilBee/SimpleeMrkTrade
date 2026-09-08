from __future__ import annotations

from web.ob_authority_registry import (
    ACTIVE_AUTHORITY_RECORDS,
    LEGACY_KEY_TO_CANONICAL_CONCEPT,
    PENDING_AUTHORITY_SLOTS,
    REGISTRY_SCHEMA_VERSION,
    authority_registry_contract,
    build_canonical_authority_registry,
    build_legacy_compatibility_projection,
    canonical_record_for_legacy_key,
    declarative_registry,
    resolve_authority_reference,
    validate_canonical_authority_registry,
)


def test_registry_contract_is_declarative_and_nonexecuting():

    contract = authority_registry_contract()

    assert (
        contract["schema_version"]
        ==
        "OB_CANONICAL_AUTHORITY_REGISTRY_V1"
    )

    assert (
        contract["one_canonical_authority_per_concept"]
        is True
    )

    assert (
        contract["duplicate_active_authority_ids_allowed"]
        is False
    )

    assert (
        contract["unknown_active_dependencies_allowed"]
        is False
    )

    assert (
        contract["dependency_cycles_allowed"]
        is False
    )

    assert (
        contract["legacy_registry_frozen"]
        is True
    )

    assert (
        contract["future_authorities_register_here_only"]
        is True
    )

    assert (
        contract["registry_grants_execution_authority"]
        is False
    )

    assert (
        contract["registry_mutates_domain_state"]
        is False
    )


def test_exact_current_active_authorities_are_registered():

    registry = build_canonical_authority_registry()

    expected = {
        "market_candidate_truth":
            "existing_canonical_engine_feed",

        "options_research":
            "OB_OPTIONS_RESEARCH_V1",

        "account_reconciliation":
            "OB_ENGINE_ACCOUNT_AUTHORITY_V1",

        "account_identity_truth_taxonomy":
            "OB_ACCOUNT_IDENTITY_TRUTH_V1",

        "owner_operating_profile":
            "OB_OWNER_OPERATING_PROFILE_V1",

        "effective_policy":
            "OB_EFFECTIVE_POLICY_V1",

        "event_authority":
            "OB_COMMAND_EVENT_CAUSAL_V1",

        "trade_intent":
            "OB_TRADE_INTENT_V1",

        "owner_fit_eligibility":
            "OB_OWNER_FIT_ELIGIBILITY_V1",

        "proof_demo_account":
            "OB_PROOF_DEMO_ACCOUNT_V1",

        "proof_sanitized_scoreboard":
            "OB_PROOF_SANITIZED_SCOREBOARD_V1",
    }

    actual = {
        concept:
            record["authority_id"]
        for concept, record
        in registry["authority_records"].items()
    }

    assert actual == expected


def test_active_authority_ids_are_unique_and_not_pending():

    registry = build_canonical_authority_registry()

    ids = [
        record["authority_id"]
        for record
        in registry["authority_records"].values()
    ]

    assert len(ids) == len(set(ids))

    assert not any(
        item.startswith("PENDING_")
        for item in ids
    )


def test_every_active_record_declares_complete_authority_boundary():

    registry = build_canonical_authority_registry()

    required = {
        "concept_key",
        "authority_id",
        "owns",
        "inputs",
        "policy_inputs",
        "allowed_trigger_classes",
        "allowed_effects",
        "state_mutation_scope",
        "forbidden_effects",
        "failure_behavior",
        "explanation_contract",
        "evidence_contract",
        "review_visibility",
        "temporal_validity",
        "deterministic",
        "learning_boundary",
        "deferred_integrations",
    }

    for concept, record in (
        registry["authority_records"].items()
    ):

        assert required <= set(record)

        assert record["concept_key"] == concept
        assert record["owns"]
        assert record["allowed_trigger_classes"]
        assert record["allowed_effects"]
        assert record["forbidden_effects"]
        assert record["failure_behavior"]
        assert record["explanation_contract"]
        assert record["evidence_contract"]
        assert record["review_visibility"]
        assert record["temporal_validity"]
        assert record["learning_boundary"]


def test_dependency_graph_is_valid_and_cycle_free():

    registry = build_canonical_authority_registry()

    validation = registry["validation"]

    assert validation["valid"] is True
    assert validation["errors"] == []
    assert validation["dependency_cycle_free"] is True


def test_registry_grants_no_execution_or_money_authority():

    registry = build_canonical_authority_registry()

    for record in registry["authority_records"].values():

        assert record["execution_authority"] is False
        assert record["broker_submission"] is False
        assert record["capital_movement"] is False
        assert record["automatic_contract_selection"] is False
        assert record["automatic_execution"] is False


def test_historical_owner_fit_aliases_resolve_without_rewriting_history():

    for alias in (
        "PENDING_OBRISK006_010",
        "PENDING_OBRISK",
    ):

        resolution = resolve_authority_reference(
            alias
        )

        assert (
            resolution["resolution"]
            ==
            "RETIRED_ALIAS"
        )

        assert (
            resolution["resolved_authority_id"]
            ==
            "OB_OWNER_FIT_ELIGIBILITY_V1"
        )


def test_historical_proof_scoreboard_alias_resolves():

    resolution = resolve_authority_reference(
        "PENDING_OBPROOF006_010"
    )

    assert (
        resolution["resolution"]
        ==
        "RETIRED_ALIAS"
    )

    assert (
        resolution["resolved_authority_id"]
        ==
        "OB_PROOF_SANITIZED_SCOREBOARD_V1"
    )


def test_future_foundation_slots_are_explicitly_pending():

    expected = {
        "mode_authority",
        "source_provenance",
        "temporal_context",
        "decision_context",
    }

    assert set(PENDING_AUTHORITY_SLOTS) == expected

    active_ids = {
        record["authority_id"]
        for record
        in ACTIVE_AUTHORITY_RECORDS.values()
    }

    for slot_key, slot in PENDING_AUTHORITY_SLOTS.items():

        assert slot["status"] == "PENDING"

        assert slot["authority_id"].startswith(
            "PENDING_"
        )

        assert slot["authority_id"] not in active_ids

        assert (
            resolve_authority_reference(
                slot_key
            )["resolution"]
            ==
            "PENDING_SLOT"
        )


def test_registry_fingerprint_is_deterministic():

    first = build_canonical_authority_registry()
    second = build_canonical_authority_registry()

    assert (
        first["registry_fingerprint"]
        ==
        second["registry_fingerprint"]
    )


def test_registry_returns_copies_not_mutable_global_truth():

    first = build_canonical_authority_registry()

    first["authority_records"][
        "owner_fit_eligibility"
    ]["authority_id"] = "CORRUPTED"

    second = build_canonical_authority_registry()

    assert (
        second["authority_records"][
            "owner_fit_eligibility"
        ]["authority_id"]
        ==
        "OB_OWNER_FIT_ELIGIBILITY_V1"
    )


def test_all_registered_implementation_refs_exist():

    registry = build_canonical_authority_registry()

    runtime = registry["runtime_validation"]

    assert (
        runtime["all_active_implementation_refs_present"]
        is True
    )

    assert all(
        item["present"] is True
        for item
        in runtime["implementations"].values()
    )


def test_legacy_registry_is_compatibility_projection_only():

    projection = build_legacy_compatibility_projection()

    assert (
        projection["role"]
        ==
        "COMPATIBILITY_PROJECTION"
    )

    assert (
        projection["canonical_successor"]
        ==
        REGISTRY_SCHEMA_VERSION
    )

    assert projection["legacy_registry_frozen"] is True

    legacy = projection["legacy_registry"]

    assert (
        legacy["owner_fit_eligibility"]["authority"]
        ==
        "OB_OWNER_FIT_ELIGIBILITY_V1"
    )

    assert (
        legacy["proof_demo_account"]["authority"]
        ==
        "OB_PROOF_DEMO_ACCOUNT_V1"
    )

    assert (
        legacy["proof_sanitized_scoreboard"]["authority"]
        ==
        "OB_PROOF_SANITIZED_SCOREBOARD_V1"
    )

    # Historical compatibility values remain exactly historical.
    assert (
        legacy["owner_operating_profile"]["owner_fit_authority"]
        ==
        "PENDING_OBRISK006_010"
    )

    assert (
        legacy["trade_intent"]["owner_fit_authority"]
        ==
        "PENDING_OBRISK"
    )


def test_every_known_legacy_key_maps_to_canonical_concept():

    for legacy_key, concept in (
        LEGACY_KEY_TO_CANONICAL_CONCEPT.items()
    ):

        record = canonical_record_for_legacy_key(
            legacy_key
        )

        assert record is not None
        assert record["concept_key"] == concept


def test_validation_rejects_duplicate_active_authority():

    broken = declarative_registry()

    broken["authority_records"][
        "proof_demo_account"
    ]["authority_id"] = (
        broken["authority_records"][
            "owner_fit_eligibility"
        ]["authority_id"]
    )

    validation = validate_canonical_authority_registry(
        broken
    )

    assert validation["valid"] is False

    assert any(
        error.startswith(
            "duplicate_active_authority_id:"
        )
        for error in validation["errors"]
    )


def test_validation_rejects_unknown_dependency():

    broken = declarative_registry()

    broken["authority_records"][
        "trade_intent"
    ]["inputs"].append(
        "OB_FAKE_AUTHORITY_V1"
    )

    validation = validate_canonical_authority_registry(
        broken
    )

    assert validation["valid"] is False

    assert any(
        error.startswith(
            "unknown_active_dependency:"
        )
        for error in validation["errors"]
    )


def test_validation_rejects_execution_grant():

    broken = declarative_registry()

    broken["authority_records"][
        "owner_fit_eligibility"
    ]["broker_submission"] = True

    validation = validate_canonical_authority_registry(
        broken
    )

    assert validation["valid"] is False

    assert any(
        error.startswith(
            "unexpected_authority_grant:"
        )
        for error in validation["errors"]
    )
