---
paths:
  - "**/tests/**"
  - "**/test/**"
  - "**/*.test.*"
  - "**/*.spec.*"
  - "**/*Tests.cs"
  - "**/*_test.go"
  - "**/test_*.py"
---
# Test discipline (kg-devkit)

Generic rules; the repo's own test rules and `Project profile` commands take precedence.

- Test only the new or changed behavior and its connections (callers/callees, shared contracts the diff touches).
  Run the focused command first; widen only when a shared fixture/contract changed. The full suite runs only when
  the user asks or the release flow demands it.
- Find the nearest existing test and fixture before writing a new one; reuse helpers instead of inventing parallel ones.
- Cover success, specific failure codes, boundaries, forbidden/foreign-owner paths and deleted/in-use records as the
  change warrants. A bug gets a regression test. No filler tests.
- Keep the real implementation for the behavior under test; mock only true boundaries (network, clock, randomness).
  Do not replace database behavior with trivial mocks when the project has a real-database fixture.
- Never weaken, skip or loosen an assertion to make a test pass. A failing architecture/guard test means a rule was
  broken: fix the code, or add a justified, minimal allow-list entry.
- Tell timing/environment failures from application defects: rerun the failing test alone, give a reproducer.
  Prefer lowering a test's cost to raising its timeout.
- If a test exposes a production defect and you do not own that code, report it with the evidence instead of editing it.
- Report the exact command, selection, counts, failures and what was not run.
