/* Owner-only Observatory lifecycle proof. No provider payloads or credentials. */
(() => {
  "use strict";

  const root = document.getElementById("mddEventTraceStatus");
  if (!root) return;

  const stages = Object.freeze([
    "RECEIVED",
    "VALIDATED",
    "NORMALIZED",
    "PUBLISHED",
    "SCANNER_CONSUMED",
    "SIMULATION_CONSUMED",
    "SOULAANA_CONSUMED",
    "SOULAANA_INTERPRETED"
  ]);

  function label(stage) {
    return stage
      .replace("SCANNER_CONSUMED", "Scanner consumed")
      .replace("SIMULATION_CONSUMED", "Simulation consumed")
      .replace("SOULAANA_CONSUMED", "Soulaana consumed")
      .replace("SOULAANA_INTERPRETED", "Soulaana interpreted")
      .replace("RECEIVED", "Received")
      .replace("VALIDATED", "Validated")
      .replace("NORMALIZED", "Normalized")
      .replace("PUBLISHED", "Published");
  }

  function validTrace(row) {
    if (!row || row.schema !== "OB_EVENT_TRACE_V1" ||
        typeof row.event_id !== "string" || row.event_id.length > 80 ||
        typeof row.event_type !== "string" || row.event_type.length > 80 ||
        typeof row.source !== "string" || row.source.length > 80 ||
        !(row.symbol === null || typeof row.symbol === "string") ||
        typeof row.snapshot_path !== "string" || row.snapshot_path.length > 160 ||
        !row.stages || typeof row.stages !== "object" ||
        typeof row.soulaana_complete !== "boolean" ||
        !Array.isArray(row.receipts) || row.receipts.length > 16) return false;

    return stages.every(stage => typeof row.stages[stage] === "boolean");
  }

  function stageChip(stage, complete) {
    const chip = document.createElement("span");
    chip.className = "mdd-trace-stage " + (complete ? "is-done" : "is-pending");
    chip.textContent = (complete ? "✓ " : "○ ") + label(stage);
    return chip;
  }

  function traceCard(row) {
    const card = document.createElement("article");
    card.className = "mdd-trace-card";

    const top = document.createElement("div");
    top.className = "mdd-trace-head";

    const identity = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = row.source + (row.symbol ? " · " + row.symbol : "");
    const detail = document.createElement("small");
    detail.textContent = row.event_type.replaceAll("_", " ") + " · " + row.event_id;
    identity.append(title, detail);

    const outcome = document.createElement("span");
    outcome.className = "mdd-badge " + (row.soulaana_complete ? "ready" : "");
    outcome.textContent = row.soulaana_complete
      ? "Soulaana interpreted"
      : "Still moving through system";

    top.append(identity, outcome);

    const path = document.createElement("p");
    path.className = "mdd-trace-path";
    path.textContent = "Protected truth: " + row.snapshot_path;

    const rail = document.createElement("div");
    rail.className = "mdd-trace-rail";
    for (const stage of stages) {
      rail.append(stageChip(stage, row.stages[stage]));
    }

    card.append(top, path, rail);
    return card;
  }

  function fail(message) {
    root.replaceChildren();
    const p = document.createElement("p");
    p.className = "mdd-empty";
    p.textContent = message;
    root.append(p);
  }

  fetch("/ob/data-desk/event-traces.json", {
    method: "GET",
    credentials: "same-origin",
    cache: "no-store",
    headers: {"Accept": "application/json"}
  }).then(async response => {
    if (!response.ok) throw new Error("protected trace unavailable");
    const data = await response.json();

    if (!data || data.schema !== "OB_EVENT_TRACE_V1" ||
        typeof data.epoch !== "string" ||
        !Number.isSafeInteger(data.latest_cursor) || data.latest_cursor < 0 ||
        !Array.isArray(data.traces) || data.traces.length > 24 ||
        data.content_attached !== false ||
        data.provider_payload_attached !== false ||
        data.credentials_attached !== false ||
        data.positions_attached !== false ||
        data.orders_attached !== false ||
        data.execution_authorized !== false ||
        data.traces.some(row => !validTrace(row))) {
      throw new Error("invalid trace");
    }

    root.replaceChildren();
    const recent = data.traces.slice(-6).reverse();
    if (!recent.length) {
      fail("No Observatory events have been published in this process yet.");
      return;
    }
    for (const row of recent) root.append(traceCard(row));
  }).catch(() => {
    fail("Event lifecycle proof is unavailable. No Soulaana consumption is assumed.");
  });
})();
