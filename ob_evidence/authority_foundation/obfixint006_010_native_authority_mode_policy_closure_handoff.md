# OBFIXINT006–010 — Native Authority + MODE_POLICY Closure

## Parent

`b28929f52d9581ffcfa94776e4b32747149235ea`

## Feature branch

`obfixint-native-authority-mode-policy-obfixint006-010`

## Purpose

This pack closes the remaining foundation integration bypasses discovered after OBFIXINT001–005.

### OBFIXINT006 — Typed native authority boundary

Certified authority artifacts reject bare mappings and arbitrary objects as native authority proof. Certified authority must originate from approved OBDATA authority modules.

### OBFIXINT007 — Native-derived verdict/reason

The certified authority API no longer accepts caller-controlled `verdict` or `reason`. Canonical gate outcome is derived from native OBDATA authority state and mapped to `ALLOW`, `REVIEW`, `BLOCK`, or `UNKNOWN`.

### OBFIXINT008 — Certified canonical context doorway

Legacy context receipts remain available for compatibility, but they are explicitly uncertified. Foundation certification requires a canonical context receipt carrying certified native-authority binding.

### OBFIXINT009 — MODE_POLICY authorship

Evidence requirements are projected from canonical MODE_POLICY state. The projection binds validated mode state, mode-state reference, effective-policy authority, requirements, policy identity, and policy hash.

### OBFIXINT010 — Adversarial closure

The original five exploit classes are closed:

1. arbitrary mapping masquerading as native authority — CLOSED
2. caller-controlled certified verdict/reason — CLOSED
3. legacy eligible context bypassing certified authority — CLOSED
4. arbitrary requirement authorship under policy identity — CLOSED
5. disconnected MODE_POLICY authorship — CLOSED

## Validation

- Focused OBFIXINT006–010: **5 passed**
- Foundation certification: **10 passed**
- OBFIXINT001–005 regression: **10 passed**
- Complete OBINT / OBFIXINT regression: **56 passed**
- Full Observatory suite: **1151 passed**

## Boundary

This remains a foundation integrity system only.

It does **not** grant:

- natural-language truth proof
- logical inference proof
- trade recommendations
- trade rankings
- automatic contract selection
- broker submission
- capital movement
- Manual Live unlock
- Hybrid execution
- Automated execution

## Files changed

- `ob_evidence/authority_foundation/obfixint006_010_native_authority_mode_policy_closure.json`
- `ob_evidence/authority_foundation/obfixint006_010_native_authority_mode_policy_closure_handoff.md`
- `tests/test_obfixint001_005_foundation_integration_closure.py`
- `tests/test_obfixint006_010_native_authority_mode_policy_closure.py`
- `tests/test_obint021_025_foundation_integrity_certification.py`
- `web/ob_canonical_reasoning_context_spine.py`
- `web/ob_foundation_integration_closure.py`
- `web/ob_foundation_integrity_certification.py`
- `web/ob_operating_mode.py`

## Seal rule

The pack is considered sealed only after:

- exact file wall
- full Observatory wall
- remote race checks
- exact commit
- feature push verification
- FF-only main integration
- non-force main push
- remote main verification
- clean final worktree

A separate read-only final foundation certification audit follows the seal before the foundation is declared fully closed.
