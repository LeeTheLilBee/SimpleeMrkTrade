from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Optional
import json


REGISTRY_SCHEMA_VERSION = "OB_CANONICAL_AUTHORITY_REGISTRY_V1"
RECORD_SCHEMA_VERSION = "OB_AUTHORITY_RECORD_V1"
COMPATIBILITY_SCHEMA_VERSION = "OB_AUTHORITY_COMPATIBILITY_PROJECTION_V1"
SERVICE_VERSION = "OBAUTH001_010_OBPOLICY001_010_OBEVENT001_010_OBCTX001_005_OBMODE001_010_CAPSIM011_015_OBCAP001_005_CANONICAL_AUTHORITY_REGISTRY"

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
                "OB_OPERATING_MODE_V1",
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
                "OB_OPERATING_MODE_V1",
                "existing_canonical_engine_feed",
                "OB_OPTIONS_RESEARCH_V1",
            ),
            policy_inputs=(
                "OB_EFFECTIVE_POLICY_V1",
                "OB_OPERATING_MODE_V1",
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
                "source_provenance",
                "temporal_context",
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
        "OB_OPERATING_MODE_V1",
        "OB_CAPITAL_POLICY_V1",
    ),

    policy_inputs=(
        "OB_OWNER_OPERATING_PROFILE_V1",
        "OB_OPERATING_MODE_V1",
        "OB_CAPITAL_POLICY_V1",
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
    ),
)


ACTIVE_AUTHORITY_RECORDS[
    "event_authority"
] = _record(
    concept_key=
        "event_authority",

    authority_id=
        "OB_COMMAND_EVENT_CAUSAL_V1",

    authority_class=
        "COMMAND_EVENT_CAUSALITY",

    implementation_ref=
        "web/ob_command_event_authority.py",

    implementation_role=
        "CANONICAL_COMMAND_EVENT_CAUSAL_INVALIDATION_LEDGER",

    owns=(
        "canonical command request envelope",
        "command idempotence and outcome ledger",
        "immutable accepted domain event envelope",
        "correlation and causation chain",
        "dependency-aware invalidation plan",
        "audit replay projection",
    ),

    triggers=(
        "explicit command request",
        "explicit domain-authority rejection",
        "explicit domain-authority accepted change",
    ),

    effects=(
        "persist command request without treating it as truth",
        "record accepted or rejected command outcome",
        "record immutable accepted domain event",
        "derive causal invalidation for structural dependents only",
        "replay durable causal evidence without reapplying domain mutation",
    ),

    state_mutation_scope=
        "COMMAND_EVENT_LEDGER_ONLY",

    forbidden=(
        "domain-state mutation",
        "command request promoted directly to truth",
        "event fabrication without accepted state change",
        "whole-system invalidation",
        "domain-history deletion",
        "owner profile mutation",
        "market truth mutation",
        "candidate score mutation",
        "broker submission",
        "capital movement",
        "automatic contract selection",
        "hybrid execution",
        "automatic execution",
    ),

    failure_behavior=(
        "Unknown target authorities, invalid fingerprints, missing causal parents, "
        "cross-authority acceptance, duplicate conflicting outcomes, and fabricated "
        "accepted events fail closed."
    ),

    explanation=(
        "Every accepted event binds the originating command, target/source authority, "
        "aggregate, before/after state references, correlation ID, causation event, "
        "event fingerprint, and dependency-aware invalidation plan."
    ),

    evidence=(
        "command fingerprint",
        "command outcome",
        "event fingerprint",
        "correlation ID",
        "causation event ID",
        "before and after state references",
        "registry fingerprint",
        "invalidation-plan fingerprint",
        "replay fingerprint",
    ),

    review_visibility=(
        "Review may reconstruct why a domain change occurred, which command caused it, "
        "what downstream authorities became stale/recompute-required, and the complete "
        "causal chain."
    ),

    temporal_validity=(
        "EVENT_IMMUTABLE; invalidation plan is bound to the registry fingerprint "
        "present when the accepted event was recorded."
    ),

    deterministic=
        True,

    learning_boundary=(
        "Learning may analyze causal histories and invalidation quality but may not "
        "invent events, accept commands, mutate domain state, or rewrite accepted history."
    ),

    compatibility_adapters=(
        "OB_TRADE_INTENT_V1 domain-local event history",
        "OB_PROOF_DEMO_ACCOUNT_V1 domain-local simulated event history",
        "OB_OWNER_OPERATING_PROFILE_V1 revision history",
        "PENDING_OBEVENT",
    ),

    deferred_integrations=(
    ),
)



