---
name: seo-audit
description: Coordinates a scoped, evidence-led web SEO audit by selecting only relevant SEO specialists, consolidating findings and producing a prioritized implementation backlog. Use for multi-area SEO audits, not a single technical question or one content brief.
---

# Scoped web SEO audit

Use this workflow in the main session. The main session is the only layer that delegates work; specialist agents never spawn other agents. Read `## Project profile` from `AGENTS.md`/`CLAUDE.md` if it is not already in context, and use its optional `SEO` section. Follow `Report language`; otherwise use the user's language. Missing optional SEO fields do not block work.

1. Bound the request: site/repository scope, URLs, target markets/languages, date range and available evidence. Inspect only relevant files. Separate source inspection from supplied live crawl/search/analytics observations.
2. Select only the needed specialists: `seo-technical-specialist`, `seo-keyword-research-specialist`, `seo-content-strategist`, `seo-offpage-specialist`, `seo-data-analyst`, `seo-ai-search-specialist`, `seo-local-international-specialist`. For an audit spanning specialties, use `seo-lead` to plan and consolidate. Do not run the entire team for a narrow question. Independent bounded tasks can be delegated in parallel by the main session.
3. Give each specialist the same relevant profile context and a bounded task packet: question, URLs/files and evidence, market/language, limits and requested output. Do not make them repeat discovery already done.
4. Consolidate duplicates and disagreements against evidence. Mark facts, hypotheses and unknowns separately. Route implementation to the appropriate existing developer agent. Website SEO belongs to SEO; app-store listings belong to ASO; web-to-app landing pages stay with SEO, with a narrow ASO handoff only when store listings are relevant.
5. Build an actionable backlog. Use P0/P1/P2/P3 triage, state confidence, effort, risk, owner/handoff, acceptance criterion, validation and success metric. Never invent a forecast or claim performance improved without measurements.

Use `references/seo-report-contract.md` for the shared evidence, severity, status and handoff contract. SEO audits are read-only. Do not modify production code, publish CMS content, change Search Console/GA4, publish robots.txt/sitemaps, contact external parties, read secrets, or create paid campaigns/accounts. Ask for explicit authorization before any such action; route code changes to developers. The profile may add limits but does not grant these permissions.

Return scope, project context, selected specialists and rationale, evidence, consolidated findings, conflicts/unknowns, prioritized backlog, success measures, implementation handoff and status.
