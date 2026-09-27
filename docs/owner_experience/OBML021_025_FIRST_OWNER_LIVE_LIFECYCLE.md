# OBML021–025 — First Owner Manual Live L1: noncircular go/no-go

September 27, 2026. **Requested first owner activation target:** September 28, 2026. This date is a desired checkpoint, **not** an automatic mode unlock or permission attestation.

## Why this is a distinct fix

Existing `web.ob_manual_live_beta_gate_report.REQUIRED_EXTERNAL_GATES` has eight external gates and correctly holds every real grant absent independently authenticated proof. One gate, `EXTERNAL_MANUAL_ORDER_RECONCILIATION`, is however logically **post-order**: a genuine filled/submitted order receipt cannot exist before the first human order is placed. Do not accidentally require a fake prior fill to enable an owner review-only mode. Equally, do not waive reconciliation once the human places an order.

The new `web.ob_manual_live_l1_phase_contract.owner_l1_first_live_phase_contract()` groups all eight unchanged source gate IDs into three stages:

**1. Before authorizing owner-only Manual Live L1 review mode (six gates).** Tower must independently verify the *current* real owner and exact trading mission account, purpose-specific fresh step-up, revocation and single-use real issuer→OB receiver; observed approved hosted runtime; independently authenticated brokerage account/options permissions; settled/spendable/protected-capital policy and reserves; current market/effective risk/kill-switch truth; distinct operating/security/compliance owner approval. This enables at most access to the review workflow after independently verified authorities, **not** a trade, purchase, fill or money transfer. A generic Tower launch and a signed OB namespace are not enough.

**2. Before EVERY actual human broker order (four rechecks).** Independently recheck current provider options entitlement, account/settlement/protected floors, current source market/safety, and separate owner Review Center decision for the exact candidate/size/terms. Deny stale/revoked/changed conditions. OB **does not** submit the order; a separately authorized owner would manually place it using the brokerage's own protected UI. An OB recommendation/ranked contract cannot self-select or authorize a trade.

**3. AFTER a human order (one gate).** Independently reconcile the genuine broker-reported submitted/filled/rejected/cancelled outcome and update the exact account's tracking and review. Without the provider receipt, the outcome is `UNVERIFIED`, never `FILLED`; do not backfill a synthetic order as real evidence.

## What remains open today

As of this source checkpoint, Tower [PR #68](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/68) is draft/source-only and does not issue an authenticated OBML owner/account/purpose-specific one-time grant. Hosted Survey/Paper adapter source is merged in the separate Tower branch but default OFF and separate from real permission. Actual broker approval, live balance/withdrawable funds, protection of trust and ATM Set 1/Set 2 reserve floors, production operator approval and owner walkthrough are not externally verified here. Therefore the returned contract **always states HOLD** and all execution/money flags false. Do not configure a production secret or replace these checks with client booleans.

For an intended IBKR account, independently inspect its own Client Portal → User menu → Settings → Trading → Trading Permissions for approved instruments and options level before any hypothetical real trade, and independently verify the **exact account** and funds with the broker. IBKR's published guide explains these permissions: https://www.ibkrguides.com/clientportal/tradingpermissions.htm and https://www.ibkrguides.com/clientportal/optionstradingpermissions.htm . A request or an OB checklist does not prove approval. Do not enter brokerage passwords, account numbers, bank balances, secrets or settlement receipts into a public GitHub issue.

## Acceptance

The new source contract imports the **existing eight** external gate identifiers without inventing a competing issuer or assessment. Tests cover complete gate accounting, noncircular first fill sequencing, per-order fresh review, hold/no-live booleans, and no browser/self-asserted verifier input. CI also runs existing OBML source/beta, rehearsal and full repository tests. No paid Render, order API, capital movement, real trade or live activation is authorized by this document/PR.
