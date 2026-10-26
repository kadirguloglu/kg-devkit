---
name: verify-change
description: Review the current repository diff and choose proportionate verification before handoff, when the user explicitly requests a final change check.
disable-model-invocation: true
user-invocable: true
---

# Change verification

When the user invokes `/verify-change`, assess the current diff and the verification evidence. The repo's
`AGENTS.md`/`CLAUDE.md` limits apply, including its `Project profile` (commands, rule documents, finish gate,
report language). This skill grants no authority to commit, push, deploy or reset a database.

1. `git status --short`, `git diff --stat`, `git diff --cached --stat` to find the scope. Tell staged, unstaged
   and untracked files apart; never claim or delete the user's changes. Read the relevant diff; open large
   generated files only if the changed schema/contract requires it. If the working tree is clean, the target is
   the last commit (`git diff --stat HEAD~1..HEAD`, `git show`); state which target you used.
2. Compare the changed behavior with its callers and contract. Read the profile's path-matched rule documents and
   only the relevant sections of the technical documents. Verify document claims against concrete code; do not
   treat an old decision record as current behavior.
3. Choose the smallest meaningful set of checks:
   - Documentation or agent/skill config only: frontmatter, existing file paths, links, stable section ids,
     contradictions/duplication and `git diff --check`; no application build.
   - Backend behavior: build plus focused regression; widen to affected groups for shared infrastructure/contracts.
   - Frontend behavior: lint/typecheck/build plus the related tests; widen if shared auth/cache/UI helpers changed.
   - Anything the profile's finish gate names (schema, security, tenancy, storage, ...): the required independent
     reviewer must pass; do not call reviewers the gate does not trigger.
4. Use a YAML/CLI validator when one exists; otherwise state the limit of the static check. Do not install new
   dependencies or plugins. Do not repeat checks that already passed for this same change without reason.
5. Review the final diff. Investigate why a failed check failed; do not loosen assertions or pull unrelated
   defects into scope. Fix inside owned files if needed and rerun only the affected checks.
6. Report (in the profile's report language, default the user's): the change and rationale, real commands and
   results, findings with source locations, checks not run and remaining risks. State test counts only when you
   can confirm them from output.
