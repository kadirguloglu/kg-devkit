# Default finish gate (ÖNERİ; hedef konum: `plugins/kg-devkit/references/finish-gate-default.md`)

Used by `release`, `verify-change` and `add-migration` **only when the Project profile has no `Finish gate` entry**.
A profile gate always wins; this table never adds a reviewer to a profile that defines its own gate.
Triggers are evaluated on the changed paths and the diff, not on the task description.

| Change in the diff | Required reviewer | Evidence the caller passes |
| --- | --- | --- |
| Migration files, entity/mapping configuration, raw SQL, new query filters, index changes | `database-reviewer` | diff, migration output, focused test output |
| Authentication, authorization, permission lists, tenant/owner filters, file upload/download, cookies/CORS/CSRF | `tenant-security-reviewer` | diff, tests for forbidden/foreign access |
| Endpoint routes, DTOs, enums, status/error codes, generated API types | `api-contract-reviewer` | diff, regenerated schema/types diff |
| Manifests or lockfiles of any package manager, CI action versions | `dependency-supply-chain-reviewer` | diff, audit command output if the profile names one |
| Nothing above | none (do not call reviewers "to be safe") | n/a |

`performance-reviewer` and `observability-reviewer` are advisory by default: call them only when the profile's gate
names them or the user asks.

Rules for every gate, profile-defined or default:
1. Run triggered reviewers in parallel (they are read-only and independent); never run the same reviewer twice on an
   unchanged diff.
2. A reviewer that is unavailable, returns `VERDICT: FAIL`/`UNCLEAR`, or returns no `VERDICT:` line blocks the
   commit/handoff. Report it as blocked; never infer a pass.
3. After fixing findings, re-run only the reviewers whose trigger paths changed again.
