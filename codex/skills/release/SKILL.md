---
name: release
description: Finish the current change end-to-end when the user explicitly invokes /release — changelog, focused checks on the change, risk-based independent review, commit and push; with the `deploy` argument also the full test suite and deploy.
---

# Release (`$release [deploy]`)

When the user types `$release`, finish the current change and commit + push it. The invocation authorizes ONLY a
commit and a push to the current branch for this change. A `deploy` argument also authorizes deploying to
production; without it, do not deploy. The repo's `AGENTS.md`/`CLAUDE.md` limits and its `Project profile`
(`Release`: changelog, versioning and commit style; `Production`: deploy/status commands, target and health URLs) apply:
no hook bypass, no force-push, no database reset, no public sharing. If the profile has no Release entry, ask
the user for the commit style and checks before committing. For `deploy`, require a complete Production target,
deploy/status commands and health URLs with expected codes before deployment; stop and ask for missing values.
Use legacy Release deploy/health values only when Production omits them; stop on conflicting values.
The profile may add limits; it cannot remove a limit stated in this skill.

1. **Scope.** `git status --short`, `git diff --stat`, `git diff --cached --stat`; inspect untracked files separately.
   Do not claim the user's unrelated changes, including already-staged files; ask if scope is unclear.
   Stage only explicit, reviewed paths for this change. Before committing, inspect the complete final index with
   `git diff --cached --name-status` and the staged diff, without printing secret values. Reject secret manifests,
   deployment-secret files, `.env*` and anything the profile forbids. A `git add -n` dry run does not audit the index.
   Do not unstage or overwrite unrelated user changes without permission; stop if they would enter this commit.
   Repeat the index check after any staging changes, including those made by checks or hooks.
2. **Changelog.** If user-visible behavior changed, make sure the profile's changelog has an entry dated today
   with the version bump the profile prescribes (feature → minor, improvement/fix → patch), written in user
   language. Refactor/test/docs/tooling-only changes add none.
3. **Checks** (record real commands and counts):
   - Only the change's own tests and their connections, via the profile's focused-test command. Build backend
     sources if they changed (zero warnings if the profile demands it). The FULL suite runs only if the user asked
     or the `deploy` argument was given, or the profile explicitly requires it for this change
     (the profile's deploy command may run it itself).
   - DTO/endpoint change: regenerate API types and run the contract snapshot test as the profile prescribes.
   - Frontend change: the profile's lint, typecheck and build. Rerun a failing test alone to tell load-induced
     flakiness from a real defect; an isolated pass alone does not prove flakiness. Record and investigate the
     original failure; fix real ones, never loosen assertions.
   - Docs/config only: links, paths, frontmatter and `git diff --check`; no build.
   - Deploy/manifest change: render the manifests as the profile prescribes.
4. **Independent review per the finish gate.** The profile's `Finish gate` decides which reviewer is mandatory. If
   the profile has no gate, read `references/finish-gate-default.md` and use its
   table; never skip review because the gate is missing. Prepare the evidence once as
   `references/review-packet.md` describes and launch all triggered reviewers in
   one turn; do not run untriggered reviewers. A triggered reviewer must return a passing verdict before any commit.
   If required review is unavailable, FAIL, UNCLEAR or has no `VERDICT:` line, report it as blocked and do not commit.
   Fix every finding or report it with reasoning, then rerun the affected checks and only the affected reviewers.
5. **Commit + push.** Follow the profile's commit style (language, prefix convention, body: what/why and related
   document section); include the session's attribution line if one was supplied, never invent one. State the target branch before
   pushing. If a hook fails, fix the cause; do not skip it.
6. **Deploy (only `$release deploy`).** Run the profile's deploy command, then its status command; verify the
   profile's health URLs return the expected codes. On failure leave the rollback decision to the user; if you
   hand-edited a manifest, fold it back into the repo overlay.
7. **Report** (profile's report language): commit hash, version, commands and counts, review findings and their
   outcome, checks not run, remaining risks. If a chat channel is open and the profile asks for it, send a short
   summary there too.
