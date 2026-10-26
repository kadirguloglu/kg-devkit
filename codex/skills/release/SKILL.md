---
name: release
description: Finish the current change end-to-end when the user explicitly invokes /release — changelog, focused checks on the change, risk-based independent review, commit and push; with the `deploy` argument also the full test suite and deploy.
---

# Release (`$release [deploy]`)

When the user types `$release`, finish the current change and commit + push it. The invocation authorizes ONLY a
commit and a push to the current branch for this change. A `deploy` argument also authorizes deploying to
production; without it, do not deploy. The repo's `AGENTS.md`/`CLAUDE.md` limits and its `Project profile`
(`Release` and `Production` entries: changelog file and versioning, commit style, commands, health URLs) apply:
no hook bypass, no force-push, no database reset, no public sharing. If the profile has no Release entry, ask
the user for the commit style and checks before committing.

1. **Scope.** `git status --short`, `git diff --stat` (staged, unstaged, untracked). Do not claim the user's
   unrelated changes; ask if unsure. Confirm with `git add -n` that secret files (secret manifests, deployment-
   secret files, `.env*`, anything the profile lists) do not enter the commit.
2. **Changelog.** If user-visible behavior changed, make sure the profile's changelog has an entry dated today
   with the version bump the profile prescribes (feature → minor, improvement/fix → patch), written in user
   language. Refactor/test/docs/tooling-only changes add none.
3. **Checks** (record real commands and counts):
   - Only the change's own tests and their connections, via the profile's focused-test command. Build backend
     sources if they changed (zero warnings if the profile demands it). The FULL suite runs only if the user asked
     or the `deploy` argument was given (the profile's deploy command may run it itself).
   - DTO/endpoint change: regenerate API types and run the contract snapshot test as the profile prescribes.
   - Frontend change: the profile's lint, typecheck and build. Rerun a failing test alone to tell load-induced
     flakiness from a real defect; fix real ones, never loosen assertions.
   - Docs/config only: links, paths, frontmatter and `git diff --check`; no build.
   - Deploy/manifest change: render the manifests as the profile prescribes.
4. **Independent review per the profile's finish gate.** The gate decides which reviewer is mandatory; a triggered
   reviewer must return a passing verdict before any commit; an untriggered one is not run (run it when in doubt).
   Give the diff and command evidence; fix every finding or report it with reasoning, and rerun affected checks.
5. **Commit + push.** Follow the profile's commit style (language, prefix convention, body: what/why and related
   document section) and end with the attribution line the session provides. State the target branch before
   pushing. If a hook fails, fix the cause; do not skip it.
6. **Deploy (only `$release deploy`).** Run the profile's deploy command, then its status command; verify the
   profile's health URLs return the expected codes. On failure leave the rollback decision to the user; if you
   hand-edited a manifest, fold it back into the repo overlay.
7. **Report** (profile's report language): commit hash, version, commands and counts, review findings and their
   outcome, checks not run, remaining risks. If a chat channel is open and the profile asks for it, send a short
   summary there too.
