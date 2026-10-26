---
name: live-check
description: Read-only health check of the production environment when the user explicitly invokes /live-check — pods, restarts, OOM, certificate, DNS, endpoints and recent errors.
---

# Production health check (`$live-check`)

Read-only. Changes nothing, deploys nothing, reads no secrets. The repo's `AGENTS.md`/`CLAUDE.md` limits and its
`Project profile` `Production` entry (cluster context, namespace, status command, health URLs and expected codes,
workload names, runbook) apply. Without a Production entry, stop and ask. Hand the work to the `devops-engineer`
agent if useful.

1. **Prerequisites.** Check that the cloud CLI session and kubectl context exist (for example `doctl account get`,
   `kubectl config get-contexts`); if not, report the state and ask the user to authenticate. Pass the profile's
   context and namespace on every `kubectl` call; keep the flags in a shell function, not a variable (zsh does
   not word-split variables), e.g. `k() { kubectl --context <ctx> -n <ns> "$@"; }`.
2. **Overall status.** The profile's status command (address, load-balancer IP, DNS, pods, certificate). Point out
   a DNS record that differs from the load-balancer IP.
3. **Pod health.** `get pods -o wide`; for unready or restart-increasing pods run `describe pod` and read the last
   termination reason (`OOMKilled`, `Error`). `top pod`/`top node` for memory/CPU pressure. If the Metrics API is
   unavailable, do not count it as an error: report it as a monitoring gap and judge pressure from OOM history and
   `describe node` allocations.
4. **Rollout.** `rollout status` for each workload and the running image tags (`get deploy -o jsonpath`). If tags
   are commit SHAs, list unreleased commits with `git log --oneline <tag>..HEAD` and flag a `-dirty-` tag.
5. **Endpoints.** `curl -sS -o /dev/null -w '%{http_code}'` against the profile's health URLs and compare with
   the expected codes.
6. **Events and logs.** `get events --sort-by=.lastTimestamp` (Warnings); for the app workloads, summarize only the
   error/warning classes in roughly the last 100 lines. Never relay raw lines, personal data, tokens or connection strings.
7. **Report** (profile's report language): green/yellow/red summary, evidence per finding (command + short output),
   suggested next step. Ask for approval before applying any fix; state clearly any check that could not run.
