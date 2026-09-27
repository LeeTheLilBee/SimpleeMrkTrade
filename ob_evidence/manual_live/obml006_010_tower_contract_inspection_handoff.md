# OBML006–010 — OB-side untrusted Tower handoff contract inspection

Parent: `02f6ca625ed6aee6b583d7ca5cebed332d1137e8`, accepted OBML001–005 source preflight. Tower owner-only handoff request remains draft [PR #68](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/68), **not** implemented Tower authorization. This pack is a separable OB consumer-side readiness aid and does not alter Tower.

## Implemented now
- Independent verification of the complete canonical OBML001–005 preflight, source recovery and upstream receipts before inspecting any presented Tower claim.
- Exact expected structural fields from request v1: issuer/audience/owner role/permission/purpose/route, session/account-fingerprint binding, issue/expiry/step-up chronology, nonce/revocation/decision identifiers and all forbidden-capability claims.
- Missing, cross-account, beta, wrong audience/purpose/route, malformed identity, expired/implausible clock fields, raw credential or execution-capability claims are reported as redacted reason codes. No token, raw principal/session ID or keycard is returned.
- A plausible or even `verified_tower_attestation=true` **client-presented** claim is still untrusted. The output never verifies Tower issuer signatures, authenticates owner, consumes a nonce, checks real revocation, unlocks a live mode or authenticates broker accounts.
- Exact deterministic proof reference, zero broker/API/capital permissions and rejection of any re-written proof. Explicit current `as_of_utc` is only a caller-provided structural check; Tower server clock is authoritative when implemented.

## Monday Tower ownership and acceptance
Tower should inspect its current canonical PR #22 and handoff draft #68 and return the *actual* trusted server-side handoff endpoint, issuer/audience contract, short-lived session and purpose-bound step-up validation, secure nonce replay/TTL/revocation handling, exact account binding, and redacted audit allow-for-review/deny receipts. Tower must own those functions. Integrate the OB-side shape inspector only as a preliminary validator; never treat it as Tower authorization. Require hosted owner crossing and negative tests with beta/non-owner, replay, wrong account, stale step-up, revoked session and forged attestation before any independent live gate is considered.

## Remaining external gates
Real broker account and options permission, current market/settlement provenance, protected floors, actual owner Review Center decision, manual human placement at broker and provider-side independent reconciliation cannot be completed from historical simulation or this source pack. No paid Render resources, direct OB–BuyBox capital path, Hybrid, Automated or deployment is included.
