// OB command-center Dashboard — birdseye, explanation-first, no provider plumbing.
(function (global) {
  "use strict";

  const esc = value => String(value == null ? "" : value)
    .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");

  const byId = id => document.getElementById(id);

  function write(id, value) {
    const el = byId(id);
    if (el) el.textContent = value == null ? "" : String(value);
  }

  function renderGlance(items) {
    const mount = byId("obUserMarketGlance");
    if (!mount) return;
    const safe = Array.isArray(items) ? items.slice(0, 3) : [];
    if (!safe.length) {
      mount.innerHTML = '<div class="ob-command-empty">Quiet sky · nothing verified needs the front page.</div>';
      return;
    }
    mount.innerHTML = safe.map(item => `
      <a class="ob-command-symbol" href="${esc(item.href)}">
        <strong>${esc(item.symbol)}</strong>
        <span>${esc(item.source)}</span>
      </a>`).join("");
  }

  function renderFacts(items) {
    const mount = byId("obAccountHealthFacts");
    if (!mount) return;
    const safe = Array.isArray(items) ? items.slice(0, 3) : [];
    mount.replaceChildren(...safe.map(item => {
      const span = document.createElement("span");
      span.textContent = item.label + " · " + item.value;
      return span;
    }));
  }

  function renderLines(id, items, formatter) {
    const mount = byId(id);
    if (!mount) return;
    const safe = Array.isArray(items) ? items.slice(0, 3) : [];
    mount.replaceChildren(...safe.map(item => {
      const div = document.createElement("div");
      div.className = "ob-command-line";
      div.textContent = formatter(item);
      return div;
    }));
  }

  function render() {
    const api = global.OB_USER_DASHBOARD_PROJECTION;
    if (!api || typeof api.project !== "function") return;
    const p = api.project();

    write("obUserBriefingTitle", p.briefing.title);
    write("obUserBriefingSummary", p.briefing.summary);

    write("obAccountHealthLabel", p.account_health.label);
    write("obAccountHealthSummary", p.account_health.summary);
    renderFacts(p.account_health.facts);

    write("obRiskLabel", p.risk.label);
    write("obRiskSummary", p.risk.summary);

    write("obAttentionLabel", p.attention.count ? p.attention.count + " thing" + (p.attention.count === 1 ? "" : "s") + " need attention" : "Nothing urgent.");
    renderLines("obAttentionList", p.attention.items, item => item);

    write("obPositionsLabel", p.positions.label);
    renderLines("obPositionsList", p.positions.items, item => item.symbol + " · " + item.state);

    write("obModeLabel", p.mode_state.label);
    write("obModeSummary", p.mode_state.detail);

    write("obNextActionLabel", p.next_action.label);
    write("obNextActionDetail", p.next_action.detail);
    const link = byId("obNextActionLink");
    if (link) link.href = p.next_action.href;

    renderGlance(p.market_glance);

    document.body.setAttribute("data-ob-user-mode", p.mode);
    document.body.setAttribute("data-ob-market-projection-state", p.source_state.projection_status);
    document.body.setAttribute("data-ob-risk-tone", p.risk.tone);
  }

  function boot() { render(); }
  window.addEventListener("obEngineFeedAdapterUpdated", render);
  window.addEventListener("obSessionStateUpdated", render);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, {once:true});
  } else {
    boot();
  }

  global.OB_USER_DASHBOARD_V91 = Object.freeze({render});
})(window);
