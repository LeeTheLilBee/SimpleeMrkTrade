from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Optional
import json


REGISTRY_SCHEMA_VERSION = "OB_CANONICAL_AUTHORITY_REGISTRY_V1"
RECORD_SCHEMA_VERSION = "OB_AUTHORITY_RECORD_V1"
COMPATIBILITY_SCHEMA_VERSION = "OB_AUTHORITY_COMPATIBILITY_PROJECTION_V1"
SERVICE_VERSION = "OBAUTH001_010_OBPOLICY001_010_CANONICAL_AUTHORITY_REGISTRY"

ROOT = Path(__file__).resolve().parents[1]


DENIED_AUTHORITY_CAPABILITIES = (
    "execution_authority",
    "broker_submission",
    "capital_movement",
    "automatic_contract_selection",
    "automatic_execution",
)


REQUIRED_RECORD_FIELDS = {
    "record_schema_version",
    "concept_key",
    "authority_id",
    "status",
    "authority_class",
    "implementation_ref",
    "implementation_role",
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
    "compatibility_adapters",
    "deferred_integrations",
    "execution_authority",
    "broker_submission",
    "capital_movement",
    "automatic_contract_selection",
    "automatic_execution",
}


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def stable_hash(value: Any) -> str:
    return sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()


def _record(
    *,
    concept_key: str,
    authority_id: str,
    authority_class: str,
    implementation_ref: str,
    implementation_role: str,
    owns,
    inputs=(),
    policy_inputs=(),
    triggers=(),
    effects=(),
    state_mutation_scope: str,
    forbidden=(),
    failure_behavior: str,
    explanation: str,
    evidence=(),
    review_visibility: str,
    temporal_validity: str,
    deterministic: bool,
    learning_boundary: str,
    compatibility_adapters=(),
    deferred_integrations=(),
) -> Dict[str, Any]:

    return {
        "record_schema_version":
            RECORD_SCHEMA_VERSION,

        "concept_key":
            concept_key,

        "authority_id":
            authority_id,

        "status":
            "ACTIVE",

        "authority_class":
            authority_class,

        "implementation_ref":
            implementation_ref,

        "implementation_role":
            implementation_role,

        "owns":
            list(owns),

        "inputs":
            list(inputs),

        "policy_inputs":
            list(policy_inputs),

        "allowed_trigger_classes":
            list(triggers),

        "allowed_effects":
            list(effects),

        "state_mutation_scope":
            state_mutation_scope,

        "forbidden_effects":
            list(forbidden),

        "failure_behavior":
            failure_behavior,

        "explanation_contract":
            explanation,

        "evidence_contract":
            list(evidence),

        "review_visibility":
            review_visibility,

        "temporal_validity":
            temporal_validity,

        "deterministic":
            bool(deterministic),

        "learning_boundary":
            learning_boundary,

        "compatibility_adapters":
            list(compatibility_adapters),

        "deferred_integrations":
            list(deferred_integrations),

        "execution_authority":
            False,

        "broker_submission":
            False,

        "capital_movement":
            False,

        "automatic_contract_selection":
            False,

        "automatic_execution":
            False,
    }


