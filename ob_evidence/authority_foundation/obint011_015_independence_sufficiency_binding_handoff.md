# OBINT011–015 — Independence + Sufficiency Binding

Status: CANDIDATE until Git remote-main verification.

Parent: `0b6155d9c6dfb0ddc3b67d54e9962e110a566d2f`

This pack binds the admitted candidate evidence set to an actual
ODBDATA086–090 `CorroborationWeightAssessment`.

The canonical sufficiency path derives the legacy
`independence_integrity_state` argument from that verified assessment;
callers do not provide the state directly on the canonical path.

Evidence requirements are integrity-bound to the effective policy identity
carried forward by the candidate context.

Important remaining boundary:

The requirement contents are not yet proven to have been natively emitted
by MODE_POLICY, and source/origin-family metadata is not yet natively
derived from the earlier provenance chain. Those are retained as explicit
integration work rather than falsely certified here.

This pack grants evidence independence and analytical-sufficiency authority
only. It grants no analytical conclusion, trade recommendation, ranking,
contract selection, broker submission, capital movement, Manual Live,
Hybrid, or Automated execution authority.
