# OBBETA001–005 — September 28 owner beta copy/source boundary correction

Base: `main@aaa8fb3f3fc6f832b1b9d7c28b6aa87e1e457bc5`, after the accepted OBML016–020 Tower namespace source correlation. This bounded UI work does **not** alter any Tower, engine, account-capital, Review Center, broker, mode or hosted authorization code.

## Finding and fix

An older beta readiness drawer described `Paper / Manual Live Level 1` as a general tester mode and instructed a `tester/owner` to manually place a trade, mark a fill and monitor it. That copy predated the source-only Manual Live authority reports and could suggest actual authorization that does not exist. The drawer now clearly distinguishes:

- Invited **testers**: Survey and Paper practice only. No trading authority.
- **Owner**: Manual Live L1 *rehearsal* and source-labeled review only. No real broker placement from this beta screen.
- **Actual owner Manual Live**: HOLD pending independent Tower server-authenticated exact account/purpose entitlement, fresh specific step-up, current revocation, one-time Tower-issued token, secure OB receiver and observed hosted crossing; separately broker account/options/settlement, protected floors, current risk/market, owner Review Center receipt, human broker placement with independently sourced reconciliation, and operating/security/compliance approval.

A good `obai1` namespace token is not a person/session/step-up/permission or broker assertion. Preserve the one canonical source receiver (PR #82), bounded local source nonce callback (PR #84) and OB source-claim correlation (PR #85). Overlapping draft PR #81 should not be merged as a second verifier. Draft owner-clearance request #68 is still separate.

The revised checklist and SOP classify rehearsal decisions and outcomes accurately, and the status cards explicitly keep real Manual Live on HOLD. Tester and owner dashboard boundaries, protected mission accounts and Live Auto Locked are unchanged. The UI wording is **not** an authenticated runtime check; server-side controls remain authoritative.

## Gate

`tests/test_obbeta001_005_owner_tester_truth.py` asserts no general tester Manual Live or broker-placement wording, practice-only receipts, fail-closed namespace semantics and separated owner/normal surfaces. The dedicated Actions workflow runs focused upstream source/consumer/replay and beta regressions plus the full repository suite. Verify exact PR head before merge. No paid Render or secrets, external account, production route, owner grant or deploy claim.

## Next actual integration, separately owned

Tower must complete PR #68's real purpose-bound server issuer/receiver and durable shared replay for actual hosted topology. OB can then consume only independently authenticated, scoped *review-only* Tower evidence via a new accepted contract, without promoting namespace receipts. A hosted beta walkthrough and authenticated provider/broker evidence remain independent external acceptance steps. Source-only UI strings and local SQLite do not satisfy those gates.
