#!/bin/sh
set -eu
cd "$(dirname "$0")"
ROOT=$(pwd -P)
[ -f "$ROOT/app/db.py" ] && [ -f "$ROOT/tools/cli.py" ] || exit 1
printf 'Exact removal targets:\n%s\n%s\n%s\n%s\n' "$ROOT/.venv" "$ROOT/tmp" "$ROOT/data/browsers" "$ROOT/data/business.sqlite"
printf 'Source, evidence and archives are preserved. Stop the project service first.\nType REMOVE to confirm: '
read -r confirmation
[ "$confirmation" = REMOVE ] || exit 1
if curl -fsS http://127.0.0.1:8775/api/state >/dev/null 2>&1; then echo 'Port 8775 is active; stop the project service first.'; exit 1; fi
rm -rf -- "$ROOT/.venv" "$ROOT/tmp" "$ROOT/data/browsers"
rm -f -- "$ROOT/data/business.sqlite"
