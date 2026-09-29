/* Tower source-status readout: no browser credentials or vendor fetch. */
(() => {
  "use strict";
  const root = document.getElementById("mddConnectionStatus");
  if (!root) return;
  const known = new Set(["public","finnhub","alpha_vantage","sec","bls","treasury","openfigi"]);
  const names = Object.freeze({
    public: "Public", finnhub: "Finnhub", alpha_vantage: "Alpha Vantage",
    sec: "SEC EDGAR", bls: "BLS", treasury: "U.S. Treasury", openfigi: "OpenFIGI"
  });
  function line(provider, state) {
    const article = document.createElement("article");
    article.style.cssText = "background:#16152d;border:1px solid #554979;border-radius:12px;padding:12px;min-width:170px;flex:1";
    const label = document.createElement("strong"); label.textContent = names[provider];
    const status = document.createElement("p"); status.textContent = state.replaceAll("_", " ");
    status.style.marginBottom = "0";
    article.append(label, status);
    return article;
  }
  fetch("/ob/data-desk/connections.json", {
    method:"GET", credentials:"same-origin", cache:"no-store",
    headers:{"Accept":"application/json"}
  }).then(async response => {
    if (!response.ok) throw Error("protected status unavailable");
    const data = await response.json();
    if (!data || data.schema !== "OB_TOWER_PROVIDER_CONNECTION_TRUTH_V1" ||
        data.owner_session_checked !== true || data.prices_attached !== false ||
        data.may_authorize_order !== false || !Array.isArray(data.provider_status) ||
        data.provider_status.length !== 7) throw Error("invalid status");
    const records = new Map();
    for (const row of data.provider_status) {
      if (!row || !known.has(row.provider) || typeof row.state !== "string" ||
          row.quote_feed_activated !== false || records.has(row.provider))
        throw Error("invalid source row");
      records.set(row.provider, row.state);
    }
    if (records.size !== 7) throw Error("missing source");
    root.textContent = "";
    root.style.cssText = "display:flex;gap:12px;flex-wrap:wrap;margin-top:12px";
    for (const [provider,state] of records) root.append(line(provider,state));
  }).catch(() => {
    root.textContent = "Connection status is unavailable. No provider connection or quote is assumed.";
  });
})();
