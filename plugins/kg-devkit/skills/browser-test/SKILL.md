---
name: browser-test
description: Test only the new or changed frontend behavior in Chrome, when the user explicitly asks for a browser check of the current diff or a commit range.
disable-model-invocation: true
user-invocable: true
argument-hint: "[commit range | file | focus note]"
context: fork
agent: frontend-browser-tester
---

# Browser test of a change

In the running dev app, use Chrome to test only the frontend changes that were just made.
Scope, environment, data and report rules live in the agent definition; this skill only supplies the target.

Target: $ARGUMENTS

- Empty target: take the working-tree changes; if the tree is clean, use `HEAD~1..HEAD`.
- A commit range (`abc123..HEAD`, `HEAD~3..HEAD`): take the frontend diff of that range.
- A file or a free-text note (for example "default interest start date"): narrow the scope to it.

Do not change code or commit/push; report any defect with repro steps.