ACTIVE_AUTHORITY_RECORDS[
    "decision_context"
] = _record(
    concept_key=
        "decision_context",

    authority_id=
        "OB_DECISION_CONTEXT_V1",

    authority_class=
        "IMMUTABLE_DECISION_CONTEXT",

    implementation_ref=
        "web/ob_decision_context.py",

    implementation_role=
        "CANONICAL_HASH_BOUND_DECISION_SNAPSHOT",

    owns=(
        "immutable hash-bound snapshot of the authorities and evidence bound to a decision",
        "decision-context fingerprint and reference",
        "explicit future-authority placeholders without fabricated future truth",
        "optional causal event and invalidation lineage snapshot",
    ),

    inputs=(
        "existing_canonical_engine_feed",
        "OB_OPTIONS_RESEARCH_V1",
        "OB_TRADE_INTENT_V1",
        "OB_ACCOUNT_IDENTITY_TRUTH_V1",
        "OB_OWNER_OPERATING_PROFILE_V1",
        "OB_EFFECTIVE_POLICY_V1",
        "OB_OWNER_FIT_ELIGIBILITY_V1",
        "OB_COMMAND_EVENT_CAUSAL_V1",
        "OB_OPERATING_MODE_V1",
    ),

    policy_inputs=(
        "OB_EFFECTIVE_POLICY_V1",
    ),

    triggers=(
        "explicit decision-context construction",
        "explicit creation of a new snapshot after relevant upstream invalidation",
    ),

    effects=(
        "bind source authority snapshots without recalculation",
        "emit deterministic Decision Context fingerprint",
        "emit immutable reviewable decision-context reference",
        "preserve future Mode/Provenance/Time authorities as pending",
    ),

    state_mutation_scope=
        "NONE",

    forbidden=(
        "source-domain mutation",
        "candidate recalculation",
        "market score recalculation",
        "candidate rank recalculation",
        "options research recalculation",
        "owner profile mutation",
        "effective policy recalculation",
        "owner fit recalculation",
        "event-history mutation",
        "future authority fabrication",
        "automatic contract selection",
        "broker submission",
        "capital movement",
        "hybrid execution",
        "automatic execution",
    ),

    failure_behavior=(
        "Missing or mismatched account identity, missing bound fingerprints, invalid Trade Intent "
        "integrity, invalid registry state, cross-account evidence, or fabricated future authority "
        "fails closed and produces no Decision Context."
    ),

    explanation=(
        "Every Decision Context exposes the exact Trade Intent, candidate, research, account, "
        "owner-profile, Effective Policy, Owner Fit, registry, optional causal lineage, and "
        "explicit pending future-authority references that produced the snapshot."
    ),

    evidence=(
        "Decision Context ID",
        "Decision Context fingerprint",
        "authority registry fingerprint",
        "Trade Intent ID and hash",
        "candidate fingerprint",
        "options research fingerprint when available",
        "account identity fingerprint",
        "owner profile ID/revision/hash",
        "Effective Policy fingerprint",
        "Owner Fit evaluation fingerprint",
        "event/invalidation lineage when supplied",
    ),

    review_visibility=(
        "Review may reconstruct exactly what OB knew and which authority revisions were bound "
        "when a decision context was created."
    ),

    temporal_validity=(
        "IMMUTABLE_SNAPSHOT; source freshness remains deferred to OBDATA. "
        "Verified OB_MARKET_TIME_V1 may be bound as immutable temporal context. "
        "Relevant upstream changes require a new Decision Context rather than mutation of history."
    ),

    deterministic=
        True,

    learning_boundary=(
        "Learning may compare historical Decision Context snapshots and outcomes but may not "
        "rewrite a sealed context, change source truth, or fabricate a different historical input."
    ),

    compatibility_adapters=(
        "PENDING_OBCTX",
    ),

    deferred_integrations=(
        "source_provenance",
    ),
)


ACTIVE_AUTHORITY_RECORDS[
    "mode_authority"
] = _record(
    concept_key=
        "mode_authority",

    authority_id=
        "OB_OPERATING_MODE_V1",

    authority_class=
        "ACCOUNT_BOUND_OPERATING_MODE",

    implementation_ref=
        "web/ob_operating_mode.py",

    implementation_role=
        "CANONICAL_ACCOUNT_BOUND_OPERATING_MODE_AUTHORITY",

    owns=(
        "explicit account-bound Observatory operating mode",
        "guarded mode transition state and revision",
        "mode capability matrix",
        "restriction-only MODE_POLICY projection",
        "mode state fingerprint and minimal reference",
    ),

    inputs=(
        "OB_ACCOUNT_IDENTITY_TRUTH_V1",
    ),

    triggers=(
        "explicit owner-authorized initial mode activation",
        "explicit owner-authorized legal mode transition",
    ),

    effects=(
        "persist account-bound operating-mode revision",
        "emit immutable mode-state reference",
        "provide restriction-only mode-policy input",
        "permit downstream Trade Intent and Decision Context mode binding",
    ),

    state_mutation_scope=
        "OPERATING_MODE_STORE_ONLY",

    forbidden=(
        "implicit default mode",
        "global mode leaking across accounts",
        "unknown account activation",
        "Hybrid activation in OBMODE001-010",
        "Automated activation in OBMODE001-010",
        "owner risk-envelope widening",
        "market truth mutation",
        "candidate score mutation",
        "automatic contract selection",
        "broker submission",
        "capital movement",
        "hybrid execution",
        "automatic execution",
    ),

    failure_behavior=(
        "Unknown accounts, missing owner authorization, illegal transitions, "
        "future-locked modes, fingerprint mismatch, and cross-account bindings "
        "fail closed."
    ),

    explanation=(
        "Every Operating Mode state names the explicit account, mode, revision, "
        "owner authorization, capability matrix, previous mode, and fingerprint."
    ),

    evidence=(
        "mode state ID",
        "mode state fingerprint",
        "account identity fingerprint",
        "mode revision",
        "previous mode",
        "owner authorization",
        "restriction-only policy projection",
    ),

    review_visibility=(
        "Review may reconstruct which operating mode governed a decision "
        "without treating mode as execution authority."
    ),

    temporal_validity=(
        "REVISION_BOUND until an explicit owner-authorized mode transition. "
        "Formal market/session time remains deferred to OBTIME."
    ),

    deterministic=
        False,

    learning_boundary=(
        "Learning may evaluate mode outcomes but may not switch mode, unlock "
        "Hybrid/Automated operation, or widen owner policy."
    ),

    compatibility_adapters=(
        "PENDING_OBMODE",
    ),

    deferred_integrations=(
    ),
)


