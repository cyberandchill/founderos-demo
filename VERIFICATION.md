# Observed verification

This is a functioning synthetic local demo, not a claim about live business operations. The original creator workflow was executed after the actual user reply `1`.

## Approved execution

- Proposal: `P1-growth-v1`; approval source and payload digest are preserved in the evidence.
- 19 persistent records: five concepts, three briefs, three NOT SENT outreach drafts, three pending assignments, one draft UGC experiment and four pending tasks.
- Every approved payload field independently matched its database row.
- Running the completed proposal again returned zero new records and `duplicate_prevented: true`.
- API counts matched direct database counts. Options 2 and 3 remained unapproved and pending.
- The browser displayed the created records before execution proof was captured.

[Record verification](evidence/verified-execution.json) · [Execution result](evidence/approved-execution.json) · [Duplicate check](evidence/idempotency-recheck.json)

## Executed checks

| Check group | Result |
| --- | --- |
| Original automated suite | 28 passed, 0 failed |
| Original post-approval browser checks | 12 passed, 0 JavaScript errors |
| Original archive/restore verification | 5 passed; all 77 restored file hashes matched; completed workflow verified in the restored snapshot |
| Public export automated suite | 28 passed, 0 failed |
| Public export isolated cold startup | 7 checks passed: all four routes, reconciled seed order count, computed 7× baseline, no inherited approval/drafts |

The public export was separately tested, including the portable namespace launcher. Its runtime starts from fresh synthetic seed data. The copied historical evidence describes the original approved run, not an automatic approval in a fresh clone.

The original and exported suites use isolated test databases. Test-generated approvals never authorize actual demonstration work. Before the export suite ran successfully, its first invocation failed to create the missing project-local temporary parent; the directory was created and the complete suite rerun. One Starlette/httpx dependency deprecation warning remains; no failing tests remain.

Run tests after bootstrap:

```sh
mkdir -p tmp
TMPDIR=$PWD/tmp .venv/bin/python -m pytest --basetemp=tmp/pytest -q
```

Tests exercise seeding/idempotency, foreign keys and attribution, exact baseline calculation, ranking, all proposed local workflows, draft/task creation, approval/rejection, payload tamper checks, transaction rollback, duplicate prevention, socket-connect denial during workflow execution, page routes, local writes, Host/mutation-header validation and campaign/cohort/flow relationships.

## Screenshot provenance and limitations

Two final 1080×1350 exports are composites/annotations of genuine browser screenshots. Original captures and hashes are included. The execution screenshot was captured after actual approval, database mutation and verification. It is not a generated illustration.

The actual Codex application window was unavailable to automated capture. The daily brief is provided as exact text plus an honest manual capture handoff, not a fabricated chat screenshot. [Daily brief](docs/DAILY-BRIEF.md).

The four named platforms are local mockups. No live Shopify/Klaviyo/CRM connection, model API, email delivery, social messaging, payment, public app hosting or production credentials exist. Marketing figures, customers, creators, fees and attributions are synthetic. Views do not establish sales lift. Expected business impact is a hypothesis, not a measured outcome.

## Simplified four-image pitch

Four new read-only focus views show the computed creator outlier, the five persisted concepts, the three actual NOT SENT outreach drafts and the approved record totals. Eight untouched full/element screenshots were captured, then four 1080×1350 annotated exports were composed without changing UI contents. Six new browser checks passed, including live creator selection and opening a saved full outreach message; no JavaScript errors or business-record mutations occurred. The 28-case suite passed again. An initial broad test invocation found duplicate test modules in nested archive/export directories; `pytest.ini` now scopes collection to `tests`, and the full suite was rerun successfully. The older two proof images remain available as supplemental evidence.