ACTIVE_AUTHORITY_RECORDS = {

    "market_candidate_truth":
        _record(
            concept_key="market_candidate_truth",
            authority_id="existing_canonical_engine_feed",
            authority_class="MARKET_TRUTH",
            implementation_ref="web/static/ob/ob_engine_feed_adapter.js",
            implementation_role="READ_ONLY_PROJECTION_OF_EXISTING_ENGINE",
            owns=(
                "source-backed candidate truth emitted by the existing engine",
                "existing candidate score and rank truth",
            ),
            triggers=(
                "canonical engine source refresh",
                "explicit engine-feed read",
            ),
            effects=(
                "project existing source-backed candidate truth",
            ),
            state_mutation_scope="NONE_IN_THIS_REGISTRY",
            forbidden=(
                "second engine creation",
                "market truth invention",
                "account mutation",
                "broker submission",
                "capital movement",
            ),
            failure_behavior=(
                "Missing, stale, or unavailable upstream truth may not be replaced "
                "with invented current truth."
            ),
            explanation=(
                "Downstream consumers retain the upstream source and candidate evidence."
            ),
            evidence=(
                "source-backed engine payload",
                "candidate score",
                "candidate rank",
                "projection metadata",
            ),
            review_visibility=(
                "Review may inspect the market/candidate truth consumed by a decision."
            ),
            temporal_validity=(
                "SOURCE_BOUND; formal provenance and expiry are deferred to OBDATA/OBTIME."
            ),
            deterministic=False,
            learning_boundary=(
                "Learning may evaluate historical candidate quality but may not "
                "silently rewrite live market truth."
            ),
            compatibility_adapters=(
                "web/static/ob/ob_engine_feed_adapter.js",
            ),
            deferred_integrations=(
                "source_provenance",
                "temporal_context",
                "decision_context",
            ),
        ),

    "options_research":
        _record(
            concept_key="options_research",
            authority_id="OB_OPTIONS_RESEARCH_V1",
            authority_class="RESEARCH",
            implementation_ref="web/static/ob/ob_options_research_contract.js",
            implementation_role="SOURCE_BACKED_RESEARCH_PROJECTION",
            owns=(
                "options research projection",
                "research contract evidence presented for owner review",
            ),
            inputs=(
                "existing_canonical_engine_feed",
            ),
            triggers=(
                "explicit symbol research",
                "candidate research refresh",
            ),
            effects=(
                "project source-backed option research evidence",
            ),
            state_mutation_scope="NONE",
            forbidden=(
                "automatic contract selection",
                "owner-selection substitution",
                "fake executable option fallback",
                "broker submission",
                "capital movement",
            ),
            failure_behavior=(
                "Missing option evidence remains missing or unavailable."
            ),
            explanation=(
                "Research explains source-backed contract evidence while the owner "
                "retains contract selection authority."
            ),
            evidence=(
                "research rows",
                "liquidity evidence when available",
                "IV evidence when available",
            ),
            review_visibility=(
                "Review may inspect the research set used by downstream decisions."
            ),
            temporal_validity=(
                "SOURCE_BOUND; formal option freshness is deferred to OBDATA/OBTIME."
            ),
            deterministic=False,
            learning_boundary=(
                "Learning may evaluate research quality but may not auto-select contracts."
            ),
            deferred_integrations=(
                "source_provenance",
                "temporal_context",
                "decision_context",
            ),
        ),

    "account_reconciliation":
        _record(
            concept_key="account_reconciliation",
            authority_id="OB_ENGINE_ACCOUNT_AUTHORITY_V1",
            authority_class="ACCOUNT_SOURCE_RECONCILIATION",
            implementation_ref="web/ob_engine_account_authority.py",
            implementation_role="SEALED_RECONCILIATION_SERVICE",
            owns=(
                "repository account-source role reconciliation",
                "conflict-preserving account projections",
                "position/reporting source-role projections",
            ),
            triggers=(
                "explicit authority-bundle read",
                "repository account-source snapshot change",
            ),
            effects=(
                "report source roles",
                "report agreements",
                "report unresolved conflicts",
            ),
            state_mutation_scope="NONE",
            forbidden=(
                "silent cross-source merge",
                "conflict erasure",
                "fabricated broker reconciliation",
                "broker submission",
                "capital movement",
            ),
            failure_behavior=(
                "UNKNOWN remains UNKNOWN and CONFLICT remains CONFLICT."
            ),
            explanation=(
                "Source-role output identifies durable, projection, and historical "
                "reporting roles and preserves conflicts."
            ),
            evidence=(
                "source registry",
                "source hashes",
                "overlap checks",
                "conflict fields",
                "reconciliation status",
            ),
            review_visibility=(
                "Review may inspect account-source reconciliation evidence."
            ),
            temporal_validity=(
                "SNAPSHOT_BOUND; account identity truth taxonomy is deferred to OBAUTH006-010."
            ),
            deterministic=True,
            learning_boundary=(
                "Learning may inspect reconciliation failures but may not "
                "auto-resolve conflicting account truth."
            ),
            compatibility_adapters=(
                "legacy build_authority_registry(values)",
                "legacy build_authority_bundle()",
            ),
            deferred_integrations=(
                "source_provenance",
                "decision_context",
            ),
        ),

    "owner_operating_profile":
        _record(
            concept_key="owner_operating_profile",
            authority_id="OB_OWNER_OPERATING_PROFILE_V1",
            authority_class="OWNER_POLICY_INPUT",
            implementation_ref="web/ob_owner_operating_profile.py",
            implementation_role="CANONICAL_OWNER_PROFILE_SERVICE",
            owns=(
                "explicit per-account growth objective",
                "explicit per-account owner risk envelope",
                "owner-confirmed operating-profile revisions",
            ),
            triggers=(
                "explicit owner draft",
                "explicit owner confirmation",
                "explicit owner revision",
            ),
            effects=(
                "persist owner-confirmed operating-profile state",
            ),
            state_mutation_scope="OWNER_PROFILE_STORE_ONLY",
            forbidden=(
                "implicit default account",
                "promised return target",
                "market score mutation",
                "broker submission",
                "capital movement",
            ),
            failure_behavior=(
                "No active profile is fabricated without explicit account identity "
                "and required owner confirmation."
            ),
            explanation=(
                "Each active profile identifies account, growth posture, risk envelope, "
                "source, and confirmation state."
            ),
            evidence=(
                "profile fingerprint",
                "account key",
                "growth objective",
                "risk envelope",
                "owner confirmation",
            ),
            review_visibility=(
                "Review may inspect the owner-profile revision governing a decision."
            ),
            temporal_validity=(
                "REVISION_BOUND until explicitly replaced or invalidated."
            ),
            deterministic=True,
            learning_boundary=(
                "Learning may propose profile changes but may not rewrite "
                "owner-confirmed growth or risk settings."
            ),
            deferred_integrations=(
                "decision_context",
            ),
        ),

    "trade_intent":
        _record(
            concept_key="trade_intent",
            authority_id="OB_TRADE_INTENT_V1",
            authority_class="DECISION_LIFECYCLE",
            implementation_ref="web/ob_trade_intent.py",
            implementation_role="CANONICAL_TRADE_INTENT_SERVICE",
            owns=(
                "candidate-to-owner decision lifecycle object",
                "guarded Trade Intent lifecycle transitions",
                "bound decision evidence",
            ),
            inputs=(
                "existing_canonical_engine_feed",
                "OB_OPTIONS_RESEARCH_V1",
            ),
            triggers=(
                "explicit intent creation",
                "explicit guarded lifecycle transition",
                "explicit evidence binding",
            ),
            effects=(
                "persist Trade Intent lifecycle state",
                "bind downstream evidence without mutating market truth",
            ),
            state_mutation_scope="TRADE_INTENT_STORE_ONLY",
            forbidden=(
                "automatic contract selection",
                "broker submission",
                "capital movement",
                "automatic execution",
            ),
            failure_behavior=(
                "Invalid lifecycle transitions fail closed."
            ),
            explanation=(
                "Lifecycle state remains attributable to explicit guarded transitions."
            ),
            evidence=(
                "intent fingerprint",
                "lifecycle state",
                "authority bindings",
                "transition history",
            ),
            review_visibility=(
                "Review may reconstruct the candidate-to-owner decision lifecycle."
            ),
            temporal_validity=(
                "LIFECYCLE_BOUND; explicit decision validity is deferred to OBCTX/OBTIME."
            ),
            deterministic=True,
            learning_boundary=(
                "Learning may evaluate process quality but may not advance "
                "Trade Intent state itself."
            ),
            deferred_integrations=(
                "event_authority",
                "mode_authority",
                "decision_context",
            ),
        ),

    "owner_fit_eligibility":
        _record(
            concept_key="owner_fit_eligibility",
            authority_id="OB_OWNER_FIT_ELIGIBILITY_V1",
            authority_class="OWNER_FIT_DECISION",
            implementation_ref="web/ob_owner_fit_eligibility.py",
            implementation_role="CANONICAL_OWNER_FIT_SERVICE",
            owns=(
                "NOW/WATCH/NOT_YET owner-specific candidate eligibility",
                "owner-fit explanation and evaluation fingerprint",
            ),
            inputs=(
                "OB_TRADE_INTENT_V1",
                "OB_OWNER_OPERATING_PROFILE_V1",
                "OB_EFFECTIVE_POLICY_V1",
                "existing_canonical_engine_feed",
                "OB_OPTIONS_RESEARCH_V1",
            ),
            policy_inputs=(
                "OB_EFFECTIVE_POLICY_V1",
            ),
            triggers=(
                "explicit owner-fit evaluation",
                "re-evaluation after a relevant bound-input change",
            ),
            effects=(
                "emit NOW/WATCH/NOT_YET",
                "produce owner-fit evidence",
            ),
            state_mutation_scope="OWNER_FIT_RESULT_ONLY",
            forbidden=(
                "market truth mutation",
                "market score recalculation",
                "candidate rank recalculation",
                "automatic contract selection",
                "broker submission",
                "capital movement",
                "automatic execution",
            ),
            failure_behavior=(
                "Missing evidence may not be converted into a fabricated pass."
            ),
            explanation=(
                "The result retains hard/deferred reasons, risk checks, growth context, "
                "options evidence, and evaluation fingerprint."
            ),
            evidence=(
                "evaluation fingerprint",
                "risk checks",
                "growth context",
                "option research gate",
                "hard and deferred reasons",
            ),
            review_visibility=(
                "Review may compare fit decision with its bound evidence."
            ),
            temporal_validity=(
                "EVALUATION_BOUND; relevant input changes require re-evaluation."
            ),
            deterministic=True,
            learning_boundary=(
                "Learning may identify fit-calibration patterns but may not silently "
                "widen the owner's risk envelope."
            ),
            compatibility_adapters=(
                "PENDING_OBRISK006_010",
                "PENDING_OBRISK",
            ),
            deferred_integrations=(
                "mode_authority",
                "source_provenance",
                "temporal_context",
                "decision_context",
            ),
        ),

    "proof_demo_account":
        _record(
            concept_key="proof_demo_account",
            authority_id="OB_PROOF_DEMO_ACCOUNT_V1",
            authority_class="SIMULATED_ACCOUNT",
            implementation_ref="web/ob_proof_demo_account.py",
            implementation_role="CANONICAL_SIMULATED_ACCOUNT_SERVICE",
            owns=(
                "proof_demo simulated account state",
                "proof_demo paper-position lifecycle",
                "proof_demo durable simulated history",
            ),
            inputs=(
                "existing_canonical_engine_feed",
                "OB_OWNER_FIT_ELIGIBILITY_V1",
                "OB_OWNER_OPERATING_PROFILE_V1",
            ),
            triggers=(
                "explicit Proof/Demo activation",
                "explicit owner-selected paper open",
                "explicit paper close",
            ),
            effects=(
                "mutate simulated Proof/Demo ledger only",
                "record realized paper P/L",
                "append simulated lifecycle evidence",
            ),
            state_mutation_scope="SIMULATED_PROOF_DEMO_ONLY",
            forbidden=(
                "real capital movement",
                "broker submission",
                "automatic contract selection",
                "live broker value claim",
                "automatic execution",
            ),
            failure_behavior=(
                "Invalid or non-NOW paper opens fail closed and live truth is never fabricated."
            ),
            explanation=(
                "Paper lifecycle remains explicitly simulated and owner-selected."
            ),
            evidence=(
                "activation fingerprint",
                "position fingerprint",
                "event fingerprint",
                "durable simulated state",
            ),
            review_visibility=(
                "Review may inspect the private Proof/Demo lifecycle."
            ),
            temporal_validity=(
                "DURABLE_SIMULATION_STATE with no live freshness claim."
            ),
            deterministic=True,
            learning_boundary=(
                "Learning may evaluate simulated outcomes but may not convert "
                "simulation into live authority."
            ),
            deferred_integrations=(
                "event_authority",
                "mode_authority",
                "decision_context",
            ),
        ),

    "proof_sanitized_scoreboard":
        _record(
            concept_key="proof_sanitized_scoreboard",
            authority_id="OB_PROOF_SANITIZED_SCOREBOARD_V1",
            authority_class="SANITIZED_PROJECTION",
            implementation_ref="web/ob_proof_scoreboard.py",
            implementation_role="PUBLIC_SAFE_AGGREGATE_PROJECTION",
            owns=(
                "aggregate public-safe Proof/Demo scoreboard projection",
            ),
            inputs=(
                "OB_PROOF_DEMO_ACCOUNT_V1",
            ),
            triggers=(
                "explicit scoreboard projection read",
            ),
            effects=(
                "calculate aggregate completed-paper-sample metrics",
                "emit sanitized deterministic projection",
            ),
            state_mutation_scope="NONE",
            forbidden=(
                "source-state mutation",
                "open-position detail exposure",
                "symbol or contract exposure",
                "market truth mutation",
                "broker submission",
                "capital movement",
            ),
            failure_behavior=(
                "No completed samples means no invented performance result."
            ),
            explanation=(
                "Projection explicitly identifies simulated/paper truth and aggregate basis."
            ),
            evidence=(
                "projection fingerprint",
                "sample counts",
                "aggregate realized paper metrics",
                "truth disclosure",
            ),
            review_visibility=(
                "Review may reproduce the sanitized aggregate from private closed samples."
            ),
            temporal_validity=(
                "PROJECTION_BOUND to current durable closed Proof/Demo sample state."
            ),
            deterministic=True,
            learning_boundary=(
                "Scoreboard projection may not alter trading, policy, or learning authority."
            ),
            compatibility_adapters=(
                "PENDING_OBPROOF006_010",
            ),
        ),
}


