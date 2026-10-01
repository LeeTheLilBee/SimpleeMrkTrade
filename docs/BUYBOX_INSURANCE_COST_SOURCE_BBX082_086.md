# BuyBox BBX082–086 — source-bound insurance cost proposal for future Teller readiness

**Source only, no paid services, no insurance binding/purchase and no live Teller
request.** Starts from BuyBox insurance/financing owner workbench PR #26 at
45446efbbba5b2e6157072ac1b5749c392b45f92, including BBX077–081.

## Reason

The current buybox.teller.readiness.question.v1 enumerates source-bound
proposed price/debt/equity/closing/reserve values, but does **not** express
original-backed insurance premium, exclusion, current coverage, or the
owner's cost-inclusion assumptions. Silently changing its exact-field wire
would break Tower's independent TWR212–216 reviewer and could misrepresent
a quote as spendable readiness. This pack instead defines a separate
buybox.teller.insurance.costs.source.v1 local proposal. It is not a
substitute for verified Teller money+management readiness.

## Implemented

- Read the exact current saved BuyBox opportunity/revision/SHA-256 under a
  fresh SQLite writer-lock transaction; no caller-provided opportunity JSON
  or role is accepted.
- Select **one current, not-superseded** financing source option and **one
  current, not-superseded** owner-recorded insurance original by ID.
  Independently reject missing/relinked original metadata and unpriced
  certificate inputs; do not silently treat unknown premium as $0.
- Bind saved revision/digest, original document digests, source-linked record
  IDs and review flags, separately recorded annual/upfront insurance premiums,
  owner cost-inclusion assumptions, and current illustrative financing overlay.
  Compare only the chosen alternatives; never sum competing offers.
- Canonical source fingerprint and <=300-second local validity, with
  recheck against current saved revision **and** exact chosen current records.
  Changed purchase price, costs, term correction, insurer source/digest or
  expiry results in stale local status. A SHA-256 is a tamper indication for
  the local record, **not** a Tower signature, actual downloaded-original
  byte verification or external insurer/broker attestation.
- Expose only CURRENT_LOCAL_UNSUBMITTED or STALE_OR_EXPIRED_LOCAL on
  recheck. Current coverage, insurer and lender confirmation, available funds,
  management capacity and Teller readiness remain UNKNOWN/False. No
  Tower/Teller/OB/Vault HTTP call, external receipt, purchase or capital release.

## Real integration still gated

A future, separately versioned Tower adapter must authenticate the principal,
entity, current permission/purpose, refresh the exact BuyBox record and
source bytes, check original/correction lineage and current opportunity
revision, and obtain a true Teller-issued source-and-terms-bound money and
management-capacity answer. Recheck acquisition closing cash plus upfront
premium without double-counting, annual operating costs and reserve floors.
For ATM acquisitions, preserve Set 1/Set 2 and vault replenishment as
separate sleeves and recheck protected floors; never direct BuyBox→OB balance.
Insurance coverage truly in force requires insurer/agent/policy confirmation
and intended lender/operating requirements, not the presence of a PDF or
certificate. Grounds/ATM operations receive a separate accepted post-close
policy/renewal handoff after verified acquisition.

Owner's BuyBox SOURCE-ONLY HOLD in issue #42 remains in force. No Render
service/disk/database, provider credential, production finance approval,
resident/tenant record, cash movement or mode unlock is created by this pack.
