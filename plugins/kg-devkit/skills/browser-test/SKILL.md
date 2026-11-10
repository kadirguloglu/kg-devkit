---
name: browser-test
description: Test only the new or changed frontend behavior in Chrome, when the user explicitly asks for a browser check of the current diff or a commit range.
disable-model-invocation: true
argument-hint: "[commit range | file | focus note]"
context: fork
agent: frontend-browser-tester
background: false
---

# Browser test of a change

In the running dev app, use Chrome to test only the frontend changes that were just made.
Scope, environment, data and report rules live in the agent definition; this skill only supplies the target.

Target: $ARGUMENTS

An empty target means the default target defined in the agent's scope rules (working tree, else the last commit).

Do not change code or commit/push; report any defect with repro steps. The profile may add limits; it cannot remove a limit stated in this skill.