ACTIVE_AUTHORITY_RECORDS[
    "account_identity_truth_taxonomy"
] = _record(
    concept_key=
        "account_identity_truth_taxonomy",

    authority_id=
        "OB_ACCOUNT_IDENTITY_TRUTH_V1",

    authority_class=
        "ACCOUNT_IDENTITY_TRUTH_TAXONOMY",

    implementation_ref=
        "web/ob_account_identity_truth.py",

    implementation_role=
        "CANONICAL_ACCOUNT_NAMESPACE_AND_TRUTH_CLASSIFICATION",

    owns=(
        "explicit Observatory account identity classification",
        "truth-state taxonomy",
        "truth-origin taxonomy",
        "source-role claim boundaries",
    ),

    inputs=(
        "OB_OWNER_OPERATING_PROFILE_V1",
        "OB_ENGINE_ACCOUNT_AUTHORITY_V1",
    ),

    triggers=(
        "explicit account identity resolution",
        "explicit truth-claim classification",
        "explicit multi-source truth reconciliation",
    ),

    effects=(
        "classify known versus unknown account identity",
        "classify CURRENT/UNKNOWN/CONFLICT/STALE truth state",
        "preserve REPOSITORY_STATE/PROJECTED/HISTORICAL/OWNER_ENTERED/SIMULATED origin",
        "refuse silent cross-source truth synthesis",
    ),

    state_mutation_scope=
        "NONE",

    forbidden=(
        "implicit default account",
        "second account registry",
        "unknown-to-known coercion",
        "conflict auto-resolution",
        "stale-to-current coercion",
        "simulated-to-live coercion",
        "owner-entered-to-source-backed coercion",
        "projection overwrite of operational state",
        "historical reporting overwrite of operational state",
        "live broker truth fabrication",
        "broker submission",
        "capital movement",
        "automatic execution",
    ),

    failure_behavior=(
        "Unknown identities remain UNKNOWN; conflicting claims remain CONFLICT; "
        "stale claims remain STALE; simulated and owner-entered origins retain "
        "their provenance instead of being promoted to live/source truth."
    ),

    explanation=(
        "Every classified claim names the explicit account, source role, truth "
        "state, origin class, permitted claim scope, and reason."
    ),

    evidence=(
        "account identity fingerprint",
        "truth claim fingerprint",
        "truth resolution fingerprint",
        "source role",
        "truth state",
        "origin class",
    ),

    review_visibility=(
        "Review may inspect the exact account identity and truth classification "
        "used by later decisions."
    ),

    temporal_validity=(
        "CLAIM_BOUND; formal source freshness and time expiry remain deferred "
        "to OBDATA/OBTIME."
    ),

    deterministic=
        True,

    learning_boundary=(
        "Learning may identify recurring account/source truth failures but may "
        "not relabel truth classes, resolve conflicts, or promote simulated data."
    ),

    compatibility_adapters=(
        "PENDING_OBAUTH006_010",
        "OB_OWNER_OPERATING_PROFILE_V1.ACCOUNT_REGISTRY",
        "OB_ENGINE_ACCOUNT_AUTHORITY_V1 source roles",
    ),

    deferred_integrations=(
        "source_provenance",
        "temporal_context",
        "decision_context",
    ),
)


