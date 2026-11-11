---
name: rollback
description: Plan and, on explicit approval, roll the production deployment back to a previous image when the user invokes /rollback — checks schema compatibility first.
disable-model-invocation: true
argument-hint: "[image-tag]"
---

# Production rollback (`/rollback [tag]`)

`/rollback` only produces a plan; rollback commands run after the user's explicit approval in the current
conversation. Without a tag, the target is the previous successful release. The repo's `AGENTS.md`/`CLAUDE.md`
limits and its `Project profile` apply: `Production` supplies context, namespace, workloads, registry repositories,
health URLs with expected codes, rollback/deploy commands and runbook; `Persistence` supplies the migrations
directory. Deploy and health values come from `Production`; a legacy `Release` value is used only when `Production` omits it, and conflicting values stop the run.
Without a Production entry or required target/health values, stop and ask. Never modify database data, DNS,
volumes or secrets; do not read business data or secret values. The profile may add limits; it cannot remove a limit stated in this skill.

1. **Current state.** Read `${CLAUDE_PLUGIN_ROOT}/skills/live-check/SKILL.md` and carry out its read-only steps (the
   file reference is intentional: that skill is user-invoked and cannot be loaded with the Skill tool): running
   image tags and rollout history of every workload. Prove that the problem started after the latest rollout; if it did not, do not recommend rollback.
2. **Target images.** Resolve the given tag, or the previous successful release from release/deployment evidence,
   to a digest for every image repository. Rollout history alone does not prove a release succeeded. All images
   use the same release tag unless the profile says otherwise. Map current and target digests to their source
   commits using build/release metadata; do not assume an image tag is a Git ref. Check inter-workload compatibility
   during the mixed-version window. Missing target, success or source evidence blocks execution.
3. **Schema compatibility (gate).** Use Persistence's migrations directory. Locate changes with
   `git log --stat <target-commit>..<current-commit> -- <migrations-dir>`, then read the migration contents.
   Compare the target's schema expectations with the schema actually applied, using the runbook's documented
   read-only migration-status evidence; source history alone is insufficient. For a project without migrations,
   establish that from the repo/runbook rather than assuming it. Missing mappings, applied-schema evidence or
   unresolved schema drift mean compatibility is UNCLEAR: report a blocked plan, do not execute. If an intervening
   applied migration drops columns/tables, narrows types or transforms data, do NOT roll back; present fix-forward
   or hotfix options. Additive-only changes may be compatible; explain why. Never reverse-migrate the live database.
4. **Plan and approval.** Write exact commands, workload order, current/target digests, expected downtime and the
   mixed-version window. For Kubernetes undo, map each target digest to a specific revision and inspect the entire
   pod-template diff: `rollout undo` can revert configuration too. Use `--to-revision=N` only when that revision's
   pinned or proven immutable image references match the target digests and its other template changes match
   the approved plan; otherwise use the profile's explicit pinned-image deployment command. Never use an
   unqualified undo. Account for GitOps/other reconciliation in the runbook.
   Get explicit approval for this concrete plan; approval does not waive the compatibility gates.
5. **Execute (after approval and passing gates).** One workload at a time with the approved command; for example
   `kubectl --context <ctx> -n <ns> rollout undo deployment/<name> --to-revision=N`, followed by
   `kubectl --context <ctx> -n <ns> rollout status deployment/<name> --timeout=600s`. For compose/plain hosts,
   redeploy the approved pinned image through the profile's command. If a workload fails, stop before the next
   and report the partial state; do not improvise further mutations. In Claude, the guard hook may ask again;
   it is absent in Codex and is not a substitute for approval.
6. **Verify.** Repeat the live-check steps from that file; confirm desired and running image digests match the approved targets for every
   workload, health codes match, pods are ready and restart counts have not increased over the recorded baseline.
7. **Realign the repo.** Before the next deploy, align its source of truth with the intended compatible state so
   it does not redeploy the faulty images. Propose an image pin, a forward fix or a selective `git revert` as
   appropriate, with the user's approval for repo mutations. Do not blindly revert migration history or snapshots
   for migrations still applied in production. Report any reconciliation/repo work still required.
8. **Report** (profile's report language): previous/target/observed tags and digests, source commits, schema and
   revision evidence, commands, verification results, remaining risk and repo work still required.
