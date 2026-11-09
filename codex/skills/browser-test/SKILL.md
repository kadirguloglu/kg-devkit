---
name: browser-test
description: Test only the new or changed frontend behavior in Chrome, when the user explicitly asks for a browser check of the current diff or a commit range.
---

# Browser test of a change

In the running dev app, use Chrome to test only the frontend changes that were just made.
Scope, environment, data and report rules live in the `frontend-browser-tester` agent definition.
Take the commit range, file or focus note from the user's invocation as the target; do not rely on
`$ARGUMENTS` expansion or Claude fork metadata.
Call the `frontend-browser-tester` role through the available sub-agent tool, passing the target and limits in the task text.
If the sub-agent tool/role is unavailable, read the definition and do the same check in the main session, and report that limitation.

- Empty target: take the working-tree changes; if the tree is clean, use `HEAD~1..HEAD` when the parent exists,
  otherwise `git show --root HEAD` for an initial commit. If there are no commits or changes, report no target.
- A commit range (`abc123..HEAD`, `HEAD~3..HEAD`): take the frontend diff of that range.
- An existing file path (check that it exists): narrow the scope to that file. Anything else is a free-text note:
  use it as a focus hint within the default target above.

Do not change code or commit/push; report any defect with repro steps.
