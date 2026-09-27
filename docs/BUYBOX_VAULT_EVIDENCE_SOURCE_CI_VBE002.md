# VBE002 — BuyBox ↔ Tower ↔ Vault evidence metadata-only CI

Parent: PR #35 draft at \`1b9a3e191cf8f8b61adb59b790033983f767f42f\`.
This pack adds test automation and documentation only, without modifying
the metadata schema, Tower preparation rules or local pending lineage engine.

GitHub CI compiles exact modules and runs the existing synthetic tests for
request fingerprinting and forbidden raw path fields, incomplete/mismatched
Tower gate denial, PENDING rather than ARCHIVED on a complete self-reported
checklist, corrections/version replay, and immutable local snapshot records.

A passing CI result confirms **only source behavior**. The
\`tower_context.identity_verified\` and other boolean arguments in the current
Tower preparation function are test inputs; they do not authenticate a
principal, entity, step-up, approval or a genuine issuer. No public route
may accept them from a caller. PENDING local lineage is not a canonical Vault
receipt, and an ARCHIVED-shaped JSON document is never archival evidence.

Original bytes transfer, independent scanner/quarantine, provider/KMS,
append-only encrypted storage, retention/legal holds, actual authenticated
Tower middleware, protected retrieval and owner acceptance remain absent.
There are no cloud secrets, paid resources, production user files or provider
calls in CI. Parent PR #35 remains DRAFT / NO LIVE ARCHIVAL. Keep the other
Vault storage preparation PR #38 and BuyBox source-only hold #42 independent.
