# OBFIXINT001–005 — Foundation Integration Closure

This additive closure pack addresses the four runtime-reproduced findings
from the post-OBINT001–025 audit without rewriting sealed OBDATA or OBINT
history.

## OBFIXINT001

Installs a verified authority-artifact boundary. Bare caller-supplied
identity/hash strings are no longer sufficient on the closure path; a
serializable native authority object is required and its complete state is
hashed.

## OBFIXINT002

Moves candidate identity from one-context ownership to stable
target/instrument/mode/policy/purpose ownership. Multiple independently
verified context receipts may therefore contribute distinct observations
to one candidate when those stable identities remain exactly compatible.

Exact option identity includes contract ID, underlying, right, strike and
expiration.

## OBFIXINT003

Independence receipts retain and hash the complete canonical origin set.
Sufficiency consumes the origins held by that verified receipt. There is
no second caller-supplied origins boundary.

## OBFIXINT004

Introduces an explicit policy-requirement authority. Requirement contents,
policy identity and requirement hash are integrity-bound before
sufficiency can consume them.

## OBFIXINT005

Complete independence and sufficiency assessment serialization is included
in the new closure receipts.

## Boundary

This closes the demonstrated integration boundary defects. It does not
authorize trading, ranking, automatic contract selection, broker
submission, capital movement, Manual Live, Hybrid, or Automated execution.

The sealed OBDATA011–100 and OBINT001–025 files remain historical,
byte-identical foundation primitives.
