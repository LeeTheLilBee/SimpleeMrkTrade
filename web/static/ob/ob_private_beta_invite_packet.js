// OBSERVATORY_V38_PRIVATE_BETA_TESTER_INVITE_PACKET_BUILDER_JS

(function () {
  const VERSION = "OB_V38_PRIVATE_BETA_TESTER_INVITE_PACKET_BUILDER";
  const ENDPOINT = "/ob/private-beta-invite-packet.json";

  // V38 SMOKE MARKERS
  // Private Beta Tester Invite Packet Builder
  // protected tester invite packet
  // invite status
  // NDA status
  // tester instructions
  // rooms to visit
  // feedback requirements
  // what not to do
  // owner pre-invite checklist
  // Tower controlled invite
  // private beta only
  // no public signup
  // no public launch
  // no public proof
  // no broker wiring
  // No broker API
  // No auto execution
  // Live Auto Locked

  let packetState = {
    status: "booting",
    httpStatus: null,
    source: "waiting",
    payload: null,
    fallbackActive: true,
    error: null
  };

  function safeText(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    return String(value);
  }

  function launchPayload() {
    if (window.OB_PRIVATE_BETA_LAUNCH_CONTROL_V37_API && window.OB_PRIVATE_BETA_LAUNCH_CONTROL_V37_API.getState) {
      const state = window.OB_PRIVATE_BETA_LAUNCH_CONTROL_V37_API.getState();
      if (state && state.payload) return state.payload;
    }

    if (window.OB_PRIVATE_BETA_LAUNCH_CONTROL_V37) return window.OB_PRIVATE_BETA_LAUNCH_CONTROL_V37;

    return {
      go_no_go: "CONDITIONAL GO",
      score: 86,
      summary: { pass: 6, warn: 1, fail: 0, total: 7 },
      owner_final_actions: [
        "Confirm tester invite list and NDA status through Tower.",
        "Confirm Manual Live stays owner/manual only.",
        "Confirm no public proof, no public launch, no broker wiring."
      ]
    };
  }

  function testerOpsPayload() {
    if (window.OB_BETA_TESTER_OPS_V30) {
      return {
        testerChecklist: window.OB_BETA_TESTER_OPS_V30.testerChecklist || [],
        feedbackQuestions: window.OB_BETA_TESTER_OPS_V30.feedbackQuestions || [],
        ndaInviteRequired: true,
        privateBeta: true
      };
    }

    return {
      testerChecklist: [
        { title: "NDA / invite required", detail: "Tester access starts only after Tower-approved invite and NDA/access rules are complete." },
        { title: "Start in Dashboard", detail: "Check mode, Tower state, mission account, snapshot source, and Soulaana guidance." },
        { title: "Read Market Map", detail: "Observe constellation counts and candidate cards without treating them as execution orders." },
        { title: "Open Symbol Page", detail: "Open one star and check movement, risk, permission, and Soulaana explanation." },
        { title: "Trade Center review only", detail: "Review candidate queue and Manual Live status. No broker API. No auto execution." },
        { title: "Record confusion", detail: "Flag anything unclear, rushed, scary, broken, or hard to understand." },
        { title: "Review Center receipts", detail: "Confirm receipts are private, filtered, classified, and not public proof." },
        { title: "Owner review queue", detail: "Feedback goes to owner review, not public proof." }
      ],
      feedbackQuestions: [
        "What did you think OB wanted you to do first?",
        "Did anything feel like pressure to trade instead of review?",
        "Could you tell whether data was snapshot data or preview fallback?",
        "Could you find Tower state, Live Auto Locked, and no-execution boundaries?",
        "Which room confused you most?",
        "What felt broken, crowded, slow, or hard to trust?"
      ],
      ndaInviteRequired: true,
      privateBeta: true
    };
  }

  function defaultRoomsToVisit() {
    return [
      {
        room: "Dashboard",
        route: "/ob/dashboard",
        tester_goal: "Confirm the first screen explains mode, mission, Tower state, source trust, and next action.",
        owner_note: "Tester should not feel pushed to trade."
      },
      {
        room: "Market Map",
        route: "/ob/market-map",
        tester_goal: "Confirm the sky/constellation view is understandable and clearly source-labeled.",
        owner_note: "Tester should understand fresh/stale/fallback labels."
      },
      {
        room: "Symbol Page",
        route: "/ob/symbol/MU",
        tester_goal: "Confirm one-symbol context explains what OB sees and what is only read-only context.",
        owner_note: "Tester should understand this is not an execution instruction."
      },
      {
        room: "Trade Center",
        route: "/ob/trade-center",
        tester_goal: "Confirm candidate queue and Manual Live wording are review-only and owner/manual.",
        owner_note: "Tester should see No broker API, No auto execution, Live Auto Locked."
      },
      {
        room: "Review Center",
        route: "/ob/review-center",
        tester_goal: "Confirm receipts, proof/demo, and feedback are private and clearly classified.",
        owner_note: "Tester should not think proof is public."
      },
      {
        room: "Owner Console",
        route: "/ob/owner-console",
        tester_goal: "Owner-only review of diagnostics, source audit, and launch control.",
        owner_note: "Do not expose owner-only controls to normal testers unless clearance allows."
      }
    ];
  }

  function whatNotToDo() {
    return [
      "Do not share OB links publicly.",
      "Do not treat candidates as financial advice or execution orders.",
      "Do not connect a broker.",
      "Do not attempt automated execution.",
      "Do not screenshot or export private proof/demo/receipt data without Tower clearance.",
      "Do not invite another tester.",
      "Do not bypass Tower, NDA, invite, or permission controls.",
      "Do not rely on stale, missing, guarded, or fallback-only feed data as current."
    ];
  }

  function feedbackRequirements() {
    const tester = testerOpsPayload();
    return tester.feedbackQuestions.map((question, index) => ({
      id: "feedback_" + (index + 1),
      question,
      required: true,
      route: "/ob/review-center",
      owner_use: "Owner reviews confusion, pressure, trust, clarity, and room usability before expanding beta."
    }));
  }

  function buildFallbackPacket() {
    const launch = launchPayload();
    const tester = testerOpsPayload();
    const rooms = defaultRoomsToVisit();

    const preInvite = [
      {
        title: "Confirm invite clearance",
        detail: "Tester must be approved by owner/Tower before seeing OB.",
        status: "required"
      },
      {
        title: "Confirm NDA status",
        detail: "Tester must understand private beta, no sharing, no public proof, and no copying.",
        status: "required"
      },
      {
        title: "Confirm tester role",
        detail: "Tester is reviewing clarity and safety, not receiving trading access.",
        status: "required"
      },
      {
        title: "Confirm source/feed warning",
        detail: "Owner must tell tester whether feed is fresh, stale, guarded, or fallback-only.",
        status: safeText(launch.go_no_go, "").includes("CONDITIONAL") ? "review" : "ready"
      },
      {
        title: "Confirm Manual Live boundary",
        detail: "Manual Live is owner/manual only. No broker API. No auto execution. Live Auto Locked.",
        status: "required"
      },
      {
        title: "Confirm feedback path",
        detail: "Tester submits confusion, bug reports, and trust concerns to owner review.",
        status: "required"
      }
    ];

    return {
      version: VERSION,
      source: "v38_safe_invite_packet_fallback",
      packet_status: "fallback",
      invite_status: "owner_review_required",
      nda_status: "required_before_access",
      tester_access: "private_beta_invite_only",
      launch_control: {
        go_no_go: safeText(launch.go_no_go, "CONDITIONAL GO"),
        score: launch.score || 86
      },
      packet_summary: {
        pre_invite_items: preInvite.length,
        rooms_to_visit: rooms.length,
        feedback_questions: feedbackRequirements().length,
        what_not_to_do: whatNotToDo().length,
        owner_final_actions: Array.isArray(launch.owner_final_actions) ? launch.owner_final_actions.length : 0
      },
      pre_invite_checklist: preInvite,
      tester_instructions: [
        "Start in Dashboard.",
        "Move through Market Map, Symbol Page, Trade Center, and Review Center in order.",
        "Write down confusion immediately.",
        "Treat every engine/candidate/feed item as read-only context.",
        "Do not trade from OB instructions.",
        "Do not share screenshots, links, proof, receipts, or tester notes."
      ],
      rooms_to_visit: rooms,
      feedback_requirements: feedbackRequirements(),
      what_not_to_do: whatNotToDo(),
      owner_final_actions: launch.owner_final_actions || [
        "Confirm tester invite list and NDA status through Tower.",
        "Confirm Manual Live stays owner/manual only.",
        "Confirm no public proof, no public launch, no broker wiring."
      ],
      tower_boundaries: {
        read_only: true,
        private_beta_only: true,
        tower_controlled_invite: true,
        nda_required: true,
        no_public_signup: true,
        no_public_launch: true,
        no_public_proof: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        invite_packet_does_not_create_permission: true
      },
      warnings: [
        "Invite packet is owner-facing.",
        "Packet does not grant access by itself.",
        "Tester access must be Tower-controlled.",
        "No public launch.",
        "No broker wiring.",
        "No execution permission changed."
      ]
    };
  }

  function normalizePayload(raw) {
    const fallback = buildFallbackPacket();
    const safe = raw && typeof raw === "object" ? raw : {};

    return {
      version: safe.version || VERSION,
      source: safe.source || fallback.source,
      packet_status: safe.packet_status || "normalized",
      invite_status: safe.invite_status || fallback.invite_status,
      nda_status: safe.nda_status || fallback.nda_status,
      tester_access: safe.tester_access || fallback.tester_access,
      launch_control: {
        ...(fallback.launch_control || {}),
        ...(safe.launch_control || {})
      },
      packet_summary: {
        ...(fallback.packet_summary || {}),
        ...(safe.packet_summary || {})
      },
      pre_invite_checklist: Array.isArray(safe.pre_invite_checklist) ? safe.pre_invite_checklist : fallback.pre_invite_checklist,
      tester_instructions: Array.isArray(safe.tester_instructions) ? safe.tester_instructions : fallback.tester_instructions,
      rooms_to_visit: Array.isArray(safe.rooms_to_visit) ? safe.rooms_to_visit : fallback.rooms_to_visit,
      feedback_requirements: Array.isArray(safe.feedback_requirements) ? safe.feedback_requirements : fallback.feedback_requirements,
      what_not_to_do: Array.isArray(safe.what_not_to_do) ? safe.what_not_to_do : fallback.what_not_to_do,
      owner_final_actions: Array.isArray(safe.owner_final_actions) ? safe.owner_final_actions : fallback.owner_final_actions,
      tower_boundaries: {
        ...(fallback.tower_boundaries || {}),
        ...(safe.tower_boundaries || {}),
        read_only: true,
        private_beta_only: true,
        tower_controlled_invite: true,
        nda_required: true,
        no_public_signup: true,
        no_public_launch: true,
        no_public_proof: true,
        no_broker_wiring: true,
        no_broker_api: true,
        no_auto_execution: true,
        live_auto_locked: true,
        invite_packet_does_not_create_permission: true
      },
      warnings: Array.isArray(safe.warnings) ? safe.warnings : fallback.warnings
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);

    window.OB_PRIVATE_BETA_INVITE_PACKET_V38 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      private_beta_invite_packet_v38: normalized,
      tester_invite_packet_status: normalized.invite_status
    };

    window.dispatchEvent(new CustomEvent("obPrivateBetaInvitePacketUpdated", {
      detail: normalized
    }));

    return normalized;
  }

  async function fetchInvitePacket() {
    packetState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      packetState.httpStatus = response.status;

      if (response.ok) {
        const payload = await response.json();
        const normalized = expose(payload);

        packetState.status = "ready";
        packetState.source = normalized.source || "invite_packet_snapshot";
        packetState.payload = normalized;
        packetState.fallbackActive = false;
      } else if (response.status === 403 || response.status === 302 || response.status === 401) {
        const fallback = expose(buildFallbackPacket());

        packetState.status = "guarded_fallback";
        packetState.source = "guarded_invite_packet_route_fallback";
        packetState.payload = fallback;
        packetState.fallbackActive = true;
        packetState.error = "Invite packet route is protected or redirected. Safe fallback active.";
      } else {
        const fallback = expose(buildFallbackPacket());

        packetState.status = "http_fallback";
        packetState.source = "http_" + response.status + "_fallback";
        packetState.payload = fallback;
        packetState.fallbackActive = true;
        packetState.error = "Invite packet route returned HTTP " + response.status + ".";
      }
    } catch (error) {
      const fallback = expose(buildFallbackPacket());

      packetState.status = "error_fallback";
      packetState.source = "fetch_error_fallback";
      packetState.payload = fallback;
      packetState.fallbackActive = true;
      packetState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    return packetState;
  }

  function statusKind(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("ready") || text.includes("approved") || text.includes("complete")) return "green";
    if (text.includes("required") || text.includes("review") || text.includes("conditional")) return "gold";
    if (text.includes("blocked") || text.includes("denied") || text.includes("fail")) return "red";
    return "gold";
  }

  function card(label, value) {
    return `
      <div class="ob-beta-invite-packet-card">
        <span>${label}</span>
        <strong>${value}</strong>
      </div>
    `;
  }

  function row(item, index, status) {
    return `
      <div class="ob-beta-invite-packet-row">
        <div class="ob-beta-invite-packet-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.title || item.room || item.id, "Packet item")}</strong>
          <span>${safeText(item.status || item.route || item.required, status || "review")}</span>
        </div>
        <span>${safeText(item.detail || item.tester_goal || item.question || item, "Review this packet item.")}</span>
        <div class="ob-beta-invite-packet-status ${statusKind(item.status || status)}">${safeText(item.status || status, "review")}</div>
      </div>
    `;
  }

  function stringRow(text, index, status) {
    return row({ title: "Instruction", detail: text, status: status || "required" }, index, status || "required");
  }

  function panelHtml() {
    const payload = packetState.payload || buildFallbackPacket();
    const summary = payload.packet_summary || {};

    return `
      <div class="ob-beta-invite-packet-panel" id="obPrivateBetaInvitePacketPanel" data-ob-v38-private-beta-invite-packet="true">
        <div class="ob-beta-invite-packet-head">
          <div>
            <div class="ob-label">Private Beta Invite Packet · V38</div>
            <div class="ob-beta-invite-packet-title">Tester Invite Packet Builder</div>
            <div class="ob-beta-invite-packet-subtitle">
              ${safeText(payload.invite_status, "owner review required")} · ${safeText(payload.nda_status, "NDA required")} · ${safeText(packetState.status, "booting")}
            </div>
          </div>

          <div class="ob-beta-invite-packet-chip-row">
            <span class="ob-beta-invite-packet-chip ${statusKind(payload.invite_status)}">${safeText(payload.invite_status, "review")}</span>
            <span class="ob-beta-invite-packet-chip gold">NDA required</span>
            <span class="ob-beta-invite-packet-chip red">Private only</span>
          </div>
        </div>

        <div class="ob-beta-invite-packet-grid">
          ${card("Invite", safeText(payload.invite_status, "review"))}
          ${card("NDA", safeText(payload.nda_status, "required"))}
          ${card("Rooms", safeText(summary.rooms_to_visit, "6"))}
          ${card("Feedback", safeText(summary.feedback_questions, "0"))}
          ${card("Do-not", safeText(summary.what_not_to_do, "0"))}
          ${card("Access", "Tower")}
        </div>

        <div class="ob-beta-invite-packet-callout">
          <strong>Packet purpose</strong>
          <span>This packet prepares a tester for private beta review. It does not grant access, it does not create permission, and it does not open OB publicly.</span>
        </div>

        <div class="ob-beta-invite-packet-section">
          <div class="ob-beta-invite-packet-section-title">Owner pre-invite checklist</div>
          <div class="ob-beta-invite-packet-list">
            ${(payload.pre_invite_checklist || []).map((item, index) => row(item, index, "required")).join("")}
          </div>
        </div>

        <div class="ob-beta-invite-packet-section">
          <div class="ob-beta-invite-packet-section-title">Rooms to visit</div>
          <div class="ob-beta-invite-packet-list">
            ${(payload.rooms_to_visit || []).map((item, index) => row(item, index, "visit")).join("")}
          </div>
        </div>

        <div class="ob-beta-invite-packet-section">
          <div class="ob-beta-invite-packet-section-title">Tester instructions</div>
          <div class="ob-beta-invite-packet-list">
            ${(payload.tester_instructions || []).map((item, index) => stringRow(item, index, "required")).join("")}
          </div>
        </div>

        <div class="ob-beta-invite-packet-section">
          <div class="ob-beta-invite-packet-section-title">What not to do</div>
          <div class="ob-beta-invite-packet-list">
            ${(payload.what_not_to_do || []).map((item, index) => stringRow(item, index, "do not")).join("")}
          </div>
        </div>

        <div class="ob-beta-invite-packet-note">
          <strong>Soulaana:</strong><br>
          The invite packet protects the door. Testers help us find confusion. They do not receive public signals, public proof, or trading access.
        </div>

        <div class="ob-beta-invite-packet-boundary">
          <strong>Boundary:</strong><br>
          Private beta only. Tower-controlled invite. NDA required. No public signup. No public launch. No public proof. No broker wiring. No broker API. No auto execution. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obPrivateBetaInvitePacketPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const launch = document.getElementById("obPrivateBetaLaunchControlPanel");
    const audit = document.getElementById("obOwnerSourceAuditPanel");
    const mapping = document.getElementById("obEngineRoomMappingPanel");
    const trust = document.getElementById("obEngineTrustLabelsPanel");
    const qa = document.getElementById("obPrivateBetaQaPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (launch && launch.parentNode) {
      launch.insertAdjacentElement("afterend", panel);
    } else if (audit && audit.parentNode) {
      audit.insertAdjacentElement("afterend", panel);
    } else if (mapping && mapping.parentNode) {
      mapping.insertAdjacentElement("afterend", panel);
    } else if (trust && trust.parentNode) {
      trust.insertAdjacentElement("afterend", panel);
    } else if (qa && qa.parentNode) {
      qa.insertAdjacentElement("afterend", panel);
    } else {
      layer.appendChild(panel);
    }
  }

  function setFlags() {
    const payload = packetState.payload || buildFallbackPacket();

    document.body.setAttribute("data-ob-v38-private-beta-invite-packet", "ready");
    window.OB_V38_PRIVATE_BETA_INVITE_PACKET_STATE = {
      version: VERSION,
      status: packetState.status,
      fallbackActive: packetState.fallbackActive,
      inviteStatus: payload.invite_status,
      ndaStatus: payload.nda_status,
      privateBetaOnly: true,
      towerControlledInvite: true,
      noPublicSignup: true,
      noPublicLaunch: true,
      noPublicProof: true,
      noBrokerWiring: true,
      noBrokerApi: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(buildFallbackPacket());

    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchInvitePacket();
    }, 1860);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.addEventListener("obPrivateBetaLaunchControlUpdated", function () {
    renderPanel();
    setFlags();
  });

  window.OB_PRIVATE_BETA_INVITE_PACKET_V38_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return packetState; },
    buildFallbackPacket,
    normalizePayload,
    expose,
    fetchInvitePacket,
    renderPanel,
    setFlags
  };
})();