ACTIVE_AUTHORITY_RECORDS[
    "temporal_context"
] = _record(
    concept_key=
        "temporal_context",

    authority_id=
        "OB_MARKET_TIME_V1",

    authority_class=
        "MARKET_TIME_AND_SESSION_AUTHORITY",

    implementation_ref=
        "web/ob_market_time_authority.py",

    implementation_role=
        "CANONICAL_SCHEDULE_BOUND_MARKET_TIME_AUTHORITY",

    owns=(
        "timezone-aware canonical observation time",
        "exchange-local market time",
        "current trading-date derivation",
        "current market-session derivation",
        "calendar-source-bound schedule identity",
        "tamper-evident market-time receipt",
    ),

    triggers=(
        "explicit verified market schedule input",
        "explicit timezone-aware observation instant",
    ),

    effects=(
        "emit canonical market-time receipt",
        "derive market session from schedule",
        "supply canonical time to temporal-validity authority",
        "supply verified time reference to Experimental simulation",
        "supply verified time-context projection to Operating Mode",
    ),

    state_mutation_scope=
        "NONE",

    forbidden=(
        "invent market-open status without schedule authority",
        "hardcode weekday as exchange calendar truth",
        "hardcode holiday calendar as canonical truth",
        "override temporal validity result",
        "override provenance",
        "override freshness",
        "override quality",
        "override lineage",
        "override revocation",
        "trade decision creation",
        "automatic contract selection",
        "broker submission",
        "capital movement",
        "Manual Live unlock",
        "Hybrid unlock",
        "Automated unlock",
    ),

    failure_behavior=(
        "Invalid schedules, naive timestamps, schedule-date mismatch, "
        "receipt tampering, and frame/time disagreement fail closed."
    ),

    explanation=(
        "Canonical market time names UTC time, exchange-local time, trading date, "
        "market session, schedule identity, and calendar-source provenance."
    ),

    evidence=(
        "market-time receipt ID",
        "market-time integrity hash",
        "schedule ID",
        "schedule hash",
        "calendar authority",
        "calendar reference",
        "calendar payload hash",
        "derived trading date",
        "derived market session",
    ),

    review_visibility=(
        "Review may reconstruct the exact schedule-bound time and session "
        "used by temporal reasoning and Experimental simulation."
    ),

    temporal_validity=(
        "RECEIPT_BOUND; each canonical market-time receipt is bound to one "
        "observation instant and one explicit market schedule."
    ),

    deterministic=
        True,

    learning_boundary=(
        "Learning may evaluate historical time/session outcomes but may not "
        "rewrite calendar truth, widen time windows, or create execution authority."
    ),

    compatibility_adapters=(
        "PENDING_OBTIME",
    ),

    deferred_integrations=(
    ),
)



ACTIVE_AUTHORITY_RECORDS[
    "capital_policy"
] = _record(
    concept_key="capital_policy",
    authority_id="OB_CAPITAL_POLICY_V1",
    authority_class="PRE_POLICY_CAPITAL_RESTRICTION",
    implementation_ref="web/ob_capital_policy_authority.py",
    implementation_role="VERIFIED_SIMULATION_ONLY_PRE_POLICY_PROJECTION",
    owns=(
        "hash-bound pre-policy Experimental capital restriction snapshot",
        "verified source-bound simulated capital capacity",
        "restriction-only capital policy layer input",
    ),
    inputs=(
        "OB_OWNER_OPERATING_PROFILE_V1",
        "OB_MARKET_TIME_V1",
    ),
    triggers=(
        "explicit verified owner profile and simulation capital assessment context",
        "explicit verified canonical session-loss evidence",
    ),
    effects=(
        "derive non-widening owner risk limit projection",
        "emit immutable simulation-only capital projection receipt",
        "feed explicit restriction-only CAPITAL_POLICY layer",
    ),
    state_mutation_scope="NONE",
    forbidden=(
        "Effective Policy import or recursive resolution",
        "real capital state claim",
        "unverified ledger promotion",
        "owner limit widening",
        "broker submission",
        "capital movement",
        "Manual Live unlock",
        "Hybrid unlock",
        "Automated unlock",
    ),
    failure_behavior=(
        "Tampered/cross-account evidence, incomplete canonical session loss, "
        "exhausted daily risk, or absent positive capacity fail closed."
    ),
    explanation=(
        "Each pre-policy projection identifies the owner baseline, verified "
        "Experimental capital and session-loss receipts, canonical limits, "
        "capacity factor, state, and hard-block reasons."
    ),
    evidence=(
        "pre-policy projection ID/integrity hash",
        "active owner profile ID/hash",
        "verified simulation capital state ID/hash",
        "verified session-loss ledger ID/hash",
        "canonical six-decimal restriction values",
    ),
    review_visibility=(
        "Review can reconstruct the projection and the restriction-only "
        "Effective Policy layer without treating simulation as real capital."
    ),
    temporal_validity="EVIDENCE_BOUND; new capital/time evidence requires a new projection.",
    deterministic=True,
    learning_boundary=(
        "Learning may inspect simulated capital-defense behavior but may not "
        "relax owner limits, alter account truth, or automatically adopt policy."
    ),
    compatibility_adapters=("PENDING_OBCAP",),
    deferred_integrations=(),
)


