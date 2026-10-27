#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
ROOT=$PWD
mkdir -p data tmp
chmod 777 data
[ ! -f data/business.sqlite ] || chmod 666 data/business.sqlite
exec bwrap --unshare-all --share-net --uid 1000 --gid 1000 --die-with-parent --new-session --cap-drop ALL --ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64 --proc /proc --dev /dev --tmpfs /tmp --ro-bind "$ROOT" /work --bind "$ROOT/data" /work/data --chdir /work /work/.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port "${FOUNDEROS_PORT:-8775}"
