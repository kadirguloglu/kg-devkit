---
paths:
  - "docs/**/*.md"
  - "**/README.md"
  - "**/ADR*.md"
---
# Documentation maintenance (kg-devkit)

Generic rules; the repo's own documentation rule and `Project profile` take precedence.

- Search for the heading/symbol/reference first, then read the relevant code. Check every active claim against the
  concrete implementation; do not present a dependency, comment or design intent as a working feature.
- Keep stable section ids, numbering and issue/bug history; fill a missing old section under the same id instead of
  renumbering or renaming files.
- Separate historical decisions and migration notes from current behavior. Link to the source for field and endpoint
  catalogs instead of copying them from code.
- If the fix needs a source-code change, report it separately instead of hiding it in a docs edit.
- Docs-only changes need reference/frontmatter/link and `git diff --check` verification. Never say tests were run when they were not.
