# TWR212–216 — BuyBox proposal → Tower → Teller source-review boundary

**Source only. No hosted BuyBox route, Teller API request, account balance, capital readiness, approval or paid infrastructure.**

## Independently reviewed source

- Dedicated Tower base: \`024ab1bc9d9508227821d90e96d01b98fdea548f\`.
- Independent BuyBox umbrella PR #26: \`728219b4fe1175dbbdb6387c578fc798e1262ef0\`; real \`buybox/teller_readiness_question.py\`, not a copied sample.
- The producer's \`buybox.teller.readiness.question.v1\` is a proposed **UNSUBMITTED** question. Its funding lanes for ATMs distinguish \`ATM_SET_1_ACQUISITION\` and \`ATM_SET_2_ACQUISITION\`; neither is spendable capital truth. Multifamily uses \`GROUNDS_ACQUISITION_UNVERIFIED\`; remaining verticals use \`MISSION_ACCOUNT_UNASSIGNED\`.

## New Tower-side intake reviewer

\`tower/buybox_teller_proposal_review.py\` validates the exact incoming versioned request field set, fixed BuyBox→Tower→Teller purpose, current-form timestamp/expiry (max 300 seconds), seven source vertical IDs, opportunity revision and SHA-256 snapshot, exact proposed terms and two-decimal monetary strings, lane isolation, and the existing BuyBox terms fingerprint. It rejects extra client assertions, \`READY\` flags, broker values, malformed/changed terms, unexpected routes, expired/naive timestamps and changed snapshot/fingerprint pairs.

A matching SHA-256 **does not authenticate** its source. The only successful outcome is \`SOURCE_ONLY_NOT_SUBMITTED\`, with money/capacity \`UNKNOWN\`, no verified Tower entity/owner, no Teller request, no receipt, and no capital/acquisition approval. Responses do not emit raw proposed amounts or private account data. No live route, browser authority, environment secret, broker call or payment action exists in this pack.

The CI job checks out the exact independent BuyBox commit, starts its actual SQLite-backed \`prepare_unsubmitted_teller_readiness_question\` in a separate process, and confirms that Tower accepts its shape while preserving the blocked status. It also runs existing registry, BuyBox and Teller regression tests.

## Dependency-gated next implementation

1. Real authenticated Tower current owner/entity/mission-sleeve/purpose approval. Re-fetch current BuyBox opportunity/revision/digest from actual protected BuyBox storage and invalidate on any material change.
2. Tower-mediated, issuer-bound, idempotent Teller readiness request for the exact terms fingerprint; independently verify Teller's current financial **and** management/expansion capacity response. Missing/stale/conflicted/changed terms are UNKNOWN, not READY.
3. Teller must mediate any underlying OB truth; BuyBox cannot read OB account balances, pool ATM Set 1 and Set 2, or override protected capital floors.
4. Separate actual lender, title, contract, evidence, owner decision and closing authorization before funding or operational handoff. A proposal, local decision note, or receipt-shaped JSON is not proof.
5. Actual owner walkthrough and external service/provider attestation before claiming live functionality.

**Cost and release constraints:** issue #42 remains SOURCE-ONLY HOLD for BuyBox. No paid Render service/disk/DB/object storage, production BuyBox deployment or owner grant. This Tower module is deliberately dormant and causes no new user-access route.
