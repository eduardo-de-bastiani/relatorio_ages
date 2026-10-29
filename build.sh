#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Source trees and tracked PDFs are never output destinations.
# template = unchanged baseline; fixture = synthetic harness test;
# document = future memorial, which does not exist in this phase.
exec python3 "$SCRIPT_DIR/scripts/migration.py" build "$@"
