# SEO report contract

Use this shared contract for web SEO findings and handoffs. Keep reports proportional to the requested scope; do not turn a narrow question into a full audit.

## Evidence and status

- Identify scope, project context, target platform/market/language, and evidence sources when relevant.
- Separate observed facts from hypotheses and unverified claims. Label missing evidence `UNKNOWN` or `NEEDS: <evidence>`.
- Source inspection must cite `path:line` when possible. Live observations must cite the URL and supplied observation context/date. Source code does not prove deployed behavior, indexing or rankings.
- Never invent numeric traffic, impressions, clicks, rank, volume, difficulty, conversion, uplift, or causal impact. State source, period and metric definition for supplied numbers.
- Findings should include severity, business impact (verified or potential), recommendation, validation method and success metric when applicable. Technical findings should add current/expected behavior, acceptance criteria and implementation handoff.
- Distinguish `NOT-APPLICABLE` from missing evidence. Specialists may use `STATUS: COMPLETE`, `PARTIAL`, `BLOCKED`; local/international specialist may use `STATUS: NOT-APPLICABLE`.

## Severity and priority

For a finding, use severity `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, or `INFO`; explain the concrete consequence and confidence. Do not call a risk a confirmed business loss without measurement.

For roadmap work, use P0 (critical indexing/security/business risk), P1 (high impact and actionable), P2 (meaningful improvement), P3 (low urgency/optional). Add effort, risk and confidence separately. These are triage labels, not forecasts.

## Handoff packet

The main session should pass only relevant context to a specialist: bounded question, profile details already in context, URLs/files and lines or diff, supplied crawl/analytics/competitor evidence, market/language, limits, and requested output. Avoid repeating a full repository scan. A specialist recommends further work to the main session; it does not start another agent.

The main session owns actual delegation, deduplication, parallel execution, conflict resolution and developer handoff. Existing engineering agents implement website code changes; SEO agents do not. Route app store listing metadata to ASO. Web-to-app landing page search optimization stays with SEO, with a narrow ASO handoff only if store listing details matter.