ACTIVE_AUTHORITY_RECORDS[
    "effective_policy"
] = _record(
    concept_key=
        "effective_policy",

    authority_id=
        "OB_EFFECTIVE_POLICY_V1",

    authority_class=
        "POLICY_REGISTRY_AND_RESOLVER",

    implementation_ref=
        "web/ob_effective_policy.py",

    implementation_role=
        "CANONICAL_MOST_RESTRICTIVE_EFFECTIVE_POLICY",

    owns=(
        "policy source registry",
        "account-bound effective risk-limit resolution",
        "per-limit winning-layer provenance",
        "effective capability default-deny projection",
    ),

    inputs=(
        "OB_OWNER_OPERATING_PROFILE_V1",
        "OB_ACCOUNT_IDENTITY_TRUTH_V1",
    ),

    policy_inputs=(
        "OB_OWNER_OPERATING_PROFILE_V1",
    ),

    triggers=(
        "explicit effective-policy resolution",
        "owner-profile binding change",
        "authorized restriction-layer change",
    ),

    effects=(
        "resolve lower upper-bounds",
        "resolve higher minimum requirements",
        "resolve FALSE-wins permissions",
        "emit deterministic effective-policy fingerprint",
        "explain every winning policy layer",
    ),

    state_mutation_scope=
        "NONE",

    forbidden=(
        "owner profile mutation",
        "policy widening",
        "silent policy adoption",
        "silent policy persistence",
        "market truth mutation",
        "candidate score mutation",
        "execution authorization",
        "broker submission",
        "capital movement",
        "automatic contract selection",
        "hybrid execution",
        "automatic execution",
    ),

    failure_behavior=(
        "Unknown accounts, missing owner-profile baselines, mixed-account "
        "layers, invalid layer fingerprints, pending authorities, and attempted "
        "policy widening fail closed."
    ),

    explanation=(
        "Every effective limit names its restriction rule, owner-profile "
        "baseline, contributors, winning layers, and whether the result "
        "tightened the owner profile."
    ),

    evidence=(
        "policy fingerprint",
        "policy layer fingerprints",
        "account identity fingerprint",
        "per-limit resolution",
        "effective capability resolution",
        "tightened keys",
    ),

    review_visibility=(
        "Review may reconstruct exactly which policy layers produced every "
        "effective limit used by Owner Fit."
    ),

    temporal_validity=(
        "RESOLUTION_BOUND; source changes require recomputation. Formal time "
        "expiry remains deferred to OBTIME/OBCTX."
    ),

    deterministic=
        True,

    learning_boundary=(
        "Learning may propose stricter policy changes but may not mutate, "
        "adopt, widen, or persist policy without later owner/event authority."
    ),

    compatibility_adapters=(
        "OB_OWNER_OPERATING_PROFILE_V1.most_restrictive_limits",
        "PENDING_OBPOLICY",
    ),

    deferred_integrations=(
        "event_authority",
        "mode_authority",
        "decision_context",
    ),
)


