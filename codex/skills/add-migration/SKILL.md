---
name: add-migration
description: Create and review a database migration for a finished model change (configuration, designer, snapshot, permission chain, API contract) when the user explicitly invokes /add-migration.
---

# Add a migration

When the user invokes `$add-migration <Name>`, turn the schema change into a migration. The repo's
`AGENTS.md`/`CLAUDE.md` limits and its `Project profile` apply (the `Persistence` entry gives the migration
command, migrations directory, naming and conventions). This skill grants NO authority to apply the migration to
a database, commit, push or deploy. Without a Persistence entry, find the ORM's migration tooling in the repo and
ask the user to confirm the command before running it.

1. **Scope.** `git status --short`; preserve the user's changes. Read the changed entities and their mapping
   configuration. Use a similar existing migration in the migrations directory as the example.
2. **Finish the model, then generate.** Do not generate before entity and configuration are done. Check the
   profile's conventions: base entity (tenant/soft-delete filters), unique indexes with the soft-delete filter,
   plain-key reference validation, money/decimal rules. Add no default rows to lookup/reference data unless the user asked.
3. **Generate.** Verify the command via the profile's help, then use the profile's
   migration command with a name that follows existing naming (`Add…`/`Change…`). Prefer the project's wrapper over
   raw tool calls, since wrappers often clean stray folders.
4. **Inspect the output.** Migration, designer and model snapshot must change together. `Up` must contain only the
   intended difference (unrelated column/index changes mean the model needs another look) and `Down` must be able
   to undo it. For data-transforming migrations, write down the effect on existing rows (default, NULL, index build time).
5. **Permissions**, if the change adds one: follow the profile's chain (constant and catalog, permission seed,
   migration, read-only role lists, frontend permission codes).
6. **Contract.** If DTOs/endpoints changed too, regenerate the API types/OpenAPI with the profile's command; the
   generated files belong in the commit.
7. **Verify.** Build the backend and run the focused tests for the area (schema tests may need Docker). Apply the
   migration to the local database ONLY if the user asks. Never reset the database.
8. **Gate.** Apply the profile's finish gate: schema/migration/query/delete changes need the database reviewer's
   passing verdict; permission or tenant scope changes also need the security reviewer. Give them the diff and
   command output.
9. **Report** (profile's report language): migration name and files, `Up`/`Down` summary, effect on existing data,
   commands run and counts, checks that could not run (for example no Docker), reviewer verdicts.

Take the migration name from the user's invocation.
