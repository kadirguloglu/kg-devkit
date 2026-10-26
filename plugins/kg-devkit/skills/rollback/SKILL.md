---
name: rollback
description: Plan and, on explicit approval, roll the production deployment back to a previous image when the user invokes /rollback — checks schema compatibility first.
disable-model-invocation: true
user-invocable: true
argument-hint: "[image-tag]"
---

# Production rollback (`/rollback [tag]`)

`/rollback` only produces a plan; rollback commands run after the user's explicit approval in the current
conversation. Without a tag, the target is the previous successful release. The repo's `AGENTS.md`/`CLAUDE.md`
limits and its `Project profile` `Production` entry (context, namespace, workload names, registry repositories,
migrations directory, health URLs, runbook) apply. Without a Production entry, stop and ask. Never touch
database data, DNS, volumes or secrets.

1. **Current state.** Run the `/kg-devkit:live-check` steps (read-only): running image tags and rollout history
   of every workload. Prove that the problem started after the latest rollout; if it did not, do not recommend rollback.
2. **Target tag.** The given tag or the previous one from rollout history; confirm it exists in the registry for
   each image repository. All images are kept on the same tag unless the profile says otherwise.
3. **Schema compatibility (gate).** List migrations between target and current (`git log --stat <target>..<current>
   -- <migrations dir>`). If any drops columns/tables, narrows types or transforms data, do NOT roll back; present
   the situation and the options (fix forward, hotfix deploy). Additive-only migrations (nullable column, new
   table) may be compatible with the old image; explain why. Never run a reverse migration against the live database.
4. **Plan and approval.** Write the exact commands, expected downtime (per the profile's update strategy) and
   affected components; get explicit approval. Do not proceed to step 5 without it.
5. **Execute (after approval).** One workload at a time: `kubectl --context <ctx> -n <ns> rollout undo
   deployment/<name> [--to-revision=N]`, then `rollout status --timeout=600s` for each.
6. **Verify.** Rerun the live-check: health URLs return their expected codes, pods ready, no restart increase.
7. **Realign the repo.** A manual rollback is overwritten by the next deploy: the faulty commit must be reverted
   (`git revert`, with the user's approval) before deploying again. State this plainly in the report.
8. **Report** (profile's report language): previous/new tags, commands run, verification results, remaining risk
   and the repo work still required.
