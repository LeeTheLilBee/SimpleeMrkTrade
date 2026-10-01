# BuyBox BBX077–081 — Insurance Desk and Financial Cost Overlay

Owner requested that insurance be a real part of acquisition discovery, risk,
financing and handoff across **all seven verticals**, not an optional ATM-only
attachment. This source-only pack implements that in [PR #141](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/141),
based on the already merged Financing Desk [PR #96](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/96).

## Owner workflow and authority

1. Upload an actual original insurance document via BuyBox's existing encrypted
   intake. All seven verticals accept supplemental `insurance_document`.
   Existing multifamily/commercial `insurance_quote` evidence can also be
   reused and retains its separate vertical-specific critical-diligence rule.
   Simply entering a URL, label or insurer name cannot create insurance truth.
2. Transcribe the exact original's document type (QUOTE, BINDER, POLICY or
   CERTIFICATE), insurer/broker, source locator, source date, relevant coverage
   categories, proposed dates, written premium and owner-proposed upfront
   payment, and exact limits/deductibles/exclusions where available. An
   unpriced certificate can have a null premium; never replace unknown with
   free insurance. Original artifact ID, evidence ID and SHA-256 are retained.
3. An existing owner can later document-review that same original using the
   existing evidence revision chain. Even when the document is marked
   DOCUMENT_SUPPORTED, insurer/producer confirmation, binding, premium payment
   and a policy truly in force remain UNKNOWN. A certificate alone does not
   independently establish present coverage; a quote is not a bound policy.
4. Changed statements are appended as source-linked corrections, not silently
   overwritten. A correction may supersede only the same recorded carrier and
   document kind; the original remains in opportunity history.
5. The room flags expired quotes, future-dated originals, proposed closing
   before the stated effective coverage or after expiry, missing dates and
   broken source links. These are review flags, not legal or professional
   insurance determinations. Asset-specific coverage codes are **prompts** to
   discuss with a qualified insurance professional, not claims of universally
   required policies or prescribed limits.
6. Financing overlay combines ONE chosen insurance record with each currently
   recorded financing alternative for a clearly labeled illustrative comparison.
   It adds owner-entered upfront premium to the unverified buyer cash gap only
   if the owner reports that premium is **not** already included in other
   closing costs. It subtracts recorded annual premium from comparable operating
   difference only if the owner says that premium is **not** already in
   reviewed annual operating expenses. Both inclusion flags are unverified
   owner cost assumptions. A certificate without a premium cannot produce a
   money estimate, and alternative insurance packages are not automatically
   summed, purchased or selected.

## Related systems — contract notification for their chats

- **Tower:** Insurance is part of BuyBox's Tower-launched private dossier.
  Actual signed owner approval, protected proof routing and close-stage gates
  remain with Tower. No new independent login, bearer token or direct Vault call.
- **The Teller:** Receives the appropriate verified insurance expense, escrow,
  upfront premium, retained liquidity, renewal and management obligations only
  in a future authenticated, version-bound readiness request. BuyBox's local
  insurance/loan overlay **does not modify protected floors or return spendable
  funds**. Annual premium is an operating-cost input, whereas a one-time upfront
  premium is a closing liquidity requirement unless properly accounted for
  elsewhere. Require refresh for materially changed insurer terms or annual
  premium.
- **Grounds / property operations:** Once authorized/acquired, transfer exact
  actual policy/binder documents, coverage dates, named insured/additional
  insured and lender clause verification requirements, premium renewal calendar,
  deductibles, exclusions, claims contact and budget treatment through its
  versioned, receiver-acknowledged handoff. Do not grant coverage by importing
  BuyBox's owner record.
- **SimpleeOnTheGo:** Include route/machine exposure, cash/vault and transport
  exposure, location/processor/vendor contract insurance obligations, actual
  bound-document proof, renewals and incident contacts in the separately
  accepted post-close operations transition. Replenishment cash remains distinct
  from premium and operating expenses.
- **Archive Vault:** Original bytes remain in encrypted local BuyBox intake
  until authenticated Tower-mediated scanning/archival. A local digest or an
  insurer-labeled PDF is not a canonical Vault archival receipt.
- **Soulaana:** Reads the current actual records/expiry and comparison flags,
  cites source evidence/original IDs and explains how a premium affects a
  model. No live insurer lookup, policy purchase or external authorization.

## Explicit production gaps

No insurer, broker, agency, rate engine, policy admin system, or lender-coverage
verification API is connected. There is no price lookup, actual coverage-in-force
confirmation, legal-jurisdiction-specific requirement engine, employee/workers
compensation underwriting, claims workflow, insurance binding or purchasing.
The workbench does not call external services or provision Render resources.
The authoritative Teller/Tower gates remain UNKNOWN/BLOCKED.

Tests cover seven empty asset verticals, real source binding and digest, quote
versus certificate semantics, missing prices, expiry and proposed close gaps,
append-only correction, double-count prevention, tampered encrypted original,
owner login, CSRF, optimistic revision and grounded Soulaana. Run the existing
BuyBox foundation CI alongside its Tower, Teller and document-integrity checks.