ACTIVE_AUTHORITY_RECORDS[
    "capital_truth"
] = _record(
    concept_key="capital_truth",
    authority_id="OB_CAPITAL_TRUTH_V1",
    authority_class="SOURCE_BOUND_CAPITAL_EVIDENCE",
    implementation_ref="web/ob_capital_truth.py",
    implementation_role="CANONICAL_READ_ONLY_CAPITAL_OBSERVATION_AUTHORITY",
    owns=(
        "immutable per-account and per-mission-scope source-labelled capital observations",
        "canonical monetary field truth states with missing distinct from zero",
        "source and source-revision fingerprints and evidence-bound capital snapshot",
    ),
    inputs=("OB_ACCOUNT_IDENTITY_TRUTH_V1",),
    triggers=(
        "explicit account/scope-bound monetary source observation",
        "explicit source freshness or conflict re-evaluation",
    ),
    effects=(
        "emit hash-bound capital observation and snapshot",
        "preserve unknown stale and conflict states without synthetic spendable balances",
        "emit non-money-bearing reference for authorized downstream mediation",
    ),
    state_mutation_scope="NONE",
    forbidden=(
        "second account namespace",
        "synthetic broker verification",
        "owner-entered or projected claim promoted to broker verified",
        "simulation promoted to real capital",
        "inferred settled cash or acquisition spendability",
        "cross-account or cross-scope aggregation",
        "ATM Set 1/Set 2 or protected floor policy rewrite",
        "direct BuyBox integration",
        "broker submission",
        "capital movement",
        "operating mode unlock",
    ),
    failure_behavior=(
        "Missing, unknown, stale, conflicting, unverified or mixed-scope "
        "monetary evidence cannot be treated as externally authenticated or deployable."
    ),
    explanation=(
        "Each monetary field retains source role, source references, value-state "
        "resolution, timestamps, account and capital-scope identity, and origin classes."
    ),
    evidence=(
        "observation IDs and SHA-256 integrity hashes",
        "account identity fingerprint and explicit capital scope",
        "source refs/revisions/payload hashes and observation/receipt/expiry times",
        "canonical integer-cent field states and snapshot fingerprint",
    ),
    review_visibility=(
        "Review and Tower-authorized consumers can inspect provenance and "
        "capital truth states; Teller independently assesses financial readiness."
    ),
    temporal_validity="EXPLICIT_AS_OF_AND_SOURCE_EXPIRY; no live balance implied.",
    deterministic=True,
    learning_boundary=(
        "Learning may compare historical source errors but never relabel evidence, "
        "spend restricted balances, alter floors or grant financial authority."
    ),
    deferred_integrations=("source_provenance",),
)


ACTIVE_AUTHORITY_RECORDS[
    "capital_waterfall"
] = _record(
    concept_key="capital_waterfall",
    authority_id="OB_CAPITAL_WATERFALL_PROJECTION_V1",
    authority_class="READ_ONLY_MISSION_CAPITAL_WATERFALL_REHEARSAL",
    implementation_ref="web/ob_capital_waterfall.py",
    implementation_role="CANONICAL_FOUR_SLEEVE_INDICATIVE_PROJECTION",
    owns=(
        "four isolated ATM Set 1/Set 2 acquisition and operations planning projections",
        "source-bound non-regressive floor and high-water candidates",
        "conditional hypothetical harvest and missing-evidence status",
    ),
    inputs=("OB_CAPITAL_TRUTH_V1",),
    triggers=(
        "explicit owner-confirmed existing plan intent and floor references",
        "four verified account-and-scope-matched capital truth snapshots",
    ),
    effects=(
        "emit tamper-evident indicative waterfall projection",
        "preserve protected floors, commitments, pending distributions and targets",
        "emit non-money-bearing lineage and review statuses",
    ),
    state_mutation_scope="NONE",
    forbidden=(
        "adopt new policy or ratchet without owner approval and external evidence",
        "treat indicative capital as settled spendable acquisition funds",
        "pool ATM Set 1/Set 2 or acquisition/operations",
        "perform harvest or capital movement",
        "issue deployment or financing readiness",
        "direct OB to BuyBox access",
        "broker order or operating mode unlock",
    ),
    failure_behavior=(
        "Missing, stale, conflicting and tampered capital evidence blocks numerical "
        "waterfall claims. No floor widening or readiness fabrication."
    ),
    explanation=(
        "Source snapshot IDs/hashes, owner plan reference, per-sleeve status, "
        "indicative allocation waterfall, and proposed nondecreasing floors/high-water."
    ),
    evidence=(
        "plan receipt/hash and declared owner policy source reference",
        "four canonical capital snapshot IDs/hashes and states",
        "read-only projection ID/hash",
    ),
    review_visibility=(
        "Only non-money-bearing proof reference is eligible for later Tower mediation; "
        "Teller remains the acquisition financing and deployment readiness authority."
    ),
    temporal_validity="FOUR_SNAPSHOT_AS_OF_BOUND; no source freshness inference.",
    deterministic=True,
    learning_boundary=(
        "Learning cannot relax floor, adopt harvest, move capital, or authorize modes."
    ),
    deferred_integrations=(),
)


