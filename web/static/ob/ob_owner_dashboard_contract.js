// OBUX021_OWNER_DASHBOARD_INTELLIGENCE_CONTRACT
(() => {
  "use strict";

  const VERSION = "OBUX021_OWNER_DASHBOARD_INTELLIGENCE_CONTRACT";

  const ENDPOINTS = Object.freeze({
    account_experience: "/ob/account-experience.json",
    engine_trust: "/ob/engine-feed-trust-labels.json",
    manual_live_readiness: "/ob/manual-live-operator-confidence-readiness-checkpoint.json",
    private_beta: "/ob/private-beta-launch-control.json"
  });

  const BOUNDARIES = Object.freeze({
    owner_only: true,
    read_only_intelligence: true,
    owner_dashboard_route_registered: false,
    tower_permission_mutation_enabled: false,
    broker_api_enabled: false,
    broker_order_submission_enabled: false,
    real_capital_movement_enabled: false,
    auto_execution_enabled: false,
    live_auto_locked: true,
    gp066_advanced: false
  });

  const POLICY_MISSIONS = Object.freeze([
    {
      account_id: "ob_acct_trust",
      mission_id: "trust",
      label: "Trust",
      display_label: "Trust OB",
      purpose: "Protect and grow trust capital without treating protected money like ordinary trading capital.",
      risk_profile: "Protected / conservative",
      capital_goal: "Protected family capital and future mission dispersal.",
      current_status: "Policy defined",
      next_action: "Preserve the protected floor and wait for verified capital data."
    },
    {
      account_id: "ob_acct_personal",
      mission_id: "personal",
      label: "Personal",
      display_label: "Personal OB",
      purpose: "Owner learning, personal capital growth, and controlled Manual Live review.",
      risk_profile: "Moderate / capped",
      capital_goal: "Owner liquidity and skill-building without borrowing from mission lanes.",
      current_status: "Policy defined",
      next_action: "Keep personal capital separate from protected and business missions."
    },
    {
      account_id: "ob_acct_simplee_world",
      mission_id: "simplee_world",
      label: "Simplee World",
      display_label: "Simplee World OB",
      purpose: "Build parent-company capital for the wider Simplee ecosystem.",
      risk_profile: "Growth / controlled",
      capital_goal: "Business operating and expansion capital.",
      current_status: "Policy defined",
      next_action: "Keep business purpose and receipts explicit."
    },
    {
      account_id: "ob_acct_atm",
      mission_id: "atm",
      label: "ATM",
      display_label: "SimpleeOnTheGo OB",
      purpose: "Build capital for ATM route acquisition, vault cash, repair, and expansion.",
      risk_profile: "Moderate becoming conservative near deployment",
      capital_goal: "ATM acquisition and operating reserve.",
      current_status: "Policy defined",
      next_action: "Do not claim milestone progress until verified account data is available."
    },
    {
      account_id: "ob_acct_apartment",
      mission_id: "apartment",
      label: "The Grounds",
      display_label: "Apartment / Grounds OB",
      purpose: "Build and protect future property acquisition reserves.",
      risk_profile: "Protected / conservative",
      capital_goal: "Acquisition, inspection, closing, repair, and reserve readiness.",
      current_status: "Policy defined",
      next_action: "Keep capital preservation ahead of aggressive growth."
    },
    {
      account_id: "ob_acct_proof_demo",
      mission_id: "proof_demo",
      label: "Proof / Demo",
      display_label: "Proof / Demo OB",
      purpose: "Demonstrate OB safely without exposing private capital or identities.",
      risk_profile: "Zero real-capital risk",
      capital_goal: "No real capital.",
      current_status: "Demo only",
      next_action: "Use for safe private proof and beta demonstration only."
    }
  ]);

  const state = {
    status: "guarded_local_policy",
    hydrated: false,
    hydrated_at: null,
    sources: {},
    errors: [],
    contract: null
  };

  const safeText = (value, fallback = "") => {
    if (value === undefined || value === null || value === "") return fallback;
    return String(value);
  };

  const safeArray = (value) => Array.isArray(value) ? value : [];

  const sourceLooksVerified = (payload) => {
    if (!payload || typeof payload !== "object") return false;

    const source = safeText(payload.source, "").toLowerCase();

    if (
      source.includes("fallback") ||
      source.includes("preview") ||
      source.includes("demo")
    ) {
      return false;
    }

    if (payload.verified === false) return false;
    return true;
  };

  const fetchSource = async (name, url) => {
    try {
      const response = await fetch(url, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      let payload = {};
      try {
        payload = await response.json();
      } catch (_error) {
        payload = {};
      }

      if (!response.ok) {
        return {
          name,
          url,
          status: "guarded",
          http_status: response.status,
          verified: false,
          payload: null,
          error: `HTTP ${response.status}`
        };
      }

      return {
        name,
        url,
        status: "available",
        http_status: response.status,
        verified: sourceLooksVerified(payload),
        payload,
        error: null
      };
    } catch (error) {
      return {
        name,
        url,
        status: "unavailable",
        http_status: null,
        verified: false,
        payload: null,
        error: error && error.message ? error.message : "fetch failed"
      };
    }
  };

  const missionIdFromItem = (item, index) => {
    const raw = safeText(
      item.mission_id ||
      item.account_id ||
      item.lane ||
      item.label,
      `mission_${index + 1}`
    ).toLowerCase();

    if (raw.includes("trust")) return "trust";
    if (raw.includes("personal")) return "personal";
    if (raw.includes("world") || raw.includes("business")) return "simplee_world";
    if (raw.includes("atm") || raw.includes("onthego")) return "atm";
    if (
      raw.includes("apartment") ||
      raw.includes("property") ||
      raw.includes("grounds")
    ) return "apartment";
    if (raw.includes("proof") || raw.includes("demo")) return "proof_demo";

    return raw.replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
  };

  const normalizeMission = (item, index, sourceVerified) => ({
    account_id: safeText(item.account_id, `owner_mission_${index + 1}`),
    mission_id: missionIdFromItem(item, index),
    label: safeText(item.label || item.lane, `Mission ${index + 1}`),
    display_label: safeText(item.display_label || item.label, `Mission ${index + 1}`),
    purpose: safeText(item.purpose, "Mission purpose is not available."),
    risk_profile: safeText(item.risk_profile || item.risk, "Risk policy unavailable."),
    allowed_modes: safeArray(item.allowed_modes),
    capital_goal: safeText(item.capital_goal || item.goal, "Capital goal not available."),
    deployment_rules: safeText(item.deployment_rules || item.blocked, ""),
    current_status: safeText(item.current_status, "Policy status unknown."),
    next_action: safeText(item.next_action, "No verified next action."),
    policy_source_verified: !!sourceVerified,

    // OBUX021 hard guard:
    // Policy text is not a balance, P&L, milestone, or verified progress report.
    actual_capital_known: false,
    actual_capital_value: null,
    capital_progress_known: false,
    capital_progress_percent: null,
    verified_snapshot: false,
    needs_attention: false
  });

  const missionSnapshot = () => {
    const snapshot = window.OB_OWNER_MISSION_SNAPSHOT;

    if (
      !snapshot ||
      snapshot.verified !== true ||
      !Array.isArray(snapshot.missions)
    ) {
      return {
        verified: false,
        missions: []
      };
    }

    return {
      verified: true,
      missions: snapshot.missions
    };
  };

  const missions = () => {
    const accountSource = state.sources.account_experience || {};
    const payload = accountSource.payload || {};

    const sourceItems = safeArray(payload.owner_mission_accounts);
    const baseItems = sourceItems.length ? sourceItems : POLICY_MISSIONS;

    const normalized = baseItems.map((item, index) =>
      normalizeMission(item, index, !!accountSource.verified)
    );

    const snapshot = missionSnapshot();

    if (!snapshot.verified) return normalized;

    const liveById = new Map(
      snapshot.missions.map((item, index) => [
        missionIdFromItem(item, index),
        item
      ])
    );

    return normalized.map((mission) => {
      const live = liveById.get(mission.mission_id);
      if (!live) return mission;

      const capitalValueIsKnown =
        live.actual_capital_known === true &&
        Number.isFinite(Number(live.actual_capital_value));

      const progressIsKnown =
        live.capital_progress_known === true &&
        Number.isFinite(Number(live.capital_progress_percent));

      return {
        ...mission,
        verified_snapshot: true,
        actual_capital_known: capitalValueIsKnown,
        actual_capital_value: capitalValueIsKnown
          ? Number(live.actual_capital_value)
          : null,
        capital_progress_known: progressIsKnown,
        capital_progress_percent: progressIsKnown
          ? Number(live.capital_progress_percent)
          : null,
        current_status: safeText(live.current_status, mission.current_status),
        next_action: safeText(live.next_action, mission.next_action),
        needs_attention: live.needs_attention === true
      };
    });
  };

  const trustSummary = () => {
    const source = state.sources.engine_trust || {};
    const payload = source.payload || {};
    const trust = payload.trust || {};

    const verified = source.verified === true;

    const freshness =
      verified &&
      Number.isFinite(Number(payload.freshness_score))
        ? Number(payload.freshness_score)
        : null;

    const level = verified
      ? safeText(trust.level, "unknown").toLowerCase()
      : "guarded";

    return {
      verified,
      label: verified
        ? safeText(trust.label || payload.display_label, "Verified source")
        : "Guarded · verify source",
      level,
      freshness_score: freshness,
      safe_to_display: verified
        ? safeText(trust.safeToDisplay, "caution")
        : "caution",
      needs_attention:
        !verified ||
        ["fallback", "missing", "stale", "guarded"].includes(level),
      explanation: verified
        ? "Soulaana can identify the trust label supplied by the engine-trust layer."
        : "Soulaana does not have a verified owner-wide engine-trust result on this surface yet."
    };
  };

  const readinessSummary = () => {
    const source = state.sources.manual_live_readiness || {};
    const payload = source.payload || {};
    const scorecard = payload.readiness_scorecard || {};

    const verified = source.verified === true;

    const blockers = verified
      ? safeArray(payload.remaining_live_blockers).map((item) => ({
          id: safeText(item.blocker_id, "blocker"),
          label: safeText(item.label, "Readiness blocker"),
          reason: safeText(item.reason, "Readiness work remains."),
          status: safeText(item.status, "blocking")
        }))
      : [];

    return {
      verified,
      label: verified
        ? safeText(
            scorecard.readiness_label,
            "Owner confidence evidence available"
          )
        : "Guarded · readiness evidence not verified",
      score:
        verified && Number.isFinite(Number(scorecard.readiness_score))
          ? Number(scorecard.readiness_score)
          : null,
      blockers,
      needs_attention: !verified || blockers.length > 0,

      // GP035 confidence tooling never creates real execution permission.
      real_manual_live_ready: false,
      broker_order_submission_enabled: false,
      auto_execution_enabled: false,
      live_auto_locked: true
    };
  };

  const betaSummary = () => {
    const source = state.sources.private_beta || {};
    const payload = source.payload || {};
    const verified = source.verified === true;

    const rawStatus =
      payload.owner_go_no_go_status ||
      payload.owner_decision ||
      payload.launch_status ||
      payload.status;

    return {
      verified,
      label: verified
        ? safeText(rawStatus, "Verified beta control evidence available")
        : "Guarded · beta launch evidence not verified",
      expansion_recommended: false,
      private_only: true,
      public_launch_enabled: false,
      explanation: verified
        ? "Owner Dashboard can summarize the protected beta-control evidence without becoming the control plane."
        : "Soulaana will not claim beta readiness from missing, protected, or fallback evidence."
    };
  };

  const historySummary = () => {
    const snapshot = window.OB_OWNER_CHANGE_HISTORY;

    if (
      snapshot &&
      snapshot.verified === true &&
      Array.isArray(snapshot.items)
    ) {
      return {
        verified: true,
        items: snapshot.items.slice(0, 8)
      };
    }

    return {
      verified: false,
      items: [
        {
          title: "No verified owner-change history yet",
          detail:
            "I will not invent a 'since you were here' story. Owner change-history needs a verified source before I summarize it."
        }
      ]
    };
  };

  const patternSummary = (missionList) => {
    const verifiedMissions = missionList.filter(
      (mission) => mission.verified_snapshot
    );

    if (!verifiedMissions.length) {
      return {
        verified: false,
        items: [
          {
            title: "Cross-mission performance patterns are not verified yet",
            detail:
              "Mission policies are defined, but policy text is not enough to claim crowding, repeated wins, repeated mistakes, or capital pressure."
          }
        ]
      };
    }

    const attentionCount = verifiedMissions.filter(
      (mission) => mission.needs_attention
    ).length;

    return {
      verified: true,
      items: [
        {
          title:
            attentionCount > 0
              ? `${attentionCount} verified mission lane(s) need owner attention`
              : "No verified mission lane is flagging owner attention",
          detail:
            "This statement comes only from the verified owner mission snapshot."
        }
      ]
    };
  };

  const ownerAttention = (
    missionList,
    trust,
    readiness,
    beta
  ) => {
    const items = [];

    missionList
      .filter(
        (mission) =>
          mission.verified_snapshot &&
          mission.needs_attention
      )
      .forEach((mission) => {
        items.push({
          priority: "high",
          source: "verified mission snapshot",
          title: `${mission.display_label} needs you`,
          detail: mission.next_action
        });
      });

    if (trust.needs_attention) {
      items.push({
        priority: "high",
        source: "engine trust",
        title: "Verify the picture Soulaana is using",
        detail: trust.explanation
      });
    }

    if (readiness.needs_attention) {
      items.push({
        priority: "medium",
        source: "Manual Live readiness",
        title: "Manual Live remains a guarded owner-readiness lane",
        detail: readiness.verified
          ? (
              readiness.blockers.length
                ? `${readiness.blockers.length} verified blocker(s) remain. Real Manual Live and Live Auto stay locked.`
                : "Confidence evidence is available, but it does not authorize real Manual Live."
            )
          : "The readiness evidence on this surface is not verified. Live Auto stays locked."
      });
    }

    if (!beta.verified) {
      items.push({
        priority: "medium",
        source: "private beta",
        title: "Do not infer beta expansion readiness",
        detail:
          "The Owner Dashboard does not currently have verified beta launch-control evidence."
      });
    }

    if (!items.length) {
      items.push({
        priority: "calm",
        source: "verified owner intelligence",
        title: "Nothing verified is demanding an owner decision",
        detail:
          "Soulaana can keep watching without manufacturing urgency."
      });
    }

    return items.slice(0, 5);
  };

  const buildContract = () => {
    const missionList = missions();
    const trust = trustSummary();
    const readiness = readinessSummary();
    const beta = betaSummary();
    const history = historySummary();
    const patterns = patternSummary(missionList);
    const attention = ownerAttention(
      missionList,
      trust,
      readiness,
      beta
    );

    const allCriticalSourcesVerified =
      trust.verified &&
      readiness.verified &&
      beta.verified;

    return {
      version: VERSION,
      role: "owner_dashboard",
      owner_only: true,
      dormant: true,

      mission_sky: missionList,
      trust,
      readiness,
      beta,
      owner_attention: attention,
      patterns,
      since_you_were_here: history,

      source_state: {
        account_experience:
          state.sources.account_experience || null,
        engine_trust:
          state.sources.engine_trust || null,
        manual_live_readiness:
          state.sources.manual_live_readiness || null,
        private_beta:
          state.sources.private_beta || null
      },

      interpretation_state: {
        all_critical_sources_verified: allCriticalSourcesVerified,
        may_claim_cross_mission_performance_patterns:
          patterns.verified,
        may_claim_change_history:
          history.verified,
        may_claim_capital_progress:
          missionList.some(
            (mission) => mission.capital_progress_known
          ),
        no_action_needed:
          allCriticalSourcesVerified &&
          attention.every(
            (item) =>
              item.priority !== "high" &&
              item.priority !== "medium"
          )
      },

      boundaries: BOUNDARIES
    };
  };

  const hydrate = async () => {
    state.status = "hydrating";
    state.errors = [];

    const [
      accountExperience,
      engineTrust,
      manualLiveReadiness,
      privateBeta
    ] = await Promise.all([
      fetchSource(
        "account_experience",
        ENDPOINTS.account_experience
      ),
      fetchSource(
        "engine_trust",
        ENDPOINTS.engine_trust
      ),
      fetchSource(
        "manual_live_readiness",
        ENDPOINTS.manual_live_readiness
      ),
      fetchSource(
        "private_beta",
        ENDPOINTS.private_beta
      )
    ]);

    state.sources = {
      account_experience: accountExperience,
      engine_trust: engineTrust,
      manual_live_readiness: manualLiveReadiness,
      private_beta: privateBeta
    };

    Object.values(state.sources).forEach((source) => {
      if (source && source.error) {
        state.errors.push(
          `${source.name}: ${source.error}`
        );
      }
    });

    state.hydrated = true;
    state.hydrated_at = new Date().toISOString();
    state.status = state.errors.length
      ? "hydrated_guarded"
      : "hydrated";
    state.contract = buildContract();

    window.dispatchEvent(
      new CustomEvent(
        "ob:owner-dashboard-contract-ready",
        {
          detail: state.contract
        }
      )
    );

    return state.contract;
  };

  state.contract = buildContract();

  window.OB_OWNER_DASHBOARD_CONTRACT_V21 = Object.freeze({
    version: VERSION,
    endpoints: ENDPOINTS,
    boundaries: BOUNDARIES,
    getState: () => state,
    getContract: () => state.contract || buildContract(),
    buildContract,
    hydrate
  });
})();
