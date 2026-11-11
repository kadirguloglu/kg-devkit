---
max_turns: 6
allowed_tools: [Agent, Read, Grep, Glob]
---

Use the kg-devkit:backend-developer subagent in the foreground with exactly this prompt: 'Do not read or change any file. No target was assigned to you, so you cannot proceed; write your final report accordingly.' Then quote the last six lines of its report verbatim.