ACTIVE_AUTHORITY_RECORDS[
    "capital_modes"
] = _record(
    concept_key="capital_modes",
    authority_id="OB_CAPITAL_MODE_REVIEW_V1",
    authority_class="NON_EXECUTING_CAPITAL_MODE_REVIEW",
    implementation_ref="web/ob_capital_modes.py",
    implementation_role="CANONICAL_ADVISORY_SIX_MODE_EVIDENCE_PROJECTION",
    owns=(
        "six advisory capital mode signals without operating-mode mutation",
        "owner-declared threshold and prior-source-bound review receipts",
        "per-sleeve deterministic hysteresis and urgent risk review precedence",
    ),
    inputs=("OB_CAPITAL_WATERFALL_PROJECTION_V1",),
    triggers=(
        "explicit owner-confirmed mode thresholds and sleeve current-mode declaration",
        "verified current four-sleeve waterfall and optional prior advisory receipt",
    ),
    effects=(
        "emit an immutable amount-free-referenceable advisory mode review",
        "preserve insufficient evidence and require consecutive distinct chronological reviews",
        "surface immediate protect-priority candidate without activating a mode",
    ),
    state_mutation_scope="NONE",
    forbidden=(
        "set Observatory Survey/Paper/Manual/Hybrid/Automated mode",
        "automatically change owner capital mode or capital policy",
        "authenticate source values or treat indicative cash as real",
        "move profit harvest, trade, purchase ATM routes or approve financing",
        "direct OB to BuyBox integration or acquisition readiness verdict",
    ),
    failure_behavior=(
        "Missing and conflicting capital evidence yields insufficient-evidence review. "
        "Duplicate, older, cross-policy or tampered review receipts cannot advance hysteresis."
    ),
    explanation=(
        "Each sleeve reports proposed mode, reason, indicative drawdown band, "
        "streak and owner-review state; no permission or readiness follows."
    ),
    evidence=(
        "mode intent receipt/hash, waterfall and source hashes",
        "chronological prior review link and immutable review fingerprint",
        "amount-free reference for future Tower authorization only",
    ),
    review_visibility=(
        "Owner sees advisory candidate; Teller alone evaluates money-side deployment "
        "and BuyBox sees only Tower-authorized Teller readiness."
    ),
    temporal_validity="WATERFALL_AND_CHRONOLOGICAL_REVIEW_BOUND; not a live-mode actuator.",
    deterministic=True,
    learning_boundary=(
        "Learning cannot adopt a mode, widen a protected floor or turn a planning "
        "recommendation into spendable acquisition money."
    ),
    deferred_integrations=(),
)


ACTIVE_AUTHORITY_RECORDS[
    "position_truth"
] = _record(
    concept_key="position_truth",
    authority_id="OB_POSITION_TRUTH_V1",
    authority_class="SOURCE_BOUND_READ_ONLY_POSITION_VIEW",
    implementation_ref="web/ob_position_truth.py",
    implementation_role="CANONICAL_OBSIM_POSITION_RECONCILIATION_AND_OBENG_SOURCE_SUMMARY",
    owns=(
        "per-lane immutable source-backed simulated open-position view",
        "reconciliation to existing OBSIM fill and receipt history",
        "existing OBENG explicit open/closed store count and unresolved source status",
    ),
    inputs=("OB_ENGINE_ACCOUNT_AUTHORITY_V1", "OB_ACCOUNT_IDENTITY_TRUTH_V1"),
    triggers=(
        "explicit source-bound OBSIM lane position projection",
        "explicit repository position-source status inspection",
    ),
    effects=(
        "emit hash-bound per-lane position source view without a new fill engine",
        "refuse synthetic position rows from repository counts or reporting history",
        "preserve simulation and repository provenance without live broker claims",
    ),
    state_mutation_scope="NONE",
    forbidden=(
        "second position or fill ledger",
        "broker authenticated position assertion",
        "treat reporting history as current open positions",
        "promote an unknown/empty repository source into zero positions",
        "cross-lane or cross-account position pooling",
        "direct BuyBox connection or acquisition affordability inference",
        "live order, capital movement or trading-mode unlock",
    ),
    failure_behavior=(
        "Contradictory OBSIM fills/marks/receipts, missing source status, account "
        "mismatch and tampered references fail closed instead of inventing positions."
    ),
    explanation=(
        "Projects exact existing simulation position IDs and OPEN fills and "
        "identifies whether repository open/closed stores are explicit or unresolved."
    ),
    evidence=(
        "account fingerprint, harness and lane references",
        "existing OBSIM trade IDs, receipt chain root and latest frame",
        "canonical immutable position snapshot hash and repository source status",
    ),
    review_visibility=(
        "Owner can distinguish simulated, repository and broker-unverified sources; "
        "Teller alone owns acquisition finance readiness."
    ),
    temporal_validity="EXPLICIT_SOURCE_FRAME_OR_REPOSITORY_REVISION_BOUND",
    deterministic=True,
    learning_boundary=(
        "Learning cannot rewrite source fills, mark missing positions as zero, "
        "or convert simulated positions into live execution authority."
    ),
    deferred_integrations=(),
)


ACTIVE_AUTHORITY_RECORDS[
    "portfolio_view"
] = _record(
    concept_key="portfolio_view",
    authority_id="OB_PORTFOLIO_VIEW_V1",
    authority_class="SOURCE_BOUND_NON_EXECUTING_PORTFOLIO_PROJECTION",
    implementation_ref="web/ob_portfolio_view.py",
    implementation_role="CANONICAL_ISOLATED_THREE_LANE_PORTFOLIO_COMPARISON",
    owns=(
        "one read-only stock/option exposure view per verified OBPOS lane",
        "immutable three-lane comparison without winner selection or pooling",
    ),
    inputs=("OB_POSITION_TRUTH_V1",),
    triggers=("explicit three-lane source-backed portfolio review",),
    effects=(
        "project existing canonical cash/equity and position exposure without new fill math",
        "emit integrity-bound non-money-bearing source reference",
    ),
    state_mutation_scope="NONE",
    forbidden=(
        "create a second position ledger",
        "rank/pick or automatically promote a strategy",
        "combine development-lane cash into account spendability",
        "claim broker authentication or Teller acquisition readiness",
        "broker order, capital transfer or live-mode unlock",
    ),
    failure_behavior=(
        "Tampered or cross-account OBPOS source, inconsistent equity/mark, missing lane "
        "or altered build reference fails closed."
    ),
    explanation="Each lane retains its own source position ID and current market-frame exposure.",
    evidence=("verified OBPOS hashes", "build refs", "comparison ID and integrity hash"),
    review_visibility="Owner sees separate simulation results; no direct BuyBox or real broker claim.",
    temporal_validity="SOURCE_FRAME_AND_OBPOS_RECEIPT_BOUND",
    deterministic=True,
    learning_boundary="No auto-winner, live authority or source-truth reclassification.",
    deferred_integrations=(),
)


