# Hand-off contract (ÖNERİ; hedef konum: `plugins/kg-devkit/references/review-packet.md`)

## Caller → read-only reviewer
Reviewers have no shell, so the caller prepares the evidence once and shares it by path instead of pasting it into
every prompt:

1. `git diff <base>...HEAD -- <paths> > <scratch>/review.diff` (or `git diff` + `git diff --cached` for the working tree).
2. Prompt = one sentence of intent + `DIFF: <path>` + `FILES: <list>` + `EVIDENCE: <command → result>` lines.
3. One packet serves all triggered reviewers; launch them in the same turn.

## Writer agent → caller (last lines of every developer / test-developer / devops report)
```
STATUS: DONE | PARTIAL | BLOCKED
CHANGED: <paths>
CHECKS: <command> → <pass/fail + counts>      (one line per command actually run)
NOT RUN: <check> — <reason>                    (omit only if nothing was skipped)
HANDOFF: <what the next agent or the main session must do>
```
`DONE` is allowed only when every check the agent's own definition requires was run and passed. A failed or skipped
required check means `PARTIAL`. The caller treats a report without a `STATUS:` line as `PARTIAL`.
