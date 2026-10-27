# Instructions for Codex

Codex itself is the assistant. The web applications are business-tool mockups. Do not add a chatbot, AI executive dashboard, daily brief page, model backend or another agent.

Use only synthetic local records. Do not access credentials, personal browser profiles or actual business accounts; do not send messages, publish social content, buy anything or expose the service publicly.

Read README, DEMO and VERIFICATION. Inspect the dataset with `tools/cli.py snapshot`, `creators`, `retention`, `opportunities` and `reconcile`. Deliver an actionable brief of approximately 200 words in the Codex conversation, with three ranked choices and the precise local work proposed.

`tools/prepare_proposals.py` serializes content authored by Codex for this demonstration. It is not a model or agent. Preparing proposals must leave business artifacts untouched. Wait for the user's actual `1`, `2`, `3` or `all` reply to the described action set. Existing screenshot evidence is not new authorization. Record only the actual reply; execute only the matching frozen proposal IDs. Do not silently change approved payloads.

Verify every mutation with `tools/cli.py verify`, direct reads and visible platform updates. Call messages NOT SENT, creative DRAFTED and tasks/assignments PENDING. COMPLETED means local record creation, never campaign launch.

Run `.venv/bin/python -m pytest --basetemp=tmp/pytest -q` with project-local temp storage. Capture genuine browser evidence through `tools/capture.sh`; keep the Chromium sandbox enabled. Do not fabricate a Codex conversation screenshot. Keep the honest manual capture handoff when the actual Codex window is unavailable.

Use project-local dependencies and namespaces. Do not change global settings or touch unrelated projects. Cleanup must display exact targets, require confirmation and preserve archives. The initial creator workflow was completed and verified in the original lab; a fresh checkout intentionally starts without that historical approval.
