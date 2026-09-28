// OB return navigation must use the existing Tower-owner endpoint, not a bypass.
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const assert = require("node:assert/strict");

const root = path.resolve(__dirname, "..");
const source = fs.readFileSync(path.join(root, "web/static/ob/ob_nav_shell.js"), "utf8");

function render(roomPath) {
  let rail = null, bar = null;
  const layer = { prepend(element) { bar = element; } };
  const document = {
    getElementById(id) { return id === "ob-app" ? {} : null; },
    querySelector(selector) { return selector === ".ob-layer" ? layer : null; },
    createElement(tag) { return { tag, innerHTML: "", setAttribute() {} }; },
    body: { prepend(element) { rail = element; } },
    addEventListener(event, callback) {
      assert.equal(event, "DOMContentLoaded");
      callback();
    }
  };
  vm.runInNewContext(source, {
    document, window: {location: {pathname: roomPath}},
    encodeURIComponent, decodeURIComponent
  });
  assert.ok(rail, "hover rail is available");
  assert.ok(bar, "route bar is available");
  return [rail.innerHTML, bar.innerHTML];
}

for (const [pathName, label] of Object.entries({
  "/ob/dashboard": "Dashboard",
  "/ob/market-map": "Market Map",
  "/ob/trade-center": "Trade Center",
  "/ob/review-center": "Review Center",
  "/ob/owner-console": "Owner Console",
  "/ob/symbol/AAPL": "Symbol Page"
})) {
  const href = "/tower/return/observatory?last_room=" + encodeURIComponent(label);
  const surfaces = render(pathName);
  for (const html of surfaces) {
    assert.ok(html.includes('href="' + href + '"'), pathName + " must link via return endpoint");
    assert.ok(html.includes('aria-label="Return to Tower Access Home"'), "accessible return action");
    assert.ok(!html.includes("https://"), "return stays same-origin");
    assert.ok(!html.includes('href="/tower/access-home"'), "receipt edge cannot be skipped");
  }
}

// The incoming navigation hint is bounded and unknown routes cannot invent a label.
for (const html of render("/ob/nonexistent")) {
  assert.ok(html.includes('href="/tower/return/observatory?last_room=unknown"'));
}

const ownerPage = fs.readFileSync(path.join(root, "web/templates/owner_dashboard.html"), "utf8");
assert.ok(ownerPage.includes('href="/tower/return/observatory?last_room=Owner%20Dashboard"'));
console.log("OB→Tower UI return: six shared rooms + dormant owner dashboard + unknown fallback passed.");