PENDING_AUTHORITY_SLOTS = {

    "event_authority": {
        "authority_id": "PENDING_OBEVENT",
        "planned_pack": "OBEVENT001-010",
        "status": "PENDING",
    },

    "mode_authority": {
        "authority_id": "PENDING_OBMODE",
        "planned_pack": "OBMODE001-010",
        "status": "PENDING",
    },

    "source_provenance": {
        "authority_id": "PENDING_OBDATA011_015",
        "planned_pack": "OBDATA011-015",
        "status": "PENDING",
    },

    "temporal_context": {
        "authority_id": "PENDING_OBTIME",
        "planned_pack": "OBTIME001-010",
        "status": "PENDING",
    },

    "decision_context": {
        "authority_id": "PENDING_OBCTX",
        "planned_pack": "OBCTX001-005",
        "status": "PENDING",
    },
}


RETIRED_AUTHORITY_ALIASES = {
    "PENDING_OBPOLICY":
        "OB_EFFECTIVE_POLICY_V1",

    "PENDING_OBAUTH006_010":
        "OB_ACCOUNT_IDENTITY_TRUTH_V1",

    "PENDING_OBRISK006_010":
        "OB_OWNER_FIT_ELIGIBILITY_V1",

    "PENDING_OBRISK":
        "OB_OWNER_FIT_ELIGIBILITY_V1",

    "PENDING_OBPROOF006_010":
        "OB_PROOF_SANITIZED_SCOREBOARD_V1",
}


