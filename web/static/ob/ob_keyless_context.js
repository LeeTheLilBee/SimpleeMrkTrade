/* OB source-only public context: one Tower-authenticated shared read, no browser provider calls.
   Soulaana receives a deterministic status-only register, never source payloads,
   live prices, candidate/scoring authority or unreviewed AI-source content. */
(function () {
  "use strict";
  const root = document.getElementById("obKeylessContextRoot");
  if (!root) return;
  const ENDPOINT = "/ob/research/keyless.json";
  const DOCS = Object.freeze({
    sec: "https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
    bls: "https://www.bls.gov/developers/api_signature.htm",
    treasury: "https://fiscaldata.treasury.gov/datasets/debt-to-the-penny/",
    openfigi: "https://www.openfigi.com/api/documentation"
  });
  const LABELS = Object.freeze({
    SOURCE_BOUND: "Source-backed reference",
    DELEGATED_ISSUER_RESEARCH: "Linked protected issuer corridor",
    REVIEW_HOLD: "Source review not activated",
    SYMBOL_REQUIRED: "Choose a ticker",
    SOURCE_HOLD: "Source unavailable / response held",
    LOCAL_QUOTA_HOLD: "Request budget hold",
    NOT_FOUND: "Identifier not found",
    AMBIGUOUS_HOLD: "Ambiguous identifier · held"
  });
  function el(tag, cls, content) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (content !== undefined) node.textContent = String(content);
    return node;
  }
  function validSymbol(value) {
    return typeof value === "string" && /^[A-Z][A-Z0-9.-]{0,15}$/.test(value) &&
      !value.includes("..");
  }
  function locationSymbol() {
    const match = window.location.pathname.match(/^\/ob\/symbol\/([A-Za-z][A-Za-z0-9.-]{0,15})\/?$/);
    return match && validSymbol(match[1].toUpperCase()) ? match[1].toUpperCase() : "";
  }
  const heading = el("div", "ob-keyless-heading");
  const text = el("div");
  text.append(el("span", "ob-keyless-eyebrow", "PUBLIC RESEARCH · NO PROVIDER LOGIN"),
    el("h2", "", "Keyless source desk"));
  const note = el("p", "ob-keyless-intro",
    "Official, dated economic, fiscal and instrument reference only. Not live stock/options quotes; no account or broker connection.");
  heading.append(text, note);
  const lookup = el("form", "ob-keyless-lookup");
  lookup.setAttribute("autocomplete", "off");
  const input = el("input");
  input.type = "text"; input.name = "symbol"; input.maxLength = 16;
  input.pattern = "[A-Za-z][A-Za-z0-9.-]{0,15}";
  input.placeholder = "Ticker (e.g. MSFT)"; input.setAttribute("aria-label", "Ticker for public identifier research");
  const submit = el("button", "", "View reference");
  submit.type = "submit";
  lookup.append(input, submit);
  const status = el("p", "ob-keyless-status", "Checking protected keyless sources…");
  status.setAttribute("role", "status");
  const grid = el("div", "ob-keyless-grid");
  const soulaana = el("section", "ob-keyless-soulaana");
  soulaana.setAttribute("aria-label", "Soulaana source-status explanation");
  const footer = el("p", "ob-keyless-footer",
    "Retrieval time is not publication or market-event time. SEC filings use their existing protected issuer-research corridor. Public account authentication remains separate. Soulaana's status register is not authorization for source-content AI, candidate, capital or trading use.");
  const providerSoulaana = el("section", "ob-keyless-soulaana");
  providerSoulaana.setAttribute("aria-label", "Soulaana provider-connection status");
  providerSoulaana.append(el("p", "ob-keyless-status", "Checking Tower provider connection states…"));
  const keyedProviderResearch = el("section", "ob-keyless-soulaana");
  keyedProviderResearch.setAttribute("aria-label", "Connected provider research");
  keyedProviderResearch.append(el("p", "ob-keyless-status",
    "Enter a ticker and choose View reference to request approved Finnhub/Alpha research through Tower."));
  root.append(heading, lookup, status, grid, soulaana, providerSoulaana, keyedProviderResearch, footer);
  let inFlight = 0;
  let currentSymbol = locationSymbol();
  if (currentSymbol) input.value = currentSymbol;

  function drawSource(row) {
    if (!row || !Object.prototype.hasOwnProperty.call(DOCS, row.source) ||
        typeof row.state !== "string" || row.quote_eligible !== false ||
        row.trading_authorized !== false || typeof row.ai_use_approved !== "boolean") return null;
    const card = el("article", "ob-keyless-card");
    const top = el("div", "ob-keyless-cardtop");
    top.append(el("h3", "", row.provider || row.source),
      el("span", "ob-keyless-badge " + (row.state === "SOURCE_BOUND" ? "good" : "hold"),
        LABELS[row.state] || "Source status held"));
    card.append(top, el("p", "ob-keyless-name", row.label || "Reference data"));
    if (row.state === "SOURCE_BOUND" && typeof row.value === "string") {
      card.append(el("strong", "ob-keyless-value", row.value),
        el("span", "ob-keyless-unit", row.unit || "reference"));
      card.append(el("p", "ob-keyless-meta",
        "Source period: " + (row.period || "not provided") +
        " · Retrieved: " + (row.retrieved_at || "unavailable")));
    } else if (row.state === "DELEGATED_ISSUER_RESEARCH") {
      card.append(el("p", "ob-keyless-meta",
        "EDGAR issuer filings and companyfacts are read through the existing source-reviewed Symbol Research corridor; this card has not fetched a filing."));
    } else {
      const explain = row.state === "SYMBOL_REQUIRED" ? "Select an exact ticker above to request one mapping." :
        row.state === "REVIEW_HOLD" ? "This public source is staged but owner display/use review is not enabled in the backend." :
        "No validated observation is displayed. We do not substitute old or synthetic values.";
      card.append(el("p", "ob-keyless-meta", explain));
    }
    if (row.source === "bls") {
      card.append(el("p", "ob-keyless-meta",
        "BLS.gov cannot vouch for the data or analyses derived from these data after the data have been retrieved from BLS.gov."));
    }
    const link = el("a", "ob-keyless-docs", "Official source ↗");
    link.href = DOCS[row.source]; link.target = "_blank"; link.rel = "noopener noreferrer";
    card.append(link);
    return card;
  }
  function validSoulaana(packet) {
    if (!packet || packet.schema !== "OB_SOULAANA_KEYLESS_STATUS_V1" ||
        packet.channel !== "SOULAANA_SOURCE_STATUS_ONLY" ||
        packet.raw_source_values_included !== false ||
        packet.source_content_ai_authorized !== false ||
        packet.candidate_admitted !== false || packet.quote_verified !== false ||
        packet.broker_execution_authorized !== false ||
        !Array.isArray(packet.source_register) || packet.source_register.length !== 4) return false;
    if (["what_i_see", "what_it_means", "what_is_missing", "next_step"].some(
        key => typeof packet[key] !== "string" || packet[key].length > 600)) return false;
    const keys = ["sec", "bls", "treasury", "openfigi"];
    return packet.source_register.every((row, index) =>
      row && row.source === keys[index] && typeof row.state === "string" &&
      typeof row.meaning === "string" && row.meaning.length <= 350 &&
      typeof row.label === "string" && row.label.length <= 50);
  }
  function renderSoulaana(packet) {
    soulaana.replaceChildren();
    const eyebrow = el("span", "ob-keyless-eyebrow", "SOULAANA · SOURCE AWARENESS");
    const title = el("h3", "", "What I can see");
    const overview = el("p", "", packet.what_i_see);
    const meaning = el("p", "", packet.what_it_means);
    const missing = el("p", "ob-keyless-soulaana-hold", packet.what_is_missing);
    const next = el("p", "", packet.next_step);
    const register = el("div", "ob-keyless-soulaana-register");
    packet.source_register.forEach(function (item) {
      const line = el("p", "");
      line.append(el("strong", "", item.label + " · "), el("span", "", item.meaning));
      register.append(line);
    });
    const guard = el("p", "ob-keyless-footer",
      "This source-status register carries no raw observations. Any content I can read appears in a separate, explicitly reviewed source-evidence brief below. No quote or execution permissions follow.");
    soulaana.append(eyebrow, title, overview, meaning, register, missing, next, guard);
  }
  const EVIDENCE_SOURCES = new Set(["bls", "treasury", "openfigi"]);
  function validSoulaanaEvidence(brief, packet) {
    if (!brief || brief.schema !== "OB_SOULAANA_KEYLESS_EVIDENCE_V1" ||
        brief.channel !== "SOULAANA_REVIEWED_PUBLIC_RESEARCH" ||
        brief.blanket_ai_authority !== false || brief.external_model_called !== false ||
        brief.live_quote_verified !== false || brief.candidate_admitted !== false ||
        brief.broker_execution_authorized !== false || brief.capital_authorized !== false ||
        brief.public_brokerage_auth_inferred !== false ||
        !Array.isArray(brief.observations) || brief.observations.length > 3 ||
        !Array.isArray(brief.source_register) || brief.source_register.length !== 4 ||
        brief.observation_count !== brief.observations.length ||
        brief.source_specific_ai_use_approved !== (brief.observations.length > 0)) return false;
    const authorized = new Set(packet.sources.filter(row =>
      EVIDENCE_SOURCES.has(row.source) && row.ai_use_approved === true &&
      row.state === "SOURCE_BOUND").map(row => row.source));
    if (authorized.size !== brief.observations.length) return false;
    const ids = ["sec", "bls", "treasury", "openfigi"];
    if (!brief.source_register.every((r, index) =>
      r && r.source === ids[index] && r.state === packet.sources[index].state &&
      r.content_readable === authorized.has(r.source))) return false;
    return brief.observations.every(item =>
      item && authorized.has(item.source) &&
      item.source_reference === DOCS[item.source] &&
      item.research_only === true && item.quote_verified === false &&
      item.execution_authorized === false &&
      typeof item.value === "string" && item.value.length <= 55 &&
      typeof item.interpretation === "string" && item.interpretation.length <= 430 &&
      typeof item.retrieved_at === "string" && item.retrieved_at.length <= 50);
  }
  function renderSoulaanaEvidence(brief) {
    const panel = el("div", "ob-keyless-soulaana-evidence");
    panel.append(el("h3", "", "The reviewed evidence I can explain"),
      el("p", "ob-keyless-meta", brief.interpretation));
    brief.observations.forEach(item => {
      const record = el("article", "ob-keyless-evidence-item");
      const link = el("a", "ob-keyless-docs", "Official source ↗");
      link.href = DOCS[item.source]; link.target = "_blank";
      link.rel = "noopener noreferrer";
      record.append(el("strong", "", item.source.toUpperCase()),
        el("p", "", item.interpretation),
        el("p", "ob-keyless-meta", "Retrieved: " + item.retrieved_at), link);
      panel.append(record);
    });
    if (brief.bls_attribution) panel.append(el("p", "ob-keyless-footer", brief.bls_attribution));
    panel.append(el("p", "ob-keyless-footer",
      "A validated, source-specific explanation—not an external model call. No live pricing, forecasts, signals, broker access or candidate admission."));
    soulaana.append(panel);
  }
  async function read(symbol) {
    const seq = ++inFlight;
    status.textContent = "Reading official references through Tower…";
    grid.replaceChildren();
    soulaana.replaceChildren();
    const suffix = symbol ? "?symbol=" + encodeURIComponent(symbol) : "";
    try {
      const response = await fetch(ENDPOINT + suffix, {
        credentials: "same-origin", cache: "no-store",
        headers: { "Accept": "application/json" }
      });
      if (seq !== inFlight) return;
      if (!response.ok) {
        status.textContent = "Tower has not supplied an authorized public-research snapshot (" +
          response.status + "). Reopen the protected Market Data Desk.";
        return;
      }
      const packet = await response.json();
      if (!packet || packet.schema !== "OB_KEYLESS_PUBLIC_CONTEXT_V1" ||
          packet.source_only !== true || packet.prices_attached !== false ||
          packet.options_chain_attached !== false || packet.live_quote_verified !== false ||
          packet.broker_execution_authorized !== false || packet.ai_input_approved !== false ||
          !Array.isArray(packet.sources) || packet.sources.length !== 4) {
        status.textContent = "Keyless response failed the source-only safety contract.";
        return;
      }
      const safeRows = packet.sources.map(drawSource).filter(Boolean);
      if (safeRows.length !== 4 || !validSoulaana(packet.soulaana_source_register) ||
          !validSoulaanaEvidence(packet.soulaana_evidence_brief, packet)) {
        status.textContent = "Keyless response failed provider/Soulaana research-evidence validation.";
        return;
      }
      grid.replaceChildren(...safeRows);
      renderSoulaana(packet.soulaana_source_register);
      renderSoulaanaEvidence(packet.soulaana_evidence_brief);
      const count = packet.sources.filter(row => row.state === "SOURCE_BOUND").length;
      status.textContent = count + " source-backed reference" + (count === 1 ? "" : "s") +
        " · as of " + packet.as_of + (symbol ? " · ticker " + symbol : "") +
        " · no live market prices connected";
    } catch (_) {
      if (seq === inFlight) status.textContent = "Keyless context was not reachable. No data or quote was inferred.";
    }
  }
  // A second, independent same-origin Tower read shares only sanitized status.
  // Public account IDs, temporary provider secrets and vendor/source responses
  // never cross this endpoint or reach Soulaana. Failure is a visible HOLD.
  const PROVIDER_ORDER = ["public", "finnhub", "alpha_vantage", "sec", "bls", "treasury", "openfigi"];
  const PROVIDER_STATES = Object.freeze({
    public: new Set(["TEMPORARY_ACCOUNT_LINK_VERIFIED", "OWNER_SELECTION_REQUIRED", "TEMPORARY_AUTH_ONLY", "NO_VERIFIED_ACCOUNT_LINK"]),
    finnhub: new Set(["READ_ONLY_CHECK_PASSED", "TEMPORARY_KEY_RECEIVED", "NOT_CONFIGURED"]),
    alpha_vantage: new Set(["READ_ONLY_CHECK_PASSED", "TEMPORARY_KEY_RECEIVED", "NOT_CONFIGURED"]),
    sec: new Set(["SEPARATE_ISSUER_RESEARCH_CONFIGURED", "RIGHTS_REVIEW_HOLD"]),
    bls: new Set(["USE_AND_OWNER_DISPLAY_CONFIGURED", "RIGHTS_REVIEW_HOLD"]),
    treasury: new Set(["USE_AND_OWNER_DISPLAY_CONFIGURED", "RIGHTS_REVIEW_HOLD"]),
    openfigi: new Set(["USE_AND_OWNER_DISPLAY_CONFIGURED", "RIGHTS_REVIEW_HOLD"])
  });
  function validProviderSoulaana(data) {
    const brief = data && data.soulaana_provider_status;
    if (!data || data.schema !== "OB_TOWER_PROVIDER_CONNECTION_TRUTH_V1" ||
        data.owner_session_checked !== true || data.source_only !== true ||
        data.dissemination_contract !== "OWNER_STATUS_ONLY" ||
        data.prices_attached !== false || data.positions_attached !== false ||
        data.real_market_feed_attached_by_this_route !== false ||
        data.live_feed_count_verified !== null || data.no_browser_provider_credentials !== true ||
        data.may_authorize_order !== false || data.may_authorize_capital !== false ||
        data.may_change_trading_mode !== false || !Array.isArray(data.provider_status) ||
        data.provider_status.length !== 7 || !brief ||
        brief.schema !== "OB_SOULAANA_PROVIDER_CONNECTION_STATUS_V1" ||
        brief.channel !== "SOULAANA_CONNECTION_STATUS_ONLY" ||
        brief.raw_provider_values_included !== false ||
        brief.account_identifiers_included !== false ||
        brief.credentials_included !== false ||
        brief.source_content_ai_authorized !== false ||
        brief.quote_verified !== false || brief.broker_execution_authorized !== false ||
        brief.capital_authorized !== false || !Array.isArray(brief.provider_register) ||
        brief.provider_register.length !== 7) return false;
    if (["what_i_see", "what_it_means", "what_is_missing", "next_step"].some(
        key => typeof brief[key] !== "string" || brief[key].length > 650)) return false;
    return PROVIDER_ORDER.every((provider, index) => {
      const row = data.provider_status[index];
      const item = brief.provider_register[index];
      return row && item && row.provider === provider &&
        row.quote_feed_activated === false && PROVIDER_STATES[provider].has(row.state) &&
        item.provider === provider && item.state === row.state &&
        typeof item.label === "string" && item.label.length <= 50 &&
        typeof item.meaning === "string" && item.meaning.length <= 360;
    });
  }
  async function readProviderSoulaana() {
    try {
      const response = await fetch("/ob/data-desk/connections.json", {
        credentials: "same-origin", cache: "no-store",
        headers: { "Accept": "application/json" }
      });
      if (!response.ok) throw Error("provider status hold");
      const packet = await response.json();
      if (!validProviderSoulaana(packet)) throw Error("provider status contract hold");
      const brief = packet.soulaana_provider_status;
      const lines = el("div", "ob-keyless-soulaana-register");
      brief.provider_register.forEach(item => {
        const row = el("p");
        row.append(el("strong", "", item.label + " · "), el("span", "", item.meaning));
        lines.append(row);
      });
      providerSoulaana.replaceChildren(
        el("span", "ob-keyless-eyebrow", "SOULAANA · TOWER CONNECTION AWARENESS"),
        el("h3", "", "What my providers can actually do"),
        el("p", "", brief.what_i_see),
        el("p", "", brief.what_it_means),
        lines,
        el("p", "ob-keyless-soulaana-hold", brief.what_is_missing),
        el("p", "", brief.next_step),
        el("p", "ob-keyless-footer",
          "I see protected connection status, not provider data, an account ID, credentials, AI-use approval, verified prices or trading authority.")
      );
    } catch (_) {
      providerSoulaana.replaceChildren(el("p", "ob-keyless-soulaana-hold",
        "Tower provider status is unavailable. No connected provider or data rights are assumed."));
    }
  }

  function validKeyedProviderResearch(packet, symbol) {
    if (!packet || packet.schema !== "OB_KEYED_PROVIDER_RESEARCH_V1" ||
        packet.symbol !== symbol || packet.owner_session_checked !== true ||
        packet.source_only !== true || packet.live_prices_attached !== false ||
        packet.positions_attached !== false || packet.orders_attached !== false ||
        packet.may_authorize_order !== false || packet.may_authorize_capital !== false ||
        packet.may_change_trading_mode !== false ||
        !Array.isArray(packet.provider_research) || packet.provider_research.length !== 2)
      return false;
    const ids = ["finnhub", "alpha_vantage"];
    if (!packet.provider_research.every((row, index) =>
      row && row.provider === ids[index] &&
      ["NOT_CONNECTED", "RIGHTS_OR_FETCH_HOLD", "SOURCE_HOLD", "SOURCE_BOUND"].includes(row.state)))
      return false;
    const brief = packet.soulaana_research;
    return brief && brief.schema === "OB_SOULAANA_KEYED_PROVIDER_RESEARCH_V1" &&
      brief.channel === "SOULAANA_REVIEWED_PROVIDER_RESEARCH" &&
      brief.raw_credentials_included === false &&
      brief.account_identifiers_included === false &&
      brief.live_quote_verified === false &&
      brief.candidate_admitted === false &&
      brief.broker_execution_authorized === false &&
      brief.capital_authorized === false &&
      brief.may_change_trading_mode === false &&
      Array.isArray(brief.observations) && brief.observations.length <= 2;
  }

  async function readKeyedProviderResearch(symbol) {
    keyedProviderResearch.replaceChildren(el("p", "ob-keyless-status",
      "Reading approved temporary-key research through Tower…"));
    try {
      const response = await fetch("/ob/research/providers.json?symbol=" + encodeURIComponent(symbol), {
        credentials: "same-origin", cache: "no-store",
        headers: {"Accept": "application/json"}
      });
      if (!response.ok) throw Error("keyed research hold");
      const packet = await response.json();
      if (!validKeyedProviderResearch(packet, symbol)) throw Error("invalid keyed research");
      const title = el("h3", "", "Connected provider research");
      const rows = el("div", "ob-keyless-soulaana-register");
      packet.provider_research.forEach(row => {
        const line = el("p", "");
        let detail = row.state.replaceAll("_", " ");
        if (row.state === "SOURCE_BOUND" && row.provider === "finnhub") {
          detail += " · " + (row.security_name || symbol) +
            (row.industry ? " · " + row.industry : "");
        } else if (row.state === "SOURCE_BOUND" && row.provider === "alpha_vantage") {
          detail += " · " + (Array.isArray(row.bars) ? row.bars.length : 0) +
            " completed daily sessions";
        }
        line.append(el("strong", "", row.provider.replace("_", " ").toUpperCase() + " · "),
          el("span", "", detail));
        rows.append(line);
      });
      const brief = packet.soulaana_research;
      const ai = el("p", "ob-keyless-soulaana-hold",
        brief.observations.length
          ? "Soulaana can read only the provider research explicitly covered by separate AI-use review."
          : "Provider AI-use rights are not approved or no source-bound keyed research is available.");
      keyedProviderResearch.replaceChildren(title, rows, ai,
        el("p", "ob-keyless-footer",
          "Historical/reference research only. This corridor does not supply a live quote, candidate, broker action or trading-mode change."));
    } catch (_) {
      keyedProviderResearch.replaceChildren(el("p", "ob-keyless-soulaana-hold",
        "Keyed provider research is unavailable or held. No provider data is assumed."));
    }
  }

  lookup.addEventListener("submit", function (event) {
    event.preventDefault();
    const symbol = String(input.value || "").trim().toUpperCase();
    if (!validSymbol(symbol)) {
      status.textContent = "Enter an uppercase-compatible ticker (1–16 letters, digits, period or hyphen).";
      return;
    }
    currentSymbol = symbol;
    input.value = symbol;
    read(currentSymbol);
    readKeyedProviderResearch(currentSymbol);
  });
  read(currentSymbol);
  readProviderSoulaana();
})();
