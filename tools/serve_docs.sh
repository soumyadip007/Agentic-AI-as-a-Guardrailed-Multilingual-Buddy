#!/usr/bin/env bash
# Serve MkDocs documentation locally (hosted docs site).
set -euo pipefail
cd "$(dirname "$0")/.."
exec mkdocs serve -a "${MKDOCS_ADDR:-127.0.0.1:8001}"