LEGACY_KEY_TO_CANONICAL_CONCEPT = {
    "effective_policy":
        "effective_policy",

    "account_identity_truth_taxonomy":
        "account_identity_truth_taxonomy",

    "market_candidate_truth":
        "market_candidate_truth",

    "options_research":
        "options_research",

    "account_operational_state":
        "account_reconciliation",

    "account_snapshot_projection":
        "account_reconciliation",

    "performance_reporting":
        "account_reconciliation",

    "owner_operating_profile":
        "owner_operating_profile",

    "owner_fit_eligibility":
        "owner_fit_eligibility",

    "trade_intent":
        "trade_intent",

    "position_records":
        "account_reconciliation",

    "proof_demo_account":
        "proof_demo_account",

    "proof_sanitized_scoreboard":
        "proof_sanitized_scoreboard",
}


def authority_registry_contract() -> Dict[str, Any]:
    return {
        "schema_version":
            REGISTRY_SCHEMA_VERSION,

        "record_schema_version":
            RECORD_SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "one_canonical_authority_per_concept":
            True,

        "duplicate_active_authority_ids_allowed":
            False,

        "unknown_active_dependencies_allowed":
            False,

        "dependency_cycles_allowed":
            False,

        "pending_slot_may_claim_active":
            False,

        "retired_alias_may_be_canonical":
            False,

        "legacy_registry_frozen":
            True,

        "future_authorities_register_here_only":
            True,

        "registry_grants_execution_authority":
            False,

        "registry_mutates_domain_state":
            False,

        "legacy_registry_role":
            "COMPATIBILITY_PROJECTION",
    }


def declarative_registry() -> Dict[str, Any]:
    return {
        "schema_version":
            REGISTRY_SCHEMA_VERSION,

        "record_schema_version":
            RECORD_SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "authority_records":
            deepcopy(ACTIVE_AUTHORITY_RECORDS),

        "pending_authority_slots":
            deepcopy(PENDING_AUTHORITY_SLOTS),

        "retired_authority_aliases":
            deepcopy(RETIRED_AUTHORITY_ALIASES),

        "legacy_key_to_canonical_concept":
            deepcopy(LEGACY_KEY_TO_CANONICAL_CONCEPT),

        "hard_rules":
            authority_registry_contract(),
    }


