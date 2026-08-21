# OBUX041–045 — Canonical Options-First Trade Center

## Purpose

OBUX041–045 replaces the legacy Trade Center presentation with the canonical
beta-facing Observatory trading cockpit.

It does not replace the existing options engine, lifecycle engine, Manual Live
operating system, proof system, fill capture, position monitoring, or review
machinery.

Those systems remain underneath the canonical room.

## Product hierarchy

The room prioritizes:

1. money already in motion;
2. decisions requiring human attention;
3. one hero trade workspace;
4. secondary candidates and proof detail.

The beta-facing room is not list-first.

## Trade workspace

One trade becomes the primary visual object.

The workspace exposes canonical, source-backed information including:

- symbol;
- thesis;
- option identity;
- strike;
- expiration;
- premium;
- bid / ask;
- IV;
- delta when available;
- liquidity / quote quality;
- rank / score;
- entry;
- stop;
- target;
- max risk;
- expected hold;
- evidence;
- lifecycle;
- position health.

## Lifecycle

The visible flight path maps the existing engine lifecycle into:

Research → Contract → Preflight → Entry → Manage → Exit → Review

No duplicate lifecycle engine is created.

## Mode transformation

### Survey

Observation and comparison only.

### Paper

The user chooses the paper contract and practices the simulated lifecycle.

### Manual Live 1

The owner chooses the option contract.

OB prepares the operating workflow.

The owner executes outside OB.

The owner reports placement / fill information back into the existing Manual
Live operating machinery.

### Hybrid

OB may display the objective ranked contract set.

The user selects the contract.

Rank order does not equal selection authority.

### Automated

Locked.

## Proof / legacy compatibility

Existing Manual Live, rehearsal, receipt, proof, and review scripts remain
loaded.

Their historical `tradeCenterMount` is retained inside a hidden compatibility
surface so proof infrastructure does not become the owner/beta-facing room.

## Quarantined legacy behavior

The canonical room does not use:

- hardcoded MU / AMD / INTC candidates;
- fixed confidence 82 / 61 / 38;
- fabricated "next monthly call";
- browser-side yfinance;
- direct browser market fetch;
- broker execution;
- automatic execution.

## Tower

No Tower code is modified by this build.
