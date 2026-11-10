# Hand-off contract

## Caller to read-only reviewer
Reviewers have no shell, so the caller prepares the evidence once and shares it by path instead of pasting it into
every prompt:

1. Save the diff to a file outside the repository's tracked files (the session scratch/temp directory):
   `git diff <base>...HEAD -- <paths>` for commits, or `git diff` plus `git diff --cached` for the working tree.
   List untracked files separately; never write secret values into the file.
2. Reviewer prompt = one sentence of intent + `DIFF: <path>` + `FILES: <changed files>` + one
   `EVIDENCE: <command> -> <result>` line per command already run (build, focused tests, migration, audit).
3. One packet serves every triggered reviewer; launch them in the same turn.

A reviewer that lacks an input answers `NEEDS: <what is missing>` and `VERDICT: UNCLEAR`: supply it and call that
reviewer once more; do not treat it as a pass.

## Writer agent to caller
Developer, test-developer and devops reports end with:

```
STATUS: DONE | PARTIAL | BLOCKED
CHANGED: <paths>
CHECKS: <command> -> <result and counts>      (one line per command actually run)
NOT RUN: <check> - <reason>                   (omit only if nothing was skipped)
HANDOFF: <what the next agent or the main session must do>
```

`DONE` means every check the agent's definition requires ran and passed. A failed or skipped required check means
`PARTIAL`; `BLOCKED` means the agent could not proceed. Treat a report without a `STATUS:` line as `PARTIAL` and
verify it before relying on it.