def validate_canonical_authority_registry(
    registry: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    source = (
        deepcopy(registry)
        if registry is not None
        else declarative_registry()
    )

    records = source.get(
        "authority_records",
        {},
    )

    pending = source.get(
        "pending_authority_slots",
        {},
    )

    retired = source.get(
        "retired_authority_aliases",
        {},
    )

    errors = []

    if not isinstance(records, dict) or not records:
        errors.append("authority_records_missing")
        records = {}

    authority_to_concept = {}

    for concept_key, record in records.items():

        if not isinstance(record, dict):
            errors.append(
                f"record_not_object:{concept_key}"
            )
            continue

        missing = (
            REQUIRED_RECORD_FIELDS
            -
            set(record)
        )

        for field in sorted(missing):
            errors.append(
                f"missing_field:{concept_key}:{field}"
            )

        if record.get("concept_key") != concept_key:
            errors.append(
                f"concept_key_mismatch:{concept_key}"
            )

        authority_id = str(
            record.get("authority_id") or ""
        ).strip()

        if not authority_id:
            errors.append(
                f"authority_id_missing:{concept_key}"
            )

        elif authority_id.startswith("PENDING_"):
            errors.append(
                f"active_authority_is_pending:{concept_key}:{authority_id}"
            )

        elif authority_id in authority_to_concept:
            errors.append(
                "duplicate_active_authority_id:"
                + authority_id
                + ":"
                + authority_to_concept[authority_id]
                + ":"
                + concept_key
            )

        else:
            authority_to_concept[
                authority_id
            ] = concept_key

        if record.get("status") != "ACTIVE":
            errors.append(
                f"active_record_status_invalid:{concept_key}"
            )

        for field in (
            "owns",
            "inputs",
            "policy_inputs",
            "allowed_trigger_classes",
            "allowed_effects",
            "forbidden_effects",
            "evidence_contract",
            "compatibility_adapters",
            "deferred_integrations",
        ):
            if not isinstance(
                record.get(field),
                list,
            ):
                errors.append(
                    f"field_not_list:{concept_key}:{field}"
                )

        for field in (
            "implementation_ref",
            "implementation_role",
            "state_mutation_scope",
            "failure_behavior",
            "explanation_contract",
            "review_visibility",
            "temporal_validity",
            "learning_boundary",
        ):
            if not str(
                record.get(field) or ""
            ).strip():
                errors.append(
                    f"text_contract_missing:{concept_key}:{field}"
                )

        for field in DENIED_AUTHORITY_CAPABILITIES:
            if record.get(field) is not False:
                errors.append(
                    f"unexpected_authority_grant:{concept_key}:{field}"
                )

    active_ids = set(
        authority_to_concept
    )

    for concept_key, record in records.items():

        if not isinstance(record, dict):
            continue

        for dependency in record.get(
            "inputs",
            [],
        ):
            if dependency not in active_ids:
                errors.append(
                    f"unknown_active_dependency:{concept_key}:{dependency}"
                )

        for policy_input in record.get(
            "policy_inputs",
            [],
        ):
            if policy_input not in active_ids:
                errors.append(
                    f"unknown_policy_input:{concept_key}:{policy_input}"
                )

        for pending_key in record.get(
            "deferred_integrations",
            [],
        ):
            if pending_key not in pending:
                errors.append(
                    f"unknown_pending_integration:{concept_key}:{pending_key}"
                )

    pending_ids = {}

    for slot_key, slot in pending.items():

        if not isinstance(slot, dict):
            errors.append(
                f"pending_slot_not_object:{slot_key}"
            )
            continue

        authority_id = str(
            slot.get("authority_id") or ""
        ).strip()

        if not authority_id.startswith("PENDING_"):
            errors.append(
                f"pending_slot_id_invalid:{slot_key}:{authority_id}"
            )

        if slot.get("status") != "PENDING":
            errors.append(
                f"pending_slot_status_invalid:{slot_key}"
            )

        if authority_id in active_ids:
            errors.append(
                f"pending_collides_with_active:{authority_id}"
            )

        if authority_id in pending_ids:
            errors.append(
                f"duplicate_pending_authority_id:{authority_id}"
            )

        pending_ids[
            authority_id
        ] = slot_key

    for alias, target in retired.items():

        if alias in active_ids:
            errors.append(
                f"retired_alias_is_active:{alias}"
            )

        if target not in active_ids:
            errors.append(
                f"retired_alias_target_unknown:{alias}:{target}"
            )

    graph = {
        authority_id:
            list(
                records[
                    concept_key
                ].get(
                    "inputs",
                    [],
                )
            )
        for authority_id, concept_key
        in authority_to_concept.items()
    }

    visiting = set()
    visited = set()

    def visit(node: str, trail) -> None:

        if node in visiting:
            errors.append(
                "dependency_cycle:"
                + "->".join(
                    list(trail) + [node]
                )
            )
            return

        if node in visited:
            return

        visiting.add(node)

        for dependency in graph.get(
            node,
            [],
        ):
            visit(
                dependency,
                list(trail) + [node],
            )

        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node, [])

    unique_errors = sorted(
        set(errors)
    )

    return {
        "valid":
            not unique_errors,

        "errors":
            unique_errors,

        "active_concept_count":
            len(records),

        "active_authority_count":
            len(active_ids),

        "pending_slot_count":
            len(pending),

        "retired_alias_count":
            len(retired),

        "dependency_cycle_free":
            not any(
                error.startswith(
                    "dependency_cycle:"
                )
                for error in unique_errors
            ),
    }


