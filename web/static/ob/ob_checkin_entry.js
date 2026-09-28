// OBUX106–110 · Unified check-in-first Observatory arrival.
// Dashboard is mounted underneath the privacy cover. This is not Tower authentication.
// Presentation preferences cannot change market truth, permission, rankings or trades.
(function (global) {
  "use strict";
  const state = () => global.OBSessionState;
  const mount = () => document.getElementById("obArrivalRoot");
  let running = false;
  function clean(value) {
    return String(value == null ? "" : value).replace(/&/g, "&amp;")
      .replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function internalReturn() {
    try {
      const source = new URL(document.referrer);
      return source.origin === global.location.origin
        && source.pathname.startsWith("/ob/");
    } catch (_) { return false; }
  }
  function choices(key, options, values) {
    return '<fieldset class="ob-entry-options"><legend>'
      + clean(key === "feeling" ? "How are you feeling?"
        : key === "energy" ? "Your energy"
        : key === "focus" ? "Your focus"
        : key === "pace" ? "Your pace" : "What brings you here?")
      + '</legend>' + options.map(value => {
        const checked = values[key] === value ? " checked" : "";
        return '<label><input type="radio" name="' + key + '" value="' + clean(value)
          + '"' + checked + ' /><span>' + clean(value) + '</span></label>';
      }).join("") + '</fieldset>';
  }
  function run(force) {
    if (running || !mount() || !state()) return Promise.resolve(false);
    const fresh = Boolean(force) || new URLSearchParams(global.location.search)
      .get("ob_arrival") === "fresh";
    const snapshot = state().snapshot();
    if (!fresh && internalReturn()
      && snapshot.ephemeral.checkIn.status !== "not_started") {
      document.documentElement.classList.remove("ob-entry-pending");
      return Promise.resolve(false);
    }
    running = true;
    const body = document.body.dataset;
    const firstSop = snapshot.persistent.beta.sopAcknowledgedVersion !== body.obSopVersion;
    const changed = !firstSop && snapshot.persistent.beta.whatsNewAcknowledgedVersion
      !== body.obWhatsNewVersion;
    const steps = [{kind:"welcome", title:"Welcome to your Observatory.", intro:
      "Before we enter the sky, check in with Soulaana. This takes only a moment, and the market remains the market."}];
    if (firstSop || changed) steps.push({kind:"beta", title:firstSop
      ? "A few things before we explore." : "What's changed in the Observatory?",
      intro: firstSop
        ? "Private beta begins in Survey and Paper. Missing or stale evidence stays visible. Manual Live, capital movement and automated trading are never unlocked by this check-in."
        : "This build has changed. Continue to review the updated entry experience and resume Survey/Paper with current source labels."});
    steps.push(
      {kind:"arrive", title:"How are you arriving?", intro:"Just context for presentation and pace. Your answers are optional."},
      {kind:"pace", title:"How should we move today?", intro:"Soulaana can adapt explanation density, not trading facts or decisions."},
      {kind:"intent", title:"What brings you to the Observatory?", intro:"Choose one, or leave everything unanswered."},
      {kind:"finish", title:"Your sky is waiting.", intro:"Enter the actual Dashboard. No extra landing page or second sign-in."}
    );
    let index = 0;
    let skipped = false;
    let acceptedSop = !firstSop;
    let remember = false;
    const values = {feeling:null,energy:null,focus:null,pace:null,intent:null};
    const host = mount();
    return new Promise(resolve => {
      function complete() {
        // A beta acknowledgment is recorded only after explicit checkbox acceptance.
        if (firstSop && acceptedSop) state().acknowledgeSop(body.obSopVersion);
        if (body.obWhatsNewVersion && (firstSop || changed))
          state().acknowledgeWhatsNew(body.obWhatsNewVersion);
        if (skipped) state().skipCheckIn();
        else state().saveCheckIn(values, remember);
        host.replaceChildren();
        document.documentElement.classList.remove("ob-entry-pending");
        document.body.classList.add("ob-observatory-awake");
        running = false;
        if (fresh && global.history && typeof global.history.replaceState === "function") {
          const next = new URL(global.location.href);
          next.searchParams.delete("ob_arrival");
          global.history.replaceState({}, "", next.pathname + next.search + next.hash);
        }
        global.dispatchEvent(new CustomEvent("ob:arrival-complete"));
        resolve(true);
      }
      function render() {
        const step = steps[index];
        let contents = "";
        if (step.kind === "beta") {
          contents = firstSop
            ? '<label class="ob-entry-check"><input type="checkbox" data-accept'
                + (acceptedSop ? " checked" : "") + ' />I understand this is a private beta and this check-in cannot authorize trading.</label>'
            : '<p>New experience version: ' + clean(body.obWhatsNewVersion) + '</p>';
        }
        if (step.kind === "arrive") contents =
          choices("feeling",["Focused","Good","Neutral","Off","Overwhelmed"],values)
          + choices("energy",["Low","Steady","High"],values);
        if (step.kind === "pace") contents =
          choices("focus",["Scattered","Okay","Locked in"],values)
          + choices("pace",["Rushed","Normal","Plenty of time"],values);
        if (step.kind === "intent") contents =
          choices("intent",["Just looking","Research","Paper practice","Review","Active work"],values)
          + '<label class="ob-entry-check"><input type="checkbox" data-remember'
          + (remember ? " checked" : "") + ' />Use this check-in in my private session review. Otherwise it stays session-only.</label>';
        const dots = steps.map((_,n) =>
          '<span' + (n===index ? ' aria-current="step"' : "") + '></span>').join("");
        host.innerHTML = '<div class="ob-entry-screen"><section class="ob-entry-dialog" role="dialog" aria-modal="true"'
          + ' aria-label="Observatory welcome and session check-in" tabindex="-1">'
          + '<span class="ob-entry-kicker">THE OBSERVATORY · SOULAANA CHECK-IN</span>'
          + '<div class="ob-entry-orbit" aria-hidden="true">✦</div>'
          + '<h2>' + clean(step.title) + '</h2><p>' + clean(step.intro) + '</p>'
          + contents + '<div class="ob-entry-progress" aria-label="Check-in progress">' + dots + '</div>'
          + '<div class="ob-entry-actions">'
          + (index ? '<button type="button" data-prev>← Back</button>' : "")
          + (index >= steps.findIndex(item => item.kind === "arrive") && step.kind !== "finish"
              ? '<button type="button" data-skip>Skip check-in</button>' : "")
          + '<button type="button" data-next>'
          + (step.kind === "finish" ? "Enter the Observatory →" : "Continue →")
          + '</button><span class="ob-entry-meta">' + (index+1) + " / " + steps.length
          + '</span></div></section></div>';
        const box = host.querySelector(".ob-entry-dialog");
        box.addEventListener("keydown", e => {
          if (e.key !== "Tab") return;
          const focusable = [...box.querySelectorAll('button:not([disabled]),input:not([disabled])')]
            .filter(element => element.offsetParent !== null);
          if (!focusable.length) return;
          if (e.shiftKey && document.activeElement === focusable[0]) {
            e.preventDefault(); focusable[focusable.length-1].focus();
          } else if (!e.shiftKey && document.activeElement === focusable[focusable.length-1]) {
            e.preventDefault(); focusable[0].focus();
          }
        });
        box.addEventListener("change", e => {
          if (e.target.matches('input[type="radio"]')) values[e.target.name] = e.target.value;
          if (e.target.matches("[data-accept]")) acceptedSop = e.target.checked;
          if (e.target.matches("[data-remember]")) remember = e.target.checked;
        });
        const previous = box.querySelector("[data-prev]");
        if (previous) previous.addEventListener("click", () => { index--; render(); });
        const skip = box.querySelector("[data-skip]");
        if (skip) skip.addEventListener("click", () => {
          skipped = true;
          index = steps.length - 1;
          render();
        });
        const next = box.querySelector("[data-next]");
        next.addEventListener("click", () => {
          if (step.kind === "beta" && firstSop && !acceptedSop) {
            const warning = box.querySelector("[data-warning]");
            if (!warning) {
              const p = document.createElement("p"); p.className="ob-entry-error";
              p.dataset.warning = "true"; p.textContent = "Confirm the beta boundary to continue.";
              next.parentNode.before(p);
            }
            return;
          }
          if (step.kind === "finish") { complete(); return; }
          index++; render();
        });
        next.focus();
      }
      try { render(); } catch (err) {
        // Do not unmask the dashboard on an incomplete or failed entry.
        host.innerHTML = '<div class="ob-entry-screen"><section class="ob-entry-dialog" role="alert">'
          + '<h2>Observatory check-in is unavailable.</h2><p>Return to Tower and try again. No session choice was applied.</p>'
          + '<a href="/tower/return/observatory">Back to Tower</a></section></div>';
        running = false; resolve(false);
      }
    });
  }
  global.OBSessionArrival = Object.freeze({
    run: () => run(false),
    openCheckIn: () => run(true),
    openSop: () => run(true),
    openWhatsNew: () => run(true),
  });
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => run(false), {once:true});
  } else run(false);
})(window);
