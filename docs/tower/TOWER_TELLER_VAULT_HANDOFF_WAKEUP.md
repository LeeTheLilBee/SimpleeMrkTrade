# The Tower — Teller/Vault Handoff Wakeup

Locked doctrine:

Tower is the face.
Teller is the workflow.
Vault is the sealed memory.

Key rule:

Teller can ask.
Tower must decide.
Vault only answers Tower.

Correct flow:

1. Workflow need appears in Teller.
2. Teller creates a structured workflow request packet.
3. Teller sends request packet to Tower.
4. Tower checks permission, identity, clearance, step-up, owner/admin approval, and redaction rules.
5. Tower requests the allowed output from Vault.
6. Vault answers Tower only.
7. Tower returns allowed workflow result/status/proof to Teller.
8. Teller displays only the workflow-safe result.

Teller does not call Vault directly.

Next Teller-facing corridor:

GP451–GP460:
ARCHIVE VAULT — TELLER TO TOWER REQUEST HANDOFF LAYER

Later Tower corridors:

GP461–GP470:
Tower Vault Request Protocol Gate

GP471–GP480:
Tower Authorized View Protocol

GP481–GP490:
Tower Authorized Download Protocol

GP491–GP500:
Tower Protocol Receipt Closeout