def runtime_implementation_validation(
    *,
    root: Optional[Path] = None,
) -> Dict[str, Any]:

    base = (
        Path(root)
        if root is not None
        else ROOT
    )

    implementations = {}

    for concept_key, record in (
        ACTIVE_AUTHORITY_RECORDS.items()
    ):
        relative = record[
            "implementation_ref"
        ]

        implementations[
            concept_key
        ] = {
            "implementation_ref":
                relative,

            "present":
                (base / relative).exists(),
        }

    return {
        "all_active_implementation_refs_present":
            all(
                item["present"]
                for item in implementations.values()
            ),

        "implementations":
            implementations,
    }


def build_canonical_authority_registry(
    *,
    root: Optional[Path] = None,
) -> Dict[str, Any]:

    base = declarative_registry()

    validation = (
        validate_canonical_authority_registry(
            base
        )
    )

    if not validation["valid"]:
        raise RuntimeError(
            "Canonical authority registry invalid: "
            + "; ".join(
                validation["errors"]
            )
        )

    return {
        **base,

        "registry_fingerprint":
            stable_hash(base),

        "validation":
            validation,

        "runtime_validation":
            runtime_implementation_validation(
                root=root
            ),
    }


def resolve_authority_reference(
    reference: Any,
) -> Dict[str, Any]:

    ref = (
        ""
        if reference is None
        else str(reference).strip()
    )

    if ref in ACTIVE_AUTHORITY_RECORDS:
        return {
            "resolution":
                "ACTIVE_CONCEPT",

            "reference":
                ref,

            "record":
                deepcopy(
                    ACTIVE_AUTHORITY_RECORDS[
                        ref
                    ]
                ),
        }

    for record in ACTIVE_AUTHORITY_RECORDS.values():
        if record["authority_id"] == ref:
            return {
                "resolution":
                    "ACTIVE_AUTHORITY_ID",

                "reference":
                    ref,

                "record":
                    deepcopy(record),
            }

    if ref in RETIRED_AUTHORITY_ALIASES:

        target = RETIRED_AUTHORITY_ALIASES[
            ref
        ]

        for record in ACTIVE_AUTHORITY_RECORDS.values():

            if record["authority_id"] == target:
                return {
                    "resolution":
                        "RETIRED_ALIAS",

                    "reference":
                        ref,

                    "resolved_authority_id":
                        target,

                    "record":
                        deepcopy(record),
                }

    for slot_key, slot in PENDING_AUTHORITY_SLOTS.items():

        if ref in {
            slot_key,
            slot["authority_id"],
        }:
            return {
                "resolution":
                    "PENDING_SLOT",

                "reference":
                    ref,

                "slot_key":
                    slot_key,

                "slot":
                    deepcopy(slot),
            }

    return {
        "resolution":
            "UNKNOWN",

        "reference":
            ref,

        "record":
            None,
    }


def canonical_record_for_legacy_key(
    legacy_key: Any,
) -> Optional[Dict[str, Any]]:

    key = (
        ""
        if legacy_key is None
        else str(legacy_key).strip()
    )

    concept_key = (
        LEGACY_KEY_TO_CANONICAL_CONCEPT.get(
            key
        )
    )

    if concept_key is None:
        return None

    return deepcopy(
        ACTIVE_AUTHORITY_RECORDS[
            concept_key
        ]
    )


def build_legacy_compatibility_projection(
    *,
    root: Optional[Path] = None,
) -> Dict[str, Any]:

    from web.ob_engine_account_authority import (
        build_authority_registry as build_legacy_registry,
        build_source_registry,
    )

    base = (
        Path(root)
        if root is not None
        else ROOT
    )

    _, values = build_source_registry(
        root=base
    )

    legacy = build_legacy_registry(
        values
    )

    return {
        "schema_version":
            COMPATIBILITY_SCHEMA_VERSION,

        "role":
            "COMPATIBILITY_PROJECTION",

        "canonical_successor":
            REGISTRY_SCHEMA_VERSION,

        "legacy_registry_frozen":
            True,

        "future_authorities_register_in":
            REGISTRY_SCHEMA_VERSION,

        "legacy_registry":
            legacy,

        "retired_alias_resolutions": {
            alias:
                resolve_authority_reference(alias)
            for alias
            in RETIRED_AUTHORITY_ALIASES
        },
    }
