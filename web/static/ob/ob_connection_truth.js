/* Tower source-status readout: no browser credentials or vendor fetch. */
(() => {
  "use strict";
  const root = document.getElementById("mddConnectionStatus");
  if (!root) return;

  const order = [
    "public","finnhub","alpha_vantage","twelve_data","finazon",
    "sec","bls","treasury","openfigi"
  ];
  const known = new Set(order);
  const keyProviders = new Set(["finnhub","alpha_vantage","twelve_data","finazon"]);
  const safeProbe = new Set([
    "NOT_CONFIGURED","NOT_TESTED","READ_ONLY_CHECK_PASSED","RATE_LIMITED",
    "ACCESS_REJECTED","REQUEST_REJECTED","PROVIDER_UNAVAILABLE","NETWORK_HOLD",
    "REDIRECT_HOLD","RESPONSE_TOO_LARGE","RESPONSE_PARSE_HOLD",
    "RESPONSE_SHAPE_HOLD","PROVIDER_MESSAGE"
  ]);
  const names = Object.freeze({
    public: "Public",
    finnhub: "Finnhub",
    alpha_vantage: "Alpha Vantage",
    twelve_data: "Twelve Data",
    finazon: "Finazon",
    sec: "SEC EDGAR",
    bls: "BLS",
    treasury: "U.S. Treasury",
    openfigi: "OpenFIGI"
  });

  function line(row) {
    const article = document.createElement("article");
    article.style.cssText =
      "background:#16152d;border:1px solid #554979;border-radius:12px;padding:12px;min-width:170px;flex:1";
    const label = document.createElement("strong");
    label.textContent = names[row.provider];
    const status = document.createElement("p");
    status.textContent = row.state.replaceAll("_", " ");
    status.style.marginBottom = "0";
    article.append(label, status);

    if (keyProviders.has(row.provider) && row.read_only_probe !== row.state &&
        row.read_only_probe !== "NOT_TESTED" && row.read_only_probe !== "NOT_CONFIGURED") {
      const probe = document.createElement("small");
      probe.textContent = "Probe: " + row.read_only_probe.replaceAll("_", " ");
      article.append(probe);
    }
    if (row.provider === "twelve_data" || row.provider === "finazon") {
      const rights = document.createElement("small");
      const internal = row.source_use_rights_verified === true
        ? "commercial/internal review configured"
        : "commercial/internal review held";
      const display = row.data_display_rights_verified === true
        ? "owner display reviewed"
        : "raw values not displayed";
      rights.textContent = internal + " · " + display;
      article.append(rights);
    }
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
        data.provider_status.length !== order.length) throw Error("invalid status");

    const records = new Map();
    for (const row of data.provider_status) {
      if (!row || !known.has(row.provider) || typeof row.state !== "string" ||
          row.quote_feed_activated !== false || records.has(row.provider))
        throw Error("invalid source row");
      if (keyProviders.has(row.provider) &&
          (!safeProbe.has(row.read_only_probe) ||
           typeof row.source_use_rights_verified !== "boolean" ||
           typeof row.data_display_rights_verified !== "boolean"))
        throw Error("invalid keyed source row");
      records.set(row.provider, row);
    }
    if (records.size !== order.length ||
        !order.every(provider => records.has(provider))) throw Error("missing source");

    root.textContent = "";
    root.style.cssText = "display:flex;gap:12px;flex-wrap:wrap;margin-top:12px";
    for (const provider of order) root.append(line(records.get(provider)));
  }).catch(() => {
    root.textContent =
      "Connection status is unavailable. No provider connection or quote is assumed.";
  });
})();
