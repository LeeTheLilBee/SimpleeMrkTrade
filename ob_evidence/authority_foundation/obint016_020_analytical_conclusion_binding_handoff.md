# OBINT016–020 — Analytical Conclusion Binding

Status: CANDIDATE until remote-main verification.

Parent: `d90a654ff12960f9f9dd597c51dc0e659eb29381`

The canonical conclusion path now consumes the verified
CandidateSufficiencyReceipt instead of accepting a caller-supplied
sufficiency state.

Support and uncertainty compatibility states are derived by the canonical
binding layer rather than accepted as direct OBDATA096–100 caller inputs.

Evidence references must belong to the admitted candidate evidence set.

Important boundary:

Receipt integrity does not prove that arbitrary natural-language claim text
is factually true, nor does it prove that an inference logically follows.
This pack governs analytical evidence binding and conclusion integrity.

No trade recommendation, ranking, automatic contract selection, broker
submission, capital movement, Manual Live unlock, Hybrid execution, or
Automated execution authority is granted.

## Support / conflict semantics

Evidence support and unresolved conflict are intentionally separate
dimensions on the canonical path.

A DIRECT claim with admitted direct evidence remains `SUPPORTED` as to its
evidence basis. If unresolved conflict exists, that conflict is preserved in
`unresolved_conflicts`, derives material uncertainty, and causes the sealed
analytical-integrity primitive to require review.

The integration layer does not erase direct support merely because conflict
exists, and it does not erase conflict merely because direct support exists.
