// OBUX022_SOULAANA_OWNER_BRIEFING_ENGINE
(() => {
  "use strict";

  const VERSION = "OBUX022_SOULAANA_OWNER_BRIEFING_ENGINE";

  const safeText = (value, fallback = "") => {
    if (value === undefined || value === null || value === "") {
      return fallback;
    }
    return String(value);
  };

  const buildBriefing = (contract) => {
    const safe = contract || {};
    const missions = Array.isArray(safe.mission_sky)
      ? safe.mission_sky
      : [];
    const attention = Array.isArray(safe.owner_attention)
      ? safe.owner_attention
      : [];

    const trust = safe.trust || {};
    const readiness = safe.readiness || {};
    const beta = safe.beta || {};
    const interpretation = safe.interpretation_state || {};

    const guardedSources = [
      !trust.verified ? "engine trust" : null,
      !readiness.verified ? "Manual Live readiness" : null,
      !beta.verified ? "private beta state" : null
    ].filter(Boolean);

    const highAttention = attention.filter(
      (item) => item.priority === "high"
    );

    const verifiedCapitalMissions = missions.filter(
      (mission) =>
        mission.actual_capital_known ||
        mission.capital_progress_known
    );

    let headline;
    let marketAndSystemRead;

    if (guardedSources.length) {
      headline =
        "I can see the Observatory structure. I will not fake the missing truth.";

      marketAndSystemRead =
        `Your owner view has ${missions.length} mission lanes defined, ` +
        `but ${guardedSources.join(", ")} ${
          guardedSources.length === 1 ? "is" : "are"
        } still guarded or unverified on this surface.`;
    } else if (highAttention.length) {
      headline =
        "I found owner-level items that deserve your attention.";

      marketAndSystemRead =
        `${highAttention.length} high-priority owner signal(s) are verified. ` +
        "I would review those before digging into lower-level evidence.";
    } else {
      headline =
        "The Observatory is calm at owner altitude.";

      marketAndSystemRead =
        "I do not see a verified owner-level emergency. I can keep watching without manufacturing urgency.";
    }

    const capitalRead =
      verifiedCapitalMissions.length
        ? `${verifiedCapitalMissions.length} mission lane(s) have verified capital or progress snapshots available.`
        : "I do not have verified capital progress for your mission lanes yet, so I will not pretend a goal is closer than the evidence proves.";

    const readinessRead = readiness.verified
      ? (
          readiness.blockers && readiness.blockers.length
            ? `Your readiness evidence still shows ${readiness.blockers.length} blocker(s). That is readiness work, not permission to trade.`
            : "Your owner confidence evidence is available, but real Manual Live and Live Auto remain locked."
        )
      : "I cannot verify the readiness evidence from this surface yet. That means we stay conservative: no real Manual Live claim and Live Auto remains locked.";

    const trustRead = trust.verified
      ? (
          trust.freshness_score === null ||
          trust.freshness_score === undefined
            ? `The feed trust layer reports ${safeText(trust.label, "a verified state")}.`
            : `The feed trust layer reports ${safeText(trust.label, "a verified state")} with freshness ${trust.freshness_score}.`
        )
      : "I do not have a verified engine-trust result here yet. I would not expand reliance on data I cannot verify.";

    const betaRead = beta.verified
      ? `Private beta control evidence is available: ${safeText(beta.label, "review it before expansion")}.`
      : "I do not have verified beta launch-control evidence on this surface, so I will not tell you beta is ready to expand.";

    const attentionRead = attention.length
      ? attention
          .slice(0, 3)
          .map((item) => safeText(item.title, "Owner item"))
          .join(" · ")
      : "Nothing verified is asking for your attention.";

    const changeHistory = safe.since_you_were_here || {};
    const changedRead = changeHistory.verified
      ? "I have verified owner-change history available and can summarize what materially changed."
      : "I do not have verified owner-change history yet. I will not invent a 'since you were here' story.";

    const patterns = safe.patterns || {};
    const lessonRead = patterns.verified
      ? "I have enough verified cross-mission evidence to surface an owner-level pattern."
      : "I do not have enough verified cross-mission performance evidence to call a pattern, win, mistake, crowding condition, or capital-pressure trend.";

    const nextMove = highAttention.length
      ? `Start with: ${safeText(highAttention[0].title, "the highest-priority verified owner item")}.`
      : guardedSources.length
        ? `Next best move: verify ${guardedSources[0]} before trusting a broader owner conclusion.`
        : "Next best move: no forced action. Review only what meaningfully changed.";

    return {
      version: VERSION,
      eyebrow: "SOULAANA · OWNER BRIEFING",
      headline,

      what_i_see: marketAndSystemRead,
      your_missions: capitalRead,
      what_needs_you: attentionRead,
      readiness: readinessRead,
      system_trust: trustRead,
      beta_state: betaRead,
      what_changed: changedRead,
      what_im_learning: lessonRead,
      what_can_wait:
        "Raw diagnostics, file-by-file evidence, and deep administrative controls can wait unless this briefing gives you a reason to open them.",
      next_best_move: nextMove,

      no_action_needed:
        interpretation.no_action_needed === true,

      owner_altitude:
        "Normal Dashboard asks what is happening in the market. Owner Dashboard asks what is happening across your Observatory.",

      evidence_rule:
        "Soulaana explains first. Raw proof stays behind Show me why.",

      boundaries: {
        owner_only: true,
        broker_action_performed: false,
        capital_action_performed: false,
        permission_mutation_performed: false,
        live_auto_locked: true
      }
    };
  };

  window.OB_OWNER_DASHBOARD_SOULAANA_V22 = Object.freeze({
    version: VERSION,
    buildBriefing
  });
})();
