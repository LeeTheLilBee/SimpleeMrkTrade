// OBUX023_MISSION_SKY
// OBUX024_OWNER_ATTENTION_READINESS_TRUST_LESSONS
// OBUX025_DORMANT_OWNER_DASHBOARD_SURFACE
(() => {
  "use strict";

  const VERSION = "OBUX023_025_OWNER_DASHBOARD_SURFACE";

  const esc = (value) =>
    String(value === undefined || value === null ? "" : value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  const tone = (priority) => {
    if (priority === "high") return "danger";
    if (priority === "medium") return "watch";
    if (priority === "calm") return "calm";
    return "";
  };

  const sourceChip = (verified, label) => `
    <span class="ob-owner-chip ${verified ? "verified" : "guarded"}">
      ${verified ? "Verified" : "Guarded"} · ${esc(label)}
    </span>
  `;

  const missionCard = (mission, index) => {
    const capitalText = mission.actual_capital_known
      ? `Verified capital snapshot available`
      : mission.capital_progress_known
        ? `Verified mission progress available`
        : "Capital progress not verified";

    const attention = mission.needs_attention
      ? "Needs owner attention"
      : "No verified attention flag";

    return `
      <article
        class="ob-owner-mission-card mission-${index + 1} ${mission.needs_attention ? "needs-attention" : ""}"
        data-mission-id="${esc(mission.mission_id)}"
      >
        <div class="ob-owner-mission-orbit">
          <span class="ob-owner-mission-star"></span>
          <span class="ob-owner-mission-index">${index + 1}</span>
        </div>

        <div class="ob-owner-mission-copy">
          <span class="ob-owner-kicker">${esc(mission.label)}</span>
          <h3>${esc(mission.display_label)}</h3>
          <p>${esc(mission.purpose)}</p>
        </div>

        <div class="ob-owner-mission-meta">
          <span>${esc(mission.risk_profile)}</span>
          <span>${esc(capitalText)}</span>
          <span>${esc(attention)}</span>
        </div>

        <div class="ob-owner-mission-next">
          <span>Soulaana · next</span>
          <strong>${esc(mission.next_action)}</strong>
        </div>
      </article>
    `;
  };

  const attentionCard = (item, index) => `
    <article class="ob-owner-attention-card ${tone(item.priority)}">
      <div class="ob-owner-attention-number">${String(index + 1).padStart(2, "0")}</div>
      <div>
        <span class="ob-owner-kicker">${esc(item.source || "owner intelligence")}</span>
        <h3>${esc(item.title)}</h3>
        <p>${esc(item.detail)}</p>
      </div>
    </article>
  `;

  const historyItem = (item) => `
    <div class="ob-owner-history-item">
      <span class="ob-owner-history-dot"></span>
      <div>
        <strong>${esc(item.title || "Owner change")}</strong>
        <span>${esc(item.detail || "")}</span>
      </div>
    </div>
  `;

  const render = (contract) => {
    const mount = document.getElementById("ownerDashboardMount");
    if (!mount) return;

    const soulaanaApi = window.OB_OWNER_DASHBOARD_SOULAANA_V22;
    const briefing = soulaanaApi && soulaanaApi.buildBriefing
      ? soulaanaApi.buildBriefing(contract)
      : {
          eyebrow: "SOULAANA · OWNER BRIEFING",
          headline: "Owner intelligence is still loading.",
          what_i_see: "I am waiting for the guarded owner contract.",
          your_missions: "",
          what_needs_you: "",
          readiness: "",
          system_trust: "",
          beta_state: "",
          what_changed: "",
          what_im_learning: "",
          what_can_wait: "",
          next_best_move: "",
          no_action_needed: false
        };

    const missions = Array.isArray(contract.mission_sky)
      ? contract.mission_sky
      : [];
    const attention = Array.isArray(contract.owner_attention)
      ? contract.owner_attention
      : [];

    const history =
      contract.since_you_were_here &&
      Array.isArray(contract.since_you_were_here.items)
        ? contract.since_you_were_here.items
        : [];

    const patterns =
      contract.patterns &&
      Array.isArray(contract.patterns.items)
        ? contract.patterns.items
        : [];

    const trust = contract.trust || {};
    const readiness = contract.readiness || {};
    const beta = contract.beta || {};

    mount.innerHTML = `
      <main
        class="ob-owner-dashboard"
        data-owner-dashboard-role="owner-only"
        data-owner-dashboard-dormant="true"
      >
        <section class="ob-owner-hero">
          <div class="ob-owner-hero-copy">
            <div class="ob-owner-hero-topline">
              <span class="ob-owner-kicker">${esc(briefing.eyebrow)}</span>
              <div class="ob-owner-chip-row">
                <span class="ob-owner-chip owner">Owner only</span>
                <span class="ob-owner-chip locked">Live Auto Locked</span>
                <span class="ob-owner-chip dormant">Dormant surface</span>
              </div>
            </div>

            <h1>${esc(briefing.headline)}</h1>

            <p class="ob-owner-lead">${esc(briefing.what_i_see)}</p>

            <div class="ob-owner-briefing-river">
              <div>
                <span>YOUR MISSIONS</span>
                <strong>${esc(briefing.your_missions)}</strong>
              </div>
              <div>
                <span>WHAT NEEDS YOU</span>
                <strong>${esc(briefing.what_needs_you)}</strong>
              </div>
              <div>
                <span>NEXT BEST MOVE</span>
                <strong>${esc(briefing.next_best_move)}</strong>
              </div>
            </div>

            <div class="ob-owner-calm-line ${briefing.no_action_needed ? "calm" : ""}">
              <span class="ob-owner-calm-dot"></span>
              <strong>
                ${
                  briefing.no_action_needed
                    ? "Nothing verified needs an owner action right now."
                    : "Soulaana is keeping uncertainty visible instead of manufacturing confidence."
                }
              </strong>
            </div>
          </div>

          <div class="ob-owner-observatory" aria-hidden="true">
            <div class="ob-owner-observatory-halo halo-1"></div>
            <div class="ob-owner-observatory-halo halo-2"></div>
            <div class="ob-owner-observatory-halo halo-3"></div>

            <div class="ob-owner-observatory-core">
              <span class="owner-star star-a"></span>
              <span class="owner-star star-b"></span>
              <span class="owner-star star-c"></span>
              <span class="owner-star star-d"></span>
              <span class="owner-star star-e"></span>
              <span class="owner-star star-f"></span>

              <div class="ob-owner-dome-line"></div>
              <div class="ob-owner-dome-beam"></div>

              <div class="ob-owner-core-label">
                <span>OWNER ALTITUDE</span>
                <strong>Whole Observatory</strong>
              </div>
            </div>
          </div>
        </section>

        <section class="ob-owner-section ob-owner-mission-sky">
          <div class="ob-owner-section-head">
            <div>
              <span class="ob-owner-kicker">MISSION SKY</span>
              <h2>Your capital has different jobs.</h2>
            </div>
            <p>
              Soulaana keeps Trust, Personal, Simplee World, ATM,
              The Grounds, and Proof/Demo separate. Policy is visible;
              unverified balances and progress are not guessed.
            </p>
          </div>

          <div class="ob-owner-mission-grid">
            ${missions.map(missionCard).join("")}
          </div>
        </section>

        <section class="ob-owner-section ob-owner-attention">
          <div class="ob-owner-section-head compact">
            <div>
              <span class="ob-owner-kicker">OWNER ATTENTION</span>
              <h2>What actually deserves Solice.</h2>
            </div>
            <p>
              No giant queue. No proof wall. Soulaana elevates only the
              owner-level conditions that change a decision.
            </p>
          </div>

          <div class="ob-owner-attention-grid">
            ${attention.map(attentionCard).join("")}
          </div>
        </section>

        <section class="ob-owner-instrument-grid">
          <article class="ob-owner-instrument readiness">
            <div class="ob-owner-instrument-head">
              <span class="ob-owner-kicker">MANUAL LIVE READINESS</span>
              ${sourceChip(readiness.verified, readiness.label || "readiness")}
            </div>

            <h3>
              ${
                readiness.verified && readiness.score !== null
                  ? `${esc(readiness.score)}% evidence score`
                  : "Readiness evidence is guarded"
              }
            </h3>

            <p>${esc(briefing.readiness)}</p>

            <div class="ob-owner-boundary-strip">
              <span>Real Manual Live: locked</span>
              <span>Broker submit: disabled</span>
              <span>Live Auto: locked</span>
            </div>
          </article>

          <article class="ob-owner-instrument trust">
            <div class="ob-owner-instrument-head">
              <span class="ob-owner-kicker">SYSTEM TRUST</span>
              ${sourceChip(trust.verified, trust.label || "engine trust")}
            </div>

            <h3>
              ${
                trust.verified && trust.freshness_score !== null
                  ? `Freshness ${esc(trust.freshness_score)}`
                  : "I will not over-trust the feed."
              }
            </h3>

            <p>${esc(briefing.system_trust)}</p>

            <div class="ob-owner-trust-meter">
              <span style="width:${
                trust.verified && trust.freshness_score !== null
                  ? Math.max(0, Math.min(100, Number(trust.freshness_score)))
                  : 18
              }%"></span>
            </div>
          </article>

          <article class="ob-owner-instrument beta">
            <div class="ob-owner-instrument-head">
              <span class="ob-owner-kicker">PRIVATE BETA</span>
              ${sourceChip(beta.verified, beta.label || "beta control")}
            </div>

            <h3>Private stays private.</h3>
            <p>${esc(briefing.beta_state)}</p>

            <div class="ob-owner-boundary-strip">
              <span>No public launch</span>
              <span>No public proof</span>
              <span>Tower owns access</span>
            </div>
          </article>
        </section>

        <section class="ob-owner-lower-grid">
          <article class="ob-owner-lessons">
            <div class="ob-owner-section-head compact">
              <div>
                <span class="ob-owner-kicker">WHAT I'M LEARNING</span>
                <h2>Patterns across the Observatory.</h2>
              </div>
            </div>

            <p class="ob-owner-feature-copy">${esc(briefing.what_im_learning)}</p>

            <div class="ob-owner-pattern-list">
              ${patterns.map((item) => `
                <div class="ob-owner-pattern-item">
                  <strong>${esc(item.title)}</strong>
                  <span>${esc(item.detail)}</span>
                </div>
              `).join("")}
            </div>
          </article>

          <article class="ob-owner-since">
            <div class="ob-owner-section-head compact">
              <div>
                <span class="ob-owner-kicker">SINCE YOU WERE HERE</span>
                <h2>Only verified changes.</h2>
              </div>
            </div>

            <p class="ob-owner-feature-copy">${esc(briefing.what_changed)}</p>

            <div class="ob-owner-history-list">
              ${history.map(historyItem).join("")}
            </div>
          </article>
        </section>

        <section class="ob-owner-wait-strip">
          <div>
            <span class="ob-owner-kicker">WHAT CAN WAIT</span>
            <strong>${esc(briefing.what_can_wait)}</strong>
          </div>
          <div>
            <span class="ob-owner-kicker">OWNER ALTITUDE</span>
            <strong>${esc(briefing.owner_altitude || "")}</strong>
          </div>
        </section>

        <details class="ob-owner-evidence">
          <summary>Show me why</summary>
          <div class="ob-owner-evidence-body">
            <div>
              <span class="ob-owner-kicker">EXPLANATION RULE</span>
              <p>${esc(briefing.evidence_rule || "Soulaana explains first.")}</p>
            </div>

            <pre>${esc(JSON.stringify({
              source_state: contract.source_state,
              interpretation_state: contract.interpretation_state,
              boundaries: contract.boundaries
            }, null, 2))}</pre>
          </div>
        </details>
      </main>
    `;

    document.body.setAttribute(
      "data-ob-owner-dashboard-surface",
      "dormant-ready"
    );
    document.body.setAttribute(
      "data-ob-owner-dashboard-owner-only",
      "true"
    );
    document.body.setAttribute(
      "data-ob-owner-dashboard-live-auto-locked",
      "true"
    );
  };

  const boot = async () => {
    const contractApi = window.OB_OWNER_DASHBOARD_CONTRACT_V21;

    if (!contractApi) {
      throw new Error(
        "Owner Dashboard intelligence contract did not load."
      );
    }

    render(contractApi.getContract());

    try {
      const hydrated = await contractApi.hydrate();
      render(hydrated);
    } catch (_error) {
      // Fail closed: the guarded local contract remains visible.
      render(contractApi.getContract());
    }
  };

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_OWNER_DASHBOARD_SURFACE_V23_25 = Object.freeze({
    version: VERSION,
    render,
    boot,
    dormant: true,
    owner_only: true,
    live_auto_locked: true,
    broker_action_performed: false,
    capital_action_performed: false,
    permission_mutation_performed: false
  });
})();
