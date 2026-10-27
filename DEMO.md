# Demonstrate with Codex

Start the local tools, then ask Codex:

> Give me my morning brief. Inspect this repository's four local mock platforms using the CLI. Rank three executable opportunities in under 200 words. Describe the exact local actions and wait for my approval.

Useful reads:

```sh
.venv/bin/python tools/cli.py snapshot
.venv/bin/python tools/cli.py creators
.venv/bin/python tools/cli.py retention
.venv/bin/python tools/cli.py opportunities
.venv/bin/python tools/cli.py reconcile
```

Codex-authored proposed content is included in `docs/P*-v1.json`. To prepare the frozen action sets as **PENDING**, without writing business artifacts:

```sh
.venv/bin/python tools/prepare_proposals.py
```

After the user has actually approved the specific creator action set with `1`, Codex can run:

```sh
.venv/bin/python tools/cli.py approve --id P1-growth-v1 --approval-text 1
.venv/bin/python tools/cli.py execute --id P1-growth-v1
.venv/bin/python tools/cli.py verify --id P1-growth-v1
```

Do not copy the approval command before receiving that actual approval. Options 2 and 3 prepare conversion and retention drafts; approve only what the user selects. The screenshot example's prior approval is historical evidence, never authorization for a new run.

View Creator CRM → Campaign assignments, Outreach drafts, Tasks and Execution proof. UGC Overview shows saved concepts; its Experiments tab shows the test design. All messages remain NOT SENT. No send API or live connection exists.

## Capture genuine proof

```sh
./tools/capture.sh --after
.venv/bin/python tools/export_carousel.py
```

Capture outputs go under `evidence/`. Copy the newly captured/exported files into `screenshots/` only after independently verifying the records. Chromium's sandbox stays enabled; the script uses a disposable project-local profile, with no host browser credentials mounted.

The daily brief was delivered in the actual Codex conversation. Automated capture of that application window was unavailable. Its exact text is included in `docs/DAILY-BRIEF.md`. There is deliberately no fake Codex chat image. To create slide 1, capture the real conversation manually, preserve the untouched original, and frame it on a 1080×1350 canvas with “Your AI knows what matters today.” and “LOCAL POC · SYNTHETIC DATA”.

## Archive and cleanup

`./archive.sh` snapshots the project database and bundles source, documentation and proof; it excludes caches, dependencies and local temporary files. Validate using the sibling SHA-256 file. Extract to an empty folder, bootstrap, then copy `data/restore-snapshot.sqlite` to `data/business.sqlite` to retain archived state.

`./cleanup.sh` prints its exact targets and requires `REMOVE`. Stop the service first. Archives, source and proof screenshots are preserved. Do not remove archives without separate authorization.
