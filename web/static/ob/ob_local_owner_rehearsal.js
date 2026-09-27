/* OBSIM046–050: browser controls for standalone 127.0.0.1 rehearsal ONLY. */
(() => {
  "use strict";
  const root = document.getElementById("localRehearsalMount");
  if (!root || root.dataset.obCsrf === undefined) return;
  const token = root.dataset.obCsrf;
  const $ = (id) => document.getElementById(id);
  const controls = ["refresh", "sample", "tick", "pause", "resume", "stop"];
  let busy = false;
  let last = null;
  let connected = false;

  function say(message) { $("feedback").textContent = message; }
  function metric(value) {
    const number = Number(value);
    return Number.isFinite(number) ? number.toLocaleString(undefined, { maximumFractionDigits: 2 }) : "—";
  }
  async function api(path, method = "GET", payload = null) {
    const options = {
      method,
      credentials: "omit",
      cache: "no-store",
      headers: { "X-OB-Rehearsal-Token": token, "Accept": "application/json" }
    };
    if (method !== "GET") {
      options.headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(payload === null ? {} : payload);
    }
    const response = await fetch(path, options);
    const result = await response.json();
    if (!response.ok) throw new Error(result && result.status ? String(result.status) : "Local endpoint unavailable");
    return result;
  }
  function renderLanes(lanes) {
    const mount = $("laneCards");
    mount.replaceChildren();
    ["CONTROL", "INTEGRATED", "EXPERIMENTAL"].forEach((key) => {
      const card = document.createElement("article");
      card.className = "lane";
      const head = document.createElement("h3");
      head.textContent = key.charAt(0) + key.slice(1).toLowerCase();
      card.appendChild(head);
      const info = lanes && typeof lanes === "object" ? lanes[key] : null;
      if (!info) {
        const p = document.createElement("p");
        p.textContent = "No accepted simulated report yet.";
        card.appendChild(p);
      } else {
        [["Equity", info.equity], ["Cash", info.cash], ["Realized P&L", info.realized_pnl], ["Unrealized P&L", info.unrealized_pnl], ["Trades", info.trades]].forEach(([label, value]) => {
          const p = document.createElement("p");
          const strong = document.createElement("strong");
          strong.textContent = metric(value);
          p.append(document.createTextNode(label + ": "), strong);
          card.appendChild(p);
        });
      }
      mount.appendChild(card);
    });
  }
  function render(data) {
    last = data;
    connected = true;
    $("sessionState").textContent = data.state || "Guarded";
    $("tickCount").textContent = metric(data.accepted_ticks);
    $("sourceKind").textContent = data.declared_source_kind || "Unverified";
    const due = data.due || {};
    $("dueStatus").textContent = due.state === "WAIT_INTERVAL" ?
      Math.max(0, Math.ceil(Number(due.due_in_seconds) || 0)) + "s remaining" :
      due.state === "READY_FOR_EXPLICIT_INPUT" ? "Ready for input" : (due.state || "Unavailable");
    $("lastHash").textContent = data.last_report_hash || "No report";
    renderLanes(data.last_lanes);
    updateControls();
  }
  function updateControls() {
    const state = last && last.state;
    const due = last && last.due && last.due.state;
    const active = connected && !busy;
    $("tick").disabled = !active || state !== "RUNNING" || due !== "READY_FOR_EXPLICIT_INPUT";
    $("pause").disabled = !active || state !== "RUNNING";
    $("resume").disabled = !active || state !== "PAUSED";
    $("stop").disabled = !active || state === "STOPPED";
    $("refresh").disabled = busy;
    $("sample").disabled = busy;
  }
  async function refresh() {
    if (busy) return;
    try { render(await api("/api/status")); }
    catch (_) {
      connected = false;
      updateControls();
      say("Local status unavailable. No trading or market-data permissions are implied.");
    }
  }
  async function mutate(path, payload, success) {
    if (busy) return;
    busy = true;
    updateControls();
    try {
      const result = await api(path, "POST", payload);
      render(result);
      say(success(result));
    } catch (error) {
      say("Request not confirmed (" + error.message + "). Refresh local status before retrying; do not assume whether a report was saved.");
    } finally {
      busy = false;
      await refresh();
      updateControls();
    }
  }

  $("refresh").addEventListener("click", refresh);
  $("sample").addEventListener("click", async () => {
    if (busy) return;
    try {
      const sample = await api("/api/example");
      $("inputJson").value = JSON.stringify(sample, null, 2);
      say("Synthetic fixture loaded for review. The marks and 10,000 units are fictional; adjust source kind and unique IDs for any later manually authored input.");
    } catch (_) { say("Synthetic sample unavailable. No simulation report has been submitted."); }
  });
  $("tick").addEventListener("click", async () => {
    let data;
    try {
      data = JSON.parse($("inputJson").value);
      if (!data || typeof data !== "object" || Array.isArray(data)) throw new Error("object");
    } catch (_) { say("Enter one complete owner-authored JSON object before submitting."); return; }
    await mutate("/api/tick", data, (result) =>
      "One simulated report accepted: " + result.accepted_ticks +
      ". Historical/synthetic only; no broker order or live account permission."
    );
  });
  $("pause").addEventListener("click", () => mutate("/api/pause", {}, () =>
    "Paused. No missing 30-second reports will be backfilled."
  ));
  $("resume").addEventListener("click", () => mutate("/api/resume", {}, () =>
    "Resumed. A fresh 30-second interval is required before explicit input."
  ));
  $("stop").addEventListener("click", () => mutate("/api/stop", {}, (result) =>
    "Sealed " + result.archive_tick_count + " report(s) as " + result.archive_state +
    ". Report-only recovery never restores a trading session."
  ));
  refresh();
  // A countdown display is NOT an unattended report, source poll or tick.
  setInterval(() => {
    if (document.visibilityState === "visible" && !busy) refresh();
  }, 1000);
})();