ACTIVE_AUTHORITY_RECORDS[
    "strategy_review"
] = _record(
    concept_key="strategy_review",
    authority_id="OB_STRATEGY_REVIEW_V1",
    authority_class="SOURCE_BOUND_OWNER_REVIEW_EVIDENCE",
    implementation_ref="web/ob_strategy_review.py",
    implementation_role="EXPLICIT_OPTION_FIRST_REVIEW_WITH_OWNER_DECLARED_STOCK_FALLBACK",
    owns=(
        "source-market-frame-bound explicit strategy candidate review packets",
        "owner-selected-for-review status distinct from executable trade intent",
    ),
    inputs=("OB_PORTFOLIO_VIEW_V1",),
    triggers=("explicit candidate set and optional owner-confirmed review selection",),
    effects=(
        "emit immutable evidence packet with exact option contract or explicit stock fallback",
        "retain no automatic winner, capital admission or trade execution",
    ),
    state_mutation_scope="NONE",
    forbidden=(
        "automatic option-contract selection or candidate ranking",
        "create executable trade intent from a review preference",
        "turn source evidence refs into authenticated broker proof",
        "bypass Effective Policy, risk controls, safety or owner decision",
        "capital movement, mode unlock or direct BuyBox connection",
    ),
    failure_behavior="Unbound frame/instrument, missing option contract, unexplained stock fallback and tampered portfolio fail closed.",
    explanation="Candidate records reveal source frame, exact instrument, explicit strategy and owner-declared review state.",
    evidence=("OBPORT ID/hash", "existing source frame IDs", "candidate source refs", "review receipt/hash"),
    review_visibility="Owner can inspect option-first choices and rationale without triggering execution.",
    temporal_validity="PORTFOLIO_FRAME_AND_EXPLICIT_SELECTION_BOUND",
    deterministic=True,
    learning_boundary="No auto-selection, no mode or capital policy promotion.",
    deferred_integrations=(),
)


ACTIVE_AUTHORITY_RECORDS[
    "safety_review"
] = _record(
    concept_key="safety_review",
    authority_id="OB_SAFETY_REVIEW_V1",
    authority_class="RESTRICTIVE_READ_ONLY_SOURCE_SAFETY_REVIEW",
    implementation_ref="web/ob_safety_review.py",
    implementation_role="CANONICAL_STRATEGY_OWNER_FIT_MODE_AND_TIME_EVIDENCE_JOIN",
    owns=(
        "source-reconciled danger/overreach/negative-dive/overtime review state",
        "fail-closed independent canonical owner-fit and Effective Policy recomputation",
        "separation of review eligibility from all execution authority",
    ),
    inputs=(
        "OB_STRATEGY_REVIEW_V1", "OB_OWNER_FIT_ELIGIBILITY_V1",
        "OB_OPERATING_MODE_V1", "OB_MARKET_TIME_V1",
    ),
    triggers=(
        "explicit selected strategy review and canonical mode/time evidence",
        "optional full canonical owner-fit source and source-labelled danger evidence",
    ),
    effects=(
        "emit deterministic BLOCK, HOLD or REVIEW_ONLY safety receipt",
        "escalate source-reported danger without allowing it to grant permission",
        "produce independently lineage-verified amount-free proof reference",
    ),
    state_mutation_scope="NONE",
    forbidden=(
        "new risk-limit, market, fill or Effective Policy resolver",
        "treat client-entered danger flags or source hash as external proof of safety",
        "assume owner-fit NOW is an execution grant",
        "automatically select option contract or permit Manual Live/Hybrid/Automated",
        "broker submission, capital movement, direct OB–BuyBox access",
    ),
    failure_behavior=(
        "Tampered strategy, mode, market time or owner-fit inputs fail closed. "
        "Missing or unknown safety source remains HOLD, explicit danger is BLOCK."
    ),
    explanation=(
        "Owner sees source-bound reason codes, canonical fit and policy fingerprints, "
        "mode/time references and a review-only decision distinct from execution."
    ),
    evidence=(
        "OBSTRAT receipt/hash", "canonical OBTIME and OBMODE fingerprints",
        "recomputed owner-fit and effective-policy fingerprints", "source-signal hash",
    ),
    review_visibility="Review-only proof; Tower/Teller/BuyBox and broker execution remain separate.",
    temporal_validity="EXPLICIT_CANONICAL_SOURCE_FRAME_AND_TIME_RECEIPT_BOUND",
    deterministic=True,
    learning_boundary="No safety, mode or policy widening from review/learning outcomes.",
    deferred_integrations=(),
)


