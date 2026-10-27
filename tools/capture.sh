#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p tmp/browser-home tmp/browser-tmp
chmod 777 tmp/browser-home tmp/browser-tmp evidence/screenshots-original evidence/test-results evidence
# No host browser profiles, credentials, or home directory are mounted.
exec bwrap --unshare-all --share-net --uid 1000 --gid 1000 --cap-drop ALL --die-with-parent --new-session --ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64 --proc /proc --dev /dev --ro-bind "$PWD" /work --bind "$PWD/evidence" /work/evidence --bind "$PWD/tmp/browser-home" /work/tmp/browser-home --bind "$PWD/tmp/browser-tmp" /tmp --chdir /work --setenv HOME /work/tmp/browser-home /work/.venv/bin/python /work/tools/capture.py "$@"
