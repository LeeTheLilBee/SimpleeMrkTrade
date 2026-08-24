// OBSERVATORY_OBUX058_CANONICAL_SESSION_STATE

(function (global) {
  "use strict";

  const SCHEMA = 1;

  const PERSIST_KEY =
    "ob.session.state.v1";

  const EPHEMERAL_KEY =
    "ob.session.ephemeral.v1";

  const TAB_ID_KEY =
    "ob.session.tab-id.v1";

  const TAB_LEASE_KEY =
    "ob.session.tab-lease.v1";

  const MAX_RECENT_SESSIONS = 10;

  const MAX_FEEDBACK = 25;


  function safeParse(
    value,
    fallback
  ) {
    try {
      const parsed =
        JSON.parse(value);

      if (
        parsed
        && typeof parsed === "object"
      ) {
        return parsed;
      }
    } catch (_) {}

    return fallback;
  }


  function now() {
    return new Date().toISOString();
  }


  function randomId() {
    if (
      global.crypto
      && typeof global.crypto.randomUUID
      === "function"
    ) {
      return global.crypto.randomUUID();
    }

    return (
      "ob-"
      + Date.now().toString(36)
      + "-"
      + Math.random()
        .toString(36)
        .slice(2, 10)
    );
  }


  function defaultPersistent() {
    return {
      schemaVersion: SCHEMA,

      beta: {
        sopAcknowledgedVersion: null,
        whatsNewAcknowledgedVersion: null,
      },

      preferences: {
        compactWhenLowEnergy: true,
      },

      selectedMode: "Survey",

      lastSafeRoute:
        "/ob/dashboard",

      recentSessions: [],

      feedback: [],

      notificationReadiness: {
        inApp: "unknown",
        browser: "unknown",
        email: "unknown",
        lastDelivery: null,
        source: "not_connected",
      },

      guidedFirstSessionComplete:
        false,
    };
  }


  function defaultEphemeral() {
    return {
      schemaVersion: SCHEMA,

      sessionId: randomId(),

      startedAt: now(),

      activeRoom: "Dashboard",

      selectedSymbol: null,

      checkIn: {
        status: "not_started",
        response: null,
        rememberForPrivateReview: false,
      },

      guidance: {
        enabled: false,
        step: "dashboard",
      },

      activeTrackedPositions: 0,

      activeTrackedPositionsSource:
        "unknown",

      feedbackThisSession: [],

      reflection: null,

      closeStatus: "open",

      returnReason: null,

      lastActivityAt: now(),
    };
  }


  function loadPersistent() {
    const base =
      defaultPersistent();

    const stored =
      safeParse(
        global.localStorage.getItem(
          PERSIST_KEY
        ),
        {}
      );

    return {
      ...base,
      ...stored,

      beta: {
        ...base.beta,
        ...(stored.beta || {}),
      },

      preferences: {
        ...base.preferences,
        ...(stored.preferences || {}),
      },

      notificationReadiness: {
        ...base.notificationReadiness,
        ...(stored.notificationReadiness || {}),
      },

      recentSessions:
        Array.isArray(
          stored.recentSessions
        )
          ? stored.recentSessions
              .slice(
                0,
                MAX_RECENT_SESSIONS
              )
          : [],

      feedback:
        Array.isArray(
          stored.feedback
        )
          ? stored.feedback
              .slice(
                0,
                MAX_FEEDBACK
              )
          : [],
    };
  }


  function loadEphemeral() {
    const base =
      defaultEphemeral();

    const stored =
      safeParse(
        global.sessionStorage.getItem(
          EPHEMERAL_KEY
        ),
        {}
      );

    /*
      A deliberately closed OB session
      starts a new ephemeral session
      on the next OB launch.

      Persistent closeout/resume context
      remains available separately.
    */
    if (
      stored.closeStatus
      === "closed"
    ) {
      return base;
    }

    return {
      ...base,
      ...stored,

      checkIn: {
        ...base.checkIn,
        ...(stored.checkIn || {}),
      },

      guidance: {
        ...base.guidance,
        ...(stored.guidance || {}),
      },

      feedbackThisSession:
        Array.isArray(
          stored.feedbackThisSession
        )
          ? stored.feedbackThisSession
          : [],
    };
  }


  let persistent =
    loadPersistent();

  let ephemeral =
    loadEphemeral();


  function emit(
    name,
    detail
  ) {
    global.dispatchEvent(
      new CustomEvent(
        name,
        {
          detail,
        }
      )
    );
  }


  function snapshot() {
    return JSON.parse(
      JSON.stringify(
        {
          persistent,
          ephemeral,
        }
      )
    );
  }


  function savePersistent() {
    global.localStorage.setItem(
      PERSIST_KEY,
      JSON.stringify(
        persistent
      )
    );

    emit(
      "ob:session-persistent-change",
      snapshot()
    );
  }


  function saveEphemeral() {
    ephemeral.lastActivityAt =
      now();

    global.sessionStorage.setItem(
      EPHEMERAL_KEY,
      JSON.stringify(
        ephemeral
      )
    );

    emit(
      "ob:session-change",
      snapshot()
    );
  }


  function setMode(mode) {
    const normalized =
      String(
        mode || ""
      ).trim();

    const allowed = [
      "Survey",
      "Paper",
      "Manual Live",
      "Hybrid",
      "Automated",
    ];

    if (
      !allowed.includes(
        normalized
      )
    ) {
      return false;
    }

    persistent.selectedMode =
      normalized;

    savePersistent();

    return true;
  }


  function recordRoute(
    route,
    room
  ) {
    const safe =
      String(
        route || ""
      );

    const allowed =
      safe.startsWith(
        "/ob/"
      )
      || safe
        === "/trade-center"
      || safe
        === "/review-center";

    if (!allowed) {
      return;
    }

    persistent.lastSafeRoute =
      safe;

    if (room) {
      ephemeral.activeRoom =
        room;
    }

    savePersistent();
    saveEphemeral();
  }


  function recordSymbol(
    symbol
  ) {
    const clean =
      String(
        symbol || ""
      )
        .toUpperCase()
        .replace(
          /[^A-Z0-9.\-]/g,
          ""
        )
        .slice(
          0,
          12
        );

    ephemeral.selectedSymbol =
      clean || null;

    saveEphemeral();
  }


  function acknowledgeSop(
    version
  ) {
    persistent
      .beta
      .sopAcknowledgedVersion =
        String(
          version || ""
        );

    savePersistent();
  }


  function acknowledgeWhatsNew(
    version
  ) {
    persistent
      .beta
      .whatsNewAcknowledgedVersion =
        String(
          version || ""
        );

    savePersistent();
  }


  function saveCheckIn(
    response,
    rememberForPrivateReview
  ) {
    ephemeral.checkIn = {
      status: "completed",

      response: {
        feeling:
          response
          && response.feeling
            ? String(
                response.feeling
              )
            : null,

        energy:
          response
          && response.energy
            ? String(
                response.energy
              )
            : null,

        focus:
          response
          && response.focus
            ? String(
                response.focus
              )
            : null,

        pace:
          response
          && response.pace
            ? String(
                response.pace
              )
            : null,

        intent:
          response
          && response.intent
            ? String(
                response.intent
              )
            : null,
      },

      rememberForPrivateReview:
        Boolean(
          rememberForPrivateReview
        ),
    };

    saveEphemeral();
  }


  function skipCheckIn() {
    ephemeral.checkIn = {
      status: "skipped",
      response: null,
      rememberForPrivateReview: false,
    };

    saveEphemeral();
  }


  function setGuidance(
    enabled,
    step
  ) {
    ephemeral.guidance = {
      enabled:
        Boolean(
          enabled
        ),

      step:
        step
        || ephemeral
          .guidance
          .step
        || "dashboard",
    };

    if (
      !enabled
      && step === "complete"
    ) {
      persistent
        .guidedFirstSessionComplete =
          true;

      savePersistent();
    }

    saveEphemeral();
  }


  function updateNotificationReadiness(
    next
  ) {
    persistent.notificationReadiness = {
      ...persistent.notificationReadiness,
      ...(next || {}),
    };

    savePersistent();
  }


  function setTrackedPositions(
    count,
    source
  ) {
    const numeric =
      Number(
        count
      );

    ephemeral.activeTrackedPositions =
      Number.isFinite(
        numeric
      )
      && numeric > 0
        ? Math.floor(
            numeric
          )
        : 0;

    ephemeral.activeTrackedPositionsSource =
      source || "unknown";

    saveEphemeral();
  }


  function captureFeedback(
    payload
  ) {
    const item = {
      id: randomId(),

      createdAt: now(),

      room:
        ephemeral.activeRoom,

      mode:
        persistent.selectedMode,

      symbol:
        ephemeral.selectedSymbol,

      build:
        document.body
          ? (
              document.body
                .dataset
                .obBuild
              || "unknown"
            )
          : "unknown",

      sopVersion:
        document.body
          ? (
              document.body
                .dataset
                .obSopVersion
              || "unknown"
            )
          : "unknown",

      category:
        payload
        && payload.category
          ? String(
              payload.category
            )
          : "Other",

      message:
        payload
        && payload.message
          ? String(
              payload.message
            ).slice(
              0,
              4000
            )
          : "",

      component:
        payload
        && payload.component
          ? String(
              payload.component
            ).slice(
              0,
              200
            )
          : null,

      sourceState:
        payload
        && payload.sourceState
          ? String(
              payload.sourceState
            ).slice(
              0,
              500
            )
          : null,

      delivery:
        "local_queue",
    };

    persistent
      .feedback
      .unshift(
        item
      );

    persistent.feedback =
      persistent.feedback.slice(
        0,
        MAX_FEEDBACK
      );

    ephemeral
      .feedbackThisSession
      .unshift(
        item.id
      );

    savePersistent();
    saveEphemeral();

    emit(
      "ob:beta-feedback",
      item
    );

    return item;
  }


  function setReflection(
    value
  ) {
    ephemeral.reflection =
      value
        ? String(
            value
          ).slice(
            0,
            500
          )
        : null;

    saveEphemeral();
  }


  function resumeCandidate() {
    /*
      1. Crash/refresh recovery:
         current ephemeral session is still open.

      2. Intentional Back-to-Tower:
         last closed session explicitly allowed resume.
    */

    if (
      ephemeral.closeStatus
        === "open"
      && persistent.lastSafeRoute
        !== "/ob/dashboard"
    ) {
      return {
        kind: "recovered_open_session",
        route:
          persistent.lastSafeRoute,
        room:
          ephemeral.activeRoom,
      };
    }

    const last =
      persistent
        .recentSessions
        .length
          ? persistent
              .recentSessions[0]
          : null;

    if (
      last
      && last.preserveForResume
      && last.lastRoute
      && last.lastRoute
        !== "/ob/dashboard"
    ) {
      return {
        kind: "return_to_tower_resume",
        route:
          last.lastRoute,
        room:
          last.lastRoom,
      };
    }

    return null;
  }


  function consumeResume() {
    if (
      persistent
        .recentSessions
        .length
    ) {
      persistent
        .recentSessions[0]
        .preserveForResume =
          false;
    }

    savePersistent();
  }


  function dismissResume() {
    persistent.lastSafeRoute =
      "/ob/dashboard";

    consumeResume();
  }


  function close(
    reason,
    preserveForResume
  ) {
    const checkInForHistory =
      ephemeral.checkIn
      && ephemeral.checkIn.status
        === "completed"
      && ephemeral
        .checkIn
        .rememberForPrivateReview
          ? ephemeral
              .checkIn
              .response
          : null;

    const receipt = {
      sessionId:
        ephemeral.sessionId,

      startedAt:
        ephemeral.startedAt,

      endedAt:
        now(),

      lastRoom:
        ephemeral.activeRoom,

      lastRoute:
        persistent.lastSafeRoute,

      mode:
        persistent.selectedMode,

      checkIn:
        checkInForHistory,

      reflection:
        ephemeral.reflection,

      feedbackCount:
        ephemeral
          .feedbackThisSession
          .length,

      reason:
        reason || "closed",

      preserveForResume:
        Boolean(
          preserveForResume
        ),
    };

    persistent
      .recentSessions
      .unshift(
        receipt
      );

    persistent.recentSessions =
      persistent
        .recentSessions
        .slice(
          0,
          MAX_RECENT_SESSIONS
        );

    ephemeral.closeStatus =
      "closed";

    ephemeral.returnReason =
      reason || "closed";

    savePersistent();
    saveEphemeral();

    return receipt;
  }


  function clearEphemeral() {
    global
      .sessionStorage
      .removeItem(
        EPHEMERAL_KEY
      );

    ephemeral =
      defaultEphemeral();

    emit(
      "ob:session-cleared",
      snapshot()
    );
  }


  function startFresh() {
    dismissResume();
    clearEphemeral();
    saveEphemeral();
  }


  function touch() {
    ephemeral.lastActivityAt =
      now();

    global
      .sessionStorage
      .setItem(
        EPHEMERAL_KEY,
        JSON.stringify(
          ephemeral
        )
      );
  }


  let tabId =
    global
      .sessionStorage
      .getItem(
        TAB_ID_KEY
      );

  if (!tabId) {
    tabId =
      randomId();

    global
      .sessionStorage
      .setItem(
        TAB_ID_KEY,
        tabId
      );
  }

  let tabClaimed = false;


  function claimTab(
    force
  ) {
    const lease =
      safeParse(
        global
          .localStorage
          .getItem(
            TAB_LEASE_KEY
          ),
        {}
      );

    const leaseTime =
      lease
      && lease.at
        ? Date.parse(
            lease.at
          )
        : 0;

    const activeOther =
      Boolean(
        lease
        && lease.tabId
        && lease.tabId
          !== tabId
        && leaseTime
        && Date.now()
          - leaseTime
          < 15000
      );

    if (
      activeOther
      && !force
    ) {
      return {
        activeOther: true,
        otherTabId:
          lease.tabId,
      };
    }

    global
      .localStorage
      .setItem(
        TAB_LEASE_KEY,
        JSON.stringify(
          {
            tabId,
            at: now(),
          }
        )
      );

    tabClaimed = true;

    return {
      activeOther: false,
      otherTabId: null,
    };
  }


  function releaseTab() {
    const lease =
      safeParse(
        global
          .localStorage
          .getItem(
            TAB_LEASE_KEY
          ),
        {}
      );

    if (
      lease.tabId
      === tabId
    ) {
      global
        .localStorage
        .removeItem(
          TAB_LEASE_KEY
        );
    }

    tabClaimed = false;
  }


  const heartbeat =
    global.setInterval(
      function () {
        if (!tabClaimed) {
          return;
        }

        global
          .localStorage
          .setItem(
            TAB_LEASE_KEY,
            JSON.stringify(
              {
                tabId,
                at: now(),
              }
            )
          );
      },
      5000
    );


  [
    "pointerdown",
    "keydown",
    "scroll",
    "touchstart",
  ].forEach(
    function (
      eventName
    ) {
      global.addEventListener(
        eventName,
        touch,
        {
          passive: true,
        }
      );
    }
  );


  global.addEventListener(
    "pagehide",
    function () {
      global.clearInterval(
        heartbeat
      );
    }
  );


  global.OBSessionState =
    Object.freeze(
      {
        schemaVersion:
          SCHEMA,

        snapshot,

        setMode,

        recordRoute,

        recordSymbol,

        acknowledgeSop,

        acknowledgeWhatsNew,

        saveCheckIn,

        skipCheckIn,

        setGuidance,

        updateNotificationReadiness,

        setTrackedPositions,

        captureFeedback,

        setReflection,

        resumeCandidate,

        consumeResume,

        dismissResume,

        close,

        clearEphemeral,

        startFresh,

        touch,

        claimTab,

        releaseTab,
      }
    );

  saveEphemeral();

})(window);
