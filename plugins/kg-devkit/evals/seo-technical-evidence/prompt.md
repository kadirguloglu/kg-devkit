---
max_turns: 8
allowed_tools: [Agent, Read, Grep, Glob]
---

Use the kg-devkit:seo-technical-specialist subagent in the foreground with exactly this prompt: 'I have no SEO profile. Inspect this supplied mock evidence only: Next.js app uses client-rendered product routes and sends an empty server HTML shell; canonical points to a staging host; robots.txt says `Disallow: /`; no sitemap file is present in this repository. The user also asks whether adding FAQPage JSON-LD guarantees a Google rich result, but supplies no current eligibility documentation. Do not claim anything about a live URL or deployed index status. Report evidence, limits, priority, recommendation and validation.'
Then return its report verbatim.