ACTIVE_AUTHORITY_RECORDS[
    "recommendation_review"
] = _record(
    concept_key="recommendation_review",
    authority_id="OB_RECOMMENDATION_REVIEW_V1",
    authority_class="NONEXECUTING_SAFETY_BOUND_OWNER_RECOMMENDATION",
    implementation_ref="web/ob_recommendation_review.py",
    implementation_role="CANONICAL_OWNER_FACING_STRATEGY_AND_SAFETY_RECEIPT",
    owns=(
        "owner-facing BLOCKED, EVIDENCE_PENDING or OWNER_REVIEW_READY recommendation proof",
        "source-bound option/stock cards and canonical safety reason codes",
    ),
    inputs=("OB_SAFETY_REVIEW_V1", "OB_STRATEGY_REVIEW_V1"),
    triggers=("explicit verified safety review and source-backed strategy candidate packet",),
    effects=(
        "present candidate provenance and review-only state without ranking",
        "emit lineage-verified, non-money-bearing proof reference",
    ),
    state_mutation_scope="NONE",
    forbidden=(
        "select candidate automatically or override canonical safety denial",
        "create trade execution intent or grant capital admission",
        "profit forecast or fake authenticated broker source",
        "broker order, capital movement, trading-mode unlock",
        "direct BuyBox integration or financial-readiness assertion",
    ),
    failure_behavior=(
        "Tampered or unmatched safety and strategy source cannot emit recommendation. "
        "BLOCK/HOLD states remain visibly restrictive, never concealed."
    ),
    explanation=(
        "Source evidence, exact contract/fallback and canonical safety reasons "
        "remain explainable while execution permission stays false."
    ),
    evidence=("full verified OBSAFE/OBSTRAT lineage", "review receipt/hash", "candidate source references"),
    review_visibility="Owner may inspect and decide later; no order or mode action in this family.",
    temporal_validity="VERIFIED_SOURCE_FRAME_TIME_AND_SAFETY_RECEIPT_BOUND",
    deterministic=True,
    learning_boundary="No recommendation ranking, permission promotion or trade outcome claims.",
    deferred_integrations=(),
)


ACTIVE_AUTHORITY_RECORDS[
    "owner_review_evidence"
] = _record(
    concept_key="owner_review_evidence",
    authority_id="OB_OWNER_REVIEW_EVIDENCE_V1",
    authority_class="SOURCE_BOUND_NONEXECUTING_OWNER_REVIEW_RECORD",
    implementation_ref="web/ob_owner_review_evidence.py",
    implementation_role="CANONICAL_OWNER_DISPOSITION_AND_ADVERSE_REVIEW_PROOF",
    owns=(
        "explicit owner-asserted review disposition, not authenticated owner session",
        "source-labelled negative dive, overtime, overreach and evidence gap review notes",
    ),
    inputs=("OB_RECOMMENDATION_REVIEW_V1",),
    triggers=(
        "verified recommendation with optional explicit owner assertion",
        "explicit source-labelled adverse review notes",
    ),
    effects=(
        "emit immutable owner review state while preserving canonical safety denials",
        "expose adverse-review-pending without inventing broker fills or actual P&L",
    ),
    state_mutation_scope="NONE",
    forbidden=(
        "reinterpret review interest as an executable order or broker authentication",
        "manufacture actual cash/fill/P&L from source review notes",
        "ignore source-bound BLOCK/HOLD to promote an owner review",
        "alter Trading Mode, protected floors, capital or Direct BuyBox access",
    ),
    failure_behavior=(
        "Invalid source lineage, duplicate issues, missing owner acknowledgement, "
        "pre-observation decision, or conflicting review disposition fails closed."
    ),
    explanation="Owner sees explicit review intent and inherited safety reasons separately from source-asserted adverse notes.",
    evidence=("verified OBREC/OBSAFE lineage", "owner assertion hash", "issue source refs and hashes", "immutable review receipt"),
    review_visibility="Owner-review-only claim. Tower authentication and broker reconciliation remain separate.",
    temporal_validity="BOUND_TO_VERIFIED_MARKET_OBSERVATION_AND_DECLARED_REVIEW_TIMESTAMP",
    deterministic=True,
    learning_boundary="No recommendation/outcome rewrite, automated trading permission or unverified profit inference.",
    deferred_integrations=(),
)


ACTIVE_AUTHORITY_RECORDS[
    "review_learning"
] = _record(
    concept_key="review_learning",
    authority_id="OB_REVIEW_LEARNING_V1",
    authority_class="BOUNDED_NONEXECUTING_REVIEW_FEEDBACK",
    implementation_ref="web/ob_review_learning.py",
    implementation_role="SOURCE_BOUND_REVIEW_TASKS_NOT_AUTONOMOUS_TRAINING",
    owns=(
        "deterministic review tasks from verified owner dispositions and adverse issues",
        "explicit absence of authenticated actual trade outcome and numeric reward labels",
    ),
    inputs=("OB_OWNER_REVIEW_EVIDENCE_V1",),
    triggers=("verified owner review and optional source-labelled adverse note",),
    effects=(
        "surface source-gap, negative-dive, overtime and overreach review tasks",
        "emit immutable non-acting feedback receipt with missing-outcome status",
    ),
    state_mutation_scope="NONE",
    forbidden=(
        "learn from an unverified owner note as realized profit",
        "autonomous risk-limit or policy changes and safety relaxation",
        "score/expected-return generation from absent actual outcome evidence",
        "broker, capital or mode operation or Direct BuyBox access",
    ),
    failure_behavior="Tampered or mismatched review lineage fails closed, with no training or outcome claim.",
    explanation="Tasks map to source issues and owner review posture; actual broker outcome remains unavailable.",
    evidence=("verified OBREV source hash", "inherited OBREC reference", "explicit issue IDs", "learning receipt/hash"),
    review_visibility="Owner can review potential lessons without silent policy adaptation.",
    temporal_validity="OBREV_SOURCE_RECEIPT_BOUND; ACTUAL_OUTCOME_NOT_PROVEN",
    deterministic=True,
    learning_boundary="No training feedback, widened risk, relaxed guardrails, mode change or live promotion.",
    deferred_integrations=(),
)


