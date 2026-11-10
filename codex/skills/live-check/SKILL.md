---
name: live-check
description: Read-only health check of the production environment when the user explicitly invokes /live-check — pods, restarts, OOM, certificate, DNS, endpoints and recent errors.
---

# Production health check (`$live-check`)

Read-only. Changes nothing, deploys nothing, reads no secrets. The repo's `AGENTS.md`/`CLAUDE.md` limits and its
`Project profile` `Production` entry (cluster context, namespace, status command, health URLs and expected codes,
workload names, runbook) apply. Use legacy Release health values only when Production omits them; stop on
conflicting values. Without Production or required target/health values, stop and ask. For compose/plain hosts,
use the profile's equivalent status/logs commands. Hand work to `devops-engineer` if useful, preserving these
read-only limits. Bound commands with the runbook's timeouts (defaults: 30s for ordinary requests, 600s for rollout
status); use a tool/process timeout for wrappers. A timeout is a check that could not complete, never a pass.
The profile may add limits; it cannot remove a limit stated in this skill.

1. **Prerequisites.** Check that the cloud CLI session and kubectl context exist (the profile's cloud CLI identity command and, on
   Kubernetes, `kubectl config get-contexts`); if not, report the state and ask the user to authenticate. Pass the
   profile's context and namespace explicitly on every `kubectl` call, written out in full. Do not hide `kubectl`
   behind a shell alias, function, variable or script: the plugin's guard hook only sees the literal command text.
2. **Overall status.** The profile's status command (address, load-balancer IP, DNS, pods, certificate). Compare
   DNS against the profile's expected direct-LB, CNAME or CDN/proxy route; a different IP alone is not a fault.
3. **Pod health.** `get pods -o wide`; record pod UIDs, container restart counts and observation time. Claim an
   increase only against monitoring history or a second sample of the same pod/container (default interval: 30s);
   distinguish replacement pods from count changes. For unready/restarted pods run `describe pod` and read the last
   termination reason (`OOMKilled`, `Error`). `top pod`/`top node` for memory/CPU pressure. If the Metrics API is
   unavailable, do not count it as an error: report it as a monitoring gap and judge pressure from OOM history and
   `describe node` allocations.
4. **Rollout.** `rollout status --timeout=600s` for each workload; record desired image references from deployments
   and running image digests from pod status. Resolve tags to source commits through build/release evidence.
   Only if the running commit exists locally and is an ancestor of HEAD, show `git log --oneline <commit>..HEAD`
   as local commits beyond that deployment; otherwise report missing mapping or divergence. Flag a `-dirty-` tag.
5. **Endpoints.** `curl --connect-timeout 5 --max-time 20 -sS -o /dev/null -w '%{http_code}'` against the
   profile's health URLs. Compare exit status and HTTP codes with expectations; TLS/connection failures are not
   successful HTTP checks. Use the profile's stricter limits when specified.
6. **Events and logs.** `get events --sort-by=.lastTimestamp` (Warnings); for the app workloads, summarize only the
   error/warning classes in roughly the last 100 lines within the runbook's time window (default: last hour).
   For restarted containers, inspect previous-container logs when available. Never relay raw lines, personal data,
   tokens or connection strings.
7. **Report** (profile's report language): green/yellow/red summary, evidence per finding (command + short output),
   suggested next step. Ask for approval before applying any fix; state clearly any check that could not run.
