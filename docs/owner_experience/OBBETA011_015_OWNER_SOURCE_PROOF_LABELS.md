# OBBETA011–015 — owner dashboard source observation vs authenticated proof

**Scope:** This changes the accepted owner dashboard's read-only labels only. It does not change canonical engine research, simulated order math, Tower authentication, broker/account permissions, market provider adapters, production modes or capital policy.

## Found issue

The previous `sourceLooksVerified` treated any successful JSON endpoint not explicitly marked `verified: false` or named fallback/demo/seed as verified. Thus even a response with `verified: true` supplied by itself, or a mere HTTP 200, could be shown as verified system trust, rehearsal source, or private beta evidence. HTTP transport only says the route responded; a JSON body's own "verified" flag is not independently authenticated provenance.

## Accepted conservative contract

- `sourceLooksVerified` retains its old name for consumer compatibility but **always returns false** until the browser consumes a deliberately specified trusted server-verified receipt, outside this pack. Do not add a client-controlled Boolean bypass.
- Valid non-empty HTTP 200 JSON is `source_observed: true`, `status: available` and `independent_provenance_authenticated: false`. Empty/malformed/failed responses stay guarded.
- The owner may still see a practice-only score, blockers and that private-beta/trust declarations arrived. They no longer show those declarations as independently verified Tower/market/broker/hosted authorization. Owner trust and private beta tiles have explicit unverified labels.
- Rehearsal scores remain explicitly practice only, while `real_manual_live_ready`, Tower clearance, broker source proof, public launch, broker orders, Hybrid/Auto remain false.
- This is a fail-closed interim state, not a permanent verification method. Genuine provenance requires a separately designed trusted issuer, exact-source binding, security/expiry/revocation/nonce checks where appropriate, and independent source/hosted acceptance.

## Regression

The standalone Node test `tests/test_obbeta011_015_owner_source_proof_labels.js` executes the real browser module with mocked same-origin endpoint responses. It checks even forged `verified:true` and `independently_authenticated:true` responses cannot be elevated; source data remains visible as observed practice; missing/failed endpoints stay guarded. The existing owner dashboard and beta tests run as part of full `pytest`.

**No paid Render, new production secret, live trading feature, broker submission, data transfer, or Tower permission is authorized by this label correction.**