ACTIVE_AUTHORITY_RECORDS[
    "adverse_guard_review"
] = _record(
    concept_key="adverse_guard_review",
    authority_id="OB_ADVERSE_GUARD_REVIEW_V1",
    authority_class="SOURCE_DISTINCT_READ_ONLY_GUARD_REVIEW",
    implementation_ref="web/ob_adverse_guard_review.py",
    implementation_role="CANONICAL_REPEATED_ADVERSE_EVIDENCE_REVIEW_NO_AUTOMATED_ACTUATOR",
    owns=(
        "source-fingerprint-distinct repeated adverse review claim visibility",
        "source-bound owner attention tasks without provider-authenticated market assertions",
    ),
    inputs=("OB_REVIEW_LEARNING_V1",),
    triggers=("explicit chronology of individually verified OBLEARN review receipts",),
    effects=(
        "derive deterministic source-assertion patterns and owner review prompts",
        "deduplicate replayed source payloads rather than counting as new incidents",
    ),
    state_mutation_scope="NONE",
    forbidden=(
        "manufacture independent incidents by replaying identical payloads",
        "call source assertions authenticated market signals or actual outcomes",
        "automatically flip a kill switch or relax/widen risk/capital policy",
        "broker order, live mode unlock or direct BuyBox connection",
    ),
    failure_behavior=(
        "Tampered lineage, duplicate review or nonchronological owner assertions fail closed; "
        "absence of adverse source is never affirmative proof of safety."
    ),
    explanation="Show distinct source-count and inherited owner review tasks without policy/return inference.",
    evidence=("verified OBLEARN hashes", "distinct source issue IDs/hashes", "chronological owner review receipts", "guard hash"),
    review_visibility="Owner sees source-asserted guard alerts; actual authenticated provider evidence remains separate.",
    temporal_validity="CHRONOLOGICAL_OWNER_REVIEW_AND_DISTINCT_SOURCE_PAYLOAD_BOUND",
    deterministic=True,
    learning_boundary="No autonomous threshold, mode or policy adaptation.",
    deferred_integrations=(),
)


ACTIVE_AUTHORITY_RECORDS[
    "soulaana_explanation"
] = _record(
    concept_key="soulaana_explanation",
    authority_id="OB_SOULAANA_EXPLANATION_V1",
    authority_class="READ_ONLY_CANONICAL_RECEIPT_EXPLANATION",
    implementation_ref="web/ob_soulaana_explanations.py",
    implementation_role="SOURCE_BOUND_RECOMMENDATION_SAFETY_AND_GUARD_TRANSLATION",
    owns=(
        "deterministic owner-facing explanation cards bound to canonical source receipts",
        "exact known or unknown reason code translation without invented market facts",
        "optional source-asserted adverse guard explanation, never an actuator",
    ),
    inputs=("OB_RECOMMENDATION_REVIEW_V1", "OB_ADVERSE_GUARD_REVIEW_V1"),
    triggers=(
        "explicit verified recommendation/safety and source lineage",
        "optional fully verified same-recommendation guard evidence",
    ),
    effects=(
        "emit immutable source-labelled explanation cards and amount-free proof reference",
        "preserve canonical BLOCKED/EVIDENCE_PENDING/OWNER_REVIEW_READY status",
    ),
    state_mutation_scope="NONE",
    forbidden=(
        "invent market, broker, return or financial source truth",
        "relabel canonical safety denial as a recommendation",
        "select winning strategy, contract, trading mode or risk limit",
        "broker order, capital movement, direct OB–BuyBox connection",
    ),
    failure_behavior=(
        "Tampered/missing recommendation or guard source lineage fails closed; "
        "unknown reason code remains exact source code without fabricated explanation."
    ),
    explanation="Owner sees why a source was held or blocked and exact receipt provenance.",
    evidence=(
        "canonical recommendation and safety receipt IDs and fingerprints",
        "optional guard receipt and verified source fingerprints",
        "deterministic card contents and immutable explanation hash",
    ),
    review_visibility="Contextual Soulaana explanation only, not a trading, money or readiness authority.",
    temporal_validity="INHERITS_VERIFIED_CANONICAL_SOURCE_TIME_AND_STATUS",
    deterministic=True,
    learning_boundary="May explain source evidence but cannot mutate source state or learning policy.",
    deferred_integrations=(),
)


PENDING_AUTHORITY_SLOTS = {

    "source_provenance": {
        "authority_id": "PENDING_OBDATA011_015",
        "planned_pack": "OBDATA011-015",
        "status": "PENDING",
    },

}


RETIRED_AUTHORITY_ALIASES = {
    "PENDING_OBCAP":
        "OB_CAPITAL_POLICY_V1",

    "PENDING_OBTIME":
        "OB_MARKET_TIME_V1",

    "PENDING_OBMODE":
        "OB_OPERATING_MODE_V1",

    "PENDING_OBCTX":
        "OB_DECISION_CONTEXT_V1",

    "PENDING_OBEVENT":
        "OB_COMMAND_EVENT_CAUSAL_V1",

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
    "capital_policy":
        "capital_policy",

    "mode_authority":
        "mode_authority",

    "decision_context":
        "decision_context",

    "event_authority":
        "event_authority",

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

        "deferred_integration_may_reference_pending_slot":
            True,

        "deferred_integration_may_reference_active_concept":
            True,

        "unknown_deferred_integration_allowed":
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

        for integration_key in record.get(
            "deferred_integrations",
            [],
        ):
            if (
                integration_key not in pending
                and integration_key not in records
            ):
                errors.append(
                    f"unknown_deferred_integration:{concept_key}:{integration_key}"
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
