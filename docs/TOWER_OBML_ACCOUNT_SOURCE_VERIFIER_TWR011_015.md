# TWR-OBML011–015 — independent OB mission-account source verification

**Source-only interop. A verified namespace is not owner identity, OBML review
permission, a real broker account, options authority, spendable capital or a
Manual Live unlock.**

Parent Tower branch: 65685fb8e54c8cea184fc38c2754175b1490a50c.
Exact independently authored Observatory exporter: draft PR #80 at
d3383a0e81ce94b484420b860d7f16e9ef96d98f, built from the existing
OBAUTH006–010 canonical account-identity resolver and mission account
namespace. The dedicated Tower branch does not itself contain
web/ob_account_identity_truth.py; copying an old alternate account registry
into Tower would violate the canonical OB boundary.

## New Tower source boundary

tower.obml_account_identity_source_verifier.py independently verifies the
obai1 short-lived HMAC export with an explicit source-only dedicated shared
key. It validates exact schema/issuer/audience/source namespace, canonical
base64url, HMAC before JSON, duplicate key rejection, account-key/fingerprint
binding, non-demo mission class, 60-second expiry, nonce form and hard-false
owner/broker/capital/Manual Live grant fields. The expected account key and
current fingerprint must come from a future independently authenticated
current OB source; reusing user/browser-token fields as the expected values
would not provide current-source provenance.

Successful verification produces immutable namespace claims ONLY.
consume_signed_ob_account_source independently re-verifies the raw signed bytes before using a separate SQLite unique hash to
deny replay across distinct connections. It rejects dirty caller
transactions and expired claims. A production adapter would need an approved
durable ledger; the module does not configure one, set a signing secret,
register an endpoint, emit a Tower owner entitlement or create any browser
session. The redacted result reports source status only and exposes no
amounts/token.

GitHub CI separately checks out exact PR #80 source and runs its actual
exporter in a separate Python process using a synthetic test-only key. Tower's
receiver validates those bytes; tests prove replay denial, wrong key/source,
tampering, expiry, proof-demo/unknown account scope, forged ability flags and
immutable verified object. Existing TWR-OBML006–010 owner preflight and default
deny are retested with exact pinned PR #68 request.

## Release still blocked

Real Tower owner account entitlement and purpose-specific fresh step-up,
revocation/session status, source account *current* identity refresh, secure
server-to-server key exchange, provider permissions/evidence, OB mode and
Effective Policy, protected capital policies, Review Center owner decision,
actual broker-side human order and independent reconciliation are separate.
Do not install real keys or enable an endpoint/Manual Live merely because
synthetic source-signature tests pass.

No new paid hosting/provider resources or Render mutation from this pack.
No direct BuyBox access to OB balances. Teller alone mediates acquisition
financial readiness. Keep original PR #68 as a handoff request until actual
issuer and receiver have real hosted owner acceptance.
