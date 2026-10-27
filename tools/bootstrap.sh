#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p tmp data evidence/screenshots-original evidence/carousel-ready evidence/test-results
python3 -m venv --without-pip .venv
curl -fsSL https://bootstrap.pypa.io/get-pip.py -o tmp/get-pip.py
.venv/bin/python tmp/get-pip.py --no-cache-dir
PIP_NO_CACHE_DIR=1 .venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/cli.py seed
PLAYWRIGHT_BROWSERS_PATH=$PWD/data/browsers TMPDIR=$PWD/tmp .venv/bin/python -m playwright install chromium
