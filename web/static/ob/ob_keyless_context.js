/* OB source-only public context: one Tower-authenticated shared read, no browser provider calls.
   This is not a price feed, signal, portfolio view or input to scanner/scoring/AI. */
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
  const footer = el("p", "ob-keyless-footer",
    "Retrieval time is not publication or market-event time. SEC filings use their existing protected issuer-research corridor. Public account authentication remains separate. No AI-use, candidate, capital or trading permission is inferred.");
  root.append(heading, lookup, status, grid, footer);
  let inFlight = 0;
  let currentSymbol = locationSymbol();
  if (currentSymbol) input.value = currentSymbol;

  function drawSource(row) {
    if (!row || !Object.prototype.hasOwnProperty.call(DOCS, row.source) ||
        typeof row.state !== "string" || row.quote_eligible !== false ||
        row.trading_authorized !== false || row.ai_use_approved !== false) return null;
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
    const link = el("a", "ob-keyless-docs", "Official source ↗");
    link.href = DOCS[row.source]; link.target = "_blank"; link.rel = "noopener noreferrer";
    card.append(link);
    return card;
  }
  async function read(symbol) {
    const seq = ++inFlight;
    status.textContent = "Reading official references through Tower…";
    grid.replaceChildren();
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
      if (safeRows.length !== 4) {
        status.textContent = "Keyless response failed provider/authority validation.";
        return;
      }
      grid.replaceChildren(...safeRows);
      const count = packet.sources.filter(row => row.state === "SOURCE_BOUND").length;
      status.textContent = count + " source-backed reference" + (count === 1 ? "" : "s") +
        " · as of " + packet.as_of + (symbol ? " · ticker " + symbol : "") +
        " · no live market prices connected";
    } catch (_) {
      if (seq === inFlight) status.textContent = "Keyless context was not reachable. No data or quote was inferred.";
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
  });
  read(currentSymbol);
})();
