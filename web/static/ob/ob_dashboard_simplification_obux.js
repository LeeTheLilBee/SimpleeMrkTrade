// OBUX010 — DASHBOARD MAIN-SURFACE SIMPLIFICATION
//
// This file intentionally loads LAST on dashboard.html.
//
// Historic OB packs may still create engineering, readiness, proof,
// beta, rehearsal, receipt, audit, feed, diagnostic, and contract panels.
//
// Those packs remain loaded.
// Their data/functions remain available.
// Their DOM nodes are MOVED — not deleted — into Show me why.
//
// Moving a DOM node preserves attached listeners.

(function () {
  "use strict";

  const VERSION = "OBUX010";

  const SHELL_ID = "obuxDashboardShell";

  const EVIDENCE_ID = "obuxDashboardEvidenceSink";


  const technicalTerms = [
    "data bridge",
    "engine feed adapter",
    "engine feed",
    "feed adapter",
    "feed diagnostics",
    "engine diagnostics",
    "engine trust",
    "engine room mapping",
    "source audit",
    "readiness checkpoint",
    "readiness",
    "beta readiness",
    "private beta",
    "tester ops",
    "tester operations",
    "qa pass",
    "proof packet",
    "proof",
    "receipt",
    "rehearsal",
    "practice loop",
    "operator confidence",
    "dry run",
    "dry-run",
    "persistence",
    "launch control",
    "invite packet",
    "feedback intake",
    "feedback review",
    "session runbook",
    "issue triage",
    "fix verification",
    "next tester",
    "account experience",
    "manual live level 1",
    "manual live safety",
    "decision packet",
    "broker checklist",
    "position monitor",
    "review foundation",
    "evidence readiness",
    "capital rule",
    "step-up enforcement",
    "candidate handoff",
    "room data polish",
    "snapshot display",
    "candidate signal card normalization"
  ];


  const protectedTerms = [
    "menu",
    "navigation",
    "notifications",
    "settings",
    "mission account",
    "account switch",
    "tower return"
  ];


  function normalize(value) {
    return String(
      value
      || ""
    )
      .replace(/\s+/g, " ")
      .trim()
      .toLowerCase();
  }


  function insideCore(node) {
    return Boolean(
      node
      && node.closest
      && node.closest(
        "#" + SHELL_ID
      )
    );
  }


  function insideEvidence(node) {
    return Boolean(
      node
      && node.closest
      && node.closest(
        "#" + EVIDENCE_ID
      )
    );
  }


  function protectedUI(node) {
    if (
      !node
      || !node.closest
    ) {
      return false;
    }


    if (
      node.closest(
        ".ob-header,"
        + ".ob-nav,"
        + ".ob-nav-shell,"
        + "[class*='navigation'],"
        + "[class*='notification'],"
        + "[class*='settings'],"
        + "[class*='mission-account']"
      )
    ) {
      return true;
    }


    const text = normalize(
      node.textContent
    );


    return protectedTerms.some(
      (term) => text.startsWith(term)
    );
  }


  function technicalPanel(node) {
    if (
      !node
      || node.nodeType !== 1
      || insideCore(node)
      || insideEvidence(node)
      || protectedUI(node)
    ) {
      return false;
    }


    const id = normalize(
      node.id
    );

    const classes = normalize(
      node.className
    );

    const text = normalize(
      node.textContent
    ).slice(
      0,
      1800
    );


    const combined = (
      id
      + " "
      + classes
      + " "
      + text
    );


    return technicalTerms.some(
      (term) => combined.includes(term)
    );
  }


  function findPanel(node) {
    if (
      !node
      || node.nodeType !== 1
    ) {
      return null;
    }


    if (
      node.matches(
        ".ob-panel,"
        + "section,"
        + "article,"
        + "[id$='Panel'],"
        + "[id*='Checkpoint'],"
        + "[id*='Readiness'],"
        + "[id*='Feed'],"
        + "[id*='Proof'],"
        + "[id*='Receipt'],"
        + "[id*='Audit']"
      )
    ) {
      return node;
    }


    if (!node.closest) {
      return null;
    }


    return node.closest(
      ".ob-panel,"
      + "section,"
      + "article,"
      + "[id$='Panel']"
    );
  }


  function moveOne(node) {
    const sink = document.getElementById(
      EVIDENCE_ID
    );


    if (!sink) {
      return false;
    }


    const panel = findPanel(
      node
    );


    if (
      !panel
      || panel === sink
      || insideCore(panel)
      || insideEvidence(panel)
      || protectedUI(panel)
      || !technicalPanel(panel)
    ) {
      return false;
    }


    panel.setAttribute(
      "data-obux-dashboard-evidence-moved",
      "true"
    );


    sink.appendChild(
      panel
    );


    const empty = sink.querySelector(
      ".obux-dashboard-evidence-empty"
    );


    if (empty) {
      empty.remove();
    }


    return true;
  }


  function sweep() {
    const sink = document.getElementById(
      EVIDENCE_ID
    );


    if (!sink) {
      return;
    }


    const candidates = Array.from(
      document.querySelectorAll(
        ".ob-layer > *,"
        + "#ob-app > *,"
        + ".ob-panel,"
        + "[id$='Panel'],"
        + "[id*='Checkpoint'],"
        + "[id*='Readiness'],"
        + "[id*='Feed'],"
        + "[id*='Proof'],"
        + "[id*='Receipt'],"
        + "[id*='Audit']"
      )
    );


    let moved = 0;


    candidates.forEach(
      (candidate) => {
        if (
          moveOne(
            candidate
          )
        ) {
          moved += 1;
        }
      }
    );


    window.OBUX_DASHBOARD_SIMPLIFICATION_STATE = {
      version: VERSION,
      moved_count: (
        document.querySelectorAll(
          '[data-obux-dashboard-evidence-moved="true"]'
        ).length
      ),
      last_sweep_moved: moved,
      panels_deleted: false,
      evidence_drawer_default_open: false
    };
  }


  function startObserver() {
    const target = document.getElementById(
      "ob-app"
    );


    if (!target) {
      return;
    }


    const observer = new MutationObserver(
      (mutations) => {
        let relevant = false;


        mutations.forEach(
          (mutation) => {
            mutation.addedNodes.forEach(
              (node) => {
                if (
                  node.nodeType === 1
                  && !insideEvidence(node)
                ) {
                  relevant = true;
                }
              }
            );
          }
        );


        if (relevant) {
          window.requestAnimationFrame(
            sweep
          );
        }
      }
    );


    observer.observe(
      target,
      {
        childList: true,
        subtree: true
      }
    );


    window.OBUX_DASHBOARD_EVIDENCE_OBSERVER = (
      observer
    );
  }


  function init() {
    // All synchronous DOMContentLoaded handlers registered
    // by previously loaded Dashboard scripts run before this one.
    sweep();

    startObserver();


    // One delayed sweep catches panels created after promises/fetches resolve.
    window.setTimeout(
      sweep,
      400
    );

    window.setTimeout(
      sweep,
      1200
    );
  }


  if (
    document.readyState === "loading"
  ) {
    document.addEventListener(
      "DOMContentLoaded",
      init,
      {
        once: true
      }
    );

  } else {
    init();
  }

})();
